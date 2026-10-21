// Formatação de números em pt-BR.

const cache = new Map<string, Intl.NumberFormat>();

function nf(min: number, max: number, estilo: 'decimal' | 'percent' = 'decimal'): Intl.NumberFormat {
  const k = `${min}|${max}|${estilo}`;
  let f = cache.get(k);
  if (!f) {
    f = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: min, maximumFractionDigits: max, style: estilo });
    cache.set(k, f);
  }
  return f;
}

export function num(x: number, casas = 1): string {
  return Number.isFinite(x) ? nf(casas, casas).format(x) : '—';
}

export function pct(x: number, casas = 2): string {
  return Number.isFinite(x) ? nf(casas, casas, 'percent').format(x) : '—';
}

/** Pontos percentuais com sinal (diferença de duas frações). */
export function pp(x: number, casas = 3): string {
  if (!Number.isFinite(x)) return '—';
  return `${x > 0 ? '+' : ''}${nf(casas, casas).format(x * 100)} pp`;
}

export function comSinal(x: number, casas = 1): string {
  if (!Number.isFinite(x)) return '—';
  return `${x > 0 ? '+' : ''}${nf(casas, casas).format(x)}`;
}

export function inteiro(x: number): string {
  return Number.isFinite(x) ? nf(0, 0).format(x) : '—';
}

/** Valor com o intervalo de 95%: "1,23 (1,10–1,40)". */
export function comIC(valor: number, ic: readonly number[] | null | undefined, casas = 2, f: (x: number, c: number) => string = num): string {
  if (!ic || ic.length !== 2) return f(valor, casas);
  return `${f(valor, casas)} (${f(ic[0], casas)}–${f(ic[1], casas)})`;
}

/** Número de casas para mostrar uma meia-largura com 2 algarismos significativos. */
export function casasPara(meiaLargura: number, max = 4): number {
  if (!(meiaLargura > 0)) return 1;
  return Math.max(0, Math.min(max, 1 - Math.floor(Math.log10(meiaLargura))));
}
