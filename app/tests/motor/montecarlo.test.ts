// Spec 009: Monte Carlo reprodutível em qualquer divisão em lotes, métricas com IC95, n e semente,
// comparação com o painel e tempo de 5.000 rodadas.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import type { Estimativa } from '../../src/mc/rodadas';
import { DIAS_POR_TIPO_ANO, MAX_RODADAS, agrega, anualiza, divideEmLotes, estimativa, nomesMetricas, rodaAtePrecisao, rodaRodadas, rodadasParaPrecisao } from '../../src/mc/rodadas';
import { preparaContexto } from '../../src/motor/contexto';
import { NENHUMA_POLITICA } from '../../src/motor/politicas';
import type { TipoDia } from '../../src/motor/tipos';
import { carregaFixture, carregaRede } from './apoio';

const LONGO = 600_000;
const SEMENTE = 20261021;

interface Corredor {
  cenario: string;
  min_ano_analitico: number;
  sim_min_ano: number | null;
}
const corredor = JSON.parse(readFileSync(resolve(__dirname, '../../../dados/derivados/painel/corredor.json'), 'utf8')) as Corredor[];

describe('spec 009: Monte Carlo', () => {
  it('1 lote ou 8 lotes dão resultados idênticos', () => {
    const ctx = preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' });
    const nomes = nomesMetricas(ctx.rede.ids);
    const N = 240;
    const umLote = agrega(rodaRodadas(Array.from({ length: N }, (_, i) => i), ctx, NENHUMA_POLITICA, SEMENTE), nomes, SEMENTE);
    // 8 "workers": cada um com o próprio contexto, lotes processados fora de ordem
    const lotes = divideEmLotes(N, 8).reverse();
    const partes = lotes.flatMap((ind) => rodaRodadas(ind, preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' }), NENHUMA_POLITICA, SEMENTE));
    const oitoLotes = agrega(partes, nomes, SEMENTE);
    expect(lotes).toHaveLength(8);
    expect(oitoLotes).toEqual(umLote);
  }, LONGO);

  it('estimativa: média, IC95 normal, n e semente', () => {
    const e = estimativa([1, 2, 3, 4, 5], 7);
    expect(e.media).toBe(3);
    expect(e.dp).toBeCloseTo(Math.sqrt(2.5), 12);
    expect(e.meiaLargura).toBeCloseTo((1.959963984540054 * Math.sqrt(2.5)) / Math.sqrt(5), 12);
    expect(e.ic95[0]).toBeCloseTo(3 - e.meiaLargura, 12);
    expect(e.n).toBe(5);
    expect(e.semente).toBe(7);
  });

  it('métricas publicadas: disponibilidade por linha, OD ponderada com tempo extra, trens-hora perdidos e minutos de interrupção, cada uma com IC95, n e semente', () => {
    const ctx = preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' });
    const ag = agrega(rodaRodadas(Array.from({ length: 100 }, (_, i) => i), ctx, NENHUMA_POLITICA, SEMENTE), nomesMetricas(ctx.rede.ids), SEMENTE);
    for (const nome of ['verde.disponibilidade', 'laranja.trensHoraPerdidos', 'azul.minutosInterrupcao', 'rede.dispOD', 'rede.extraMin', 'rede.minutosParInterrompido', 'rede.trensHoraPerdidos']) {
      const e = ag.porMetrica[nome];
      expect(e, nome).toBeDefined();
      expect(e.n).toBe(100);
      expect(e.semente).toBe(SEMENTE);
      expect(e.ic95[0]).toBeLessThanOrEqual(e.media);
      expect(e.ic95[1]).toBeGreaterThanOrEqual(e.media);
    }
  }, LONGO);

  it('Laranja sem redundância: minutos parados por ano contra o painel (1.852 simulado, 1.797 analítico)', () => {
    const rede = carregaRede();
    const p = carregaFixture();
    const N = 1500;
    const porTipo: Partial<Record<TipoDia, Estimativa>> = {};
    const tecnicas: Partial<Record<TipoDia, Estimativa>> = {};
    for (const tipoDia of ['util', 'sabado', 'domingo'] as TipoDia[]) {
      const ctx = preparaContexto(rede, p, { tipoDia });
      const ag = agrega(rodaRodadas(Array.from({ length: N }, (_, i) => i), ctx, NENHUMA_POLITICA, SEMENTE), nomesMetricas(rede.ids), SEMENTE);
      porTipo[tipoDia] = ag.porMetrica['laranja.minutosInterrupcao'];
      const mr = ag.porMetrica['laranja.minutosMR'];
      const ef = ag.porMetrica['laranja.minutosEF'];
      tecnicas[tipoDia] = { ...mr, media: mr.media + ef.media, ep: Math.hypot(mr.ep, ef.ep) };
    }
    const total = anualiza(porTipo);
    const soLinha = anualiza(tecnicas);
    const ref = corredor.find((c) => c.cenario === 'so_laranja');
    expect(ref?.sim_min_ano).toBeCloseTo(1852.34, 1);
    expect(ref?.min_ano_analitico).toBeCloseTo(1797.04, 1);
    const contem = (e: Estimativa, x: number) => e.ic95[0] <= x && x <= e.ic95[1];
    console.log(
      `Laranja, minutos parados por ano (${N} rodadas por tipo de dia, semente ${SEMENTE}, calendário ${JSON.stringify(DIAS_POR_TIPO_ANO)}):`,
      `total ${total.media.toFixed(0)} [${total.ic95.map((x) => x.toFixed(0)).join(', ')}]`,
      `só MR+EF ${soLinha.media.toFixed(0)} [${soLinha.ic95.map((x) => x.toFixed(0)).join(', ')}]`,
      `contém 1852: ${contem(total, 1852.34)}; contém 1797: ${contem(total, 1797.04)}`,
    );
    // critério da spec: o IC contém 1.852 ou 1.797, ou a diferença é explicada no relatório (plan.md da 009)
    expect(Math.abs(total.media - 1797.04) / 1797.04).toBeLessThan(0.15);
  }, LONGO);

  it('rodadas para a meia-largura ficar em 5% da média dos minutos parados de cada linha cabem no teto do modo adaptativo', () => {
    const ctx = preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' });
    const ag = agrega(rodaRodadas(Array.from({ length: 1500 }, (_, i) => i), ctx, NENHUMA_POLITICA, SEMENTE), nomesMetricas(ctx.rede.ids), SEMENTE);
    const necessarias = Object.fromEntries(ctx.rede.ids.map((l) => [l, rodadasParaPrecisao(ag.porMetrica[`${l}.minutosInterrupcao`])]));
    console.log('rodadas necessárias para 5% (dia útil):', JSON.stringify(necessarias));
    for (const n of Object.values(necessarias)) expect(n).toBeLessThanOrEqual(MAX_RODADAS);
  }, LONGO);

  it('modo adaptativo para quando atinge a precisão pedida', () => {
    const ctx = preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' });
    const r = rodaAtePrecisao(ctx, NENHUMA_POLITICA, SEMENTE, ['rede.minutosInterrupcao'], { alvo: 0.15, lote: 200, max: 4000 });
    expect(r.atingiu).toBe(true);
    const e = r.agregado.porMetrica['rede.minutosInterrupcao'];
    expect(e.meiaLargura).toBeLessThanOrEqual(0.15 * e.media);
    expect(r.rodadas.length % 200).toBe(0);
    expect(r.rodadas.length).toBeLessThan(4000);
  }, LONGO);

  it('tempo de 5.000 rodadas (1 rodada = 1 dia útil), em Node, uma thread', () => {
    const ctx = preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' });
    const t0 = performance.now();
    const rod = rodaRodadas(Array.from({ length: 5000 }, (_, i) => i), ctx, NENHUMA_POLITICA, SEMENTE);
    const s = (performance.now() - t0) / 1000;
    console.log(`5.000 rodadas em ${s.toFixed(1)} s (${((s / 5000) * 1000).toFixed(2)} ms por dia)`);
    expect(rod).toHaveLength(5000);
    expect(s).toBeLessThan(120);
  }, LONGO);
});
