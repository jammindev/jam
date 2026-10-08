import { mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { migrations as defaultMigrations } from './migrations.ts';

const IN_MEMORY = ':memory:';
// The app and the CLI share the file: wait up to 5 s for the other process's
// lock instead of failing at once with SQLITE_BUSY.
const BUSY_TIMEOUT_MS = 5000;

/** Opens (or creates) the SQLite file and brings its schema up to date. */
export function openDatabase(path: string): DatabaseSync {
  if (path !== IN_MEMORY) {
    mkdirSync(dirname(path), { recursive: true });
  }
  const db = new DatabaseSync(path, { timeout: BUSY_TIMEOUT_MS });
  try {
    migrate(db, defaultMigrations);
  } catch (error) {
    // Do not leave an open handle behind for a caller that would retry.
    db.close();
    throw error;
  }
  return db;
}

/**
 * SQLite stores a free integer in the file header, `PRAGMA user_version`.
 * We use it as the number of migrations already applied.
 */
export function schemaVersion(db: DatabaseSync): number {
  const row = db.prepare('PRAGMA user_version').get();
  return Number(row?.user_version ?? 0);
}

/**
 * Applies the migrations the file has not seen yet, all in one transaction:
 * if one fails, none is kept and the version does not move.
 */
export function migrate(db: DatabaseSync, migrations: readonly string[]): void {
  // IMMEDIATE takes the write lock at once, and the version is read inside the
  // transaction: two processes opening a new file together cannot both migrate.
  db.exec('BEGIN IMMEDIATE');
  try {
    const current = schemaVersion(db);
    if (current > migrations.length) {
      // Typically another worktree added a migration this code does not know.
      throw new Error(
        `database is at version ${current} but this code knows ${migrations.length} migration(s): ` +
          'it was written by a newer version of jam',
      );
    }
    if (current < migrations.length) {
      for (const sql of migrations.slice(current)) {
        db.exec(sql);
      }
      // PRAGMA does not accept bound parameters; the value is an integer we computed.
      db.exec(`PRAGMA user_version = ${migrations.length}`);
    }
    db.exec('COMMIT');
  } catch (error) {
    // Some failures (disk full, I/O error) already make SQLite roll back on its
    // own; a second ROLLBACK would throw and hide the real cause.
    if (db.isTransaction) db.exec('ROLLBACK');
    throw error;
  }
}
