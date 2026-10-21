// Web Worker da comparação de cenários: roda um lote de rodadas de A e de B com as mesmas sementes.

import { preparaContexto } from '../motor/contexto';
import type { Rede } from '../motor/rede';
import { montaRede } from '../motor/rede';
import type { Politicas } from '../motor/politicas';
import type { Cenario, Parametros, RedeJson } from '../motor/tipos';
import type { Rodada } from '../mc/rodadas';
import { rodaRodadasAB } from './ab';

export interface LadoAB {
  redeJson: RedeJson;
  chaveRede: string;
  cenario: Cenario;
  politicas: Politicas;
}

export interface PedidoLoteAB {
  tipo: 'ab';
  id: number;
  indices: number[];
  parametros: Parametros;
  a: LadoAB;
  b: LadoAB;
  sementeBase: number;
}

export type RespostaAB = { tipo: 'progresso'; id: number; feitas: number } | { tipo: 'resultado'; id: number; rodadas: Rodada[] } | { tipo: 'erro'; id: number; mensagem: string };

const escopo = self as unknown as DedicatedWorkerGlobalScope;
const redes = new Map<string, Rede>();

function rede(lado: LadoAB): Rede {
  let r = redes.get(lado.chaveRede);
  if (!r) {
    r = montaRede(lado.redeJson);
    redes.set(lado.chaveRede, r);
  }
  return r;
}

escopo.onmessage = (ev: MessageEvent<PedidoLoteAB>) => {
  const m = ev.data;
  if (m.tipo !== 'ab') return;
  try {
    const ctxA = preparaContexto(rede(m.a), m.parametros, m.a.cenario);
    const ctxB = preparaContexto(rede(m.b), m.parametros, m.b.cenario);
    const rodadas = rodaRodadasAB(m.indices, ctxA, m.a.politicas, ctxB, m.b.politicas, m.sementeBase, (feitas) => escopo.postMessage({ tipo: 'progresso', id: m.id, feitas } satisfies RespostaAB));
    escopo.postMessage({ tipo: 'resultado', id: m.id, rodadas } satisfies RespostaAB);
  } catch (erro) {
    escopo.postMessage({ tipo: 'erro', id: m.id, mensagem: erro instanceof Error ? erro.message : String(erro) } satisfies RespostaAB);
  }
};
