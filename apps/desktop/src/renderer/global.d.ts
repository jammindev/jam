import type { CoreApi } from '@jam/protocol';

declare global {
  interface Window {
    /** Exposed by the preload (src/preload/index.ts). */
    jam: CoreApi;
  }
}
