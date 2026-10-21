// Web Worker da expansão da rede (spec 014): avalia candidatas ou faz a busca exaustiva sem travar a página.

import type { Candidata, ItemRanking, OpcoesEstados } from '../motor/expansao';
import { avaliaCandidatas, buscaExaustiva } from '../motor/expansao';
import type { Rede } from '../motor/rede';
import { montaRede } from '../motor/rede';
import type { Cenario, Parametros, RedeJson } from '../motor/tipos';

export type PedidoExpansao =
  | { tipo: 'candidatas'; redeJson: RedeJson; chaveRede: string; parametros: Parametros; cenario: Cenario; candidatas: Candidata[]; opcoes: OpcoesEstados }
  | { tipo: 'busca'; redeJson: RedeJson; chaveRede: string; parametros: Parametros; cenario: Cenario; distanciaMaxKm: number; opcoes: OpcoesEstados };

export type RespostaExpansao =
  | { tipo: 'candidatas'; ranking: ItemRanking[]; segundos: number }
  | { tipo: 'busca'; porGanho: ItemRanking[]; porKm: ItemRanking[]; segundos: number }
  | { tipo: 'erro'; mensagem: string };

const escopo = self as unknown as DedicatedWorkerGlobalScope;
let guardada: { chave: string; rede: Rede } | null = null;

escopo.onmessage = (ev: MessageEvent<PedidoExpansao>) => {
  const m = ev.data;
  const t0 = performance.now();
  try {
    if (!guardada || guardada.chave !== m.chaveRede) guardada = { chave: m.chaveRede, rede: montaRede(m.redeJson) };
    if (m.tipo === 'candidatas') {
      const ranking = avaliaCandidatas(guardada.rede, m.parametros, m.cenario, m.candidatas, m.opcoes);
      escopo.postMessage({ tipo: 'candidatas', ranking, segundos: (performance.now() - t0) / 1000 } satisfies RespostaExpansao);
    } else {
      const r = buscaExaustiva(guardada.rede, m.parametros, m.cenario, m.distanciaMaxKm, m.opcoes);
      escopo.postMessage({ tipo: 'busca', ...r, segundos: (performance.now() - t0) / 1000 } satisfies RespostaExpansao);
    }
  } catch (erro) {
    escopo.postMessage({ tipo: 'erro', mensagem: erro instanceof Error ? erro.message : String(erro) } satisfies RespostaExpansao);
  }
};
