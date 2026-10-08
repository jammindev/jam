import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import type { DatabaseSync } from 'node:sqlite';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { migrate, openDatabase, schemaVersion } from '../src/db/database.ts';
import { migrations } from '../src/db/migrations.ts';

let dir: string;
beforeEach(() => {
  dir = mkdtempSync(join(tmpdir(), 'jam-db-'));
});
afterEach(() => {
  rmSync(dir, { recursive: true, force: true });
});

function tableNames(db: DatabaseSync): string[] {
  const rows = db.prepare("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name").all();
  return rows.map((row) => String(row.name));
}

describe('openDatabase', () => {
  it('migrates a new database to the latest version', () => {
    const db = openDatabase(join(dir, 'jam.db'));
    expect(schemaVersion(db)).toBe(migrations.length);
    expect(schemaVersion(db)).toBe(1);
    expect(tableNames(db)).toContain('repos');
    db.close();
  });

  it('creates the parent folder when it does not exist', () => {
    const db = openDatabase(join(dir, 'nested', 'folder', 'jam.db'));
    expect(schemaVersion(db)).toBe(1);
    db.close();
  });

  it('does not replay migrations on a second opening', () => {
    const path = join(dir, 'jam.db');
    const first = openDatabase(path);
    first
      .prepare('INSERT INTO repos (path, test_command, acceptance_command, created_at) VALUES (?, ?, ?, ?)')
      .run('/code/house', 'pnpm test', null, '2026-10-08T00:00:00.000Z');
    first.close();

    // Replaying migration 1 would fail ("table repos already exists") or wipe the row.
    const second = openDatabase(path);
    expect(schemaVersion(second)).toBe(1);
    expect(second.prepare('SELECT COUNT(*) AS count FROM repos').get()).toEqual({ count: 1 });
    second.close();
  });
});

describe('migrate', () => {
  it('refuses a database written by a newer version of jam', () => {
    const db = openDatabase(':memory:');
    db.exec('PRAGMA user_version = 99');
    expect(() => migrate(db, migrations)).toThrow(/version 99.*1 migration/);
    db.close();
  });

  it('rolls back every pending migration when one of them fails', () => {
    const db = openDatabase(':memory:');
    const broken = [...migrations, 'CREATE TABLE extra (id INTEGER)', 'THIS IS NOT SQL'];
    expect(() => migrate(db, broken)).toThrow();
    expect(schemaVersion(db)).toBe(1);
    expect(tableNames(db)).not.toContain('extra');
    db.close();
  });
});
