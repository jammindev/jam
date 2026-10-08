// Electron wraps errors thrown by `ipcMain.handle` as
// "Error invoking remote method 'core:call': JsonRpcError: <message>".
// Only the core's message is useful to the user.
const IPC_PREFIX = /^Error invoking remote method '[^']+': (?:\w*Error: )?/;

export function errorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return message.replace(IPC_PREFIX, '');
}
