import { z } from 'zod';

// JSON-RPC 2.0 envelope (https://www.jsonrpc.org/specification).
// The envelope only checks the outer shape; each method validates its own params.

export const ErrorCode = {
  ParseError: -32700,
  InvalidRequest: -32600,
  MethodNotFound: -32601,
  InvalidParams: -32602,
  InternalError: -32603,
  // Application error (the -32000..-32099 range is reserved for servers):
  // the repo passed to `repos.add` cannot be registered.
  RepoInvalid: -32001,
} as const;
export type ErrorCode = (typeof ErrorCode)[keyof typeof ErrorCode];

const idSchema = z.union([z.string(), z.number().int()]);
export type RequestId = z.infer<typeof idSchema>;

// `id` is required: notifications (requests without id) are not used yet,
// so a message without id is treated as an invalid request.
export const requestSchema = z.object({
  jsonrpc: z.literal('2.0'),
  id: idSchema,
  method: z.string().min(1),
  params: z.unknown().optional(),
});
export type Request = z.infer<typeof requestSchema>;

export const errorObjectSchema = z.object({
  code: z.number().int(),
  message: z.string(),
  data: z.unknown().optional(),
});
export type ErrorObject = z.infer<typeof errorObjectSchema>;

export const successResponseSchema = z.object({
  jsonrpc: z.literal('2.0'),
  id: idSchema,
  // `z.unknown()` would also accept a missing key; a success must carry a result.
  result: z.unknown().refine((value) => value !== undefined, 'result is required'),
});

export const errorResponseSchema = z.object({
  jsonrpc: z.literal('2.0'),
  // `null` when the request id could not be read (parse error, invalid request).
  id: idSchema.nullable(),
  error: errorObjectSchema,
});

export const responseSchema = z.union([errorResponseSchema, successResponseSchema]);
export type SuccessResponse = z.infer<typeof successResponseSchema>;
export type ErrorResponse = z.infer<typeof errorResponseSchema>;
export type Response = z.infer<typeof responseSchema>;
