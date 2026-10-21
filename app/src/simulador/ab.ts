// Comparação de dois cenários com números aleatórios comuns (spec 011): a rodada i de A e de B usa a
// mesma semente, derivada de (semente-base, i). A diferença B − A é pareada rodada a rodada.

import type { Contexto } from '../motor/contexto';
import { simulaDia } from '../motor/dia';
import type { Politicas } from '../motor/politicas';
import { sementeDaRodada } from '../motor/prng';
import type { Rodada } from '../mc/rodadas';
import { metricasDoDia } from '../mc/rodadas';

export function rodaRodadasAB(
  indices: readonly number[],
  ctxA: Contexto,
  politicasA: Politicas,
  ctxB: Contexto,
  politicasB: Politicas,
  sementeBase: number,
  aoProgresso?: (feitas: number) => void,
): Rodada[] {
  const ids = ctxA.rede.ids;
  const saida: Rodada[] = [];
  indices.forEach((indice, k) => {
    const semente = sementeDaRodada(sementeBase, indice);
    const a = simulaDia(ctxA, politicasA, semente, { registrar: false });
    const b = simulaDia(ctxB, politicasB, semente, { registrar: false });
    saida.push({ indice, semente, valores: metricasDoDia(a, ids), valoresB: metricasDoDia(b, ids) });
    if (aoProgresso && (k + 1) % 50 === 0) aoProgresso(k + 1);
  });
  return saida;
}
