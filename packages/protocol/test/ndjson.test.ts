import { describe, expect, it } from 'vitest';
import { ErrorCode } from '../src/jsonrpc.ts';
import { createNdjsonDecoder, encodeMessage } from '../src/ndjson.ts';

describe('NDJSON framing', () => {
  it('encodes one message per line', () => {
    expect(encodeMessage({ a: 1 })).toBe('{"a":1}\n');
  });

  it('keeps a message on one line even when a string contains a newline', () => {
    const line = encodeMessage({ text: 'two\nlines' });
    expect(line.split('\n')).toEqual(['{"text":"two\\nlines"}', '']);
  });

  it('waits for the end of line before emitting a message split in two chunks', () => {
    const decoder = createNdjsonDecoder();
    expect(decoder.push('{"jsonrpc":"2.0",')).toEqual([]);
    expect(decoder.push('"id":1}\n')).toEqual([{ ok: true, value: { jsonrpc: '2.0', id: 1 } }]);
  });

  it('emits two messages received in a single chunk', () => {
    const decoder = createNdjsonDecoder();
    expect(decoder.push('{"id":1}\n{"id":2}\n')).toEqual([
      { ok: true, value: { id: 1 } },
      { ok: true, value: { id: 2 } },
    ]);
  });

  it('turns a non-JSON line into a parse error (-32700) and keeps going', () => {
    const decoder = createNdjsonDecoder();
    const decoded = decoder.push('not json\n{"id":3}\n');
    expect(decoded).toHaveLength(2);
    expect(decoded[0]).toMatchObject({ ok: false, error: { code: ErrorCode.ParseError } });
    expect(decoded[1]).toEqual({ ok: true, value: { id: 3 } });
  });

  it('hands over a last line without newline when the stream ends', () => {
    const decoder = createNdjsonDecoder();
    expect(decoder.push('{"id":1}')).toEqual([]);
    expect(decoder.end()).toEqual([{ ok: true, value: { id: 1 } }]);
  });

  it('reports an unfinished non-JSON tail as a parse error at the end', () => {
    const decoder = createNdjsonDecoder();
    decoder.push('{"id":');
    expect(decoder.end()).toMatchObject([{ ok: false, error: { code: ErrorCode.ParseError } }]);
  });

  it('returns nothing at the end when every line was complete', () => {
    const decoder = createNdjsonDecoder();
    decoder.push('{"id":1}\n');
    expect(decoder.end()).toEqual([]);
  });

  it('ignores blank lines and Windows line endings', () => {
    const decoder = createNdjsonDecoder();
    expect(decoder.push('\n{"id":4}\r\n\n')).toEqual([{ ok: true, value: { id: 4 } }]);
  });
});
