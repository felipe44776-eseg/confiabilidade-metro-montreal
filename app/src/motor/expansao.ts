// Expansão da rede (spec 014, núcleo de cálculo): que ligação construir para a rede ficar mais confiável.
//
// Método de estados: cada componente de falha (material rodante por trecho e sentido, equipamento
// fixo por trecho, causa comum por par de linhas, trechos da candidata) fica fora de serviço com a
// probabilidade estacionária p = νd / (1 + νd), com ν a taxa média do cenário e d a duração média.
// Cada amostra sorteia os componentes fora, monta o conjunto de arestas bloqueadas e mede a
// disponibilidade origem-destino ponderada pela oferta de hoje (grafo.ts). O ganho de uma candidata
// usa números aleatórios comuns: os componentes da rede atual saem iguais com e sem ela.

import type { Contexto } from './contexto';
import { duracaoMediaMin, preparaContexto, reducaoCausaComum } from './contexto';
import type { Grafo, LinhaGrafo } from './grafo';
import { avaliaOD, efeitoBloqueio, linhasDoHorario, montaGrafo } from './grafo';
import { hipotese } from './hipoteses';
import { NENHUMA_POLITICA } from './politicas';
import { Rng, misturaSemente } from './prng';
import type { Rede } from './rede';
import { haversineKm, trechoFisico } from './rede';
import type { Cenario, Parametros, Sentido } from './tipos';

const Z95 = 1.959963984540054;
const LOTES = 50;
export const AMOSTRAS_PADRAO = 200_000;
const DIAS_ANO = 365;

export interface EstacaoNova {
  id: string;
  nome: string;
  lat: number;
  lon: number;
}

export interface Candidata {
  id: string;
  nome: string;
  /** Linha existente que a candidata prolonga, ou id de uma linha nova. */
  linha: string;
  /** Estações na ordem do traçado (ids da rede atual ou de `estacoesNovas`). Prolongamento começa num terminal. */
  sequencia: string[];
  estacoesNovas?: EstacaoNova[];
  /** km de via por trecho; sem ele, linha reta × fator_tracado_candidata (hipótese). */
  kmTrechos?: number[];
  /** Linhas com que a candidata divide alimentação ou controle (causa comum). Sem ele: as linhas das estações onde ela encosta. */
  compartilhaCausaComumCom?: string[];
  fonte?: string;
  status: 'em obras (OSM)' | 'hipótese de traçado' | 'livre';
  /** Linha existente de onde vêm as taxas por km de uma linha nova (ex.: anel da Laranja). Sem ele: a própria linha, ou a média da rede. */
  herdaTaxasDe?: string;
  /**
   * Outras linhas do mesmo projeto, avaliadas junto (ex.: Rosa com o prolongamento da Azul, que torna
   * Vertières uma correspondência). Podem usar as estações novas umas das outras.
   */
  extras?: Candidata[];
}

export interface OpcoesEstados {
  amostras?: number;
  semente?: number;
  rotaAlternativa?: boolean; // padrão: ligada (é o que dá valor a uma ligação nova)
  retornoParcial?: boolean;
  tratamentoCausaComum?: boolean;
}

export interface EstimativaSimples {
  media: number;
  ic95: [number, number];
  meiaLargura: number;
  n: number; // amostras
  semente: number;
}

export interface AvaliacaoEstados {
  dispOD: EstimativaSimples;
  minutosParAno: EstimativaSimples;
  dispLinha: Record<string, EstimativaSimples>;
  amostras: number;
  semente: number;
}

interface Componente {
  p: number;
  arestas: number[];
  linhas: string[];
  rotulo: string;
}

interface ModeloEstados {
  grafo: Grafo;
  componentes: Componente[];
  minutosJanela: number;
  linhas: string[];
}

interface TaxasLinha {
  // por minuto
  mr: number;
  ef: number;
  dMR: number; // duração média, minutos
  dEF: number;
  km: number;
}

function taxasDasLinhas(ctx: Contexto): Record<string, TaxasLinha> {
  const saida: Record<string, TaxasLinha> = {};
  for (const linha of ctx.rede.ids) {
    const minutos = Math.max(1, (ctx.horario.fimServico[linha] - ctx.horario.inicioServico[linha]) / 60);
    const fonte = (c: 'MR' | 'EF') => ctx.fontes.find((f) => f.linha === linha && f.causa === c);
    const mr = fonte('MR');
    const ef = fonte('EF');
    const km = ctx.rede.linhas[linha].kmTrecho.reduce((a, b) => a + b, 0);
    saida[linha] = {
      mr: mr ? mr.acum[mr.acum.length - 1] / minutos : 0,
      ef: ef ? ef.acum[ef.acum.length - 1] / minutos : 0,
      dMR: mr ? duracaoMediaMin(mr.duracao) : 0,
      dEF: ef ? duracaoMediaMin(ef.duracao) : 0,
      km,
    };
  }
  return saida;
}

const pEstacionaria = (taxaMin: number, dMin: number) => (taxaMin * dMin) / (1 + taxaMin * dMin);

/** Componentes da rede atual, com as arestas do grafo dado (que pode ter candidatas). */
function componentesDaRede(ctx: Contexto, grafo: Grafo, op: Required<Pick<OpcoesEstados, 'retornoParcial' | 'tratamentoCausaComum'>>, deslocamento: Record<string, number>): Componente[] {
  const taxas = taxasDasLinhas(ctx);
  const comps: Componente[] = [];
  for (const linha of ctx.rede.ids) {
    const tx = taxas[linha];
    const n = ctx.rede.linhas[linha].n;
    const off = deslocamento[linha] ?? 0;
    // material rodante: proporcional ao tempo de trem em cada trecho e sentido
    const tempo: number[][] = [new Array(n - 1).fill(0), new Array(n - 1).fill(0)];
    let total = 0;
    for (const ls of ctx.horario.porLinha[linha]) {
      for (const v of ls.viagens) {
        for (let s = v.inicio; s < v.fim; s++) {
          const dt = v.chegada[s + 1 - v.inicio] - v.partida[s - v.inicio];
          tempo[ls.sentido][trechoFisico(n, ls.sentido, s)] += dt;
          total += dt;
        }
      }
    }
    for (const sentido of [0, 1] as Sentido[]) {
      for (let g = 0; g < n - 1; g++) {
        const nu = total > 0 ? (tx.mr * tempo[sentido][g]) / total : 0;
        if (nu <= 0) continue;
        comps.push({ p: pEstacionaria(nu, tx.dMR), arestas: efeitoBloqueio(grafo, linha, g + off, [sentido], op.retornoParcial), linhas: [linha], rotulo: `MR ${linha} trecho ${g} sentido ${sentido}` });
      }
    }
    // equipamento fixo: pesos dos locais com posição + falhas sem posição uniformes por km
    const peso = new Array(n - 1).fill(0);
    const loc = ctx.locais[linha];
    const est = ctx.rede.linhas[linha].estacoes;
    loc.kms.forEach((km, i) => {
      let g = 0;
      for (let k = 0; k < n - 1; k++) if (est[k].km <= km) g = k;
      peso[Math.min(g, n - 2)] += loc.pesosAcum[i] - (i > 0 ? loc.pesosAcum[i - 1] : 0);
    });
    const kmLinha = tx.km || 1;
    for (let g = 0; g < n - 1; g++) peso[g] += (loc.pesoSemPosicao * ctx.rede.linhas[linha].kmTrecho[g]) / kmLinha;
    const somaPeso = peso.reduce((a, b) => a + b, 0) || 1;
    for (let g = 0; g < n - 1; g++) {
      const nu = (tx.ef * peso[g]) / somaPeso;
      if (nu <= 0) continue;
      const sentidosEF: Sentido[][] = ctx.sentidosEF === 2 ? [[0, 1]] : [[0], [1]];
      for (const ss of sentidosEF) {
        comps.push({ p: pEstacionaria(nu / sentidosEF.length, tx.dEF), arestas: efeitoBloqueio(grafo, linha, g + off, ss, op.retornoParcial), linhas: [linha], rotulo: `EF ${linha} trecho ${g}` });
      }
    }
  }
  const reducao = reducaoCausaComum(ctx, { ...NENHUMA_POLITICA, tratamentoCausaComum: op.tratamentoCausaComum });
  for (const cc of ctx.causaComum) {
    const nu = (ctx.parametros.causa_comum[cc.par].taxa_por_hora_op.valor * (1 - reducao)) / 60;
    const arestas = cc.linhas.flatMap((l) => grafo.arestasDaLinha.get(l) ?? []);
    comps.push({ p: pEstacionaria(nu, duracaoMediaMin(cc.duracao)), arestas, linhas: [...cc.linhas], rotulo: `causa comum ${cc.par}` });
  }
  return comps;
}

/** Sorteia os componentes fora de serviço (Bernoulli independentes, por afinamento geométrico). */
function sorteiaFora(rng: Rng, p: Float64Array, pMax: number, saida: number[]): void {
  saida.length = 0;
  if (pMax <= 0) return;
  const logq = Math.log1p(-pMax);
  let i = -1;
  for (;;) {
    i += 1 + Math.floor(Math.log(rng.uniformeAberto()) / logq);
    if (i >= p.length) break;
    if (rng.uniforme() * pMax < p[i]) saida.push(i);
  }
}

interface Acumulador {
  od: Float64Array; // por lote: soma da disponibilidade OD
  linha: Record<string, Float64Array>;
}

function avaliaModelo(m: ModeloEstados, amostras: number, semente: number, rotaAlternativa: boolean, extra?: { comps: Componente[]; semente: number }): Acumulador {
  const base = Float64Array.from(m.componentes.map((c) => c.p));
  const pMaxBase = base.reduce((a, b) => Math.max(a, b), 0);
  const ext = extra ? Float64Array.from(extra.comps.map((c) => c.p)) : new Float64Array(0);
  const pMaxExt = ext.reduce((a, b) => Math.max(a, b), 0);
  const rngA = new Rng(misturaSemente(semente, 0x0e57ad05));
  const rngB = new Rng(misturaSemente(extra?.semente ?? semente, 0xca9d1da7));
  const acc: Acumulador = { od: new Float64Array(LOTES), linha: {} };
  for (const l of m.linhas) acc.linha[l] = new Float64Array(LOTES);
  const foraA: number[] = [];
  const foraB: number[] = [];
  const porLote = Math.ceil(amostras / LOTES);
  for (let j = 0; j < amostras; j++) {
    const lote = Math.min(LOTES - 1, Math.floor(j / porLote));
    sorteiaFora(rngA, base, pMaxBase, foraA);
    if (extra) sorteiaFora(rngB, ext, pMaxExt, foraB);
    if (foraA.length === 0 && foraB.length === 0) {
      acc.od[lote] += 1;
      for (const l of m.linhas) acc.linha[l][lote] += 1;
      continue;
    }
    const arestas = new Set<number>();
    const linhasFora = new Set<string>();
    for (const i of foraA) {
      for (const e of m.componentes[i].arestas) arestas.add(e);
      for (const l of m.componentes[i].linhas) linhasFora.add(l);
    }
    for (const i of foraB) {
      const c = (extra as { comps: Componente[] }).comps[i];
      for (const e of c.arestas) arestas.add(e);
      for (const l of c.linhas) linhasFora.add(l);
    }
    const r = avaliaOD(m.grafo, [...arestas].sort((a, b) => a - b), rotaAlternativa);
    acc.od[lote] += 1 - r.indisponivel;
    for (const l of m.linhas) if (!linhasFora.has(l)) acc.linha[l][lote] += 1;
  }
  const tamanhos = new Float64Array(LOTES);
  for (let j = 0; j < amostras; j++) tamanhos[Math.min(LOTES - 1, Math.floor(j / porLote))]++;
  for (let k = 0; k < LOTES; k++) {
    const t = tamanhos[k] || 1;
    acc.od[k] /= t;
    for (const l of m.linhas) acc.linha[l][k] /= t;
  }
  return acc;
}

function resumo(lotes: Float64Array, amostras: number, semente: number, escala = 1): EstimativaSimples {
  const xs = [...lotes].map((x) => x * escala);
  const media = xs.reduce((a, b) => a + b, 0) / xs.length;
  const dp = Math.sqrt(xs.reduce((a, b) => a + (b - media) ** 2, 0) / (xs.length - 1));
  const mh = (Z95 * dp) / Math.sqrt(xs.length);
  return { media, ic95: [media - mh, media + mh], meiaLargura: mh, n: amostras, semente };
}

function opcoesPadrao(o: OpcoesEstados) {
  return {
    amostras: o.amostras ?? AMOSTRAS_PADRAO,
    semente: o.semente ?? 20261021,
    rotaAlternativa: o.rotaAlternativa ?? true,
    retornoParcial: o.retornoParcial ?? false,
    tratamentoCausaComum: o.tratamentoCausaComum ?? false,
  };
}

/** Rede atual pelo método de estados (validação contra a camada diária). */
export function avaliaRedeAtual(rede: Rede, parametros: Parametros, cenario: Cenario, opcoes: OpcoesEstados = {}): AvaliacaoEstados {
  const op = opcoesPadrao(opcoes);
  const ctx = preparaContexto(rede, parametros, cenario);
  const grafo = ctx.grafo;
  const modelo: ModeloEstados = { grafo, componentes: componentesDaRede(ctx, grafo, op, {}), minutosJanela: (ctx.horario.janelaRede[1] - ctx.horario.janelaRede[0]) / 60, linhas: rede.ids };
  const acc = avaliaModelo(modelo, op.amostras, op.semente, op.rotaAlternativa);
  const dispLinha: Record<string, EstimativaSimples> = {};
  for (const l of rede.ids) dispLinha[l] = resumo(acc.linha[l], op.amostras, op.semente);
  const indisp = acc.od.map((x) => 1 - x);
  return {
    dispOD: resumo(acc.od, op.amostras, op.semente),
    minutosParAno: resumo(indisp, op.amostras, op.semente, modelo.minutosJanela * DIAS_ANO),
    dispLinha,
    amostras: op.amostras,
    semente: op.semente,
  };
}

export interface ItemRanking {
  candidata: Candidata;
  km: number;
  /** Ganho de disponibilidade OD (fração), candidata independente da rede atual. */
  ganho: EstimativaSimples;
  /** Ganho com a candidata dividindo a causa comum das linhas em que encosta. */
  ganhoComCausaComum: EstimativaSimples;
  ganhoPorKm: number;
  minutosParAnoEvitados: EstimativaSimples;
  amostras: number;
  semente: number;
  hipoteses: string[];
}

type Montagem = { linhas: LinhaGrafo[]; deslocamento: Record<string, number>; kms: number[]; trechos: { linha: string; g: number; km: number }[]; encosta: string[] };

/** Linhas do grafo com a candidata (e as linhas extras do mesmo projeto) e o deslocamento de índices de uma linha prolongada pelo começo. */
function linhasComCandidata(ctx: Contexto, c: Candidata): Montagem {
  const base = linhasDoHorario(ctx.rede, ctx.horario, ctx.cenario.pontosRetorno);
  const conhecidas = new Map<string, { id: string; nome: string; lat: number; lon: number }>();
  for (const e of ctx.rede.estacoes) conhecidas.set(e.id, { id: e.id, nome: e.nome, lat: e.lat, lon: e.lon });
  const partes = [c, ...(c.extras ?? [])];
  for (const p of partes) for (const e of p.estacoesNovas ?? []) conhecidas.set(e.id, e);
  const total: Montagem = { linhas: base, deslocamento: {}, kms: [], trechos: [], encosta: [] };
  for (const p of partes) {
    const m = aplicaCandidata(ctx, base, p, conhecidas);
    for (const [l, k] of Object.entries(m.deslocamento)) total.deslocamento[l] = (total.deslocamento[l] ?? 0) + k;
    total.kms.push(...m.kms);
    total.trechos.push(...m.trechos);
    total.encosta.push(...m.encosta.filter((l) => !total.encosta.includes(l)));
  }
  const ids = new Set(partes.map((p) => p.linha));
  total.encosta = total.encosta.filter((l) => !ids.has(l));
  return total;
}

function aplicaCandidata(ctx: Contexto, base: LinhaGrafo[], c: Candidata, conhecidas: Map<string, { id: string; nome: string; lat: number; lon: number }>): Montagem {
  const seq = c.sequencia.map((id) => {
    const e = conhecidas.get(id);
    if (!e) throw new Error(`candidata ${c.id}: estação desconhecida ${id}`);
    return e;
  });
  if (seq.length < 2) throw new Error(`candidata ${c.id}: precisa de pelo menos duas estações`);
  const fator = hipotese('fator_tracado_candidata', ctx.parametros, ctx.cenario);
  const v = hipotese('velocidade_comercial_candidata_kmh', ctx.parametros, ctx.cenario);
  const kms = seq.slice(1).map((e, i) => c.kmTrechos?.[i] ?? haversineKm(seq[i].lat, seq[i].lon, e.lat, e.lon) * fator);
  const tempos = kms.map((km) => (km / v) * 3600);
  const encosta = new Set<string>();
  for (const e of seq) for (const u of ctx.rede.estacoes) if (u.id === e.id) for (const p of u.plataformas) encosta.add(p.linha);
  const deslocamento: Record<string, number> = {};
  const existente = base.find((l) => l.id === c.linha);
  if (!existente) {
    base.push({ id: c.linha, estacoes: seq, tempo0: tempos, tempo1: [...tempos], km: kms, pontasRetorno: [0, seq.length - 1], candidata: true });
    return { linhas: base, deslocamento, kms, trechos: kms.map((km, g) => ({ linha: c.linha, g, km })), encosta: [...encosta].filter((l) => l !== c.linha) };
  }
  const n = existente.estacoes.length;
  if (seq[0].id === existente.estacoes[n - 1].id) {
    existente.estacoes = [...existente.estacoes, ...seq.slice(1)];
    existente.tempo0 = [...existente.tempo0, ...tempos];
    existente.tempo1 = [...existente.tempo1, ...tempos];
    existente.km = [...existente.km, ...kms];
    existente.pontasRetorno = [...existente.pontasRetorno, existente.estacoes.length - 1];
    return { linhas: base, deslocamento, kms, trechos: kms.map((km, i) => ({ linha: c.linha, g: n - 1 + i, km })), encosta: [...encosta].filter((l) => l !== c.linha) };
  }
  if (seq[0].id === existente.estacoes[0].id) {
    const k = seq.length - 1;
    const novas = seq.slice(1).reverse();
    const kmsR = [...kms].reverse();
    const temposR = [...tempos].reverse();
    existente.estacoes = [...novas, ...existente.estacoes];
    existente.tempo0 = [...temposR, ...existente.tempo0];
    existente.tempo1 = [...temposR, ...existente.tempo1];
    existente.km = [...kmsR, ...existente.km];
    existente.pontasRetorno = [0, ...existente.pontasRetorno.map((r) => r + k)];
    deslocamento[c.linha] = k;
    return { linhas: base, deslocamento, kms, trechos: kmsR.map((km, g) => ({ linha: c.linha, g, km })), encosta: [...encosta].filter((l) => l !== c.linha) };
  }
  throw new Error(`candidata ${c.id}: o prolongamento da linha ${c.linha} precisa começar num terminal`);
}

/** Avalia candidatas contra a rede atual e devolve o ranking por ganho de disponibilidade origem-destino. */
export function avaliaCandidatas(rede: Rede, parametros: Parametros, cenario: Cenario, candidatas: Candidata[], opcoes: OpcoesEstados = {}): ItemRanking[] {
  const op = opcoesPadrao(opcoes);
  const ctx = preparaContexto(rede, parametros, cenario);
  const transferenciaS = hipotese('tempo_transferencia_min', parametros, cenario) * 60;
  const taxas = taxasDasLinhas(ctx);
  // taxas por km herdadas da rede (hipótese): média ponderada pelo km
  let kmRede = 0;
  let mrRede = 0;
  let efRede = 0;
  let dMR = 0;
  let dEF = 0;
  for (const l of rede.ids) {
    kmRede += taxas[l].km;
    mrRede += taxas[l].mr;
    efRede += taxas[l].ef;
    dMR += taxas[l].mr * taxas[l].dMR;
    dEF += taxas[l].ef * taxas[l].dEF;
  }
  const porKm = { mr: mrRede / kmRede, ef: efRede / kmRede, dMR: dMR / (mrRede || 1), dEF: dEF / (efRede || 1) };
  const baseModelo: ModeloEstados = {
    grafo: ctx.grafo,
    componentes: componentesDaRede(ctx, ctx.grafo, op, {}),
    minutosJanela: (ctx.horario.janelaRede[1] - ctx.horario.janelaRede[0]) / 60,
    linhas: rede.ids,
  };
  const accBase = avaliaModelo(baseModelo, op.amostras, op.semente, op.rotaAlternativa);
  const saida: ItemRanking[] = [];
  for (const c of candidatas) {
    const montagem = linhasComCandidata(ctx, c);
    const grafo = montaGrafo(montagem.linhas, transferenciaS, { pesosDe: ctx.grafo });
    const comps = componentesDaRede(ctx, grafo, op, montagem.deslocamento);
    const fonteTaxa = new Map([c, ...(c.extras ?? [])].map((p) => [p.linha, p.herdaTaxasDe ?? p.linha]));
    const herdaDe = (linhaCand: string) => {
      const l = fonteTaxa.get(linhaCand) ?? linhaCand;
      return taxas[l] ? { mr: taxas[l].mr / (taxas[l].km || 1), ef: taxas[l].ef / (taxas[l].km || 1), dMR: taxas[l].dMR, dEF: taxas[l].dEF } : porKm;
    };
    const extra: Componente[] = [];
    montagem.trechos.forEach(({ linha, g, km }) => {
      const herda = herdaDe(linha);
      const linhasCand = [linha];
      for (const s of [0, 1] as Sentido[]) extra.push({ p: pEstacionaria((herda.mr * km) / 2, herda.dMR), arestas: efeitoBloqueio(grafo, linha, g, [s], op.retornoParcial), linhas: linhasCand, rotulo: `MR candidata ${c.id} trecho ${g}` });
      const sentidosEF: Sentido[][] = ctx.sentidosEF === 2 ? [[0, 1]] : [[0], [1]];
      for (const ss of sentidosEF) extra.push({ p: pEstacionaria((herda.ef * km) / sentidosEF.length, herda.dEF), arestas: efeitoBloqueio(grafo, linha, g, ss, op.retornoParcial), linhas: linhasCand, rotulo: `EF candidata ${c.id} trecho ${g}` });
    });
    const modelo: ModeloEstados = { grafo, componentes: comps, minutosJanela: baseModelo.minutosJanela, linhas: rede.ids };
    const sementeExtra = misturaSemente(op.semente, 0xc0ffee);
    const accSem = avaliaModelo(modelo, op.amostras, op.semente, op.rotaAlternativa, { comps: extra, semente: sementeExtra });
    // com causa comum: os componentes de causa comum das linhas em que encosta também tiram a candidata
    const compartilha = new Set(c.compartilhaCausaComumCom ?? montagem.encosta);
    const arestasCand = [c, ...(c.extras ?? [])].flatMap((p) => grafo.arestasDaLinha.get(p.linha) ?? []);
    const compsCC = comps.map((k) => (k.rotulo.startsWith('causa comum') && k.linhas.some((l) => compartilha.has(l)) ? { ...k, arestas: [...new Set([...k.arestas, ...arestasCand])] } : k));
    const accCom = avaliaModelo({ ...modelo, componentes: compsCC }, op.amostras, op.semente, op.rotaAlternativa, { comps: extra, semente: sementeExtra });
    const dif = (acc: Acumulador) => accBase.od.map((b, k) => acc.od[k] - b);
    const ganho = resumo(dif(accSem), op.amostras, op.semente);
    const ganhoCom = resumo(dif(accCom), op.amostras, op.semente);
    const kmTotal = montagem.kms.reduce((a, b) => a + b, 0);
    saida.push({
      candidata: c,
      km: kmTotal,
      ganho,
      ganhoComCausaComum: ganhoCom,
      ganhoPorKm: kmTotal > 0 ? ganho.media / kmTotal : 0,
      minutosParAnoEvitados: resumo(dif(accSem), op.amostras, op.semente, baseModelo.minutosJanela * DIAS_ANO),
      amostras: op.amostras,
      semente: op.semente,
      hipoteses: [
        `traçado: ${c.status}${c.fonte ? ` (${c.fonte})` : ''}`,
        c.kmTrechos ? 'km de via informado' : `km = linha reta × ${hipotese('fator_tracado_candidata', parametros, cenario)}`,
        `velocidade comercial ${hipotese('velocidade_comercial_candidata_kmh', parametros, cenario)} km/h`,
        ...[c, ...(c.extras ?? [])].map((p) => {
          const l = p.herdaTaxasDe ?? p.linha;
          return taxas[l] ? `${p.linha}: taxas por km herdadas da linha ${l}` : `${p.linha}: taxas por km herdadas da média da rede`;
        }),
        `pares ponderados pela oferta de hoje (${cenario.tipoDia})`,
        op.rotaAlternativa ? 'rota alternativa ligada' : 'rota alternativa desligada',
        op.retornoParcial ? 'retorno parcial ligado (pontas de viagem do horário)' : 'sem retorno parcial: trecho bloqueado para a linha inteira',
      ],
    });
  }
  return saida.sort((a, b) => b.ganho.media - a.ganho.media);
}

/** Candidata livre: ligação direta entre duas estações da rede atual. */
export function candidataLivre(rede: Rede, idA: string, idB: string, km?: number): Candidata {
  const a = rede.estacoes.find((e) => e.id === idA);
  const b = rede.estacoes.find((e) => e.id === idB);
  if (!a || !b) throw new Error(`estação desconhecida: ${a ? idB : idA}`);
  return { id: `livre:${idA}-${idB}`, nome: `${a.nome} – ${b.nome}`, linha: `livre:${idA}-${idB}`, sequencia: [idA, idB], kmTrechos: km !== undefined ? [km] : undefined, status: 'livre' };
}

/** Todas as ligações diretas entre estações da rede atual até `distanciaMaxKm` em linha reta, sem as que já existem. */
export function candidatasDaBusca(rede: Rede, distanciaMaxKm: number, kmMinimo = 0): Candidata[] {
  const vizinhas = new Set<string>();
  for (const id of rede.ids) {
    const est = rede.linhas[id].estacoes;
    for (let g = 0; g < est.length - 1; g++) {
      vizinhas.add(`${est[g].id}|${est[g + 1].id}`);
      vizinhas.add(`${est[g + 1].id}|${est[g].id}`);
    }
  }
  const saida: Candidata[] = [];
  const E = rede.estacoes;
  for (let i = 0; i < E.length; i++) {
    for (let j = i + 1; j < E.length; j++) {
      if (vizinhas.has(`${E[i].id}|${E[j].id}`)) continue;
      const d = haversineKm(E[i].lat, E[i].lon, E[j].lat, E[j].lon);
      if (d <= distanciaMaxKm && d >= kmMinimo) saida.push(candidataLivre(rede, E[i].id, E[j].id));
    }
  }
  return saida;
}

/** Busca exaustiva (spec 014): ranking por ganho e por ganho por km. */
export function buscaExaustiva(rede: Rede, parametros: Parametros, cenario: Cenario, distanciaMaxKm: number, opcoes: OpcoesEstados = {}): { porGanho: ItemRanking[]; porKm: ItemRanking[] } {
  const kmMin = hipotese('km_minimo_candidata', parametros, cenario);
  const ranking = avaliaCandidatas(rede, parametros, cenario, candidatasDaBusca(rede, distanciaMaxKm, kmMin), opcoes);
  return { porGanho: ranking, porKm: [...ranking].sort((a, b) => b.ganhoPorKm - a.ganhoPorKm) };
}
