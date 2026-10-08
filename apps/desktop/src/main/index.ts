import { join } from 'node:path';
import { isMethodName, type MethodParams } from '@jam/protocol';
import { app, BrowserWindow, ipcMain } from 'electron';
import { startCore, type CoreProcess } from './core-process.ts';

let core: CoreProcess | undefined;
let mainWindow: BrowserWindow | undefined;

function createWindow(): void {
  const window = new BrowserWindow({
    width: 960,
    height: 640,
    webPreferences: {
      preload: join(import.meta.dirname, '../preload/index.cjs'),
      // The renderer sees neither Node nor Electron: only what the preload exposes.
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
    },
  });
  mainWindow = window;

  // The window only ever shows the app's own page: no pop-ups, no navigation away
  // (a link in displayed content must not load a foreign page that could call window.jam).
  window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  window.webContents.on('will-navigate', (event, url) => {
    // Reloading the same page stays allowed (Vite reloads it in dev).
    if (url !== window.webContents.getURL()) event.preventDefault();
  });

  // electron-vite sets this URL in dev (Vite server with hot reload). A packaged
  // app ignores it: an environment variable must not decide what page gets window.jam.
  const devServerUrl = app.isPackaged ? undefined : process.env.ELECTRON_RENDERER_URL;
  if (devServerUrl) {
    void window.loadURL(devServerUrl);
  } else {
    void window.loadFile(join(import.meta.dirname, '../renderer/index.html'));
  }
}

void app.whenReady().then(() => {
  // Same file as the CLI's default, since the app is named "jam" (productName).
  const running = startCore(join(app.getPath('userData'), 'jam.db'));
  core = running;

  // The single bridge between the renderer and the core.
  ipcMain.handle('core:call', (event, method: unknown, params: unknown) => {
    // Only the app's window may reach the core.
    if (event.sender !== mainWindow?.webContents) {
      throw new Error('core:call refused: unknown sender');
    }
    if (typeof method !== 'string' || !isMethodName(method)) {
      throw new Error(`unknown method: ${String(method)}`);
    }
    // Params are not checked here: the core validates them and answers -32602.
    return running.client.call(method, params as MethodParams<typeof method>);
  });

  createWindow();
});

// One window for now: closing it quits the app, and the core with it.
app.on('window-all-closed', () => app.quit());

app.on('will-quit', (event) => {
  if (!core) return;
  // Hold the exit until the core has closed its database cleanly.
  event.preventDefault();
  const stopping = core;
  core = undefined;
  void stopping.stop().then(() => app.quit());
});
