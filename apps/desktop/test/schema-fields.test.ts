import { listCommands } from '@jam/core/commands';
import { describe, expect, it } from 'vitest';
import { fieldsFromSchema, paramsFromForm } from '../src/renderer/schema-fields.ts';

function paramsSchemaOf(commandId: string) {
  const command = listCommands().find(({ id }) => id === commandId);
  if (!command) throw new Error(`no command ${commandId}`);
  return command.paramsSchema;
}

describe('fieldsFromSchema', () => {
  it('turns the repo.add params schema into one field per property', () => {
    expect(fieldsFromSchema(paramsSchemaOf('repo.add'))).toEqual([
      { name: 'path', label: 'Chemin absolu du repo', required: true },
      { name: 'testCommand', label: 'Commande de tests', required: true },
      { name: 'acceptanceCommand', label: 'Commande de recette (facultative)', required: false },
    ]);
  });

  it('returns no field for a command without params', () => {
    expect(fieldsFromSchema(paramsSchemaOf('repo.list'))).toEqual([]);
  });

  it('falls back to the property name when there is no description', () => {
    expect(fieldsFromSchema({ type: 'object', properties: { name: { type: 'string' } } })).toEqual([
      { name: 'name', label: 'name', required: false },
    ]);
  });

  it('refuses properties that are not strings, rather than dropping them silently', () => {
    expect(() => fieldsFromSchema({ type: 'object', properties: { count: { type: 'number' } } })).toThrow(/count/);
  });
});

describe('paramsFromForm', () => {
  const fields = fieldsFromSchema(paramsSchemaOf('repo.add'));

  it('keeps filled fields and drops empty optional ones', () => {
    expect(paramsFromForm(fields, { path: '/code/house', testCommand: 'pnpm test', acceptanceCommand: '  ' })).toEqual({
      path: '/code/house',
      testCommand: 'pnpm test',
    });
  });

  it('keeps an empty required field, so the core reports it as invalid', () => {
    expect(paramsFromForm(fields, {})).toEqual({ path: '', testCommand: '' });
  });
});
