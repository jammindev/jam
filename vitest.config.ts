import { defineConfig } from 'vitest/config';

// One Vitest run for the whole monorepo: every package keeps its tests in `test/`.
export default defineConfig({
  test: {
    include: ['packages/*/test/**/*.test.ts', 'apps/*/test/**/*.test.ts'],
  },
});
