import { describe, expect, it } from 'vitest';
import { errorMessage } from '../src/renderer/errors.ts';

describe('errorMessage', () => {
  it('strips the prefix Electron adds to errors crossing IPC', () => {
    const error = new Error("Error invoking remote method 'core:call': JsonRpcError: /code/house is not a git repository");
    expect(errorMessage(error)).toBe('/code/house is not a git repository');
  });

  it('keeps other messages as they are', () => {
    expect(errorMessage(new Error('boom'))).toBe('boom');
    expect(errorMessage('plain text')).toBe('plain text');
  });
});
