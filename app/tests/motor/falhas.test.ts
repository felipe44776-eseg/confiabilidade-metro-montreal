// Spec 007: falhas injetadas e sorteadas, registro e reprodutibilidade.
import { describe, expect, it } from 'vitest';
import { preparaContexto } from '../../src/motor/contexto';
import type { FalhaInjetada, ResultadoDia } from '../../src/motor/dia';
import { simulaDia } from '../../src/motor/dia';
import { NENHUMA_POLITICA } from '../../src/motor/politicas';
import { carregaFixture, carregaRede } from './apoio';

const OITO_HORAS = 8 * 3600;
const DEZ_MIN = 600;

function ctxSemFalhas() {
  return preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util', semFalhas: true });
}

function roda(injetadas: FalhaInjetada[]): ResultadoDia {
  return simulaDia(ctxSemFalhas(), NENHUMA_POLITICA, 1, { injetadas, trajetorias: true });
}

function atrasoFinal(r: ResultadoDia, chave: string): Map<string, number> {
  const m = new Map<string, number>();
  for (const t of r.trajetorias?.[chave] ?? []) {
    const p = t.ultima - t.viagem.inicio;
    m.set(t.viagem.id, t.chegada[p] - t.viagem.chegada[p]);
  }
  return m;
}

/** Viagem da Laranja no sentido 0 que está entre estações às 08:00. */
function viagemEmCirculacao(): string {
  const ls = carregaRede().horarios.util.porLinha.laranja[0];
  const v = ls.viagens.find((x) => x.partida[0] < OITO_HORAS - 600 && x.chegada[x.chegada.length - 1] > OITO_HORAS + 600 && x.inicio === 0);
  if (!v) throw new Error('sem viagem');
  return v.id;
}

describe('spec 007: reprodutibilidade', () => {
  it('mesma semente e parâmetros dão o mesmo registro (mesmo hash); outra semente dá outro', () => {
    const ctx = preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' });
    const a = simulaDia(ctx, NENHUMA_POLITICA, 42);
    const b = simulaDia(preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' }), NENHUMA_POLITICA, 42);
    expect(a.registro.length).toBeGreaterThan(0);
    expect(b.hash).toBe(a.hash);
    expect(b.registro).toEqual(a.registro);
    const c = simulaDia(ctx, NENHUMA_POLITICA, 43);
    expect(c.hash).not.toBe(a.hash);
  });
});

describe('spec 007: falha de trem', () => {
  it('bloqueia o trecho no sentido do trem, os de trás esperam e o atraso aparece no registro', () => {
    const viagem = viagemEmCirculacao();
    const base = roda([]);
    const r = roda([{ tipo: 'MR', t: OITO_HORAS, duracaoS: DEZ_MIN, linha: 'laranja', viagem }]);
    const falha = r.registro.find((e) => e.tipo === 'FALHA_TREM');
    expect(falha).toMatchObject({ linha: 'laranja', trem: viagem, sentido: 0, fluxo: 'injetada' });
    expect(falha?.trecho).not.toBeNull();
    const atraso = atrasoFinal(r, 'laranja:0');
    const atrasoBase = atrasoFinal(base, 'laranja:0');
    expect(atraso.get(viagem)).toBeGreaterThanOrEqual(DEZ_MIN - 1);
    // os trens de trás esperam: várias viagens do mesmo sentido chegam atrasadas
    const atrasadas = [...atraso.entries()].filter(([id, d]) => id !== viagem && d > 60);
    expect(atrasadas.length).toBeGreaterThan(2);
    expect([...atrasoBase.values()].every((d) => d === 0)).toBe(true);
    // o outro sentido não é afetado
    expect([...atrasoFinal(r, 'laranja:1').values()].every((d) => d === 0)).toBe(true);
    expect(r.registro.filter((e) => e.tipo === 'ATRASO' && e.linha === 'laranja').length).toBeGreaterThan(2);
    expect(r.porLinha.laranja.minutosInterrupcao).toBeCloseTo(10, 6);
    expect(r.porLinha.verde.minutosInterrupcao).toBe(0);
  });
});

describe('spec 007: falha de equipamento fixo', () => {
  it('bloqueia o trecho num sentido ou nos dois, conforme o parâmetro', () => {
    const umSentido = roda([{ tipo: 'EF', t: OITO_HORAS, duracaoS: DEZ_MIN, linha: 'laranja', trecho: 10, sentidos: [0] }]);
    const doisSentidos = roda([{ tipo: 'EF', t: OITO_HORAS, duracaoS: DEZ_MIN, linha: 'laranja', trecho: 10, sentidos: [0, 1] }]);
    const atrasados = (r: ResultadoDia, chave: string) => [...atrasoFinal(r, chave).values()].filter((d) => d > 60).length;
    expect(atrasados(umSentido, 'laranja:0')).toBeGreaterThan(0);
    expect(atrasados(umSentido, 'laranja:1')).toBe(0);
    expect(atrasados(doisSentidos, 'laranja:0')).toBeGreaterThan(0);
    expect(atrasados(doisSentidos, 'laranja:1')).toBeGreaterThan(0);
    const ev = doisSentidos.registro.find((e) => e.tipo === 'FALHA_EF');
    expect(ev).toMatchObject({ linha: 'laranja', trecho: 10, sentido: null });
    expect(umSentido.registro.find((e) => e.tipo === 'FALHA_EF')?.sentido).toBe(0);
  });

  it('o parâmetro sentidos_bloqueio_ef vale para as falhas sorteadas', () => {
    const rede = carregaRede();
    const p = carregaFixture();
    for (const sentidos of [1, 2]) {
      const ctx = preparaContexto(rede, p, { tipoDia: 'util', hipoteses: { sentidos_bloqueio_ef: sentidos } });
      const evs = [0, 1, 2, 3, 4, 5].flatMap((s) => simulaDia(ctx, NENHUMA_POLITICA, s).registro.filter((e) => e.tipo === 'FALHA_EF'));
      expect(evs.length).toBeGreaterThan(0);
      for (const e of evs) expect(e.sentido === null).toBe(sentidos === 2);
    }
  });
});

describe('spec 007: causa comum', () => {
  it('para a Verde e a Laranja ao mesmo tempo', () => {
    const r = roda([{ tipo: 'CC', t: OITO_HORAS, duracaoS: DEZ_MIN, par: 'verde-laranja' }]);
    const cc = r.registro.filter((e) => e.tipo === 'CAUSA_COMUM');
    expect(cc.map((e) => e.linha).sort()).toEqual(['laranja', 'verde']);
    expect(new Set(cc.map((e) => e.t)).size).toBe(1);
    expect(r.porLinha.verde.minutosInterrupcao).toBeCloseTo(10, 6);
    expect(r.porLinha.laranja.minutosInterrupcao).toBeCloseTo(10, 6);
    expect(r.porLinha.azul.minutosInterrupcao).toBe(0);
    expect(r.porLinha.amarela.minutosInterrupcao).toBe(0);
    expect(r.porLinha.verde.minutosPorCausa.CC).toBeCloseTo(10, 6);
  });
});

describe('spec 007: registro', () => {
  it('cada evento tem hora, linha, trem, trecho, tipo e origem do sorteio', () => {
    const ctx = preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' });
    const eventos = [1, 2, 3, 4, 5, 6, 7, 8].flatMap((s) => simulaDia(ctx, NENHUMA_POLITICA, s).registro);
    expect(eventos.length).toBeGreaterThan(10);
    for (const e of eventos) {
      expect(Number.isFinite(e.t)).toBe(true);
      expect(e.linha).toBeTruthy();
      expect(e.tipo).toBeTruthy();
      expect(e.fluxo).toBeTruthy();
      for (const campo of ['trem', 'trecho', 'sentido', 'sorteio', 'duracaoS'] as const) expect(campo in e).toBe(true);
    }
    for (const e of eventos.filter((x) => x.tipo === 'FALHA_TREM')) {
      expect(e.trem).toMatch(/^[a-z]+:[01]:\d+$/);
      expect(e.trecho).not.toBeNull();
      expect(e.fluxo).toBe('falhas_mr');
      expect(e.sorteio).not.toBeNull();
    }
    for (const e of eventos.filter((x) => x.tipo === 'FALHA_EF')) {
      expect(e.trecho).not.toBeNull();
      expect(e.fluxo).toBe('falhas_ef');
    }
    // cada registro sai em ordem de hora
    for (const s of [1, 2, 3]) {
      const reg = simulaDia(ctx, NENHUMA_POLITICA, s).registro;
      for (let i = 1; i < reg.length; i++) expect(reg[i].t).toBeGreaterThanOrEqual(reg[i - 1].t);
    }
  });

  it('falhas sorteadas por dia batem com a taxa do cenário', () => {
    const ctx = preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' });
    const esperado = ctx.fontes.reduce((a, f) => a + f.acum[f.acum.length - 1], 0);
    let total = 0;
    const N = 600;
    for (let s = 0; s < N; s++) {
      const r = simulaDia(ctx, NENHUMA_POLITICA, s, { registrar: false });
      for (const m of Object.values(r.porLinha)) total += m.falhas.MR + m.falhas.EF;
    }
    // Poisson-agrupado: tolerância de 8% em 600 dias
    expect(Math.abs(total / N - esperado) / esperado).toBeLessThan(0.08);
  });
});
