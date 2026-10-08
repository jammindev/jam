import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createNdjsonDecoder, type Response } from '@jam/protocol';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

const cliPath = fileURLToPath(new URL('../src/cli.ts', import.meta.url));

let dir: string;
beforeEach(() => {
  // realpath: repos are stored by real path, and macOS's temp folder sits behind a symlink.
  dir = realpathSync(mkdtempSync(join(tmpdir(), 'jam-cli-')));
});
afterEach(() => {
  rmSync(dir, { recursive: true, force: true });
});

/**
 * Starts the real CLI as a child process, sends the requests on stdin, closes
 * stdin and returns the responses read on stdout plus the exit code.
 */
function runCli(args: string[], requests: unknown[], env: NodeJS.ProcessEnv = {}) {
  return new Promise<{ responses: Response[]; exitCode: number | null; stderr: string }>((resolve, reject) => {
    const child = spawn(process.execPath, [cliPath, ...args], { env: { ...process.env, ...env } });
    const decoder = createNdjsonDecoder();
    const responses: Response[] = [];
    let stderr = '';
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (chunk: string) => {
      for (const line of decoder.push(chunk)) {
        if (line.ok) responses.push(line.value as Response);
      }
    });
    child.stderr.on('data', (chunk: string) => (stderr += chunk));
    child.on('error', reject);
    child.on('close', (exitCode) => resolve({ responses, exitCode, stderr }));
    for (const request of requests) child.stdin.write(`${JSON.stringify(request)}\n`);
    child.stdin.end();
  });
}

const ping = { jsonrpc: '2.0', id: 1, method: 'ping', params: {} };

describe('jam-core CLI', () => {
  it('answers ping on stdout and exits once stdin is closed', async () => {
    const { responses, exitCode } = await runCli(['serve', '--db', join(dir, 'jam.db')], [ping]);
    expect(responses).toEqual([{ jsonrpc: '2.0', id: 1, result: { pong: true, pid: expect.any(Number) } }]);
    expect(exitCode).toBe(0);
  });

  it('keeps a repo across two runs of the process', async () => {
    const db = join(dir, 'jam.db');
    const repoPath = join(dir, 'house');
    mkdirSync(join(repoPath, '.git'), { recursive: true });

    const firstRun = await runCli(
      ['serve', '--db', db],
      [{ jsonrpc: '2.0', id: 1, method: 'repos.add', params: { path: repoPath, testCommand: 'pnpm test' } }],
    );
    expect(firstRun.responses[0]).toMatchObject({ id: 1, result: { path: repoPath } });

    const secondRun = await runCli(['serve', '--db', db], [{ jsonrpc: '2.0', id: 2, method: 'repos.list', params: {} }]);
    expect(secondRun.responses).toMatchObject([{ id: 2, result: [{ path: repoPath, testCommand: 'pnpm test' }] }]);
  });

  it('stores the database in JAM_DATA_DIR when --db is absent', async () => {
    const dataDir = join(dir, 'data');
    const { responses } = await runCli(['serve'], [ping], { JAM_DATA_DIR: dataDir });
    expect(responses).toHaveLength(1);
    expect(existsSync(join(dataDir, 'jam.db'))).toBe(true);
  });

  it('exits with code 1 and no usage message when the database cannot be opened', async () => {
    // A folder cannot be opened as a SQLite file.
    const { exitCode, stderr } = await runCli(['serve', '--db', dir], [ping]);
    expect(exitCode).toBe(1);
    expect(stderr).not.toContain('Usage');
  });

  it('refuses an empty --db, which SQLite would turn into a throwaway database', async () => {
    const { exitCode, stderr, responses } = await runCli(['serve', '--db', ''], [ping]);
    expect(exitCode).toBe(2);
    expect(stderr).toContain('--db must not be empty');
    expect(stderr).toContain('Usage');
    expect(responses).toEqual([]);
  });

  it('refuses an unknown option with a usage message', async () => {
    const { exitCode, stderr } = await runCli(['serve', '--nope'], []);
    expect(exitCode).toBe(2);
    expect(stderr).toContain('Usage');
  });

  it('refuses an unknown sub-command with a usage message', async () => {
    const { exitCode, stderr, responses } = await runCli(['launch'], []);
    expect(exitCode).toBe(2);
    expect(stderr).toContain('Usage');
    expect(responses).toEqual([]);
  });
});
