// Web Worker da viagem de A a B (spec 015): roda um lote de dias e devolve as métricas da viagem em cada um.

import type { Rodada } from '../mc/rodadas';
import type { Contexto } from '../motor/contexto';
import { preparaContexto } from '../motor/contexto';
import type { Politicas } from '../motor/politicas';
import type { Rede } from '../motor/rede';
import { montaRede } from '../motor/rede';
import type { Cenario, Parametros, RedeJson } from '../motor/tipos';
import { preparaViagem, rodaViagem } from '../motor/viagem';

export interface PedidoViagem {
  redeJson: RedeJson;
  chaveRede: string;
  parametros: Parametros;
  cenario: Cenario;
  politicas: Politicas;
  sementeBase: number;
  rodadas: number;
  origem: string; // id da estação
  destino: string;
}

export type PedidoLoteViagem = { tipo: 'viagem'; id: number; indices: number[] } & Omit<PedidoViagem, 'rodadas'>;

export type RespostaViagem = { tipo: 'progresso'; id: number; feitas: number } | { tipo: 'resultado'; id: number; rodadas: Rodada[] } | { tipo: 'erro'; id: number; mensagem: string };

const escopo = self as unknown as DedicatedWorkerGlobalScope;
let redeGuardada: { chave: string; rede: Rede } | null = null;

function contexto(m: PedidoLoteViagem): Contexto {
  if (!redeGuardada || redeGuardada.chave !== m.chaveRede) redeGuardada = { chave: m.chaveRede, rede: montaRede(m.redeJson) };
  return preparaContexto(redeGuardada.rede, m.parametros, m.cenario);
}

escopo.onmessage = (ev: MessageEvent<PedidoLoteViagem>) => {
  const m = ev.data;
  if (m.tipo !== 'viagem') return;
  try {
    const ctx = contexto(m);
    const av = preparaViagem(ctx, m.origem, m.destino, m.politicas.rotaAlternativa);
    if (!av) throw new Error('não há caminho entre as estações escolhidas');
    const rodadas = rodaViagem(m.indices, ctx, m.politicas, m.sementeBase, av, (feitas) => escopo.postMessage({ tipo: 'progresso', id: m.id, feitas } satisfies RespostaViagem));
    escopo.postMessage({ tipo: 'resultado', id: m.id, rodadas } satisfies RespostaViagem);
  } catch (erro) {
    escopo.postMessage({ tipo: 'erro', id: m.id, mensagem: erro instanceof Error ? erro.message : String(erro) } satisfies RespostaViagem);
  }
};
