import { z } from 'zod';

// The protocol's single source of truth: each method name maps to the zod
// schemas of its params and result. Types are inferred from these schemas,
// and the same schemas validate messages at runtime on both sides.

export const repoSchema = z.object({
  id: z.number().int(),
  // Absolute path of the git checkout on this machine.
  path: z.string(),
  testCommand: z.string(),
  // Optional: FR-028 allows the acceptance step to be a command or a skill.
  acceptanceCommand: z.string().nullable(),
  // ISO 8601 timestamp.
  createdAt: z.string(),
});
export type Repo = z.infer<typeof repoSchema>;

export const addRepoParamsSchema = z.strictObject({
  // macOS only (ADR 0005): an absolute path starts with "/". A plain `startsWith`
  // keeps this file free of Node APIs, so the renderer can import it too.
  path: z.string().startsWith('/', 'path must be absolute').describe('Chemin absolu du repo'),
  testCommand: z.string().trim().min(1, 'testCommand must not be empty').describe('Commande de tests'),
  acceptanceCommand: z
    .string()
    .trim()
    .min(1, 'acceptanceCommand must not be empty')
    .optional()
    .describe('Commande de recette (facultative)'),
});

export const commandDescriptorSchema = z.object({
  id: z.string(),
  title: z.string(),
  // The protocol method the command runs.
  method: z.string(),
  // JSON Schema of the method params: the format MCP tools will expect (ADR 0007).
  paramsSchema: z.record(z.string(), z.unknown()),
});
export type CommandDescriptor = z.infer<typeof commandDescriptorSchema>;

// Methods without params still take an object, so every call has the same shape.
const noParams = z.strictObject({});

export const methods = {
  ping: {
    params: noParams,
    result: z.object({ pong: z.literal(true), pid: z.number().int() }),
  },
  'repos.list': {
    params: noParams,
    result: z.array(repoSchema),
  },
  'repos.add': {
    params: addRepoParamsSchema,
    result: repoSchema,
  },
  'commands.list': {
    params: noParams,
    result: z.array(commandDescriptorSchema),
  },
} as const satisfies Record<string, { params: z.ZodType; result: z.ZodType }>;

export type MethodName = keyof typeof methods;
/** What a caller sends. */
export type MethodParams<M extends MethodName> = z.input<(typeof methods)[M]['params']>;
/** What a handler receives, after validation (strings trimmed, etc.). */
export type ParsedParams<M extends MethodName> = z.output<(typeof methods)[M]['params']>;
export type MethodResult<M extends MethodName> = z.output<(typeof methods)[M]['result']>;

/**
 * The typed way to call the core, whatever carries the messages: the stdio
 * client in the Electron main process, or `window.jam` in the renderer.
 */
export type CoreApi = {
  call<M extends MethodName>(method: M, params: MethodParams<M>): Promise<MethodResult<M>>;
};

export function isMethodName(name: string): name is MethodName {
  // `Object.hasOwn` so that inherited names such as "toString" are not methods.
  return Object.hasOwn(methods, name);
}
