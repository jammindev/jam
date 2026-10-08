import { mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { startCore, type CoreProcess } from '../src/main/core-process.ts';

// Under Vitest, `process.execPath` is Node itself, so ELECTRON_RUN_AS_NODE has no
// effect: the core starts exactly as the app starts it, minus Electron.

let dir: string;
let core: CoreProcess | undefined;
beforeEach(() => {
  dir = mkdtempSync(join(tmpdir(), 'jam-core-process-'));
});
afterEach(async () => {
  await core?.stop();
  core = undefined;
  rmSync(dir, { recursive: true, force: true });
});

function isRunning(pid: number): boolean {
  try {
    process.kill(pid, 0); // signal 0 only checks that the process exists
    return true;
  } catch {
    return false;
  }
}

describe('startCore', () => {
  it('starts the core on the given database and answers ping', async () => {
    core = startCore(join(dir, 'jam.db'));
    const { pong, pid } = await core.client.call('ping', {});
    expect(pong).toBe(true);
    expect(pid).not.toBe(process.pid);
  });

  it('stops the core cleanly: it exits on its own (code 0), not through the fallback SIGKILL', async () => {
    const running = startCore(join(dir, 'jam.db'));
    const { pid } = await running.client.call('ping', {});

    const exit = await running.stop();

    expect(exit).toEqual({ code: 0, signal: null });
    expect(isRunning(pid)).toBe(false);
  });

  it('keeps a repo when the app quits and starts again (startCore → stop → startCore)', async () => {
    const db = join(dir, 'jam.db');
    const repoPath = join(dir, 'house');
    mkdirSync(join(repoPath, '.git'), { recursive: true });

    const first = startCore(db);
    await first.client.call('repos.add', { path: repoPath, testCommand: 'pnpm test' });
    await first.stop();

    core = startCore(db);
    const repos = await core.client.call('repos.list', {});
    expect(repos.map((repo) => repo.testCommand)).toEqual(['pnpm test']);
  });

  it('turns a killed core into "connection closed" errors, without crashing', async () => {
    core = startCore(join(dir, 'jam.db'));
    const { pid } = await core.client.call('ping', {});

    process.kill(pid, 'SIGKILL');

    // Sent while the core dies: the write may fail with EPIPE or never be answered.
    await expect(core.client.call('ping', {})).rejects.toThrow(/connection closed/);
    await expect(core.client.call('repos.list', {})).rejects.toThrow(/connection closed/);
  });

  it('resolves stop() on a core that is already dead', async () => {
    core = startCore(join(dir, 'jam.db'));
    const { pid } = await core.client.call('ping', {});
    process.kill(pid, 'SIGKILL');
    await expect(core.client.call('ping', {})).rejects.toThrow(/connection closed/);

    await expect(core.stop()).resolves.toEqual({ code: null, signal: 'SIGKILL' });
  });
});
