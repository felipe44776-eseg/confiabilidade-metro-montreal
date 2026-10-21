// Fila de prioridade (heap binário de mínimo). Empate na hora é desfeito pela ordem de inserção,
// para que a simulação seja determinística.

interface Item<T> {
  t: number;
  seq: number;
  valor: T;
}

export class Heap<T> {
  private itens: Item<T>[] = [];
  private seq = 0;

  get tamanho(): number {
    return this.itens.length;
  }

  insere(t: number, valor: T): void {
    const item = { t, seq: this.seq++, valor };
    const a = this.itens;
    a.push(item);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (!menor(a[i], a[p])) break;
      [a[i], a[p]] = [a[p], a[i]];
      i = p;
    }
  }

  /** Remove e devolve o item de menor hora, ou undefined se a fila está vazia. */
  retira(): { t: number; valor: T } | undefined {
    const a = this.itens;
    if (a.length === 0) return undefined;
    const topo = a[0];
    const ultimo = a.pop() as Item<T>;
    if (a.length > 0) {
      a[0] = ultimo;
      let i = 0;
      for (;;) {
        const e = 2 * i + 1;
        const d = e + 1;
        let m = i;
        if (e < a.length && menor(a[e], a[m])) m = e;
        if (d < a.length && menor(a[d], a[m])) m = d;
        if (m === i) break;
        [a[i], a[m]] = [a[m], a[i]];
        i = m;
      }
    }
    return { t: topo.t, valor: topo.valor };
  }
}

function menor<T>(x: Item<T>, y: Item<T>): boolean {
  return x.t < y.t || (x.t === y.t && x.seq < y.seq);
}
