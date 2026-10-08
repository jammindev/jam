import { isMethodName, methods } from '@jam/protocol';
import { describe, expect, it } from 'vitest';
import { commands, listCommands } from '../src/commands.ts';

describe('command registry', () => {
  it('registers the two S1 commands', () => {
    expect(listCommands().map(({ id, title, method }) => ({ id, title, method }))).toEqual([
      { id: 'repo.add', title: 'Ajouter un repo', method: 'repos.add' },
      { id: 'repo.list', title: 'Lister les repos', method: 'repos.list' },
    ]);
  });

  it('points every command to an existing protocol method', () => {
    for (const command of commands) {
      expect(isMethodName(command.method), command.id).toBe(true);
    }
  });

  it('derives the params JSON Schema of repo.add from the method schema', () => {
    const repoAdd = listCommands().find((command) => command.id === 'repo.add');
    expect(repoAdd?.paramsSchema).toMatchObject({
      type: 'object',
      properties: {
        path: { type: 'string' },
        testCommand: { type: 'string' },
        acceptanceCommand: { type: 'string' },
      },
    });
    expect(repoAdd?.paramsSchema.required).toEqual(['path', 'testCommand']);
  });

  it('describes repo.list as taking no params', () => {
    const repoList = listCommands().find((command) => command.id === 'repo.list');
    expect(repoList?.paramsSchema).toMatchObject({ type: 'object', properties: {} });
  });

  it('returns descriptors that satisfy the commands.list result schema', () => {
    expect(methods['commands.list'].result.safeParse(listCommands()).success).toBe(true);
  });
});
