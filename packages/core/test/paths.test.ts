import { describe, expect, it } from 'vitest';
import { defaultDatabasePath } from '../src/paths.ts';

describe('defaultDatabasePath', () => {
  it('uses the app data folder, so the CLI and the app share one database', () => {
    expect(defaultDatabasePath({}, '/Users/someone')).toBe('/Users/someone/Library/Application Support/jam/jam.db');
  });

  it('follows JAM_DATA_DIR when it is set', () => {
    expect(defaultDatabasePath({ JAM_DATA_DIR: '/tmp/jam-data' }, '/Users/someone')).toBe('/tmp/jam-data/jam.db');
  });

  it('ignores an empty JAM_DATA_DIR', () => {
    expect(defaultDatabasePath({ JAM_DATA_DIR: '' }, '/Users/someone')).toBe(
      '/Users/someone/Library/Application Support/jam/jam.db',
    );
  });
});
