// Pool de Web Workers da viagem de A a B (spec 015): mesma divisão em lotes do PoolMC, então o resultado
// não depende do número de workers, e a rodada i é o mesmo dia da aba "Muitos dias".

import { workersPadrao } from '../mc/pool';
import type { Agregado, Rodada } from '../mc/rodadas';
import { agrega, divideEmLotes } from '../mc/rodadas';
import type { PedidoLoteViagem, PedidoViagem, RespostaViagem } from './trabalhador_viagem';

export interface ResultadoViagem extends Agregado {
  segundos: number;
  workers: number;
}

export class PoolViagem {
  private workers: Worker[] = [];
  private rejeita: ((e: Error) => void) | null = null;

  constructor(readonly tamanho: number = workersPadrao()) {}

  /** `nomes`: as métricas de cada dia, na ordem de nomesViagem (calculadas na página com o mesmo cenário). */
  executa(pedido: PedidoViagem, nomes: readonly string[], aoProgresso?: (feitas: number, total: number) => void): Promise<ResultadoViagem> {
    this.cancela();
    const lotes = divideEmLotes(pedido.rodadas, this.tamanho);
    const t0 = performance.now();
    const feitas = new Array<number>(lotes.length).fill(0);
    const { rodadas: total, ...base } = pedido;
    return new Promise<ResultadoViagem>((resolve, reject) => {
      this.rejeita = reject;
      const resultados: Rodada[][] = new Array(lotes.length);
      let pendentes = lotes.length;
      lotes.forEach((indices, id) => {
        const w = new Worker(new URL('./trabalhador_viagem.ts', import.meta.url), { type: 'module' });
        this.workers.push(w);
        w.onmessage = (ev: MessageEvent<RespostaViagem>) => {
          const m = ev.data;
          if (m.tipo === 'progresso') {
            feitas[id] = m.feitas;
            aoProgresso?.(feitas.reduce((x, y) => x + y, 0), total);
          } else if (m.tipo === 'resultado') {
            resultados[id] = m.rodadas;
            feitas[id] = m.rodadas.length;
            aoProgresso?.(feitas.reduce((x, y) => x + y, 0), total);
            w.terminate();
            if (--pendentes === 0) {
              this.workers = [];
              this.rejeita = null;
              resolve({ ...agrega(resultados.flat(), nomes, pedido.sementeBase), segundos: (performance.now() - t0) / 1000, workers: lotes.length });
            }
          } else {
            this.cancela();
            reject(new Error(m.mensagem));
          }
        };
        w.onerror = (e) => {
          this.cancela();
          reject(new Error(e.message));
        };
        const msg: PedidoLoteViagem = { tipo: 'viagem', id, indices, ...base };
        w.postMessage(msg);
      });
    });
  }

  cancela(): void {
    for (const w of this.workers) w.terminate();
    this.workers = [];
    const r = this.rejeita;
    this.rejeita = null;
    r?.(new Error('cancelado'));
  }
}
