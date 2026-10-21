// Spec 007: com as falhas desligadas, o motor reproduz o horário do GTFS.
import { describe, expect, it } from 'vitest';
import { preparaContexto } from '../../src/motor/contexto';
import type { Trajetoria } from '../../src/motor/dia';
import { simulaDia, trensEmViagem } from '../../src/motor/dia';
import { NENHUMA_POLITICA } from '../../src/motor/politicas';
import { trensProgramados } from '../../src/motor/rede';
import { faixaDe } from '../../src/motor/taxas';
import type { TipoDia } from '../../src/motor/tipos';
import { carregaFixture, carregaRede, mediana } from './apoio';

const TOLERANCIA_INTERVALO_S = 30;
const TOLERANCIA_PONTA_A_PONTA_S = 60;
// Trens em viagem às 08:00 de um dia útil (spec 007: 26, 32, 2 e 9; o GTFS dá 31 na Laranja pela spec 004)
const TRENS_08H: Record<string, number> = { verde: 26, laranja: 32, amarela: 2, azul: 9 };

function semFalhas(tipoDia: TipoDia) {
  const ctx = preparaContexto(carregaRede(), carregaFixture(), { tipoDia, semFalhas: true });
  return simulaDia(ctx, NENHUMA_POLITICA, 1, { trajetorias: true });
}

/** Intervalos medianos por faixa horária na estação local 0 de cada viagem completa. */
function intervalosPorFaixa(tj: Trajetoria[], simulado: boolean): Record<string, number> {
  const porFaixa: Record<string, number[]> = {};
  const saidas = tj
    .filter((t) => !t.cancelada && t.viagem.inicio === 0)
    .map((t) => (simulado ? t.partida[0] : t.viagem.partida[0]))
    .sort((a, b) => a - b);
  for (let i = 1; i < saidas.length; i++) {
    const f = faixaDe(Math.floor(saidas[i] / 3600));
    (porFaixa[f] ??= []).push(saidas[i] - saidas[i - 1]);
  }
  return Object.fromEntries(Object.entries(porFaixa).map(([f, xs]) => [f, mediana(xs)]));
}

describe('spec 007: dia sem falhas reproduz o horário', () => {
  for (const tipoDia of ['util', 'sabado', 'domingo'] as TipoDia[]) {
    it(`intervalo por faixa a até 30 s e ponta a ponta a até 1 min (${tipoDia})`, () => {
      const r = semFalhas(tipoDia);
      expect(r.registro).toHaveLength(0);
      for (const [chave, tj] of Object.entries(r.trajetorias ?? {})) {
        const sim = intervalosPorFaixa(tj, true);
        const prog = intervalosPorFaixa(tj, false);
        for (const f of Object.keys(prog)) expect(Math.abs(sim[f] - prog[f]), `${chave} ${f}`).toBeLessThanOrEqual(TOLERANCIA_INTERVALO_S);
        for (const t of tj) {
          const v = t.viagem;
          const p = v.fim - v.inicio;
          const durSim = t.chegada[p] - t.partida[0];
          const durProg = v.chegada[p] - v.partida[0];
          expect(Math.abs(durSim - durProg), v.id).toBeLessThanOrEqual(TOLERANCIA_PONTA_A_PONTA_S);
        }
      }
    });
  }

  it('trens em viagem às 08:00 de dia útil: 26, 32, 2 e 9, com tolerância de 1', () => {
    const r = semFalhas('util');
    const rede = carregaRede();
    for (const [linha, esperado] of Object.entries(TRENS_08H)) {
      const tj = [...(r.trajetorias?.[`${linha}:0`] ?? []), ...(r.trajetorias?.[`${linha}:1`] ?? [])];
      const n = trensEmViagem(tj, 8 * 3600);
      expect(Math.abs(n - esperado), linha).toBeLessThanOrEqual(1);
      expect(n).toBe(trensProgramados(rede.horarios.util, linha, 8 * 3600));
    }
  });

  it('viagem de ponta a ponta no dia útil dentro das faixas da pesquisa (36-38, 46-49, 6-7, 15-17 min)', () => {
    const faixas: Record<string, [number, number]> = { verde: [36, 38], laranja: [46, 49], amarela: [6, 7], azul: [15, 17] };
    const rede = carregaRede();
    for (const [linha, [a, b]] of Object.entries(faixas)) {
      for (const ls of rede.horarios.util.porLinha[linha]) {
        const completas = ls.viagens.filter((v) => v.inicio === 0 && v.fim === ls.n - 1).map((v) => (v.chegada[v.chegada.length - 1] - v.partida[0]) / 60);
        const m = mediana(completas);
        expect(m, `${linha} sentido ${ls.sentido}`).toBeGreaterThanOrEqual(a - 1);
        expect(m, `${linha} sentido ${ls.sentido}`).toBeLessThanOrEqual(b + 1);
      }
    }
  });
});
