#!/usr/bin/env node
// jam-core: the core as a standalone process (ADR 0006).
// The desktop app starts it the same way; anyone can drive it from a terminal:
//   echo '{"jsonrpc":"2.0","id":1,"method":"ping"}' | node packages/core/src/cli.ts serve
// Requests arrive on stdin and responses leave on stdout, one JSON per line.
// stderr is kept for logs so that stdout only ever carries protocol messages.

import { parseArgs } from 'node:util';
import { openDatabase } from './db/database.ts';
import { defaultDatabasePath } from './paths.ts';
import { createHandlers, serve } from './server.ts';

const USAGE = 'Usage: jam-core serve [--db <path>]';

// Exit codes: 2 = wrong command line (usage shown), 1 = runtime failure.
async function main(argv: string[]): Promise<number> {
  let parsed;
  try {
    parsed = parseArgs({ args: argv, allowPositionals: true, options: { db: { type: 'string' } } });
  } catch (error) {
    console.error(error instanceof Error ? error.message : error);
    console.error(USAGE);
    return 2;
  }
  const { positionals, values } = parsed;

  if (positionals.length !== 1 || positionals[0] !== 'serve') {
    console.error(USAGE);
    return 2;
  }
  // SQLite reads "" as "a private temporary database": the data would vanish silently.
  if (values.db === '') {
    console.error('--db must not be empty');
    console.error(USAGE);
    return 2;
  }

  const db = openDatabase(values.db ?? defaultDatabasePath());
  try {
    // Runs until stdin closes: the parent (the app, or a shell pipe) owns our lifetime.
    await serve({ input: process.stdin, output: process.stdout, handlers: createHandlers(db) });
  } finally {
    db.close();
  }
  return 0;
}

try {
  process.exitCode = await main(process.argv.slice(2));
} catch (error) {
  // Unreadable database, missing permissions, failed migration…: not a typo, so no usage.
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
}
