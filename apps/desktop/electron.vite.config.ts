import react from '@vitejs/plugin-react';
import { defineConfig } from 'electron-vite';

// Default entries: src/main/index.ts, src/preload/index.ts, src/renderer/index.html.
export default defineConfig({
  main: {
    build: {
      // Dependencies normally stay external and load from node_modules at runtime.
      // @jam/protocol ships TypeScript sources, so it is bundled into the main instead.
      externalizeDeps: { exclude: ['@jam/protocol'] },
    },
  },
  preload: {
    build: {
      // A sandboxed preload cannot be an ES module: force CommonJS.
      rollupOptions: { output: { format: 'cjs', entryFileNames: '[name].cjs' } },
    },
  },
  renderer: {
    plugins: [react()],
  },
});
