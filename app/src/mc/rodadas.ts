// Monte Carlo (spec 009): rodadas independentes, uma por dia de operação.
// A rodada i usa a semente derivada de (semente-base, i). Por isso o resultado não depende de quantos
// workers dividem as rodadas: a agregação ordena pelo índice antes de somar.

import type { Contexto } from '../motor/contexto';
import type { ResultadoDia } from '../motor/dia';
import { simulaDia } from '../motor/dia';
import type { Politicas } from '../motor/politicas';
import { sementeDaRodada } from '../motor/prng';
import type { TipoDia } from '../motor/tipos';

/** Calendário típico: 365 dias, feriados com horário de domingo (aproximação declarada). */
export const DIAS_POR_TIPO_ANO: Record<TipoDia, number> = { util: 251, sabado: 52, domingo: 62 };

/** Quantil da normal para o intervalo de 95%. */
const Z95 = 1.959963984540054;

export interface Rodada {
  indice: number;
  semente: number;
  valores: number[];
  valoresB?: number[]; // mesma semente com as políticas de comparação (números aleatórios comuns)
}

export interface Estimativa {
  media: number;
  dp: number;
  ep: number;
  ic95: [number, number];
  meiaLargura: number;
  n: number;
  semente: number;
}

export function nomesMetricas(ids: string[]): string[] {
  const nomes: string[] = [];
  for (const l of ids) {
    for (const m of [
      'minutosInterrupcao',
      'minutosMR',
      'minutosEF',
      'minutosCC',
      'disponibilidade',
      'trensHoraPerdidos',
      'viagensAfetadas',
      'viagensCanceladas',
      'frotaCompleta',
      'falhasMR',
      'falhasEF',
      'falhasCC',
    ])
      nomes.push(`${l}.${m}`);
  }
  for (const m of ['minutosInterrupcao', 'trensHoraPerdidos', 'dispOD', 'extraMin', 'minutosParInterrompido']) nomes.push(`rede.${m}`);
  return nomes;
}

export function metricasDoDia(r: ResultadoDia, ids: string[]): number[] {
  const v: number[] = [];
  for (const l of ids) {
    const m = r.porLinha[l];
    v.push(
      m.minutosInterrupcao,
      m.minutosPorCausa.MR,
      m.minutosPorCausa.EF,
      m.minutosPorCausa.CC,
      m.disponibilidade,
      m.trensHoraPerdidos,
      m.viagensAfetadas,
      m.viagensCanceladas,
      m.frotaCompleta ? 1 : 0,
      m.falhas.MR,
      m.falhas.EF,
      m.falhas.CC,
    );
  }
  v.push(r.rede.minutosInterrupcao, r.rede.trensHoraPerdidos, r.rede.dispOD, r.rede.extraMin, r.rede.minutosParInterrompido);
  return v;
}

/** Função pura: roda as rodadas dos índices dados. Com `politicasB`, roda também a variante com a mesma semente. */
export function rodaRodadas(
  indices: readonly number[],
  ctx: Contexto,
  politicas: Politicas,
  sementeBase: number,
  politicasB?: Politicas,
  aoProgresso?: (feitas: number) => void,
): Rodada[] {
  const ids = ctx.rede.ids;
  const saida: Rodada[] = [];
  indices.forEach((indice, k) => {
    const semente = sementeDaRodada(sementeBase, indice);
    const a = simulaDia(ctx, politicas, semente, { registrar: false });
    const rodada: Rodada = { indice, semente, valores: metricasDoDia(a, ids) };
    if (politicasB) rodada.valoresB = metricasDoDia(simulaDia(ctx, politicasB, semente, { registrar: false }), ids);
    saida.push(rodada);
    if (aoProgresso && (k + 1) % 50 === 0) aoProgresso(k + 1);
  });
  return saida;
}

export function estimativa(xs: readonly number[], semente: number): Estimativa {
  const n = xs.length;
  let soma = 0;
  for (const x of xs) soma += x;
  const media = n ? soma / n : NaN;
  let q = 0;
  for (const x of xs) q += (x - media) * (x - media);
  const dp = n > 1 ? Math.sqrt(q / (n - 1)) : 0;
  const ep = n ? dp / Math.sqrt(n) : NaN;
  const meiaLargura = Z95 * ep;
  return { media, dp, ep, ic95: [media - meiaLargura, media + meiaLargura], meiaLargura, n, semente };
}

export interface Agregado {
  porMetrica: Record<string, Estimativa>;
  porMetricaB?: Record<string, Estimativa>;
  diferenca?: Record<string, Estimativa>; // B - A, pareada
  n: number;
  sementeBase: number;
}

/** Agrega na ordem dos índices: o mesmo conjunto de rodadas dá o mesmo resultado, em qualquer divisão em lotes. */
export function agrega(rodadas: readonly Rodada[], nomes: readonly string[], sementeBase: number): Agregado {
  const ordenadas = [...rodadas].sort((a, b) => a.indice - b.indice);
  const porMetrica: Record<string, Estimativa> = {};
  const temB = ordenadas.length > 0 && ordenadas.every((r) => r.valoresB);
  const porMetricaB: Record<string, Estimativa> = {};
  const diferenca: Record<string, Estimativa> = {};
  nomes.forEach((nome, j) => {
    porMetrica[nome] = estimativa(
      ordenadas.map((r) => r.valores[j]),
      sementeBase,
    );
    if (temB) {
      porMetricaB[nome] = estimativa(
        ordenadas.map((r) => (r.valoresB as number[])[j]),
        sementeBase,
      );
      diferenca[nome] = estimativa(
        ordenadas.map((r) => (r.valoresB as number[])[j] - r.valores[j]),
        sementeBase,
      );
    }
  });
  const ag: Agregado = { porMetrica, n: ordenadas.length, sementeBase };
  if (temB) {
    ag.porMetricaB = porMetricaB;
    ag.diferenca = diferenca;
  }
  return ag;
}

/** Soma por tipo de dia ponderada pelo calendário: total por ano, com intervalo. */
export function anualiza(porTipo: Partial<Record<TipoDia, Estimativa>>, dias: Record<TipoDia, number> = DIAS_POR_TIPO_ANO): Estimativa {
  let media = 0;
  let variancia = 0;
  let n = 0;
  let semente = 0;
  for (const [tipo, e] of Object.entries(porTipo) as [TipoDia, Estimativa][]) {
    media += dias[tipo] * e.media;
    variancia += dias[tipo] * dias[tipo] * e.ep * e.ep;
    n += e.n;
    semente = e.semente;
  }
  const ep = Math.sqrt(variancia);
  const meiaLargura = Z95 * ep;
  return { media, dp: NaN, ep, ic95: [media - meiaLargura, media + meiaLargura], meiaLargura, n, semente };
}

/** Rodadas necessárias para a meia-largura do IC95 ficar em `alvo` × média (spec 009: 5%). */
export function rodadasParaPrecisao(e: Estimativa, alvo = 0.05): number {
  if (!(e.media > 0) || !(e.dp > 0)) return e.n;
  return Math.ceil(((Z95 * e.dp) / (alvo * e.media)) ** 2);
}

/** Teto de rodadas do modo adaptativo (spec 009). */
export const MAX_RODADAS = 50_000;
/** Tamanho do lote do modo adaptativo: a precisão é conferida a cada lote. */
export const LOTE_ADAPTATIVO = 1_000;
/** Precisão pedida pela spec 009: meia-largura do IC95 até 5% da média dos minutos parados. */
export const PRECISAO_ALVO = 0.05;

/**
 * Roda lotes de rodadas (índices 0, 1, 2, ...) até a meia-largura do IC95 das métricas indicadas ficar
 * em `alvo` × média, ou até `max` rodadas. Determinístico: o mesmo pedido para no mesmo ponto.
 */
export function rodaAtePrecisao(
  ctx: Contexto,
  politicas: Politicas,
  sementeBase: number,
  metricas: readonly string[],
  opcoes: { alvo?: number; lote?: number; max?: number; politicasB?: Politicas } = {},
): { agregado: Agregado; atingiu: boolean; rodadas: Rodada[] } {
  const alvo = opcoes.alvo ?? PRECISAO_ALVO;
  const lote = opcoes.lote ?? LOTE_ADAPTATIVO;
  const max = opcoes.max ?? MAX_RODADAS;
  const nomes = nomesMetricas(ctx.rede.ids);
  const rodadas: Rodada[] = [];
  for (;;) {
    const ini = rodadas.length;
    const n = Math.min(lote, max - ini);
    rodadas.push(...rodaRodadas(Array.from({ length: n }, (_, i) => ini + i), ctx, politicas, sementeBase, opcoes.politicasB));
    const agregado = agrega(rodadas, nomes, sementeBase);
    const atingiu = metricas.every((m) => {
      const e = agregado.porMetrica[m];
      return e && (e.media === 0 || e.meiaLargura <= alvo * Math.abs(e.media));
    });
    if (atingiu || rodadas.length >= max) return { agregado, atingiu, rodadas };
  }
}

/** Divide índices 0..n-1 em k lotes contíguos (o pool usa um lote por worker). */
export function divideEmLotes(n: number, k: number): number[][] {
  const lotes: number[][] = [];
  const tam = Math.ceil(n / k);
  for (let i = 0; i < n; i += tam) lotes.push(Array.from({ length: Math.min(tam, n - i) }, (_, j) => i + j));
  return lotes;
}
