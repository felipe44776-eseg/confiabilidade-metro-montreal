// Pool de Web Workers da comparação A/B (mesma divisão em lotes do PoolMC; o resultado não depende do número de workers).

import type { Agregado } from '../mc/rodadas';
import { agrega, divideEmLotes, nomesMetricas } from '../mc/rodadas';
import { workersPadrao } from '../mc/pool';
import type { Rodada } from '../mc/rodadas';
import type { Parametros } from '../motor/tipos';
import type { LadoAB, PedidoLoteAB, RespostaAB } from './trabalhador_ab';

export interface ResultadoAB extends Agregado {
  segundos: number;
  workers: number;
}

export class PoolAB {
  private workers: Worker[] = [];
  private rejeita: ((e: Error) => void) | null = null;

  constructor(readonly tamanho: number = workersPadrao()) {}

  executa(parametros: Parametros, a: LadoAB, b: LadoAB, sementeBase: number, rodadas: number, aoProgresso?: (feitas: number, total: number) => void): Promise<ResultadoAB> {
    this.cancela();
    const lotes = divideEmLotes(rodadas, this.tamanho);
    const nomes = nomesMetricas(Object.keys(a.redeJson.linhas));
    const t0 = performance.now();
    const feitas = new Array<number>(lotes.length).fill(0);
    return new Promise<ResultadoAB>((resolve, reject) => {
      this.rejeita = reject;
      const resultados: Rodada[][] = new Array(lotes.length);
      let pendentes = lotes.length;
      lotes.forEach((indices, id) => {
        const w = new Worker(new URL('./trabalhador_ab.ts', import.meta.url), { type: 'module' });
        this.workers.push(w);
        w.onmessage = (ev: MessageEvent<RespostaAB>) => {
          const m = ev.data;
          if (m.tipo === 'progresso') {
            feitas[id] = m.feitas;
            aoProgresso?.(feitas.reduce((x, y) => x + y, 0), rodadas);
          } else if (m.tipo === 'resultado') {
            resultados[id] = m.rodadas;
            feitas[id] = m.rodadas.length;
            aoProgresso?.(feitas.reduce((x, y) => x + y, 0), rodadas);
            w.terminate();
            if (--pendentes === 0) {
              this.workers = [];
              this.rejeita = null;
              resolve({ ...agrega(resultados.flat(), nomes, sementeBase), segundos: (performance.now() - t0) / 1000, workers: lotes.length });
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
        const msg: PedidoLoteAB = { tipo: 'ab', id, indices, parametros, a, b, sementeBase };
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
