// Linhas novas numa viagem (spec 016): a viagem de A a B com linhas construídas, no mesmo dia simulado
// da rede atual.
//
// O dia da rede atual sai do motor (spec 007) sem mudança. Sobre ele, cada linha nova:
// - entra no grafo das estações como na expansão (spec 014): o prolongamento estende a própria linha; a
//   linha nova (proposta ou desenhada) é uma linha a mais, com baldeação nas estações em que encosta;
// - falha com as taxas por km e as durações observadas da linha de que herda (prolongamento: a própria
//   linha; linha nova: `herdaTaxasDe` ou a média da rede), num fluxo de sorteio próprio. A rede atual tem
//   as mesmas falhas com e sem a linha nova (números aleatórios comuns), então o ganho é pareado;
// - tem trens próprios: no prolongamento, cada viagem do horário que chega ao terminal antigo segue pelo
//   trecho novo (e a que sai dele vem do trecho novo); na linha nova, as partidas por hora da linha de
//   referência, espaçadas por igual. Numa interrupção, as conexões do trecho parado não acontecem; depois,
//   os trens seguem o horário, sem fila (simplificação declarada no plano da spec 016).

import type { Contexto, Duracao } from './contexto';
import type { ResultadoDia } from './dia';
import { sorteiaDuracao } from './dia';
import type { Candidata } from './expansao';
import { linhasComCandidata } from './expansao';
import type { BloqueioOD, Grafo, OrigemBloqueio } from './grafo';
import { chave, efeitoBloqueio, montaGrafo } from './grafo';
import { hipotese } from './hipoteses';
import type { Politicas } from './politicas';
import { criaFluxo } from './prng';
import { sorteiaInstantes } from './taxas';
import type { Sentido } from './tipos';

/** Fonte de falha de um trecho novo (material rodante por sentido; equipamento fixo por trecho). */
export interface FonteNova {
  causa: 'MR' | 'EF';
  linha: string; // linha no grafo com as linhas novas
  trecho: number; // trecho físico nesse grafo
  /** MR: o sentido da fonte. EF: null (dois sentidos, ou um sorteado, pela hipótese sentidos_bloqueio_ef). */
  sentido: Sentido | null;
  acum: Float64Array;
  forma: number;
  escala: number;
  /** Uma duração (linha herdada) ou a mistura das linhas, com peso pela taxa (média da rede). */
  duracoes: { peso: number; d: Duracao }[];
  sub: number; // fluxo de sorteio (estável: não depende de quais outras linhas são construídas juntas)
}

/** Trens das linhas novas num dia sem falhas: uma conexão por trem e trecho. */
export interface ConexoesNovas {
  dep: number[];
  arr: number[];
  de: number[]; // nó do grafo com as linhas novas
  para: number[];
  aresta: number[];
  viagem: number[]; // 0..nViagens-1, próprio das linhas novas
  nViagens: number;
}

/** Falha injetada numa linha nova (testes). */
export interface FalhaNovaInjetada {
  t: number;
  duracaoS: number;
  linha: string;
  trecho: number;
  sentidos: Sentido[];
}

export interface VarianteRede {
  id: string;
  nome: string;
  partes: Candidata[];
  g: Grafo;
  deslocamento: Record<string, number>;
  /** Linhas do grafo com trecho novo e a linha de que cada uma herda as taxas ("media" = média da rede). */
  herda: Record<string, string>;
  /** Linha que dá as partidas por hora de cada linha nova (no prolongamento, a própria). */
  referencia: Record<string, string>;
  trechosNovos: { linha: string; trecho: number; km: number }[];
  arestasNovas: number[];
  /** Causa comum de uma linha atual que também para linhas novas: arestas a mais. */
  ccExtra: Record<string, number[]>;
  fontes: FonteNova[];
  conexoes: ConexoesNovas;
  km: number;
  retornoParcial: boolean;
  politicas: Pick<Politicas, 'retiradaTrem' | 'operacaoDegradada'>;
  injetadas: FalhaNovaInjetada[];
  hipoteses: string[];
  /** Nó e aresta, no grafo da variante, de cada nó e aresta do grafo da rede atual. */
  mapaNo: Int32Array;
  mapaAresta: Int32Array;
  /** Conexões dos trens novos em ordem de partida (ao milissegundo; empate pela ordem de criação). */
  ordemConexoes: Int32Array;
}

export interface OpcoesVariante {
  politicas: Politicas;
  /** A linha nova para junto quando a causa comum atinge as linhas em que ela encosta. */
  causaComumCompartilhada: boolean;
  id?: string;
  nome?: string;
  injetadas?: FalhaNovaInjetada[];
}

/** FNV-1a de 30 bits: fluxo de sorteio de uma fonte a partir do nome dela. */
function hash30(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return (h >>> 0) & 0x3fffffff;
}

/** Partes de um conjunto de candidatas (com as extras de cada projeto), sem repetir; erro se forem incompatíveis. */
export function partesDe(ctx: Contexto, cands: readonly Candidata[]): Candidata[] {
  const vistas = new Map<string, Candidata>();
  for (const c of cands) {
    for (const p of [c, ...(c.extras ?? [])]) {
      if (vistas.has(p.id)) continue;
      const { extras: _extras, ...sem } = p;
      vistas.set(p.id, sem);
    }
  }
  const partes = [...vistas.values()];
  const porLinha = new Map<string, Candidata>();
  const pontas = new Map<string, Candidata>();
  for (const p of partes) {
    if (ctx.rede.linhas[p.linha]) {
      const k = `${p.linha}|${p.sequencia[0]}`;
      const outra = pontas.get(k);
      if (outra) throw new Error(`${outra.nome} e ${p.nome} prolongam a mesma ponta da linha: escolha uma`);
      pontas.set(k, p);
      continue;
    }
    const outra = porLinha.get(p.linha);
    if (outra) throw new Error(`${outra.nome} e ${p.nome} são versões da mesma linha: escolha uma`);
    porLinha.set(p.linha, p);
  }
  return partes;
}

function multiplica(acum: Float64Array, f: number): Float64Array {
  const s = new Float64Array(acum.length);
  for (let i = 0; i < acum.length; i++) s[i] = acum[i] * f;
  return s;
}

/** Linhas atuais com plataforma nas estações da sequência. */
function linhasQueEncosta(ctx: Contexto, p: Candidata): string[] {
  const s = new Set<string>();
  for (const id of p.sequencia) for (const e of ctx.rede.estacoes) if (e.id === id) for (const pl of e.plataformas) s.add(pl.linha);
  s.delete(p.linha);
  return [...s];
}

function viagensDoDia(ctx: Contexto, linha: string): number {
  return ctx.horario.porLinha[linha].reduce((n, ls) => n + ls.viagens.length, 0);
}

/** A rede com as linhas novas, pronta para medir viagens no mesmo dia da rede atual. */
export function preparaVariante(ctx: Contexto, cands: readonly Candidata[], op: OpcoesVariante): VarianteRede {
  const partes = partesDe(ctx, cands);
  if (!partes.length) throw new Error('nenhuma linha nova');
  const transferenciaS = hipotese('tempo_transferencia_min', ctx.parametros, ctx.cenario) * 60;
  const montagem = linhasComCandidata(ctx, { ...partes[0], extras: partes.slice(1) });
  const g = montaGrafo(montagem.linhas, transferenciaS, { pesosDe: ctx.grafo });
  const deslocamento = montagem.deslocamento;
  const ids = ctx.rede.ids;

  // trechos novos: os de linhas novas e os do prolongamento, fora dos índices da linha atual
  const trechosNovos: VarianteRede['trechosNovos'] = [];
  for (const l of g.linhas) {
    const base = ctx.rede.linhas[l.id];
    const off = deslocamento[l.id] ?? 0;
    for (let t = 0; t < l.estacoes.length - 1; t++) {
      if (!base || t - off < 0 || t - off >= base.n - 1) trechosNovos.push({ linha: l.id, trecho: t, km: l.km[t] });
    }
  }
  const linhasComNovo = [...new Set(trechosNovos.map((t) => t.linha))];
  const parteDaLinha = (linha: string) => partes.find((p) => p.linha === linha);

  // de onde vêm as taxas
  const herda: Record<string, string> = {};
  for (const L of linhasComNovo) {
    if (ctx.rede.linhas[L]) herda[L] = L;
    else {
      const h = parteDaLinha(L)?.herdaTaxasDe;
      herda[L] = h && ctx.rede.linhas[h] ? h : 'media';
    }
  }
  const kmLinha = (R: string) => ctx.rede.linhas[R].kmTrecho.reduce((a, b) => a + b, 0);
  const kmRede = ids.reduce((s, R) => s + kmLinha(R), 0);
  const fonteDe = (R: string, causa: 'MR' | 'EF') => {
    const f = ctx.fontes.find((x) => x.linha === R && x.causa === causa);
    if (!f) throw new Error(`sem fonte de falha ${causa} na linha ${R}`);
    return f;
  };
  const fontes: FonteNova[] = [];
  for (const tr of trechosNovos) {
    const R = herda[tr.linha];
    const tBase = tr.trecho - (deslocamento[tr.linha] ?? 0);
    for (const causa of ['MR', 'EF'] as const) {
      let acum: Float64Array;
      let forma = 1;
      let escala = 1;
      let duracoes: FonteNova['duracoes'];
      if (R !== 'media') {
        const f = fonteDe(R, causa);
        acum = multiplica(f.acum, tr.km / kmLinha(R));
        forma = f.renovacao.forma;
        escala = f.renovacao.escalaNormalizada;
        duracoes = [{ peso: 1, d: f.duracao }];
      } else {
        acum = new Float64Array(ctx.fontes[0].acum.length);
        duracoes = [];
        for (const L of ids) {
          const f = fonteDe(L, causa);
          for (let i = 0; i < acum.length; i++) acum[i] += (f.acum[i] * tr.km) / kmRede;
          duracoes.push({ peso: f.acum[f.acum.length - 1], d: f.duracao });
        }
      }
      if (causa === 'MR') {
        const meia = multiplica(acum, 0.5);
        for (const s of [0, 1] as Sentido[]) fontes.push({ causa, linha: tr.linha, trecho: tr.trecho, sentido: s, acum: meia, forma, escala, duracoes, sub: hash30(`${tr.linha}|${tBase}|MR|${s}`) });
      } else fontes.push({ causa, linha: tr.linha, trecho: tr.trecho, sentido: null, acum, forma, escala, duracoes, sub: hash30(`${tr.linha}|${tBase}|EF`) });
    }
  }

  // causa comum compartilhada: só para linhas novas (o prolongamento já é a mesma linha)
  const ccExtra: Record<string, number[]> = {};
  if (op.causaComumCompartilhada) {
    for (const L of linhasComNovo) {
      if (ctx.rede.linhas[L]) continue;
      const p = parteDaLinha(L);
      const com = p?.compartilhaCausaComumCom ?? (p ? linhasQueEncosta(ctx, p) : []);
      for (const X of com) ccExtra[X] = [...(ccExtra[X] ?? []), ...(g.arestasDaLinha.get(L) ?? [])];
    }
  }

  // trens das linhas novas
  const no = new Map<string, number>();
  g.nos.forEach((x, i) => no.set(`${x.linha}|${x.indice}`, i));
  const conexoes: ConexoesNovas = { dep: [], arr: [], de: [], para: [], aresta: [], viagem: [], nViagens: 0 };
  const viagemSintetica = (L: string, s: Sentido, t0: number, trechos: number[]) => {
    const l = g.linhas.find((x) => x.id === L);
    if (!l || !trechos.length) return;
    const id = conexoes.nViagens++;
    let t = t0;
    for (const tr of trechos) {
      const dur = s === 0 ? l.tempo0[tr] : l.tempo1[tr];
      const [a, b] = s === 0 ? [tr, tr + 1] : [tr + 1, tr];
      const e = g.chaveAresta.get(chave(L, tr, s));
      const na = no.get(`${L}|${a}`);
      const nb = no.get(`${L}|${b}`);
      if (e === undefined || na === undefined || nb === undefined) throw new Error(`linha nova ${L}: trecho ${tr} fora do grafo`);
      conexoes.dep.push(t);
      conexoes.arr.push(t + dur);
      conexoes.de.push(na);
      conexoes.para.push(nb);
      conexoes.aresta.push(e);
      conexoes.viagem.push(id);
      t += dur;
    }
  };
  const intervalo = (a: number, b: number) => Array.from({ length: Math.max(0, b - a + 1) }, (_, i) => a + i);
  const referencia: Record<string, string> = {};
  for (const L of linhasComNovo) {
    const l = g.linhas.find((x) => x.id === L)!;
    const nG = l.estacoes.length;
    const base = ctx.rede.linhas[L];
    if (base) {
      // prolongamento: as viagens do horário seguem pelo trecho novo
      referencia[L] = L;
      const n = base.n;
      const off = deslocamento[L] ?? 0;
      const [s0, s1] = ctx.horario.porLinha[L];
      if (nG - off > n) {
        const jE = off + n - 1;
        const ida = intervalo(jE, nG - 2);
        const volta = [...ida].reverse();
        const totalVolta = ida.reduce((s, t) => s + l.tempo1[t], 0);
        for (const v of s0.viagens) if (v.fim === n - 1) viagemSintetica(L, 0, v.chegada[v.fim - v.inicio], ida);
        for (const v of s1.viagens) if (v.inicio === 0) viagemSintetica(L, 1, v.partida[0] - totalVolta, volta);
      }
      if (off > 0) {
        const ida = intervalo(0, off - 1).reverse(); // do terminal antigo (índice off) até o novo (0)
        const volta = intervalo(0, off - 1);
        const totalVolta = volta.reduce((s, t) => s + l.tempo0[t], 0);
        for (const v of s1.viagens) if (v.fim === n - 1) viagemSintetica(L, 1, v.chegada[v.fim - v.inicio], ida);
        for (const v of s0.viagens) if (v.inicio === 0) viagemSintetica(L, 0, v.partida[0] - totalVolta, volta);
      }
      continue;
    }
    // linha nova: partidas por hora da linha de referência, espaçadas por igual
    const p = parteDaLinha(L);
    const toca = p ? linhasQueEncosta(ctx, p) : [];
    const candidatasRef = p?.herdaTaxasDe && ctx.rede.linhas[p.herdaTaxasDe] ? [p.herdaTaxasDe] : toca.length ? toca : ids;
    const ref = [...candidatasRef].sort((a, b) => viagensDoDia(ctx, b) - viagensDoDia(ctx, a))[0];
    referencia[L] = ref;
    const todos = intervalo(0, nG - 2);
    for (const s of [0, 1] as Sentido[]) {
      const porHora = new Map<number, number>();
      for (const v of ctx.horario.porLinha[ref][s].viagens) {
        const h = Math.floor(v.partida[0] / 3600);
        porHora.set(h, (porHora.get(h) ?? 0) + 1);
      }
      for (const [h, k] of [...porHora.entries()].sort((a, b) => a[0] - b[0])) {
        for (let j = 0; j < k; j++) viagemSintetica(L, s, h * 3600 + ((j + 0.5) * 3600) / k, s === 0 ? todos : [...todos].reverse());
      }
    }
  }

  const arestasNovas: number[] = [];
  for (const tr of trechosNovos) for (const s of [0, 1] as Sentido[]) {
    const e = g.chaveAresta.get(chave(tr.linha, tr.trecho, s));
    if (e !== undefined) arestasNovas.push(e);
  }
  const km = trechosNovos.reduce((s, t) => s + t.km, 0);
  // índices da rede atual no grafo da variante (o prolongamento pelo começo desloca a linha)
  const mapaNo = Int32Array.from(ctx.grafo.nos, (x) => no.get(`${x.linha}|${x.indice + (deslocamento[x.linha] ?? 0)}`) ?? -1);
  const mapaAresta = Int32Array.from(ctx.grafo.arestas, (e) => (e.linha ? (g.chaveAresta.get(chave(e.linha, e.trecho + (deslocamento[e.linha] ?? 0), e.sentido)) ?? -1) : -1));
  const ordemConexoes = Int32Array.from(conexoes.dep.map((_, k) => k)).sort((a, b) => Math.round(conexoes.dep[a] * 1000) - Math.round(conexoes.dep[b] * 1000) || a - b);
  const nomeLinha = (L: string) => parteDaLinha(L)?.nome ?? L;
  const hipoteses = [
    ...partes.map((p) => `${p.nome}: traçado ${p.status}${p.fonte ? ` (${p.fonte})` : ''}; ${p.kmTrechos ? 'km de via informado' : `km = linha reta × ${hipotese('fator_tracado_candidata', ctx.parametros, ctx.cenario)}`}`),
    `velocidade comercial dos trechos novos: ${hipotese('velocidade_comercial_candidata_kmh', ctx.parametros, ctx.cenario)} km/h`,
    ...linhasComNovo.map((L) =>
      ctx.rede.linhas[L]
        ? `${L}: o trecho novo falha com as taxas por km e as durações observadas da própria linha, e as viagens do horário seguem por ele`
        : `${nomeLinha(L)}: taxas por km ${herda[L] === 'media' ? 'da média da rede' : `da linha ${herda[L]}`}, durações ${herda[L] === 'media' ? 'das linhas atuais, com peso pela taxa' : `da linha ${herda[L]}`}; partidas por hora da linha ${referencia[L]}, espaçadas por igual`,
    ),
    'trens das linhas novas seguem o horário depois de cada interrupção, sem fila',
    op.causaComumCompartilhada ? 'causa comum: a linha nova para junto com as linhas em que encosta' : 'causa comum: a linha nova é independente das linhas atuais',
    op.politicas.retornoParcial ? 'retorno parcial ligado (pontas de viagem do horário e os terminais antigos)' : 'sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento',
  ];
  return {
    id: op.id ?? partes.map((p) => p.id).join('+'),
    nome: op.nome ?? partes.map((p) => p.nome).join(' + '),
    partes,
    g,
    deslocamento,
    herda,
    referencia,
    trechosNovos,
    arestasNovas,
    ccExtra,
    fontes,
    conexoes,
    km,
    retornoParcial: op.politicas.retornoParcial,
    politicas: { retiradaTrem: op.politicas.retiradaTrem, operacaoDegradada: op.politicas.operacaoDegradada },
    injetadas: op.injetadas ?? [],
    hipoteses,
    mapaNo,
    mapaAresta,
    ordemConexoes,
  };
}

/** Arestas que um bloqueio da rede atual tira de serviço no grafo com as linhas novas. */
function arestasNaVariante(v: VarianteRede, o: OrigemBloqueio): number[] {
  if (o.causa === 'CC') return [...(v.g.arestasDaLinha.get(o.linha) ?? []), ...(v.ccExtra[o.linha] ?? [])];
  return efeitoBloqueio(v.g, o.linha, (o.trecho ?? 0) + (v.deslocamento[o.linha] ?? 0), o.sentidos, v.retornoParcial);
}

function escolheDuracao(u: number, ds: FonteNova['duracoes']): Duracao {
  if (ds.length === 1) return ds[0].d;
  const total = ds.reduce((s, x) => s + x.peso, 0);
  let x = u * total;
  for (const d of ds) {
    if (x < d.peso) return d.d;
    x -= d.peso;
  }
  return ds[ds.length - 1].d;
}

/** Falhas das linhas novas num dia (semente da rodada), como bloqueios do grafo com as linhas novas. */
export function falhasDaLinhaNova(ctx: Contexto, v: VarianteRede, semente: number): { bloqueios: BloqueioOD[]; falhas: number } {
  const bloqueios: BloqueioOD[] = [];
  let falhas = 0;
  if (!ctx.cenario.semFalhas) {
    const { parametros: p, cenario: c } = ctx;
    const pRet = hipotese('p_retirada', p, c);
    const tRet = hipotese('tempo_retirada_min', p, c) * 60;
    const tAtiv = hipotese('tempo_ativacao_degradada_min', p, c) * 60;
    for (const f of v.fontes) {
      const instantes = sorteiaInstantes(criaFluxo(semente, 'linhas_novas', f.sub * 2), f.acum, f.forma, f.escala);
      if (!instantes.length) continue;
      const rd = criaFluxo(semente, 'linhas_novas', f.sub * 2 + 1);
      for (const t of instantes) {
        falhas++;
        const dur = sorteiaDuracao(rd, escolheDuracao(rd.uniforme(), f.duracoes));
        const uSentido = rd.uniforme(); // sempre sorteados: o fluxo não depende das políticas
        const uPolitica = rd.uniforme();
        let parada = dur;
        if (f.causa === 'MR' && v.politicas.retiradaTrem && dur > 0 && uPolitica < pRet) parada = Math.min(dur, tRet);
        if (f.causa === 'EF' && v.politicas.operacaoDegradada && dur > tAtiv) parada = tAtiv;
        if (parada <= 0) continue;
        const sentidos: Sentido[] = f.sentido !== null ? [f.sentido] : ctx.sentidosEF === 2 ? [0, 1] : [uSentido < 0.5 ? 0 : 1];
        bloqueios.push({ ini: t, fim: t + parada, arestas: efeitoBloqueio(v.g, f.linha, f.trecho, sentidos, v.retornoParcial), origem: { causa: f.causa, linha: f.linha, trecho: f.trecho, sentidos, nova: true } });
      }
    }
  }
  for (const inj of v.injetadas) {
    falhas++;
    if (inj.duracaoS > 0) bloqueios.push({ ini: inj.t, fim: inj.t + inj.duracaoS, arestas: efeitoBloqueio(v.g, inj.linha, inj.trecho, inj.sentidos, v.retornoParcial), origem: { causa: 'EF', linha: inj.linha, trecho: inj.trecho, sentidos: inj.sentidos, nova: true } });
  }
  return { bloqueios, falhas };
}

/** Bloqueios do dia no grafo com as linhas novas: os da rede atual, refeitos nesse grafo, e os das linhas novas. */
export function bloqueiosDaVariante(ctx: Contexto, v: VarianteRede, r: ResultadoDia): { todos: BloqueioOD[]; daNova: BloqueioOD[]; falhasNovas: number } {
  const todos: BloqueioOD[] = [];
  for (const b of r.bloqueiosOD ?? []) {
    if (!b.origem) throw new Error('bloqueio sem origem: o dia precisa vir do motor com bloqueiosOD');
    todos.push({ ini: b.ini, fim: b.fim, arestas: arestasNaVariante(v, b.origem), origem: b.origem });
  }
  const nova = falhasDaLinhaNova(ctx, v, r.semente);
  todos.push(...nova.bloqueios);
  return { todos, daNova: nova.bloqueios, falhasNovas: nova.falhas };
}

/** Por aresta, os intervalos [ini, fim) parados, em pares num vetor. */
export type Cortes = Map<number, number[]>;

export function cortesDe(bloqueios: readonly BloqueioOD[]): Cortes | null {
  if (!bloqueios.length) return null;
  const m: Cortes = new Map();
  for (const b of bloqueios) {
    for (const e of b.arestas) {
      let l = m.get(e);
      if (!l) m.set(e, (l = []));
      l.push(b.ini, b.fim);
    }
  }
  return m;
}

/** A conexão [d, c) na aresta cruza um intervalo parado: o trem não faz esse trecho. */
export function cortada(c: Cortes | null, aresta: number, d: number, a: number): boolean {
  const l = c?.get(aresta);
  if (!l) return false;
  for (let i = 0; i < l.length; i += 2) if (l[i] < a && l[i + 1] > d) return true;
  return false;
}
