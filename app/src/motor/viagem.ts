// Confiabilidade de uma viagem de uma estação a outra (spec 015).
//
// Duas medidas, sobre o mesmo dia simulado:
// 1. Disponibilidade do caminho: fração da janela de serviço em que o caminho de sempre (ou, com a
//    política de rota alternativa, algum caminho) está livre, a partir dos bloqueios do grafo
//    (o mesmo método da disponibilidade origem-destino da rede, spec 009), no total e por trecho.
// 2. Atraso de quem viaja: para saídas a cada 10 minutos, a chegada mais cedo ao destino com os trens
//    simulados do dia (atrasos, bloqueios, cortes e cancelamentos), contra a mesma saída num dia sem
//    falhas. A busca é a de conexões em ordem de partida (connection scan): cada conexão é um trem
//    andando de uma estação à seguinte.

import type { Contexto } from './contexto';
import type { ResultadoDia, Trajetoria } from './dia';
import { calculaTrajetorias, novoEstado, simulaDia } from './dia';
import type { Grafo, SegmentoBloqueado } from './grafo';
import { chave, dijkstra, melhorNo, segmentosBloqueados } from './grafo';
import { hipotese } from './hipoteses';
import type { Politicas } from './politicas';
import { sementeDaRodada } from './prng';
import type { Rede } from './rede';
import { estacaoGlobal, trechoFisico } from './rede';
import type { Sentido } from './tipos';

/** Intervalo entre as saídas simuladas, em segundos. */
export const PASSO_SAIDAS_S = 600;
/** Limiares de atraso mostrados (escolha de apresentação, spec 015). */
export const LIMIARES_ATRASO_MIN = [5, 15, 60] as const;

export interface TrechoViagem {
  linha: string;
  sentido: Sentido;
  /** Estações (índice global na linha) de embarque e de desembarque. */
  de: number;
  ate: number;
  deNome: string;
  ateNome: string;
  paradas: number;
  arestas: number[];
  minutos: number;
}

export interface RotaViagem {
  origem: number; // índice da estação no grafo
  destino: number;
  trechos: TrechoViagem[];
  /** Tempo do caminho no grafo (percurso mediano mais baldeações), em minutos. */
  minutos: number;
  arestas: number[];
}

export function indiceEstacao(g: Grafo, id: string): number {
  return g.estacoes.findIndex((e, i) => i < g.nEstacoesBase && e.id === id);
}

/** Caminho de sempre entre duas estações: o mais rápido sem falhas (grafo da spec 009). Null se não houver. */
export function rotaDoPar(g: Grafo, origem: number, destino: number): RotaViagem | null {
  const N = g.nEstacoesBase;
  if (origem < 0 || destino < 0 || origem >= N || destino >= N || origem === destino) return null;
  const p = origem * N + destino;
  const cam = g.caminho0[p];
  if (!cam || cam.length === 0 || !Number.isFinite(g.dist0[p])) return null;
  const trechos: TrechoViagem[] = [];
  let k = 0;
  while (k < cam.length) {
    const e = g.arestas[cam[k]];
    if (!e.linha) {
      k++;
      continue;
    }
    const arestas = [cam[k]];
    let seg = e.peso;
    while (k + 1 < cam.length && g.arestas[cam[k + 1]].linha === e.linha && g.arestas[cam[k + 1]].sentido === e.sentido) {
      k++;
      arestas.push(cam[k]);
      seg += g.arestas[cam[k]].peso;
    }
    const ultima = g.arestas[cam[k]];
    const de = g.nos[e.de];
    const ate = g.nos[ultima.para];
    trechos.push({
      linha: e.linha,
      sentido: e.sentido,
      de: de.indice,
      ate: ate.indice,
      deNome: g.estacoes[de.estacao].nome,
      ateNome: g.estacoes[ate.estacao].nome,
      paradas: arestas.length,
      arestas,
      minutos: seg / 60,
    });
    k++;
  }
  return { origem, destino, trechos, minutos: g.dist0[p] / 60, arestas: Array.from(cam) };
}

function contemAlguma(ordenadas: readonly number[], conjunto: ReadonlySet<number>): boolean {
  for (const e of ordenadas) if (conjunto.has(e)) return true;
  return false;
}

/**
 * Segundos sem caminho na janela, no total e por trecho. Sem rota alternativa, falta caminho quando
 * alguma aresta do caminho de sempre está bloqueada; com ela, quando nenhum caminho liga as estações.
 * Cada trecho conta só as próprias arestas (a disponibilidade do componente, para a conta em série).
 */
export function semCaminho(g: Grafo, rota: RotaViagem, segmentos: readonly SegmentoBloqueado[], rotaAlternativa: boolean): { total: number; porTrecho: number[] } {
  const porTrecho = rota.trechos.map(() => 0);
  let total = 0;
  const mascara = new Uint8Array(g.arestas.length);
  for (const s of segmentos) {
    const ativas = new Set(s.arestas);
    const dur = s.b - s.a;
    rota.trechos.forEach((t, i) => {
      if (contemAlguma(t.arestas, ativas)) porTrecho[i] += dur;
    });
    if (!contemAlguma(rota.arestas, ativas)) continue;
    if (!rotaAlternativa) {
      total += dur;
      continue;
    }
    for (const e of s.arestas) mascara[e] = 1;
    const { dist } = dijkstra(g, rota.origem, mascara);
    if (!Number.isFinite(melhorNo(g, rota.destino, dist)[1])) total += dur;
    for (const e of s.arestas) mascara[e] = 0;
  }
  return { total, porTrecho };
}

// ---------- conexões do dia (connection scan) ----------

export interface Conexoes {
  dep: Float64Array;
  arr: Float64Array;
  de: Int32Array; // nó do grafo (plataforma)
  para: Int32Array;
  viagem: Int32Array;
  aresta: Int32Array; // aresta do grafo percorrida
  nViagens: number;
}

/** Por linha: nó do grafo de cada estação e aresta de cada trecho físico em cada sentido. */
interface IndiceLinha {
  no: Int32Array;
  aresta: [Int32Array, Int32Array];
}
const indices = new WeakMap<Grafo, Map<string, IndiceLinha>>();
function indiceDasLinhas(g: Grafo): Map<string, IndiceLinha> {
  let m = indices.get(g);
  if (m) return m;
  m = new Map();
  for (const l of g.linhas) {
    const n = l.estacoes.length;
    const no = new Int32Array(n).fill(-1);
    g.nos.forEach((x, i) => {
      if (x.linha === l.id) no[x.indice] = i;
    });
    const aresta: [Int32Array, Int32Array] = [new Int32Array(Math.max(n - 1, 0)).fill(-1), new Int32Array(Math.max(n - 1, 0)).fill(-1)];
    for (let t = 0; t < n - 1; t++) for (const s of [0, 1] as Sentido[]) aresta[s][t] = g.chaveAresta.get(chave(l.id, t, s)) ?? -1;
    m.set(l.id, { no, aresta });
  }
  indices.set(g, m);
  return m;
}

/** Bits reservados ao índice da conexão na chave de ordenação (até 2^20 conexões por dia). */
const BITS_INDICE = 2 ** 20;

/**
 * Conexões de um conjunto de trajetórias (chave linha:sentido), em ordem de partida. Com `permitida`
 * (por aresta), só as conexões que a pessoa pode usar: sem rota alternativa, as do caminho de sempre.
 */
export function conexoesDe(g: Grafo, rede: Rede, trajetorias: Record<string, Trajetoria[]>, permitida: Uint8Array | null = null): Conexoes {
  const porLinha = indiceDasLinhas(g);
  // linhas-sentido com alguma aresta permitida (as outras nem entram)
  const usa = (linha: string, sentido: Sentido): boolean => {
    if (!permitida) return true;
    const ix = porLinha.get(linha);
    return !!ix && ix.aresta[sentido].some((a) => a >= 0 && permitida[a] === 1);
  };
  let total = 0;
  for (const [k, lista] of Object.entries(trajetorias)) {
    const linha = k.slice(0, k.lastIndexOf(':'));
    if (lista.length && !usa(linha, lista[0].viagem.sentido)) continue;
    for (const tr of lista) if (!tr.cancelada) total += Math.max(0, tr.ultima - tr.viagem.inicio);
  }
  const dep0 = new Float64Array(total);
  const arr0 = new Float64Array(total);
  const de0 = new Int32Array(total);
  const para0 = new Int32Array(total);
  const viagem0 = new Int32Array(total);
  const aresta0 = new Int32Array(total);
  let m = 0;
  let nViagens = 0;
  for (const [k, lista] of Object.entries(trajetorias)) {
    const linha = k.slice(0, k.lastIndexOf(':'));
    const n = rede.linhas[linha]?.n;
    const ix = porLinha.get(linha);
    if (!n || !ix || (lista.length && !usa(linha, lista[0].viagem.sentido))) continue;
    for (const tr of lista) {
      if (tr.cancelada) continue;
      const v = tr.viagem;
      const sentido = v.sentido;
      const id = nViagens++;
      for (let s = v.inicio; s < tr.ultima; s++) {
        const p = s - v.inicio;
        const d = tr.partida[p];
        const c = tr.chegada[p + 1];
        const a = ix.aresta[sentido][trechoFisico(n, sentido, s)];
        const n1 = ix.no[estacaoGlobal(n, sentido, s)];
        const n2 = ix.no[estacaoGlobal(n, sentido, s + 1)];
        if (!Number.isFinite(d) || !Number.isFinite(c) || a < 0 || n1 < 0 || n2 < 0 || (permitida && !permitida[a])) continue;
        dep0[m] = d;
        arr0[m] = c;
        de0[m] = n1;
        para0[m] = n2;
        viagem0[m] = id;
        aresta0[m] = a;
        m++;
      }
    }
  }
  if (m >= BITS_INDICE) throw new Error(`conexões demais num dia: ${m}`);
  // ordena por partida (ao milissegundo) com a ordenação numérica nativa: chave = partida em ms × 2^20 + índice
  const chaves = new Float64Array(m);
  for (let i = 0; i < m; i++) chaves[i] = Math.round(dep0[i] * 1000) * BITS_INDICE + i;
  chaves.sort();
  const dep = new Float64Array(m);
  const arr = new Float64Array(m);
  const de = new Int32Array(m);
  const para = new Int32Array(m);
  const viagem = new Int32Array(m);
  const aresta = new Int32Array(m);
  for (let k = 0; k < m; k++) {
    const i = chaves[k] % BITS_INDICE;
    dep[k] = dep0[i];
    arr[k] = arr0[i];
    de[k] = de0[i];
    para[k] = para0[i];
    viagem[k] = viagem0[i];
    aresta[k] = aresta0[i];
  }
  return { dep, arr, de, para, viagem, aresta, nViagens };
}

function primeiraDesde(dep: Float64Array, t: number): number {
  let lo = 0;
  let hi = dep.length;
  while (lo < hi) {
    const m = (lo + hi) >> 1;
    if (dep[m] < t) lo = m + 1;
    else hi = m;
  }
  return lo;
}

/**
 * Chegada mais cedo ao destino saindo da origem no instante t. Seguir no mesmo trem não custa nada;
 * trocar de plataforma custa `transferenciaS`. `permitida` (por aresta) restringe ao caminho de sempre.
 * Infinity se não chega até o fim do serviço.
 */
export function chegadaMaisCedo(
  g: Grafo,
  cx: Conexoes,
  origem: number,
  destino: number,
  t: number,
  transferenciaS: number,
  permitida: Uint8Array | null,
): number {
  const cedo = new Float64Array(g.nos.length).fill(Infinity);
  for (const no of g.nosDaEstacao[origem]) cedo[no] = t;
  const embarcou = new Uint8Array(cx.nViagens);
  let melhor = Infinity;
  for (let i = primeiraDesde(cx.dep, t); i < cx.dep.length; i++) {
    const d = cx.dep[i];
    if (d >= melhor) break;
    if (permitida && !permitida[cx.aresta[i]]) continue;
    const v = cx.viagem[i];
    if (!embarcou[v] && cedo[cx.de[i]] > d) continue;
    embarcou[v] = 1;
    const c = cx.arr[i];
    const no = cx.para[i];
    if (c >= cedo[no]) continue;
    cedo[no] = c;
    const est = g.nos[no].estacao;
    if (est === destino) {
      if (c < melhor) melhor = c;
      continue;
    }
    for (const outro of g.nosDaEstacao[est]) if (outro !== no && c + transferenciaS < cedo[outro]) cedo[outro] = c + transferenciaS;
  }
  return melhor;
}

// ---------- avaliação por dia ----------

export interface AvaliadorViagem {
  rota: RotaViagem;
  rotaAlternativa: boolean;
  transferenciaS: number;
  permitida: Uint8Array | null;
  janela: [number, number];
  /** Saídas com chegada no dia sem falhas, e essa chegada. */
  saidas: Float64Array;
  chegadaSemFalhas: Float64Array;
  /** Horas (do dia de operação) que têm saídas, em ordem. */
  horas: number[];
}

/** Trajetórias de um dia sem falhas: o horário com as mesmas regras de circulação do motor. */
export function trajetoriasSemFalhas(ctx: Contexto): Record<string, Trajetoria[]> {
  const saida: Record<string, Trajetoria[]> = {};
  for (const linha of ctx.rede.ids) {
    for (const ls of ctx.horario.porLinha[linha]) saida[`${linha}:${ls.sentido}`] = calculaTrajetorias(novoEstado(ls), ctx.intervaloMinimoS);
  }
  return saida;
}

export function preparaViagem(ctx: Contexto, origemId: string, destinoId: string, rotaAlternativa: boolean): AvaliadorViagem | null {
  const g = ctx.grafo;
  const rota = rotaDoPar(g, indiceEstacao(g, origemId), indiceEstacao(g, destinoId));
  if (!rota) return null;
  const transferenciaS = hipotese('tempo_transferencia_min', ctx.parametros, ctx.cenario) * 60;
  let permitida: Uint8Array | null = null;
  if (!rotaAlternativa) {
    permitida = new Uint8Array(g.arestas.length);
    for (const e of rota.arestas) permitida[e] = 1;
  }
  const cx = conexoesDe(g, ctx.rede, trajetoriasSemFalhas(ctx), permitida);
  const janela = ctx.horario.janelaRede;
  const saidas: number[] = [];
  const chegadas: number[] = [];
  for (let t = Math.ceil(janela[0] / PASSO_SAIDAS_S) * PASSO_SAIDAS_S; t < janela[1]; t += PASSO_SAIDAS_S) {
    const c = chegadaMaisCedo(g, cx, rota.origem, rota.destino, t, transferenciaS, permitida);
    if (Number.isFinite(c)) {
      saidas.push(t);
      chegadas.push(c);
    }
  }
  const horas = [...new Set(saidas.map((t) => Math.floor(t / 3600)))];
  return { rota, rotaAlternativa, transferenciaS, permitida, janela: [janela[0], janela[1]], saidas: Float64Array.from(saidas), chegadaSemFalhas: Float64Array.from(chegadas), horas };
}

/** Nomes das métricas de um dia, na ordem de `metricasViagemDia`. */
export function nomesViagem(av: AvaliadorViagem): string[] {
  return [
    'disp',
    ...av.rota.trechos.map((_, i) => `disp.trecho.${i}`),
    'minSemCaminho',
    'diaComInterrupcao',
    ...LIMIARES_ATRASO_MIN.map((m) => `atraso${m}`),
    'naoChega',
    'atrasoMedioMin',
    ...av.horas.map((h) => `atraso${LIMIARES_ATRASO_MIN[0]}.h${h}`),
  ];
}

export function metricasViagemDia(ctx: Contexto, av: AvaliadorViagem, r: ResultadoDia): number[] {
  const g = ctx.grafo;
  const T = Math.max(av.janela[1] - av.janela[0], 1);
  const sem = semCaminho(g, av.rota, segmentosBloqueados(r.bloqueiosOD ?? [], av.janela), av.rotaAlternativa);
  const cx = conexoesDe(g, ctx.rede, r.trajetorias ?? {}, av.permitida);
  const acima = LIMIARES_ATRASO_MIN.map(() => 0);
  const porHora = new Map<number, [number, number]>(av.horas.map((h) => [h, [0, 0]]));
  let naoChega = 0;
  let somaAtraso = 0;
  let chegaram = 0;
  av.saidas.forEach((t, i) => {
    const c = chegadaMaisCedo(g, cx, av.rota.origem, av.rota.destino, t, av.transferenciaS, av.permitida);
    const atraso = Number.isFinite(c) ? Math.max(0, c - av.chegadaSemFalhas[i]) : Infinity;
    if (Number.isFinite(atraso)) {
      somaAtraso += atraso / 60;
      chegaram++;
    } else naoChega++;
    LIMIARES_ATRASO_MIN.forEach((m, k) => {
      if (atraso > m * 60) acima[k]++;
    });
    const h = porHora.get(Math.floor(t / 3600)) as [number, number];
    h[1]++;
    if (atraso > LIMIARES_ATRASO_MIN[0] * 60) h[0]++;
  });
  const n = Math.max(av.saidas.length, 1);
  return [
    1 - sem.total / T,
    ...sem.porTrecho.map((x) => 1 - x / T),
    sem.total / 60,
    sem.total > 0 ? 1 : 0,
    ...acima.map((x) => x / n),
    naoChega / n,
    chegaram ? somaAtraso / chegaram : 0,
    ...av.horas.map((h) => {
      const [a, tot] = porHora.get(h) as [number, number];
      return tot ? a / tot : 0;
    }),
  ];
}

/** Simula o dia com o que a viagem precisa: trajetórias e bloqueios do grafo (sem a disponibilidade da rede toda). */
export function simulaDiaViagem(ctx: Contexto, politicas: Politicas, semente: number): ResultadoDia {
  return simulaDia(ctx, politicas, semente, { registrar: false, trajetorias: true, bloqueiosOD: true, odDaRede: false });
}

/** Rodadas da viagem: a rodada i usa a semente da rodada i do Monte Carlo (o mesmo dia sorteado). */
export function rodaViagem(
  indices: readonly number[],
  ctx: Contexto,
  politicas: Politicas,
  sementeBase: number,
  av: AvaliadorViagem,
  aoProgresso?: (feitas: number) => void,
): { indice: number; semente: number; valores: number[] }[] {
  return indices.map((indice, k) => {
    const semente = sementeDaRodada(sementeBase, indice);
    const valores = metricasViagemDia(ctx, av, simulaDiaViagem(ctx, politicas, semente));
    if (aoProgresso && (k + 1) % 25 === 0) aoProgresso(k + 1);
    return { indice, semente, valores };
  });
}
