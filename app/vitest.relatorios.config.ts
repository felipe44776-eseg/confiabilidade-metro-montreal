/// <reference types="vitest/config" />
// Relatórios que rodam o motor com os dados reais e gravam resultados (fora da suíte de testes normal).
// Uso: npx vitest run --config vitest.relatorios.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  test: {
    include: ['relatorios/**/*.relatorio.ts'],
    testTimeout: 3_600_000,
  },
});
