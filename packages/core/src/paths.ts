import { homedir } from 'node:os';
import { join } from 'node:path';

/**
 * Database used when `--db` is not given. It is the file the desktop app uses
 * (Electron's `userData` folder for an app named "jam"), so `jam-core` shows the
 * app's repos. `JAM_DATA_DIR` moves it elsewhere.
 */
export function defaultDatabasePath(env: NodeJS.ProcessEnv = process.env, home: string = homedir()): string {
  const dataDir = env.JAM_DATA_DIR || join(home, 'Library', 'Application Support', 'jam');
  return join(dataDir, 'jam.db');
}
