// Taxa de falha do cenário (spec 005) e sorteio dos instantes de falha (spec 006).
//
// λ(t) = taxa-base por trem-hora × Π multiplicadores das condições daquela hora × trens em circulação.
// Os instantes vêm de uma renovação Weibull no tempo reescalado Λ(t) = ∫ λ: forma 1 é Poisson com
// taxa variável; forma < 1 agrupa falhas. A escala é normalizada para média 1 no tempo reescalado,
// para que o número esperado de falhas seja o do modelo de taxa (desvio registrado no plan.md da 007).

import type { Rng } from './prng';
import { gamaFuncao } from './prng';
import type { HorarioDia } from './rede';
import { MINUTOS_DIA_OPERACAO } from './rede';
import type { Causa, Cenario, Condicoes, Parametros, Taxa } from './tipos';

/** Faixas horárias do modelo de taxa, em hora de serviço (pipeline/modelo_taxa.py, FAIXAS). */
export const FAIXAS_HORARIAS: readonly [number, number, string][] = [
  [5, 6, 'abertura'],
  [7, 9, 'pico_manha'],
  [10, 15, 'entrepico'],
  [16, 18, 'pico_tarde'],
  [19, 22, 'noite'],
  [23, 29, 'fim'],
];

export function faixaDe(hora: number): string {
  for (const [a, b, nome] of FAIXAS_HORARIAS) if (hora >= a && hora <= b) return nome;
  return hora < FAIXAS_HORARIAS[0][0] ? FAIXAS_HORARIAS[0][2] : FAIXAS_HORARIAS[FAIXAS_HORARIAS.length - 1][2];
}

/** Nível de cada fator numa hora: faixa e tipo de dia vêm do relógio; o resto do cenário ou da referência. */
export function condicoesDaHora(cenario: Cenario, hora: number): Condicoes {
  return { ...(cenario.condicoes ?? {}), ...(cenario.condicoesPorHora?.[hora] ?? {}), faixa: faixaDe(hora), tipo_dia: cenario.tipoDia };
}

/** Produto dos multiplicadores. Nível sem coeficiente (referência ou indicador desligado) vale 1. */
export function multiplicador(taxa: Taxa, cond: Condicoes): number {
  let m = 1;
  for (const [fator, niveis] of Object.entries(taxa.multiplicadores)) {
    const nivel = cond[fator] ?? taxa.referencia?.[fator] ?? '0';
    const p = niveis[nivel];
    if (p) m *= p.valor;
  }
  return m;
}

/**
 * Taxa acumulada Λ por minuto do dia de operação: lambdaAcum[m] = falhas esperadas até o início do minuto m.
 * Tamanho MINUTOS_DIA_OPERACAO + 1.
 */
export function taxaAcumulada(params: Parametros, horario: HorarioDia, cenario: Cenario, linha: string, causa: Causa): Float64Array {
  const taxa = params.taxas[causa];
  const base = taxa.base_por_trem_hora[linha]?.valor;
  // dado ausente nunca vira zero (constituição, princípio 6): taxa zero faria a linha nunca falhar
  if (base === undefined) throw new Error(`parametros.json sem taxa-base de ${causa} para a linha ${linha}`);
  const trens = horario.trensPorMinuto[linha];
  const acum = new Float64Array(MINUTOS_DIA_OPERACAO + 1);
  const multHora = new Map<number, number>();
  for (let m = 0; m < MINUTOS_DIA_OPERACAO; m++) {
    const hora = Math.floor(m / 60);
    let mult = multHora.get(hora);
    if (mult === undefined) {
      mult = multiplicador(taxa, condicoesDaHora(cenario, hora));
      multHora.set(hora, mult);
    }
    acum[m + 1] = acum[m] + (base * mult * trens[m]) / 60;
  }
  return acum;
}

/** Taxa constante por hora entre dois instantes (causa comum: eventos por hora de operação). */
export function taxaAcumuladaConstante(porHora: number, ini: number, fim: number): Float64Array {
  const acum = new Float64Array(MINUTOS_DIA_OPERACAO + 1);
  for (let m = 0; m < MINUTOS_DIA_OPERACAO; m++) {
    const a = Math.max(ini, m * 60);
    const b = Math.min(fim, (m + 1) * 60);
    acum[m + 1] = acum[m] + (b > a ? (porHora * (b - a)) / 3600 : 0);
  }
  return acum;
}

/** Primeiro instante (s) em que Λ atinge x. Supõe 0 < x <= Λ(fim); trechos de taxa zero são pulados. */
export function inverteAcumulada(acum: Float64Array, x: number): number {
  if (x <= acum[0]) return 0;
  let lo = 0;
  let hi = acum.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (acum[mid] < x) lo = mid;
    else hi = mid;
  }
  const d = acum[hi] - acum[lo];
  const frac = d > 0 ? (x - acum[lo]) / d : 1;
  return (lo + Math.min(Math.max(frac, 0), 1)) * 60;
}

export interface Renovacao01 {
  forma: number;
  escalaNormalizada: number; // escala que dá média 1 no tempo reescalado
  escalaArquivo: number;
}

export function renovacaoDe(params: Parametros, linha: string, causa: Causa): Renovacao01 {
  const r = params.renovacao[`${linha}|${causa}`];
  const forma = r && r.forma.valor > 0 ? r.forma.valor : 1;
  return { forma, escalaNormalizada: 1 / gamaFuncao(1 + 1 / forma), escalaArquivo: r?.escala.valor ?? 1 };
}

/**
 * Instantes de falha no dia. O primeiro intervalo é o de equilíbrio (tempo residual de uma renovação
 * estacionária), porque cada rodada é um dia tirado do meio da operação, não o primeiro dia da rede.
 */
export function sorteiaInstantes(rng: Rng, acum: Float64Array, forma: number, escala: number): number[] {
  const total = acum[acum.length - 1];
  const saida: number[] = [];
  if (!(total > 0)) return saida;
  // residual de equilíbrio: U × X, com X da distribuição ponderada pelo comprimento.
  // Para a Weibull, (X/escala)^forma ~ Gama(1 + 1/forma).
  let x = rng.uniforme() * escala * Math.pow(rng.gama(1 + 1 / forma), 1 / forma);
  while (x <= total) {
    saida.push(inverteAcumulada(acum, x));
    x += rng.weibull(forma, escala);
  }
  return saida;
}

/** Falhas esperadas no dia, para conferência. */
export function falhasEsperadas(acum: Float64Array): number {
  return acum[acum.length - 1];
}
