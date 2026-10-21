// Efeito do cenário no número de falhas (spec 011): falhas esperadas por dia, pela mesma taxa acumulada
// que o motor usa no sorteio. Serve para a pessoa ver que o cenário escolhido está valendo.

import type { Contexto } from '../motor/contexto';
import { reducaoCausaComum } from '../motor/contexto';
import type { Politicas } from '../motor/politicas';
import { falhasEsperadas } from '../motor/taxas';

export interface FalhasLinha {
  MR: number;
  EF: number;
  /** Causa comum: um evento conta uma vez em cada linha que para, como na lista do dia e no Monte Carlo. */
  CC: number;
  total: number;
}

export interface Esperado {
  porLinha: Record<string, FalhasLinha>;
  total: number;
}

/** Falhas esperadas por dia de operação no cenário do contexto. Das políticas, só o tratamento da causa comum muda a contagem. */
export function esperadoPorDia(ctx: Contexto, politicas: Politicas): Esperado {
  const porLinha: Record<string, FalhasLinha> = {};
  for (const l of ctx.rede.ids) porLinha[l] = { MR: 0, EF: 0, CC: 0, total: 0 };
  for (const f of ctx.fontes) porLinha[f.linha][f.causa] += falhasEsperadas(f.acum);
  const mantidos = 1 - reducaoCausaComum(ctx, politicas);
  for (const c of ctx.causaComum) {
    const e = falhasEsperadas(c.acum) * mantidos;
    for (const l of c.linhas) porLinha[l].CC += e;
  }
  let total = 0;
  for (const v of Object.values(porLinha)) {
    v.total = v.MR + v.EF + v.CC;
    total += v.total;
  }
  return { porLinha, total };
}
