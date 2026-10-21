// Estrutura da rede a partir de rede.json: linhas, trechos, viagens do horário em ordem de
// circulação e trens em circulação minuto a minuto.
//
// Convenção de índices
// - Índice global de estação: posição em `estacoes` da linha (ordem do sentido 0).
// - Índice local: posição ao longo do próprio sentido. Sentido 0: local = global. Sentido 1: local L
//   é a estação global n - 1 - L.
// - Trecho físico g: entre as estações globais g e g + 1. No sentido 1, o trecho local j é o físico
//   n - 2 - j.

import type { EstacaoJson, RedeJson, Sentido, TipoDia, ViagemJson } from './tipos';
import { TIPOS_DIA } from './tipos';

/** Dia de operação mais longo que o horário cobre (o serviço passa da meia-noite). */
export const MINUTOS_DIA_OPERACAO = 30 * 60;

export interface Viagem {
  id: string; // linha:sentido:índice no horário
  linha: string;
  sentido: Sentido;
  indice: number;
  inicio: number; // primeira parada (índice local)
  fim: number; // última parada (índice local, inclusive)
  chegada: Float64Array; // por parada, posição p = parada local - inicio
  partida: Float64Array;
}

export interface LinhaSentido {
  linha: string;
  sentido: Sentido;
  n: number;
  /** Viagens numa ordem que respeita, em cada trecho, a ordem de entrada do horário (sem ultrapassagem). */
  viagens: Viagem[];
  /** servidas[a * n + b]: viagens que param na parada local a e depois na b. */
  servidas: Int32Array;
  /** Tempo de percurso mediano de cada trecho local, em segundos. */
  percursoMediano: Float64Array;
}

export interface LinhaRede {
  id: string;
  cor?: string;
  estacoes: EstacaoJson[];
  n: number;
  kmTrecho: Float64Array; // por trecho físico
}

export interface HorarioDia {
  tipoDia: TipoDia;
  porLinha: Record<string, [LinhaSentido, LinhaSentido]>;
  /** Trens em circulação segundo o horário, no meio de cada minuto do dia de operação. */
  trensPorMinuto: Record<string, Int16Array>;
  inicioServico: Record<string, number>;
  fimServico: Record<string, number>;
  janelaRede: [number, number];
  /** Estações (índice global) onde alguma viagem começa ou termina: pontos de retorno verificados pelo horário. */
  pontasDeViagem: Record<string, number[]>;
}

export interface EstacaoUnica {
  id: string;
  nome: string;
  lat: number;
  lon: number;
  plataformas: { linha: string; indice: number }[];
}

export interface Rede {
  ids: string[];
  linhas: Record<string, LinhaRede>;
  correspondencias: RedeJson['correspondencias'];
  horarios: Record<TipoDia, HorarioDia>;
  estacoes: EstacaoUnica[];
}

export function trechoFisico(n: number, sentido: Sentido, local: number): number {
  return sentido === 0 ? local : n - 2 - local;
}

export function estacaoGlobal(n: number, sentido: Sentido, local: number): number {
  return sentido === 0 ? local : n - 1 - local;
}

export function montaRede(json: RedeJson): Rede {
  const ids = Object.keys(json.linhas);
  const linhas: Record<string, LinhaRede> = {};
  const porId = new Map<string, EstacaoUnica>();
  for (const id of ids) {
    const estacoes = json.linhas[id].estacoes;
    const n = estacoes.length;
    const kmTrecho = new Float64Array(n - 1);
    for (let g = 0; g < n - 1; g++) kmTrecho[g] = Math.abs(estacoes[g + 1].km - estacoes[g].km);
    linhas[id] = { id, cor: json.linhas[id].cor, estacoes, n, kmTrecho };
    estacoes.forEach((e, indice) => {
      let u = porId.get(e.id);
      if (!u) {
        u = { id: e.id, nome: e.nome, lat: e.lat, lon: e.lon, plataformas: [] };
        porId.set(e.id, u);
      }
      u.plataformas.push({ linha: id, indice });
    });
  }
  const horarios = {} as Record<TipoDia, HorarioDia>;
  for (const tipo of TIPOS_DIA) horarios[tipo] = montaHorario(tipo, json, linhas, ids);
  return { ids, linhas, correspondencias: json.correspondencias, horarios, estacoes: [...porId.values()] };
}

function montaHorario(tipoDia: TipoDia, json: RedeJson, linhas: Record<string, LinhaRede>, ids: string[]): HorarioDia {
  const porLinha: Record<string, [LinhaSentido, LinhaSentido]> = {};
  const trensPorMinuto: Record<string, Int16Array> = {};
  const inicioServico: Record<string, number> = {};
  const fimServico: Record<string, number> = {};
  const pontasDeViagem: Record<string, number[]> = {};
  let janelaIni = Infinity;
  let janelaFim = -Infinity;
  for (const id of ids) {
    const n = linhas[id].n;
    const doDia = json.horarios[tipoDia]?.[id] ?? { '0': [], '1': [] };
    const s0 = montaSentido(id, 0, n, doDia['0'] ?? []);
    const s1 = montaSentido(id, 1, n, doDia['1'] ?? []);
    porLinha[id] = [s0, s1];
    const dif = new Int32Array(MINUTOS_DIA_OPERACAO + 1);
    let ini = Infinity;
    let fim = -Infinity;
    const pontas = new Set<number>([0, n - 1]);
    for (const ls of [s0, s1]) {
      for (const v of ls.viagens) {
        const t0 = v.partida[0];
        const t1 = v.chegada[v.chegada.length - 1];
        ini = Math.min(ini, t0);
        fim = Math.max(fim, t1);
        // minuto m conta se o meio dele (60m + 30 s) está em [t0, t1)
        const m0 = Math.max(0, Math.ceil((t0 - 30) / 60));
        const m1 = Math.min(MINUTOS_DIA_OPERACAO, Math.ceil((t1 - 30) / 60));
        if (m1 > m0) {
          dif[m0]++;
          dif[m1]--;
        }
        pontas.add(estacaoGlobal(n, ls.sentido, v.inicio));
        pontas.add(estacaoGlobal(n, ls.sentido, v.fim));
      }
    }
    const grade = new Int16Array(MINUTOS_DIA_OPERACAO);
    let acc = 0;
    for (let m = 0; m < MINUTOS_DIA_OPERACAO; m++) {
      acc += dif[m];
      grade[m] = acc;
    }
    trensPorMinuto[id] = grade;
    inicioServico[id] = ini;
    fimServico[id] = fim;
    pontasDeViagem[id] = [...pontas].sort((a, b) => a - b);
    janelaIni = Math.min(janelaIni, ini);
    janelaFim = Math.max(janelaFim, fim);
  }
  return { tipoDia, porLinha, trensPorMinuto, inicioServico, fimServico, janelaRede: [janelaIni, janelaFim], pontasDeViagem };
}

function montaSentido(linha: string, sentido: Sentido, n: number, lista: ViagemJson[]): LinhaSentido {
  const viagens: Viagem[] = lista.map((v, indice) => {
    const k = v.tempos.length;
    const chegada = new Float64Array(k);
    const partida = new Float64Array(k);
    v.tempos.forEach(([c, p], i) => {
      chegada[i] = c;
      partida[i] = p;
    });
    return { id: `${linha}:${sentido}:${indice}`, linha, sentido, indice, inicio: v.inicio, fim: v.inicio + k - 1, chegada, partida };
  });
  const ordenadas = ordemDeCirculacao(viagens, n);
  const servidas = new Int32Array(n * n);
  for (const v of viagens) for (let a = v.inicio; a <= v.fim; a++) for (let b = a + 1; b <= v.fim; b++) servidas[a * n + b]++;
  const percursoMediano = new Float64Array(Math.max(n - 1, 0));
  for (let j = 0; j < n - 1; j++) {
    const tempos: number[] = [];
    for (const v of viagens) if (v.inicio <= j && v.fim >= j + 1) tempos.push(v.chegada[j + 1 - v.inicio] - v.partida[j - v.inicio]);
    tempos.sort((a, b) => a - b);
    percursoMediano[j] = tempos.length ? tempos[Math.floor(tempos.length / 2)] : 0;
  }
  return { linha, sentido, n, viagens: ordenadas, servidas, percursoMediano };
}

/**
 * Ordenação topológica: em cada trecho, a viagem que entra antes no horário vem antes.
 * Viagens que começam no meio da linha (retornos parciais) ficam na posição certa em cada trecho.
 */
function ordemDeCirculacao(viagens: Viagem[], n: number): Viagem[] {
  const entra = viagens.map(() => [] as number[]);
  const grau = new Int32Array(viagens.length);
  for (let j = 0; j < n - 1; j++) {
    const usam = viagens
      .map((v, i) => ({ i, t: v.inicio <= j && v.fim >= j + 1 ? v.partida[j - v.inicio] : NaN }))
      .filter((x) => !Number.isNaN(x.t))
      .sort((a, b) => a.t - b.t || a.i - b.i);
    for (let k = 1; k < usam.length; k++) {
      entra[usam[k - 1].i].push(usam[k].i);
      grau[usam[k].i]++;
    }
  }
  const prontas = viagens.map((_, i) => i).filter((i) => grau[i] === 0);
  const saida: Viagem[] = [];
  const chave = (i: number) => viagens[i].partida[0];
  while (prontas.length) {
    prontas.sort((a, b) => chave(a) - chave(b) || a - b);
    const i = prontas.shift() as number;
    saida.push(viagens[i]);
    for (const k of entra[i]) if (--grau[k] === 0) prontas.push(k);
  }
  if (saida.length !== viagens.length) throw new Error('horário com ultrapassagem: não há ordem de circulação');
  return saida;
}

/** Trens em circulação segundo o horário num instante (segundos do dia de operação). */
export function trensProgramados(h: HorarioDia, linha: string, t: number): number {
  let total = 0;
  for (const ls of h.porLinha[linha]) for (const v of ls.viagens) if (v.partida[0] <= t && t < v.chegada[v.chegada.length - 1]) total++;
  return total;
}

/** Distância em linha reta entre dois pontos, em km. */
export function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371.0088;
  const r = Math.PI / 180;
  const dlat = (lat2 - lat1) * r;
  const dlon = (lon2 - lon1) * r;
  const a = Math.sin(dlat / 2) ** 2 + Math.cos(lat1 * r) * Math.cos(lat2 * r) * Math.sin(dlon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}
