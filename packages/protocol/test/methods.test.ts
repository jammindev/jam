import { describe, expect, expectTypeOf, it } from 'vitest';
import {
  isMethodName,
  methods,
  type CommandDescriptor,
  type MethodName,
  type MethodParams,
  type MethodResult,
  type Repo,
} from '../src/methods.ts';

const addParams = methods['repos.add'].params;

describe('protocol methods', () => {
  it('declares exactly the four S1 methods', () => {
    expect(Object.keys(methods).sort()).toEqual(['commands.list', 'ping', 'repos.add', 'repos.list']);
  });

  it('recognises method names', () => {
    expect(isMethodName('ping')).toBe(true);
    expect(isMethodName('repos.delete')).toBe(false);
    expect(isMethodName('toString')).toBe(false);
  });

  it('accepts valid repos.add params, with or without an acceptance command', () => {
    expect(addParams.safeParse({ path: '/code/house', testCommand: 'pnpm test' }).success).toBe(true);
    expect(
      addParams.safeParse({ path: '/code/house', testCommand: 'pnpm test', acceptanceCommand: 'pnpm e2e' }).success,
    ).toBe(true);
  });

  it('refuses a relative path', () => {
    expect(addParams.safeParse({ path: 'code/house', testCommand: 'pnpm test' }).success).toBe(false);
  });

  it('refuses an empty or blank test command', () => {
    expect(addParams.safeParse({ path: '/code/house', testCommand: '' }).success).toBe(false);
    expect(addParams.safeParse({ path: '/code/house', testCommand: '   ' }).success).toBe(false);
  });

  it('accepts a ping result carrying the process id', () => {
    expect(methods.ping.result.safeParse({ pong: true, pid: 42 }).success).toBe(true);
    expect(methods.ping.result.safeParse({ pong: false, pid: 42 }).success).toBe(false);
  });

  it('infers params and result types from the zod schemas', () => {
    expectTypeOf<MethodName>().toEqualTypeOf<'ping' | 'repos.list' | 'repos.add' | 'commands.list'>();
    expectTypeOf<MethodResult<'ping'>>().toEqualTypeOf<{ pong: true; pid: number }>();
    expectTypeOf<MethodResult<'repos.list'>>().toEqualTypeOf<Repo[]>();
    expectTypeOf<MethodResult<'repos.add'>>().toEqualTypeOf<Repo>();
    expectTypeOf<MethodResult<'commands.list'>>().toEqualTypeOf<CommandDescriptor[]>();
    expectTypeOf<MethodParams<'repos.add'>>().toEqualTypeOf<{
      path: string;
      testCommand: string;
      acceptanceCommand?: string | undefined;
    }>();
    expectTypeOf<Repo>().toEqualTypeOf<{
      id: number;
      path: string;
      testCommand: string;
      acceptanceCommand: string | null;
      createdAt: string;
    }>();
  });
});
