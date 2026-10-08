import { mkdirSync, mkdtempSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { PassThrough } from 'node:stream';
import { createNdjsonDecoder, ErrorCode, type Response } from '@jam/protocol';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { openDatabase } from '../src/db/database.ts';
import { createHandlers, serve, type Handlers } from '../src/server.ts';

let dir: string;
beforeEach(() => {
  // realpath: repos are stored by real path, and macOS's temp folder sits behind a symlink.
  dir = realpathSync(mkdtempSync(join(tmpdir(), 'jam-server-')));
});
afterEach(() => {
  rmSync(dir, { recursive: true, force: true });
});

/** Runs the server on in-memory streams and collects every response it writes. */
function startServer(handlers: Handlers) {
  const input = new PassThrough();
  const output = new PassThrough();
  output.setEncoding('utf8');
  const decoder = createNdjsonDecoder();
  const responses: Response[] = [];
  const waiters: Array<() => void> = [];
  output.on('data', (chunk: string) => {
    for (const line of decoder.push(chunk)) {
      if (line.ok) responses.push(line.value as Response);
    }
    for (const wake of waiters.splice(0)) wake();
  });
  const done = serve({ input, output, handlers });

  return {
    /** Strings and bytes are written as they are; anything else becomes one JSON line. */
    send(message: unknown) {
      const raw = typeof message === 'string' || Buffer.isBuffer(message);
      input.write(raw ? message : `${JSON.stringify(message)}\n`);
    },
    async waitFor(count: number): Promise<Response[]> {
      while (responses.length < count) {
        await new Promise<void>((wake) => waiters.push(wake));
      }
      return responses;
    },
    async stop() {
      input.end();
      await done;
    },
  };
}

function request(id: number, method: string, params?: unknown) {
  return { jsonrpc: '2.0', id, method, params };
}

describe('server', () => {
  it('answers ping with its process id', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send(request(1, 'ping', {}));
    expect(await server.waitFor(1)).toEqual([{ jsonrpc: '2.0', id: 1, result: { pong: true, pid: process.pid } }]);
    await server.stop();
  });

  it('treats missing params as an empty object', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send(request(1, 'repos.list'));
    expect(await server.waitFor(1)).toEqual([{ jsonrpc: '2.0', id: 1, result: [] }]);
    await server.stop();
  });

  it('adds then lists a repo', async () => {
    const path = join(dir, 'house');
    mkdirSync(join(path, '.git'), { recursive: true });
    const server = startServer(createHandlers(openDatabase(':memory:')));

    server.send(request(1, 'repos.add', { path, testCommand: ' pnpm test ' }));
    await server.waitFor(1);
    server.send(request(2, 'repos.list', {}));
    const [added, listed] = await server.waitFor(2);

    expect(added).toMatchObject({ id: 1, result: { path, testCommand: 'pnpm test', acceptanceCommand: null } });
    expect(listed).toMatchObject({ id: 2, result: [{ path }] });
    await server.stop();
  });

  it('returns the command registry', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send(request(1, 'commands.list', {}));
    const [response] = await server.waitFor(1);
    expect(response).toMatchObject({ result: [{ id: 'repo.add' }, { id: 'repo.list' }] });
    await server.stop();
  });

  it('answers an unknown method with -32601', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send(request(7, 'repos.delete', {}));
    expect(await server.waitFor(1)).toMatchObject([{ id: 7, error: { code: ErrorCode.MethodNotFound } }]);
    await server.stop();
  });

  it('answers invalid params with -32602', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send(request(3, 'repos.add', { path: 'relative/path', testCommand: 'pnpm test' }));
    const [response] = await server.waitFor(1);
    expect(response).toMatchObject({ id: 3, error: { code: ErrorCode.InvalidParams } });
    expect(JSON.stringify(response)).toContain('path must be absolute');
    await server.stop();
  });

  it('answers a repo error with -32001', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send(request(4, 'repos.add', { path: join(dir, 'missing'), testCommand: 'pnpm test' }));
    expect(await server.waitFor(1)).toMatchObject([{ id: 4, error: { code: ErrorCode.RepoInvalid } }]);
    await server.stop();
  });

  it('answers a non-JSON line with -32700 and a null id', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send('{oops\n');
    expect(await server.waitFor(1)).toMatchObject([{ id: null, error: { code: ErrorCode.ParseError } }]);
    await server.stop();
  });

  it('answers a malformed envelope with -32600, keeping its id when readable', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send({ jsonrpc: '1.0', id: 9, method: 'ping' });
    server.send({ hello: 'world' });
    expect(await server.waitFor(2)).toMatchObject([
      { id: 9, error: { code: ErrorCode.InvalidRequest } },
      { id: null, error: { code: ErrorCode.InvalidRequest } },
    ]);
    await server.stop();
  });

  it('hides unexpected failures behind -32603', async () => {
    const handlers = createHandlers(openDatabase(':memory:'));
    const server = startServer({
      ...handlers,
      'repos.list': () => {
        throw new Error('disk on fire');
      },
    });
    server.send(request(5, 'repos.list', {}));
    const [response] = await server.waitFor(1);
    expect(response).toMatchObject({ id: 5, error: { code: ErrorCode.InternalError } });
    expect(JSON.stringify(response)).not.toContain('disk on fire');
    await server.stop();
  });

  it('serves concurrent requests without waiting for slower ones', async () => {
    let releaseSlowPing = () => {};
    const handlers = createHandlers(openDatabase(':memory:'));
    const server = startServer({
      ...handlers,
      ping: () =>
        new Promise((resolve) => {
          releaseSlowPing = () => resolve({ pong: true, pid: 0 });
        }),
    });

    server.send(request(1, 'ping', {}));
    server.send(request(2, 'repos.list', {}));
    const [first] = await server.waitFor(1);
    expect(first).toMatchObject({ id: 2 });

    releaseSlowPing();
    const responses = await server.waitFor(2);
    expect(responses[1]).toMatchObject({ id: 1, result: { pong: true } });
    await server.stop();
  });

  it('answers a last request sent without a trailing newline', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send(JSON.stringify(request(1, 'ping', {})));
    await server.stop();
    expect(await server.waitFor(1)).toMatchObject([{ id: 1, result: { pong: true } }]);
  });

  it('decodes a multi-byte character split across two byte chunks', async () => {
    const path = join(dir, 'café');
    mkdirSync(join(path, '.git'), { recursive: true });
    const server = startServer(createHandlers(openDatabase(':memory:')));

    const bytes = Buffer.from(`${JSON.stringify(request(1, 'repos.add', { path, testCommand: 't' }))}\n`);
    const cut = bytes.indexOf(Buffer.from('é')) + 1; // in the middle of "é" (2 bytes in UTF-8)
    server.send(bytes.subarray(0, cut));
    server.send(bytes.subarray(cut));

    expect(await server.waitFor(1)).toMatchObject([{ id: 1, result: { path } }]);
    await server.stop();
  });

  it('treats params: null as no params', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send({ jsonrpc: '2.0', id: 1, method: 'repos.list', params: null });
    expect(await server.waitFor(1)).toEqual([{ jsonrpc: '2.0', id: 1, result: [] }]);
    await server.stop();
  });

  it('does not echo a decimal id, which JSON-RPC does not allow', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send({ jsonrpc: '2.0', id: 1.5, method: 'ping' });
    expect(await server.waitFor(1)).toMatchObject([{ id: null, error: { code: ErrorCode.InvalidRequest } }]);
    await server.stop();
  });

  it('stops cleanly when the output breaks (the app vanished while the core was writing)', async () => {
    const input = new PassThrough();
    const output = new PassThrough();
    const done = serve({ input, output, handlers: createHandlers(openDatabase(':memory:')), logError: () => {} });

    output.destroy(Object.assign(new Error('write EPIPE'), { code: 'EPIPE' }));
    input.write(`${JSON.stringify(request(1, 'ping', {}))}\n`);

    await expect(done).resolves.toBeUndefined();
  });

  it('stops cleanly when the input fails', async () => {
    const input = new PassThrough();
    const done = serve({
      input,
      output: new PassThrough(),
      handlers: createHandlers(openDatabase(':memory:')),
      logError: () => {},
    });

    input.destroy(new Error('read ECONNRESET'));

    await expect(done).resolves.toBeUndefined();
  });

  it('finishes pending requests before resolving when the input ends', async () => {
    const server = startServer(createHandlers(openDatabase(':memory:')));
    server.send(request(1, 'ping', {}));
    await server.stop();
    expect(await server.waitFor(1)).toHaveLength(1);
  });
});
