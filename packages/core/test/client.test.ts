import { mkdirSync, mkdtempSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { PassThrough } from 'node:stream';
import { ErrorCode, type Repo } from '@jam/protocol';
import { createClient, JsonRpcError } from '@jam/protocol/client';
import { afterEach, beforeEach, describe, expect, expectTypeOf, it } from 'vitest';
import { openDatabase } from '../src/db/database.ts';
import { createHandlers, serve, type Handlers } from '../src/server.ts';

let dir: string;
beforeEach(() => {
  // realpath: repos are stored by real path, and macOS's temp folder sits behind a symlink.
  dir = realpathSync(mkdtempSync(join(tmpdir(), 'jam-client-')));
});
afterEach(() => {
  rmSync(dir, { recursive: true, force: true });
});

/** A client and a server talking through two in-memory pipes, as they will through stdio. */
function connect(handlers: Handlers = createHandlers(openDatabase(':memory:'))) {
  const toServer = new PassThrough();
  const toClient = new PassThrough();
  const served = serve({ input: toServer, output: toClient, handlers, logError: () => {} });
  const client = createClient({ readable: toClient, writable: toServer });
  return { client, toServer, toClient, served };
}

describe('protocol client', () => {
  it('calls ping and gets a typed result', async () => {
    const { client } = connect();
    const result = await client.call('ping', {});
    expectTypeOf(result).toEqualTypeOf<{ pong: true; pid: number }>();
    expect(result).toEqual({ pong: true, pid: process.pid });
  });

  it('adds and lists repos', async () => {
    const path = join(dir, 'house');
    mkdirSync(join(path, '.git'), { recursive: true });
    const { client } = connect();

    await client.call('repos.add', { path, testCommand: 'pnpm test' });
    const repos = await client.call('repos.list', {});

    expectTypeOf(repos).toEqualTypeOf<Repo[]>();
    expect(repos.map((repo) => repo.path)).toEqual([path]);
  });

  it('turns a JSON-RPC error into a typed exception', async () => {
    const { client } = connect();
    const failure = client.call('repos.add', { path: join(dir, 'missing'), testCommand: 'pnpm test' });
    await expect(failure).rejects.toBeInstanceOf(JsonRpcError);
    await expect(failure).rejects.toMatchObject({ code: ErrorCode.RepoInvalid });
  });

  it('matches concurrent responses to their calls by id', async () => {
    let releaseSlowPing = () => {};
    const handlers = createHandlers(openDatabase(':memory:'));
    const { client } = connect({
      ...handlers,
      ping: () =>
        new Promise((resolve) => {
          releaseSlowPing = () => resolve({ pong: true, pid: 123 });
        }),
    });

    const slow = client.call('ping', {});
    const fast = await client.call('repos.list', {});
    expect(fast).toEqual([]);

    releaseSlowPing();
    expect(await slow).toEqual({ pong: true, pid: 123 });
  });

  it('rejects a result that does not match the method schema', async () => {
    const toClient = new PassThrough();
    const toServer = new PassThrough();
    const client = createClient({ readable: toClient, writable: toServer });

    const call = client.call('ping', {});
    toClient.write('{"jsonrpc":"2.0","id":1,"result":{"pong":"yes"}}\n');
    await expect(call).rejects.toThrow(/invalid result for ping/);
  });

  it('treats a write error (core gone, EPIPE) as a closed connection instead of crashing', async () => {
    const toClient = new PassThrough();
    const toServer = new PassThrough();
    const client = createClient({ readable: toClient, writable: toServer });

    const pending = client.call('ping', {});
    // Without a listener, this 'error' event would be thrown as an uncaught exception.
    toServer.destroy(Object.assign(new Error('write EPIPE'), { code: 'EPIPE' }));
    await expect(pending).rejects.toThrow(/connection closed/);
    await expect(client.call('ping', {})).rejects.toThrow(/connection closed/);
  });

  it('ignores unreadable lines and responses to unknown ids', async () => {
    const toClient = new PassThrough();
    const toServer = new PassThrough();
    const client = createClient({ readable: toClient, writable: toServer });

    const call = client.call('ping', {});
    toClient.write('not json\n');
    toClient.write('{"jsonrpc":"2.0","id":999,"result":{"pong":true,"pid":1}}\n');
    toClient.write('{"jsonrpc":"2.0","id":1,"result":{"pong":true,"pid":2}}\n');
    expect(await call).toEqual({ pong: true, pid: 2 });
  });

  it('rejects a call whose response envelope is malformed, instead of waiting forever', async () => {
    const toClient = new PassThrough();
    const client = createClient({ readable: toClient, writable: new PassThrough() });

    const call = client.call('ping', {});
    toClient.write('{"jsonrpc":"2.0","id":1,"error":{"code":"oops","message":"bad"}}\n');
    await expect(call).rejects.toThrow(/invalid response/);
  });

  it('reports errors the core could not tie to a call (id null) to the log', async () => {
    const toClient = new PassThrough();
    const logged: unknown[] = [];
    const client = createClient({
      readable: toClient,
      writable: new PassThrough(),
      logError: (...args) => logged.push(args),
    });

    toClient.write('{"jsonrpc":"2.0","id":null,"error":{"code":-32700,"message":"Parse error"}}\n');
    // A later normal call proves the line was processed before we look at the log.
    const call = client.call('ping', {});
    toClient.write('{"jsonrpc":"2.0","id":1,"result":{"pong":true,"pid":1}}\n');
    await call;
    expect(JSON.stringify(logged)).toContain('Parse error');
  });

  it('resolves a call answered on a last line without newline, just before the stream ends', async () => {
    const toClient = new PassThrough();
    const client = createClient({ readable: toClient, writable: new PassThrough() });

    const call = client.call('ping', {});
    toClient.end('{"jsonrpc":"2.0","id":1,"result":{"pong":true,"pid":3}}');
    expect(await call).toEqual({ pong: true, pid: 3 });
  });

  it('rejects params that cannot be encoded as JSON', async () => {
    const client = createClient({ readable: new PassThrough(), writable: new PassThrough() });
    // A BigInt survives Electron's IPC cloning but not JSON.stringify.
    await expect(client.call('ping', { big: 1n } as never)).rejects.toThrow(TypeError);
  });

  it('treats a read error as a closed connection', async () => {
    const toClient = new PassThrough();
    const client = createClient({ readable: toClient, writable: new PassThrough() });

    const pending = client.call('ping', {});
    toClient.destroy(new Error('read ECONNRESET'));
    await expect(pending).rejects.toThrow(/connection closed/);
  });

  it('rejects pending calls when the stream closes, and every call after that', async () => {
    const toClient = new PassThrough();
    const toServer = new PassThrough();
    const client = createClient({ readable: toClient, writable: toServer });

    const pending = client.call('ping', {});
    toClient.end();
    await expect(pending).rejects.toThrow(/connection closed/);
    await expect(client.call('ping', {})).rejects.toThrow(/connection closed/);
  });
});
