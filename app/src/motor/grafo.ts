// Grafo de estações para as métricas origem-destino (spec 009) e para a expansão da rede (spec 014).
//
// Nó = plataforma (estação numa linha). Arestas dirigidas: trecho de linha (peso = tempo de percurso
// mediano do horário) e transferência entre plataformas da mesma estação (peso = hipótese
// tempo_transferencia_min). Pares origem-destino: estações distintas da rede atual, com peso = oferta
// (viagens programadas que servem o par; com baldeação, o menor valor entre as pernas).

import type { HorarioDia, Rede } from './rede';
import type { Sentido } from './tipos';

export interface EstacaoGrafo {
  id: string;
  nome: string;
  lat: number;
  lon: number;
}

/** Linha do grafo. Tempos por trecho físico g (entre as estações g e g + 1). */
export interface LinhaGrafo {
  id: string;
  estacoes: EstacaoGrafo[];
  tempo0: number[]; // sentido 0 (g -> g + 1), segundos
  tempo1: number[]; // sentido 1 (g + 1 -> g), segundos
  km: number[];
  pontasRetorno: number[]; // estações (índice) onde um trem pode voltar
  candidata?: boolean;
}

export interface ArestaGrafo {
  de: number;
  para: number;
  peso: number;
  linha: string; // vazio na transferência
  trecho: number;
  sentido: Sentido;
}

/** O que causou um bloqueio do grafo: permite refazer o efeito num grafo com linhas novas (spec 016). */
export interface OrigemBloqueio {
  causa: 'MR' | 'EF' | 'CC';
  linha: string;
  /** Trecho físico (null na causa comum, que para a linha inteira). */
  trecho: number | null;
  sentidos: Sentido[];
  /** Falha sorteada numa linha nova (spec 016). */
  nova?: boolean;
}

/** Arestas sem serviço durante [ini, fim) (segundos do dia de operação). */
export interface BloqueioOD {
  ini: number;
  fim: number;
  arestas: number[];
  origem?: OrigemBloqueio;
}

/** Intervalo [a, b) do dia em que o conjunto de arestas bloqueadas não muda (ids em ordem crescente). */
export interface SegmentoBloqueado {
  a: number;
  b: number;
  arestas: number[];
}

/**
 * Varredura no tempo: divide a janela nos instantes em que um bloqueio começa ou termina e devolve os
 * pedaços com alguma aresta bloqueada. Usada pela disponibilidade da rede (spec 009) e da viagem (spec 015).
 */
export function segmentosBloqueados(bloqueios: readonly BloqueioOD[], janela: readonly [number, number]): SegmentoBloqueado[] {
  const [ini, fim] = janela;
  if (bloqueios.length === 0) return [];
  const marcos = new Set<number>([ini, fim]);
  for (const b of bloqueios) {
    if (b.ini > ini && b.ini < fim) marcos.add(b.ini);
    if (b.fim > ini && b.fim < fim) marcos.add(b.fim);
  }
  const ts = [...marcos].sort((a, b) => a - b);
  const saida: SegmentoBloqueado[] = [];
  for (let i = 0; i + 1 < ts.length; i++) {
    const a = ts[i];
    const b = ts[i + 1];
    const meio = (a + b) / 2;
    const ativas = new Set<number>();
    for (const bl of bloqueios) if (bl.ini <= meio && meio < bl.fim) for (const e of bl.arestas) ativas.add(e);
    if (ativas.size) saida.push({ a, b, arestas: [...ativas].sort((x, y) => x - y) });
  }
  return saida;
}

export interface AvaliacaoOD {
  /** Fração da oferta (pares ponderados) sem caminho. */
  indisponivel: number;
  /** Minutos extras de viagem, média ponderada sobre todos os pares (pares sem caminho contam 0). */
  extraMin: number;
}

export interface Grafo {
  linhas: LinhaGrafo[];
  estacoes: EstacaoGrafo[];
  nEstacoesBase: number; // pares só entre as estações da rede atual
  nos: { estacao: number; linha: string; indice: number }[];
  arestas: ArestaGrafo[];
  saida: number[][];
  nosDaEstacao: number[][];
  arestasDaLinha: Map<string, number[]>;
  chaveAresta: Map<string, number>; // linha|trecho|sentido -> aresta
  pesos: Float64Array; // por par o * N + d
  pesoTotal: number;
  dist0: Float64Array; // por par, sem bloqueios
  caminho0: Int32Array[]; // arestas do caminho mínimo sem bloqueios, por par
  paresDaAresta: Int32Array[];
  cache: Map<string, AvaliacaoOD>;
}

const LIMITE_CACHE = 20000;

export function chave(linha: string, trecho: number, sentido: Sentido): string {
  return `${linha}|${trecho}|${sentido}`;
}

/** Linhas do grafo a partir do horário de um tipo de dia. */
export function linhasDoHorario(rede: Rede, horario: HorarioDia, pontosExtras?: Record<string, number[]>): LinhaGrafo[] {
  return rede.ids.map((id) => {
    const l = rede.linhas[id];
    const [s0, s1] = horario.porLinha[id];
    const n = l.n;
    const tempo0: number[] = [];
    const tempo1: number[] = [];
    for (let g = 0; g < n - 1; g++) {
      tempo0.push(s0.percursoMediano[g]);
      tempo1.push(s1.percursoMediano[n - 2 - g]);
    }
    const pontas = new Set([...(horario.pontasDeViagem[id] ?? [0, n - 1]), ...(pontosExtras?.[id] ?? [])]);
    return {
      id,
      estacoes: l.estacoes.map((e) => ({ id: e.id, nome: e.nome, lat: e.lat, lon: e.lon })),
      tempo0,
      tempo1,
      km: [...l.kmTrecho],
      pontasRetorno: [...pontas].sort((a, b) => a - b),
    };
  });
}

/**
 * Monta o grafo. `pesosDe`: grafo da rede atual de onde copiar os pesos dos pares (a expansão mede o
 * ganho sobre a oferta de hoje). Sem ele, os pesos vêm do horário de `horario`.
 */
export function montaGrafo(
  linhas: LinhaGrafo[],
  transferenciaS: number,
  opcoes: { rede?: Rede; horario?: HorarioDia; pesosDe?: Grafo; nEstacoesBase?: number } = {},
): Grafo {
  const indiceEstacao = new Map<string, number>();
  const estacoes: EstacaoGrafo[] = [];
  const nos: Grafo['nos'] = [];
  const nosDaEstacao: number[][] = [];
  const noDe = new Map<string, number>();
  // Com pesosDe, as estações da rede atual mantêm os mesmos índices (os pares são comparáveis).
  for (const e of opcoes.pesosDe?.estacoes.slice(0, opcoes.pesosDe.nEstacoesBase) ?? []) {
    indiceEstacao.set(e.id, estacoes.length);
    estacoes.push(e);
    nosDaEstacao.push([]);
  }
  for (const l of linhas) {
    l.estacoes.forEach((e, indice) => {
      let ie = indiceEstacao.get(e.id);
      if (ie === undefined) {
        ie = estacoes.length;
        indiceEstacao.set(e.id, ie);
        estacoes.push(e);
        nosDaEstacao.push([]);
      }
      const no = nos.length;
      nos.push({ estacao: ie, linha: l.id, indice });
      nosDaEstacao[ie].push(no);
      noDe.set(`${l.id}|${indice}`, no);
    });
  }
  const arestas: ArestaGrafo[] = [];
  const arestasDaLinha = new Map<string, number[]>();
  const chaveAresta = new Map<string, number>();
  for (const l of linhas) {
    const lista: number[] = [];
    for (let g = 0; g < l.estacoes.length - 1; g++) {
      const a = noDe.get(`${l.id}|${g}`) as number;
      const b = noDe.get(`${l.id}|${g + 1}`) as number;
      for (const [de, para, peso, sentido] of [
        [a, b, l.tempo0[g], 0],
        [b, a, l.tempo1[g], 1],
      ] as [number, number, number, Sentido][]) {
        chaveAresta.set(chave(l.id, g, sentido), arestas.length);
        lista.push(arestas.length);
        arestas.push({ de, para, peso, linha: l.id, trecho: g, sentido });
      }
    }
    arestasDaLinha.set(l.id, lista);
  }
  for (const grupo of nosDaEstacao) {
    for (const a of grupo) for (const b of grupo) if (a !== b) arestas.push({ de: a, para: b, peso: transferenciaS, linha: '', trecho: -1, sentido: 0 });
  }
  const saida: number[][] = nos.map(() => []);
  arestas.forEach((e, i) => saida[e.de].push(i));

  const N = opcoes.nEstacoesBase ?? opcoes.pesosDe?.nEstacoesBase ?? estacoes.length;
  const grafo: Grafo = {
    linhas,
    estacoes,
    nEstacoesBase: N,
    nos,
    arestas,
    saida,
    nosDaEstacao,
    arestasDaLinha,
    chaveAresta,
    pesos: new Float64Array(N * N),
    pesoTotal: 0,
    dist0: new Float64Array(N * N),
    caminho0: [],
    paresDaAresta: [],
    cache: new Map(),
  };
  const semBloqueio = new Uint8Array(arestas.length);
  const caminho0: Int32Array[] = new Array(N * N);
  const usos: number[][] = arestas.map(() => []);
  for (let o = 0; o < N; o++) {
    const { dist, anterior } = dijkstra(grafo, o, semBloqueio);
    for (let d = 0; d < N; d++) {
      if (d === o) continue;
      const p = o * N + d;
      const [no, valor] = melhorNo(grafo, d, dist);
      grafo.dist0[p] = valor;
      const cam: number[] = [];
      let atual = no;
      while (atual >= 0 && anterior[atual] >= 0) {
        cam.push(anterior[atual]);
        atual = arestas[anterior[atual]].de;
      }
      cam.reverse();
      caminho0[p] = Int32Array.from(cam);
      for (const e of cam) usos[e].push(p);
    }
  }
  grafo.caminho0 = caminho0;
  grafo.paresDaAresta = usos.map((u) => Int32Array.from(u));
  if (opcoes.pesosDe) {
    grafo.pesos.set(opcoes.pesosDe.pesos);
  } else if (opcoes.rede && opcoes.horario) {
    calculaPesos(grafo, opcoes.rede, opcoes.horario);
  } else {
    grafo.pesos.fill(1);
    for (let o = 0; o < N; o++) grafo.pesos[o * N + o] = 0;
  }
  let total = 0;
  for (let p = 0; p < N * N; p++) total += grafo.pesos[p];
  grafo.pesoTotal = total;
  return grafo;
}

/** Peso do par = viagens programadas que o servem; com baldeação, a menor oferta entre as pernas. */
function calculaPesos(g: Grafo, rede: Rede, horario: HorarioDia): void {
  const N = g.nEstacoesBase;
  for (let p = 0; p < N * N; p++) {
    const cam = g.caminho0[p];
    if (!cam || cam.length === 0) continue;
    let peso = Infinity;
    let k = 0;
    while (k < cam.length) {
      const e = g.arestas[cam[k]];
      if (!e.linha) {
        k++;
        continue;
      }
      // perna: arestas consecutivas da mesma linha e sentido
      let fimK = k;
      while (fimK + 1 < cam.length && g.arestas[cam[fimK + 1]].linha === e.linha && g.arestas[cam[fimK + 1]].sentido === e.sentido) fimK++;
      const ultima = g.arestas[cam[fimK]];
      const ls = horario.porLinha[e.linha]?.[e.sentido];
      if (ls && rede.linhas[e.linha]) {
        const n = ls.n;
        const a = e.sentido === 0 ? g.nos[e.de].indice : n - 1 - g.nos[e.de].indice;
        const b = e.sentido === 0 ? g.nos[ultima.para].indice : n - 1 - g.nos[ultima.para].indice;
        peso = Math.min(peso, ls.servidas[a * n + b]);
      }
      k = fimK + 1;
    }
    g.pesos[p] = Number.isFinite(peso) ? peso : 0;
  }
}

export function melhorNo(g: Grafo, estacao: number, dist: Float64Array): [number, number] {
  let melhor = -1;
  let valor = Infinity;
  for (const no of g.nosDaEstacao[estacao]) {
    if (dist[no] < valor) {
      valor = dist[no];
      melhor = no;
    }
  }
  return [melhor, valor];
}

/** Caminhos mínimos a partir de todas as plataformas da estação de origem (Dijkstra O(V²); V é pequeno). */
export function dijkstra(g: Grafo, origem: number, bloqueada: Uint8Array): { dist: Float64Array; anterior: Int32Array } {
  const V = g.nos.length;
  const dist = new Float64Array(V).fill(Infinity);
  const anterior = new Int32Array(V).fill(-1);
  const feito = new Uint8Array(V);
  for (const no of g.nosDaEstacao[origem]) dist[no] = 0;
  for (;;) {
    let u = -1;
    let du = Infinity;
    for (let v = 0; v < V; v++) {
      if (!feito[v] && dist[v] < du) {
        du = dist[v];
        u = v;
      }
    }
    if (u < 0) break;
    feito[u] = 1;
    for (const e of g.saida[u]) {
      if (bloqueada[e]) continue;
      const a = g.arestas[e];
      const nd = du + a.peso;
      if (nd < dist[a.para]) {
        dist[a.para] = nd;
        anterior[a.para] = e;
      }
    }
  }
  return { dist, anterior };
}

/**
 * Disponibilidade origem-destino com um conjunto de arestas bloqueadas (ids em ordem crescente).
 * Sem rota alternativa, o par só vale pelo caminho de sempre; com ela, por qualquer caminho livre.
 */
export function avaliaOD(g: Grafo, bloqueadas: number[], rotaAlternativa: boolean): AvaliacaoOD {
  if (bloqueadas.length === 0) return { indisponivel: 0, extraMin: 0 };
  const k = (rotaAlternativa ? 'A' : 'D') + bloqueadas.join(',');
  const guardado = g.cache.get(k);
  if (guardado) return guardado;
  const N = g.nEstacoesBase;
  const atingido = new Uint8Array(N * N);
  const origens = new Set<number>();
  for (const e of bloqueadas) {
    for (const p of g.paresDaAresta[e] ?? []) {
      atingido[p] = 1;
      origens.add(Math.floor(p / N));
    }
  }
  let pesoFora = 0;
  let extra = 0;
  if (!rotaAlternativa) {
    for (let p = 0; p < N * N; p++) if (atingido[p]) pesoFora += g.pesos[p];
  } else {
    const mascara = new Uint8Array(g.arestas.length);
    for (const e of bloqueadas) mascara[e] = 1;
    for (const o of [...origens].sort((a, b) => a - b)) {
      const { dist } = dijkstra(g, o, mascara);
      for (let d = 0; d < N; d++) {
        const p = o * N + d;
        if (!atingido[p]) continue;
        const [, valor] = melhorNo(g, d, dist);
        if (!Number.isFinite(valor)) pesoFora += g.pesos[p];
        else extra += (g.pesos[p] * Math.max(0, valor - g.dist0[p])) / 60;
      }
    }
  }
  const r = { indisponivel: g.pesoTotal > 0 ? pesoFora / g.pesoTotal : 0, extraMin: g.pesoTotal > 0 ? extra / g.pesoTotal : 0 };
  if (g.cache.size >= LIMITE_CACHE) g.cache.clear();
  g.cache.set(k, r);
  return r;
}

/**
 * Arestas que ficam sem serviço com um trecho bloqueado. Sem retorno parcial a linha inteira para,
 * nos dois sentidos. Com ele, para só o pedaço entre os pontos de retorno que cercam o trecho, nos
 * sentidos bloqueados.
 */
export function efeitoBloqueio(g: Grafo, linha: string, trecho: number, sentidos: readonly Sentido[], retornoParcial: boolean): number[] {
  const todas = g.arestasDaLinha.get(linha) ?? [];
  if (!retornoParcial) return todas;
  const l = g.linhas.find((x) => x.id === linha);
  if (!l) return [];
  let ra = 0;
  let rb = l.estacoes.length - 1;
  for (const r of l.pontasRetorno) {
    if (r <= trecho && r > ra) ra = r;
    if (r >= trecho + 1 && r < rb) rb = r;
  }
  const saida: number[] = [];
  for (let t = ra; t < rb; t++) {
    for (const s of sentidos) {
      const e = g.chaveAresta.get(chave(linha, t, s));
      if (e !== undefined) saida.push(e);
    }
  }
  return saida;
}
