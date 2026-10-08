import { existsSync, mkdirSync, mkdtempSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { openDatabase } from '../src/db/database.ts';
import { addRepo, listRepos, RepoInvalidError } from '../src/repos.ts';

let dir: string;
beforeEach(() => {
  // realpath: on macOS the temp folder itself sits behind a symlink (/var → /private/var).
  dir = realpathSync(mkdtempSync(join(tmpdir(), 'jam-repos-')));
});
afterEach(() => {
  rmSync(dir, { recursive: true, force: true });
});

/** Creates a folder that looks like a git checkout. */
function fakeRepo(name: string): string {
  const path = join(dir, name);
  mkdirSync(join(path, '.git'), { recursive: true });
  return path;
}

/** True when the temp folder's disk treats "X" and "x" as the same name. */
function caseInsensitiveDisk(): boolean {
  const probe = mkdtempSync(join(tmpdir(), 'jam-Case-'));
  try {
    return existsSync(probe.replace('jam-Case-', 'jam-case-'));
  } finally {
    rmSync(probe, { recursive: true, force: true });
  }
}

describe('repos', () => {
  it('adds a repo and lists it', () => {
    const db = openDatabase(':memory:');
    const path = fakeRepo('house');

    const added = addRepo(db, { path, testCommand: 'pnpm test' });

    expect(added).toMatchObject({ path, testCommand: 'pnpm test', acceptanceCommand: null });
    expect(typeof added.id).toBe('number');
    expect(new Date(added.createdAt).toISOString()).toBe(added.createdAt);
    expect(listRepos(db)).toEqual([added]);
    db.close();
  });

  it('keeps the optional acceptance command', () => {
    const db = openDatabase(':memory:');
    const added = addRepo(db, { path: fakeRepo('chef'), testCommand: 'pytest', acceptanceCommand: 'make e2e' });
    expect(added.acceptanceCommand).toBe('make e2e');
    db.close();
  });

  it('accepts a worktree, where .git is a file', () => {
    const db = openDatabase(':memory:');
    const path = join(dir, 'worktree');
    mkdirSync(path);
    writeFileSync(join(path, '.git'), 'gitdir: /somewhere/else\n');
    expect(addRepo(db, { path, testCommand: 'pnpm test' }).path).toBe(path);
    db.close();
  });

  it('lists repos in the order they were added', () => {
    const db = openDatabase(':memory:');
    addRepo(db, { path: fakeRepo('b'), testCommand: 't' });
    addRepo(db, { path: fakeRepo('a'), testCommand: 't' });
    expect(listRepos(db).map((repo) => repo.path)).toEqual([join(dir, 'b'), join(dir, 'a')]);
    db.close();
  });

  it('refuses a duplicate, even written with a trailing slash', () => {
    const db = openDatabase(':memory:');
    const path = fakeRepo('house');
    addRepo(db, { path, testCommand: 'pnpm test' });
    expect(() => addRepo(db, { path: `${path}/`, testCommand: 'pnpm test' })).toThrow(RepoInvalidError);
    expect(listRepos(db)).toHaveLength(1);
    db.close();
  });

  it('stores the real path, so a symlink to a known repo is a duplicate', () => {
    const db = openDatabase(':memory:');
    const path = fakeRepo('house');
    const link = join(dir, 'house-link');
    symlinkSync(path, link);

    expect(addRepo(db, { path: link, testCommand: 'pnpm test' }).path).toBe(path);
    expect(() => addRepo(db, { path, testCommand: 'pnpm test' })).toThrow(/already registered/);
    db.close();
  });

  // macOS disks (APFS) ignore case by default: "house" and "House" are the same
  // folder. Linux disks (CI) do not, so the test only runs where it applies.
  it.skipIf(!caseInsensitiveDisk())('refuses the same repo written with another case', () => {
    const db = openDatabase(':memory:');
    const path = fakeRepo('House');

    // realpathSync.native asks the OS, which answers with the case stored on disk.
    expect(addRepo(db, { path: join(dir, 'house'), testCommand: 'pnpm test' }).path).toBe(path);
    expect(() => addRepo(db, { path, testCommand: 'pnpm test' })).toThrow(/already registered/);
    db.close();
  });

  it('refuses a path that is a file, not a folder', () => {
    const db = openDatabase(':memory:');
    const file = join(dir, 'notes.txt');
    writeFileSync(file, 'hello');
    expect(() => addRepo(db, { path: file, testCommand: 'pnpm test' })).toThrow(/is not a folder/);
    db.close();
  });

  it('refuses a folder without .git', () => {
    const db = openDatabase(':memory:');
    const path = join(dir, 'plain');
    mkdirSync(path);
    expect(() => addRepo(db, { path, testCommand: 'pnpm test' })).toThrow(/not a git repository/);
    db.close();
  });

  it('refuses a path that does not exist', () => {
    const db = openDatabase(':memory:');
    expect(() => addRepo(db, { path: join(dir, 'missing'), testCommand: 'pnpm test' })).toThrow(RepoInvalidError);
    db.close();
  });

  it('keeps repos after the database is closed and reopened', () => {
    const file = join(dir, 'jam.db');
    const path = fakeRepo('house');

    const first = openDatabase(file);
    const added = addRepo(first, { path, testCommand: 'pnpm test' });
    first.close();

    const second = openDatabase(file);
    expect(listRepos(second)).toEqual([added]);
    second.close();
  });
});
