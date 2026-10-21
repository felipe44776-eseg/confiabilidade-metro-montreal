/// <reference types="vitest/config" />
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { defineConfig } from 'vite';

// O site e servido em https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/
// e montado por publicacao/monta_site.py: a saida deste build vai para ../_site_app e e copiada para ../_site.

// Equipe e versao dos dados no rodape (spec 013), lidas no build: docs/equipe.json e o manifesto das fontes.
const equipe = (JSON.parse(readFileSync(resolve(__dirname, '../docs/equipe.json'), 'utf8')) as { integrantes: { nome: string }[] }).integrantes.map((p) => p.nome);
const manifesto = JSON.parse(readFileSync(resolve(__dirname, '../fontes/fontes_manifesto.json'), 'utf8')) as { release: string; releases?: string[] };
const releases = manifesto.releases ?? [manifesto.release];

export default defineConfig({
  base: process.env.VITE_BASE ?? '/confiabilidade-metro-montreal/',
  define: {
    __EQUIPE__: JSON.stringify(equipe),
    __RELEASES__: JSON.stringify(releases),
  },
  build: {
    outDir: resolve(__dirname, '../_site_app'),
    emptyOutDir: true,
    // O MapLibre sozinho tem cerca de 1 MB minificado; dividir o pacote nao reduz o que a pagina precisa baixar.
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      input: {
        mapa: resolve(__dirname, 'mapa/index.html'),
        simulador: resolve(__dirname, 'simulador/index.html'),
      },
    },
  },
  worker: {
    // workers do Monte Carlo, da comparacao A/B e da expansao importam o motor como modulo ES
    format: 'es',
  },
  test: {
    include: ['tests/**/*.test.ts'],
  },
});
