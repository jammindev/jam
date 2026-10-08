import { existsSync, realpathSync, statSync } from 'node:fs';
import { join, resolve } from 'node:path';
import type { DatabaseSync } from 'node:sqlite';
import type { ParsedParams, Repo } from '@jam/protocol';

/** A repo that cannot be registered. The server reports it as REPO_INVALID (-32001). */
export class RepoInvalidError extends Error {
  override name = 'RepoInvalidError';
}

/** Params are already validated by the protocol schema (absolute path, non-empty commands). */
export function addRepo(db: DatabaseSync, params: ParsedParams<'repos.add'>): Repo {
  const given = resolve(params.path);
  if (!existsSync(given) || !statSync(given).isDirectory()) {
    throw new RepoInvalidError(`${given} is not a folder`);
  }
  // The real path as the OS sees it: "/code/house/", a symlink to it and, on
  // macOS's case-insensitive disk, "/code/House" are the same repo, stored once.
  // `.native` calls realpath(3), which also returns the case stored on disk;
  // the JavaScript version keeps the case as typed.
  const path = realpathSync.native(given);
  // `.git` is a folder in a regular checkout and a file in a git worktree.
  if (!existsSync(join(path, '.git'))) {
    throw new RepoInvalidError(`${path} is not a git repository`);
  }

  // No "SELECT then INSERT": the app and the CLI could both pass the SELECT at
  // the same moment. The UNIQUE constraint on `path` decides, atomically.
  try {
    const row = db
      .prepare(
        `INSERT INTO repos (path, test_command, acceptance_command, created_at)
         VALUES (?, ?, ?, ?)
         RETURNING *`,
      )
      .get(path, params.testCommand, params.acceptanceCommand ?? null, new Date().toISOString());
    return toRepo(row);
  } catch (error) {
    if (isUniqueViolation(error)) throw new RepoInvalidError(`${path} is already registered`);
    throw error;
  }
}

/** SQLite's extended error code for a UNIQUE constraint violation. */
const SQLITE_CONSTRAINT_UNIQUE = 2067;

function isUniqueViolation(error: unknown): boolean {
  return error instanceof Error && 'errcode' in error && error.errcode === SQLITE_CONSTRAINT_UNIQUE;
}

export function listRepos(db: DatabaseSync): Repo[] {
  // `id` breaks ties between repos added within the same millisecond.
  return db.prepare('SELECT * FROM repos ORDER BY created_at, id').all().map(toRepo);
}

type Row = Record<string, unknown> | undefined;

/** Maps a snake_case SQL row to the protocol's `Repo`. */
function toRepo(row: Row): Repo {
  if (!row) throw new Error('expected a repos row');
  return {
    id: Number(row.id),
    path: String(row.path),
    testCommand: String(row.test_command),
    acceptanceCommand: row.acceptance_command == null ? null : String(row.acceptance_command),
    createdAt: String(row.created_at),
  };
}
