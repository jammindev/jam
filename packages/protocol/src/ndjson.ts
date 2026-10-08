import { ErrorCode, type ErrorObject } from './jsonrpc.ts';

// NDJSON framing: one JSON value per line. It works on any byte stream
// (stdio today, a Unix socket later) without changing the protocol.

export type DecodedLine = { ok: true; value: unknown } | { ok: false; error: ErrorObject };

export function encodeMessage(message: unknown): string {
  // JSON.stringify never emits a raw newline, so one message is exactly one line.
  return `${JSON.stringify(message)}\n`;
}

/**
 * Turns text chunks into JSON values. Chunks may cut a message anywhere, so the
 * unfinished tail is kept until its newline arrives. Streams feeding the decoder
 * must be read as UTF-8 text (`setEncoding('utf8')`) so a multi-byte character
 * split across two chunks is not corrupted.
 */
export function createNdjsonDecoder() {
  let pending = '';

  return {
    push(chunk: string): DecodedLine[] {
      pending += chunk;
      const lines = pending.split('\n');
      // The last element is either '' (chunk ended on a newline) or an unfinished line.
      pending = lines.pop() ?? '';
      return decodeLines(lines);
    },
    /**
     * Call when the stream ends: a last message written without its newline
     * (`printf` instead of `echo`) is still delivered instead of being dropped.
     */
    end(): DecodedLine[] {
      const tail = pending;
      pending = '';
      return decodeLines([tail]);
    },
  };
}

function decodeLines(lines: string[]): DecodedLine[] {
  return lines.map((line) => line.trim()).filter((line) => line !== '').map(parseLine);
}

function parseLine(line: string): DecodedLine {
  try {
    return { ok: true, value: JSON.parse(line) };
  } catch {
    return { ok: false, error: { code: ErrorCode.ParseError, message: 'Parse error' } };
  }
}
