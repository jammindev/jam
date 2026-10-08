import type { CoreApi } from '@jam/protocol';
import { contextBridge, ipcRenderer } from 'electron';

// The only door from the renderer to the outside world: `window.jam.call`.
// It forwards a protocol call to the main process, which relays it to the core.
const jam: CoreApi = {
  call: (method, params) => ipcRenderer.invoke('core:call', method, params),
};

contextBridge.exposeInMainWorld('jam', jam);
