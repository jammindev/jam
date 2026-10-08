import type { DatabaseSync } from 'node:sqlite';
import type { Readable, Writable } from 'node:stream';
import {
  createNdjsonDecoder,
  encodeMessage,
  ErrorCode,
  isMethodName,
  methods,
  requestSchema,
  type DecodedLine,
  type ErrorObject,
  type MethodName,
  type MethodResult,
  type ParsedParams,
  type RequestId,
  type Response,
  type SuccessResponse,
} from '@jam/protocol';
import { z } from 'zod';
import { listCommands } from './commands.ts';
import { addRepo, listRepos, RepoInvalidError } from './repos.ts';

/** One handler per protocol method; it receives params already validated by zod. */
export type Handlers = {
  [M in MethodName]: (params: ParsedParams<M>) => MethodResult<M> | Promise<MethodResult<M>>;
};

export function createHandlers(db: DatabaseSync): Handlers {
  return {
    ping: () => ({ pong: true, pid: process.pid }),
    'repos.list': () => listRepos(db),
    'repos.add': (params) => addRepo(db, params),
    'commands.list': () => listCommands(),
  };
}

type ServeOptions = {
  input: Readable;
  output: Writable;
  handlers: Handlers;
  /** Where unexpected errors are reported. Defaults to stderr, which stays free for logs. */
  logError?: (error: unknown) => void;
};

/**
 * Reads NDJSON requests from `input` and writes one response per request to
 * `output`. Requests run concurrently: a slow one does not hold the others,
 * and responses go out in completion order (the client matches them by id).
 * Resolves once `input` has ended and every pending response is written.
 * A broken stream also ends it, so the caller can still close the database:
 * a failing input, or a failing output (the app vanished: EPIPE).
 */
export function serve({ input, output, handlers, logError = console.error }: ServeOptions): Promise<void> {
  const decoder = createNdjsonDecoder();
  const pending = new Set<Promise<void>>();
  let outputBroken = false;
  input.setEncoding('utf8');

  // One decoded line → one response, written as soon as it is ready.
  function answer(line: DecodedLine): void {
    const response = line.ok
      ? handleMessage(line.value, handlers, logError)
      : Promise.resolve(errorResponse(null, line.error));
    const work = response
      .then((message) => {
        // Nobody is listening any more: drop the response.
        if (!outputBroken) output.write(encodeMessage(message));
      })
      .finally(() => pending.delete(work));
    pending.add(work);
  }

  const onData = (chunk: string) => decoder.push(chunk).forEach(answer);
  input.on('data', onData);

  return new Promise((resolve) => {
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      void Promise.all(pending).then(() => resolve());
    };

    input.on('end', () => {
      // A last request without its trailing newline is still answered.
      decoder.end().forEach(answer);
      finish();
    });
    input.on('error', (error) => {
      logError(error);
      finish();
    });
    output.on('error', (error) => {
      logError(error);
      outputBroken = true;
      // No one can read our answers: stop taking requests, so the process can exit.
      input.off('data', onData);
      input.destroy();
      finish();
    });
  });
}

/** Turns one decoded JSON value into its JSON-RPC response. Never throws. */
export async function handleMessage(
  message: unknown,
  handlers: Handlers,
  logError: (error: unknown) => void = console.error,
): Promise<Response> {
  const request = requestSchema.safeParse(message);
  if (!request.success) {
    return errorResponse(readableId(message), { code: ErrorCode.InvalidRequest, message: 'Invalid request' });
  }
  const { id, method } = request.data;

  if (!isMethodName(method)) {
    return errorResponse(id, { code: ErrorCode.MethodNotFound, message: `Method not found: ${method}` });
  }

  // Methods without params may omit them; every params schema expects an object.
  const params = methods[method].params.safeParse(request.data.params ?? {});
  if (!params.success) {
    return errorResponse(id, {
      code: ErrorCode.InvalidParams,
      message: z.prettifyError(params.error),
      data: params.error.issues,
    });
  }

  try {
    // TypeScript cannot link `handlers[method]` to the params of that same method
    // when `method` is a union; the zod parse above guarantees they match.
    const handler = handlers[method] as (params: unknown) => ResultValue | Promise<ResultValue>;
    const result = await handler(params.data);
    return { jsonrpc: '2.0', id, result };
  } catch (error) {
    if (error instanceof RepoInvalidError) {
      return errorResponse(id, { code: ErrorCode.RepoInvalid, message: error.message });
    }
    // Details stay in the logs: the client only learns that something broke.
    logError(error);
    return errorResponse(id, { code: ErrorCode.InternalError, message: 'Internal error' });
  }
}

/** Any JSON value except `undefined`: a success response always carries a result. */
type ResultValue = SuccessResponse['result'];

function errorResponse(id: RequestId | null, error: ErrorObject): Response {
  return { jsonrpc: '2.0', id, error };
}

/** JSON-RPC asks to echo the id of an invalid request when it can be read. */
function readableId(message: unknown): RequestId | null {
  if (typeof message !== 'object' || message === null || !('id' in message)) return null;
  const { id } = message;
  return typeof id === 'string' || (typeof id === 'number' && Number.isInteger(id)) ? id : null;
}
