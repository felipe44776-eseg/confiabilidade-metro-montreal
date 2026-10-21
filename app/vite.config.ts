/// <reference types="vitest/config" />
import { resolve } from 'node:path';
import { defineConfig } from 'vite';

// O site e servido em https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/
// e montado por publicacao/monta_site.py: a saida deste build vai para ../_site_app e e copiada para ../_site.
export default defineConfig({
  base: process.env.VITE_BASE ?? '/confiabilidade-metro-montreal/',
  build: {
    outDir: resolve(__dirname, '../_site_app'),
    emptyOutDir: true,
    // O MapLibre sozinho tem cerca de 1 MB minificado; dividir o pacote nao reduz o que a pagina precisa baixar.
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      input: {
        mapa: resolve(__dirname, 'mapa/index.html'),
      },
    },
  },
  test: {
    include: ['tests/**/*.test.ts'],
  },
});
