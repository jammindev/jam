import { spawn, type ChildProcess } from 'node:child_process';
import { createRequire } from 'node:module';
import type { CoreApi } from '@jam/protocol';
import { createClient } from '@jam/protocol/client';

const require = createRequire(import.meta.url);

/**
 * How the core ended. A clean stop is `{ code: 0, signal: null }`; a core killed
 * by the fallback timeout (or by anyone else) shows `signal: 'SIGKILL'`.
 */
export type CoreExit = { code: number | null; signal: NodeJS.Signals | null };

export type CoreProcess = { client: CoreApi; stop(): Promise<CoreExit> };

/**
 * Starts the core as a child process and connects a client to its stdio.
 *
 * `process.execPath` is the Electron binary; with ELECTRON_RUN_AS_NODE=1 it
 * behaves as the Node it embeds. The app therefore needs no system Node, and
 * the core runs exactly as it does from the CLI (`node src/cli.ts serve`).
 */
export function startCore(dbPath: string): CoreProcess {
  const cliPath = require.resolve('@jam/core/cli');
  const child = spawn(process.execPath, [cliPath, 'serve', '--db', dbPath], {
    env: { ...process.env, ELECTRON_RUN_AS_NODE: '1' },
    // stdin/stdout carry the protocol; the core's logs go straight to our stderr.
    stdio: ['pipe', 'pipe', 'inherit'],
  });
  child.on('error', (error) => console.error('[core] failed to start:', error));
  child.on('exit', (code, signal) => console.error(`[core] exited (code ${code}, signal ${signal})`));

  return {
    client: createClient({ readable: child.stdout, writable: child.stdin }),
    stop: () => stopChild(child),
  };
}

const STOP_TIMEOUT_MS = 2000;

function stopChild(child: ChildProcess): Promise<CoreExit> {
  if (child.exitCode !== null || child.signalCode !== null) {
    return Promise.resolve({ code: child.exitCode, signal: child.signalCode });
  }
  return new Promise((resolve) => {
    const forceKill = setTimeout(() => child.kill('SIGKILL'), STOP_TIMEOUT_MS);
    child.once('exit', (code, signal) => {
      clearTimeout(forceKill);
      resolve({ code, signal });
    });
    // Closing stdin is the polite way to stop: the core answers pending
    // requests, closes the database, then exits on its own.
    child.stdin?.end();
  });
}
