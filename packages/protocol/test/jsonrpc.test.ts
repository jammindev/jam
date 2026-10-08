import { describe, expect, it } from 'vitest';
import { ErrorCode, requestSchema, responseSchema } from '../src/jsonrpc.ts';

describe('JSON-RPC envelope', () => {
  it('accepts a well-formed request', () => {
    const result = requestSchema.safeParse({ jsonrpc: '2.0', id: 1, method: 'ping', params: {} });
    expect(result.success).toBe(true);
  });

  it('accepts a request without params', () => {
    expect(requestSchema.safeParse({ jsonrpc: '2.0', id: 'a', method: 'ping' }).success).toBe(true);
  });

  it.each([
    ['wrong version', { jsonrpc: '1.0', id: 1, method: 'ping' }],
    ['missing method', { jsonrpc: '2.0', id: 1 }],
    ['empty method', { jsonrpc: '2.0', id: 1, method: '' }],
    ['missing id', { jsonrpc: '2.0', method: 'ping' }],
    ['non-integer id', { jsonrpc: '2.0', id: 1.5, method: 'ping' }],
    ['not an object', [1, 2, 3]],
  ])('rejects a request with %s', (_label, value) => {
    expect(requestSchema.safeParse(value).success).toBe(false);
  });

  it('accepts success and error responses', () => {
    expect(responseSchema.safeParse({ jsonrpc: '2.0', id: 1, result: { pong: true } }).success).toBe(true);
    expect(
      responseSchema.safeParse({
        jsonrpc: '2.0',
        id: null,
        error: { code: ErrorCode.ParseError, message: 'Parse error' },
      }).success,
    ).toBe(true);
  });

  it('rejects a response that has neither result nor error', () => {
    expect(responseSchema.safeParse({ jsonrpc: '2.0', id: 1 }).success).toBe(false);
  });

  it('exposes the standard error codes plus REPO_INVALID', () => {
    expect(ErrorCode).toEqual({
      ParseError: -32700,
      InvalidRequest: -32600,
      MethodNotFound: -32601,
      InvalidParams: -32602,
      InternalError: -32603,
      RepoInvalid: -32001,
    });
  });
});
