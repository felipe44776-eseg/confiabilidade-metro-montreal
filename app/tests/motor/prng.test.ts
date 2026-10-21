// Gerador pseudoaleatório, fila de prioridade e sorteio de instantes (base das specs 007 e 009).
import { describe, expect, it } from 'vitest';
import { Heap } from '../../src/motor/heap';
import { FLUXOS, Rng, criaFluxo, gamaFuncao, misturaSemente, sementeDaRodada } from '../../src/motor/prng';
import { inverteAcumulada, sorteiaInstantes, taxaAcumuladaConstante } from '../../src/motor/taxas';

const N = 200_000;

describe('gerador pseudoaleatório', () => {
  it('mesma semente, mesma sequência; sementes vizinhas, sequências diferentes', () => {
    const a = new Rng(123);
    const b = new Rng(123);
    const c = new Rng(124);
    const xa = Array.from({ length: 50 }, () => a.proximo());
    expect(Array.from({ length: 50 }, () => b.proximo())).toEqual(xa);
    expect(Array.from({ length: 50 }, () => c.proximo())).not.toEqual(xa);
  });

  it('uniforme em [0, 1) com média 1/2 e variância 1/12', () => {
    const r = new Rng(9);
    let s = 0;
    let q = 0;
    for (let i = 0; i < N; i++) {
      const u = r.uniforme();
      expect(u >= 0 && u < 1).toBe(true);
      s += u;
      q += u * u;
    }
    expect(s / N).toBeCloseTo(0.5, 2);
    expect(q / N - (s / N) ** 2).toBeCloseTo(1 / 12, 2);
  });

  it('normal, Weibull e Gama com as médias teóricas', () => {
    const r = new Rng(10);
    let sn = 0;
    let sw = 0;
    let sg = 0;
    for (let i = 0; i < N; i++) {
      sn += r.normal();
      sw += r.weibull(0.7, 2);
      sg += r.gama(1.8);
    }
    expect(sn / N).toBeCloseTo(0, 2);
    expect(sw / N / (2 * gamaFuncao(1 + 1 / 0.7))).toBeCloseTo(1, 1);
    expect(sg / N).toBeCloseTo(1.8, 1);
  });

  it('função gama confere com valores conhecidos', () => {
    expect(gamaFuncao(1)).toBeCloseTo(1, 10);
    expect(gamaFuncao(5)).toBeCloseTo(24, 8);
    expect(gamaFuncao(0.5)).toBeCloseTo(Math.sqrt(Math.PI), 10);
  });

  it('fluxos separados por fonte e sub-fluxo; semente da rodada depende só de (base, índice)', () => {
    expect(new Set(Object.values(FLUXOS)).size).toBe(Object.keys(FLUXOS).length);
    const a = criaFluxo(5, 'falhas_mr', 0).proximo();
    expect(criaFluxo(5, 'falhas_mr', 0).proximo()).toBe(a);
    expect(criaFluxo(5, 'falhas_ef', 0).proximo()).not.toBe(a);
    expect(criaFluxo(5, 'falhas_mr', 1).proximo()).not.toBe(a);
    expect(sementeDaRodada(1, 7)).toBe(sementeDaRodada(1, 7));
    expect(sementeDaRodada(1, 7)).not.toBe(sementeDaRodada(1, 8));
    expect(misturaSemente(1, 2)).not.toBe(misturaSemente(2, 1));
  });
});

describe('fila de prioridade', () => {
  it('retira em ordem de hora e, no empate, em ordem de inserção', () => {
    const h = new Heap<string>();
    const r = new Rng(3);
    const itens = Array.from({ length: 500 }, (_, i) => ({ t: Math.floor(r.uniforme() * 50), id: `x${i}` }));
    for (const x of itens) h.insere(x.t, x.id);
    const saida: { t: number; id: string }[] = [];
    for (let x = h.retira(); x; x = h.retira()) saida.push({ t: x.t, id: x.valor });
    const esperado = itens.map((x, i) => ({ ...x, i })).sort((a, b) => a.t - b.t || a.i - b.i).map(({ t, id }) => ({ t, id }));
    expect(saida).toEqual(esperado);
  });
});

describe('sorteio de instantes', () => {
  it('Poisson (forma 1) com taxa constante: média e variância iguais à taxa × tempo', () => {
    const acum = taxaAcumuladaConstante(2, 5 * 3600, 25 * 3600); // 2 por hora durante 20 h
    expect(acum[acum.length - 1]).toBeCloseTo(40, 9);
    const r = new Rng(77);
    const cont: number[] = [];
    for (let i = 0; i < 4000; i++) cont.push(sorteiaInstantes(r, acum, 1, 1).length);
    const m = cont.reduce((a, b) => a + b, 0) / cont.length;
    const v = cont.reduce((a, b) => a + (b - m) ** 2, 0) / (cont.length - 1);
    expect(m).toBeCloseTo(40, 0);
    expect(v / m).toBeCloseTo(1, 1);
  });

  it('renovação Weibull com forma < 1 e início em equilíbrio: mesma média, mais variância (agrupamento)', () => {
    const acum = taxaAcumuladaConstante(2, 5 * 3600, 25 * 3600);
    const forma = 0.6;
    const escala = 1 / gamaFuncao(1 + 1 / forma);
    const r = new Rng(78);
    const cont: number[] = [];
    for (let i = 0; i < 6000; i++) cont.push(sorteiaInstantes(r, acum, forma, escala).length);
    const m = cont.reduce((a, b) => a + b, 0) / cont.length;
    const v = cont.reduce((a, b) => a + (b - m) ** 2, 0) / (cont.length - 1);
    expect(Math.abs(m - 40) / 40).toBeLessThan(0.02);
    expect(v / m).toBeGreaterThan(1.3);
  });

  it('inversão da taxa acumulada cai dentro da janela', () => {
    const acum = taxaAcumuladaConstante(3, 6 * 3600, 7 * 3600);
    expect(inverteAcumulada(acum, 1e-9)).toBeGreaterThanOrEqual(6 * 3600);
    expect(inverteAcumulada(acum, 1e-9)).toBeLessThan(6 * 3600 + 1);
    expect(inverteAcumulada(acum, 1.5)).toBeCloseTo(6.5 * 3600, 0);
    expect(inverteAcumulada(acum, acum[acum.length - 1])).toBeCloseTo(7 * 3600, 6); // o fim da janela, não o fim do dia
  });
});
