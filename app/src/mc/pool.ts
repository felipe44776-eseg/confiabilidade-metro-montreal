// Pool de Web Workers do Monte Carlo: divide as rodadas em lotes, mostra o progresso e permite cancelar.
// O resultado é o mesmo com 1 ou 16 workers (a semente de cada rodada só depende do índice).

import type { DoTrabalhador, ParaTrabalhador, PedidoMC } from './protocolo';
import type { Agregado, Rodada } from './rodadas';
import { agrega, divideEmLotes, nomesMetricas } from './rodadas';

/** Teto de workers: acima disso o ganho some e a memória pesa. */
const MAX_WORKERS = 16;
const WORKERS_SEM_INFORMACAO = 4;

export interface ResultadoMC extends Agregado {
  segundos: number;
  workers: number;
}

export function workersPadrao(): number {
  const n = typeof navigator !== 'undefined' && navigator.hardwareConcurrency ? navigator.hardwareConcurrency : WORKERS_SEM_INFORMACAO;
  return Math.max(1, Math.min(MAX_WORKERS, n));
}

export class PoolMC {
  private workers: Worker[] = [];
  private rejeita: ((e: Error) => void) | null = null;

  constructor(readonly tamanho: number = workersPadrao()) {}

  executa(pedido: PedidoMC, aoProgresso?: (feitas: number, total: number) => void): Promise<ResultadoMC> {
    this.cancela();
    const lotes = divideEmLotes(pedido.rodadas, this.tamanho);
    const nomes = nomesMetricas(Object.keys(pedido.redeJson.linhas));
    const t0 = performance.now();
    const feitas = new Array<number>(lotes.length).fill(0);
    const { rodadas: _total, ...base } = pedido;
    return new Promise<ResultadoMC>((resolve, reject) => {
      this.rejeita = reject;
      const resultados: Rodada[][] = new Array(lotes.length);
      let pendentes = lotes.length;
      if (pendentes === 0) {
        resolve({ ...agrega([], nomes, pedido.sementeBase), segundos: 0, workers: 0 });
        return;
      }
      lotes.forEach((indices, id) => {
        const w = new Worker(new URL('./trabalhador.ts', import.meta.url), { type: 'module' });
        this.workers.push(w);
        w.onmessage = (ev: MessageEvent<DoTrabalhador>) => {
          const m = ev.data;
          if (m.tipo === 'progresso') {
            feitas[id] = m.feitas;
            aoProgresso?.(feitas.reduce((a, b) => a + b, 0), pedido.rodadas);
          } else if (m.tipo === 'resultado') {
            resultados[id] = m.rodadas;
            feitas[id] = m.rodadas.length;
            aoProgresso?.(feitas.reduce((a, b) => a + b, 0), pedido.rodadas);
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
        const msg: ParaTrabalhador = { tipo: 'roda', id, indices, ...base };
        w.postMessage(msg);
      });
    });
  }

  /** Interrompe os workers; a promessa em curso é rejeitada com "cancelado". */
  cancela(): void {
    for (const w of this.workers) w.terminate();
    this.workers = [];
    const r = this.rejeita;
    this.rejeita = null;
    r?.(new Error('cancelado'));
  }
}
