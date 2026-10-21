// Web Worker: roda um lote de rodadas e devolve as métricas de cada uma.

import { preparaContexto } from '../motor/contexto';
import type { Rede } from '../motor/rede';
import { montaRede } from '../motor/rede';
import type { DoTrabalhador, ParaTrabalhador } from './protocolo';
import { rodaRodadas } from './rodadas';

const escopo = self as unknown as DedicatedWorkerGlobalScope;
let redeGuardada: { chave: string; rede: Rede } | null = null;

function envia(m: DoTrabalhador): void {
  escopo.postMessage(m);
}

escopo.onmessage = (ev: MessageEvent<ParaTrabalhador>) => {
  const m = ev.data;
  if (m.tipo !== 'roda') return;
  try {
    if (!redeGuardada || redeGuardada.chave !== m.chaveRede) redeGuardada = { chave: m.chaveRede, rede: montaRede(m.redeJson) };
    const ctx = preparaContexto(redeGuardada.rede, m.parametros, m.cenario);
    const rodadas = rodaRodadas(m.indices, ctx, m.politicas, m.sementeBase, m.politicasB, (feitas) => envia({ tipo: 'progresso', id: m.id, feitas }));
    envia({ tipo: 'resultado', id: m.id, rodadas });
  } catch (erro) {
    envia({ tipo: 'erro', id: m.id, mensagem: erro instanceof Error ? erro.message : String(erro) });
  }
};
