import type { Readable, Writable } from 'node:stream';
import { responseSchema, type ErrorObject, type RequestId } from './jsonrpc.ts';
import { methods, type CoreApi, type MethodName, type MethodParams, type MethodResult } from './methods.ts';
import { createNdjsonDecoder, encodeMessage } from './ndjson.ts';

/** The core answered with a JSON-RPC error (unknown method, invalid params, invalid repo…). */
export class JsonRpcError extends Error {
  override name = 'JsonRpcError';
  readonly code: number;
  readonly data: unknown;

  constructor(error: ErrorObject) {
    super(error.message);
    this.code = error.code;
    this.data = error.data;
  }
}

type PendingCall = {
  method: MethodName;
  resolve: (result: unknown) => void;
  reject: (error: Error) => void;
};

/**
 * Typed client of the core. `writable` carries requests to the core and
 * `readable` brings its responses back (for a child process: its stdin and stdout).
 * Several calls can be in flight: each response is matched to its call by `id`.
 */
export function createClient({
  readable,
  writable,
  logError = console.error,
}: {
  readable: Readable;
  writable: Writable;
  /** Where messages that match no call are reported. Defaults to stderr. */
  logError?: (...args: unknown[]) => void;
}): CoreApi {
  const decoder = createNdjsonDecoder();
  const pending = new Map<RequestId, PendingCall>();
  let nextId = 1;
  let closed = false;

  readable.setEncoding('utf8');
  readable.on('data', (chunk: string) => {
    for (const line of decoder.push(chunk)) {
      if (line.ok) settle(line.value);
    }
  });
  // Once the core is gone, nothing will ever answer: fail fast instead of hanging.
  const close = () => {
    closed = true;
    for (const call of pending.values()) call.reject(connectionClosed());
    pending.clear();
  };
  readable.on('end', () => {
    for (const line of decoder.end()) {
      if (line.ok) settle(line.value);
    }
    close();
  });
  readable.on('close', close);
  // Writing to a core that has died fails with EPIPE, reading may fail too.
  // Unhandled, these 'error' events would crash the Electron main process;
  // they mean the same as a close.
  writable.on('error', close);
  readable.on('error', close);

  function settle(message: unknown): void {
    const response = responseSchema.safeParse(message);
    if (!response.success) {
      // A broken envelope that still names one of our calls: fail that call
      // rather than leaving it waiting forever.
      const id = rawId(message);
      const call = id === undefined ? undefined : pending.get(id);
      if (id !== undefined && call) {
        pending.delete(id);
        call.reject(new Error(`invalid response for ${call.method}: ${response.error.message}`));
      }
      return;
    }
    if (response.data.id === null) {
      // The core could not read one of our requests (-32700, -32600): no call
      // to blame, but it must not go unnoticed.
      if ('error' in response.data) logError('[core] error without id:', response.data.error);
      return;
    }
    const call = pending.get(response.data.id);
    if (!call) return;
    pending.delete(response.data.id);

    if ('error' in response.data) {
      call.reject(new JsonRpcError(response.data.error));
      return;
    }
    // The core is another process: its data is external and gets validated too.
    const result = methods[call.method].result.safeParse(response.data.result);
    if (result.success) {
      call.resolve(result.data);
    } else {
      call.reject(new Error(`invalid result for ${call.method}: ${result.error.message}`));
    }
  }

  return {
    call<M extends MethodName>(method: M, params: MethodParams<M>): Promise<MethodResult<M>> {
      if (closed) return Promise.reject(connectionClosed());
      const id = nextId++;
      return new Promise<MethodResult<M>>((resolve, reject) => {
        // Encode first: if the params cannot become JSON (a BigInt, say), the
        // promise rejects and nothing is left behind in `pending`.
        const line = encodeMessage({ jsonrpc: '2.0', id, method, params });
        // `resolve` receives a value already checked against the result schema of `method`.
        pending.set(id, { method, resolve: resolve as (result: unknown) => void, reject });
        writable.write(line);
      });
    },
  };
}

/** The `id` of a message we could not validate, if it has one. */
function rawId(message: unknown): RequestId | undefined {
  if (typeof message !== 'object' || message === null || !('id' in message)) return undefined;
  const { id } = message;
  return typeof id === 'string' || typeof id === 'number' ? id : undefined;
}

function connectionClosed(): Error {
  return new Error('connection closed: the core is not running');
}
