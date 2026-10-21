// Spec 008: camada de frota (reserva fria k-de-n) contra o Markov nascimento-morte do painel.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { frotaCompletaMarkov, simulaFrota } from '../../src/motor/frota';
import { Rng } from '../../src/motor/prng';

interface LinhaKdn {
  linha: string;
  trens_necessarios: number;
  reservas: number;
  reparo_dias: number;
  lambda_trem_dia: number;
  disponibilidade: number;
}
const kdn = JSON.parse(readFileSync(resolve(__dirname, '../../../dados/derivados/painel/kdn.json'), 'utf8')) as LinhaKdn[];
const TOLERANCIA_PP = 0.05;
const DIAS_SIMULADOS = 200_000;

describe('spec 008: reserva fria k-de-n', () => {
  it('o Markov do motor reproduz o painel (kdn.json) em todas as linhas, reservas e tempos de reparo', () => {
    expect(kdn.length).toBeGreaterThan(20);
    for (const x of kdn) {
      const p = frotaCompletaMarkov({ n: x.trens_necessarios, s: x.reservas, lambdaDia: x.lambda_trem_dia, reparoDias: x.reparo_dias });
      // kdn.json guarda λ com 5 casas; o arredondamento move P em até ~2e-4
      expect(Math.abs(p - x.disponibilidade), `${x.linha} s=${x.reservas} reparo=${x.reparo_dias}`).toBeLessThan(1e-3);
    }
  });

  it('Laranja, n = 48, λ = 0,00835, reparo 1 dia: simulação por eventos bate com o Markov a até 5 pontos', () => {
    const esperado = [0.671, 0.938, 0.992];
    for (const s of [0, 1, 2]) {
      const p = { n: 48, s, lambdaDia: 0.00835, reparoDias: 1 };
      const markov = frotaCompletaMarkov(p);
      const sim = simulaFrota(new Rng(1000 + s), p, DIAS_SIMULADOS);
      expect(Math.abs(markov - esperado[s])).toBeLessThan(0.001);
      expect(Math.abs(sim.pFrotaCompleta - markov), `s=${s}`).toBeLessThan(TOLERANCIA_PP);
      // com 200 mil dias a diferença real é bem menor que a tolerância
      expect(Math.abs(sim.pFrotaCompleta - markov)).toBeLessThan(0.01);
    }
  });

  it('sensibilidade ao tempo de reparo (0,5 a 4 dias): a chance de frota completa cai quando o reparo demora', () => {
    for (const s of [0, 1, 2]) {
      const ps = [0.5, 1, 2, 4].map((reparoDias) => frotaCompletaMarkov({ n: 48, s, lambdaDia: 0.00835, reparoDias }));
      for (let i = 1; i < ps.length; i++) expect(ps[i]).toBeLessThan(ps[i - 1]);
    }
  });
});
