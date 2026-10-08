import { methods, type CommandDescriptor, type MethodName } from '@jam/protocol';
import { z } from 'zod';

// The command registry (ADR 0007): every UI action is a named command.
// The palette lists them today; MCP tools will expose the same list to agents.
// A command runs a protocol method, so its params are those of the method.

type CommandDefinition = { id: string; title: string; method: MethodName };

export const commands = [
  { id: 'repo.add', title: 'Ajouter un repo', method: 'repos.add' },
  { id: 'repo.list', title: 'Lister les repos', method: 'repos.list' },
] as const satisfies readonly CommandDefinition[];

export function listCommands(): CommandDescriptor[] {
  return commands.map((command) => ({
    ...command,
    // Derived from the zod schema, never written by hand: one declaration only.
    // `io: 'input'` describes what a caller sends (optional fields stay optional).
    paramsSchema: z.toJSONSchema(methods[command.method].params, { io: 'input' }),
  }));
}
