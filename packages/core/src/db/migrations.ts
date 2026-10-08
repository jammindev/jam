// Numbered schema migrations (ADR 0010). Migration N is `migrations[N - 1]`.
// A shipped migration is never edited: a schema change is a new entry at the end.

export const migrations: readonly string[] = [
  // 1. Repos known to jam, with the commands the pipeline runs on them.
  `CREATE TABLE repos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    test_command TEXT NOT NULL,
    acceptance_command TEXT,
    created_at TEXT NOT NULL
  )`,
];
