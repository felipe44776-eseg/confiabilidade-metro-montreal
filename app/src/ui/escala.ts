// Escala para confiabilidade alta (spec 016, decisão D54). Perto de 100%, a disponibilidade esconde as
// diferenças: 99,54% e 99,98% parecem iguais, mas o tempo sem caminho cai 23 vezes. A página mostra o
// complemento (tempo sem caminho por dia), o número de noves e a razão contra a rede atual, medida no
// mesmo dia simulado. Funções puras, sem DOM.

import type { Estimativa } from '../mc/rodadas';

const Z95 = 1.959963984540054;

/** Número de noves da disponibilidade: −log10(1 − A). 99% são 2 noves; 99,9%, 3. Infinity se A = 1. */
export function noves(a: number): number {
  const u = 1 - a;
  return u > 0 ? -Math.log10(u) : Infinity;
}

/** Noves com intervalo: a transformação é crescente, então leva os extremos do intervalo da disponibilidade. */
export function novesIC(e: Pick<Estimativa, 'media' | 'ic95'>): { media: number; ic95: [number, number] } {
  return { media: noves(e.media), ic95: [noves(Math.max(0, e.ic95[0])), noves(Math.min(1, e.ic95[1]))] };
}

/**
 * Razão X / Y das médias de duas medidas pareadas (o mesmo dia simulado com e sem a linha nova), com o
 * intervalo de 95% pelo método delta. `dif` é a estimativa de X − Y dia a dia: dela sai a covariância,
 * Cov(X, Y) = (Var X + Var Y − Var(X − Y)) / 2. Null se a média de Y for zero.
 */
export function razaoPareada(x: Estimativa, y: Estimativa, dif: Estimativa): { media: number; ic95: [number, number] } | null {
  if (!(y.media > 0)) return null;
  const r = x.media / y.media;
  const cov = (x.dp * x.dp + y.dp * y.dp - dif.dp * dif.dp) / 2;
  const n = Math.max(1, Math.min(x.n, y.n));
  const v = Math.max(0, (x.dp * x.dp - 2 * r * cov + r * r * y.dp * y.dp) / (n * y.media * y.media));
  const mh = Z95 * Math.sqrt(v);
  return { media: r, ic95: [Math.max(0, r - mh), r + mh] };
}

/** "26 vezes menos" para razões abaixo de 1; "2,1 vezes mais" acima. `f` formata o número. */
export function textoRazao(r: number, f: (x: number, casas: number) => string): string {
  if (!Number.isFinite(r)) return '—';
  if (r === 0) return 'nenhum minuto';
  if (Math.abs(r - 1) < 0.005) return 'igual';
  const vezes = r < 1 ? 1 / r : r;
  const casas = vezes >= 10 ? 0 : 1;
  return `${f(vezes, casas)} ${vezes >= 1.95 ? 'vezes' : 'vez'} ${r < 1 ? 'menos' : 'mais'}`;
}
