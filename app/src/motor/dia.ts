// Camada diária (spec 007): um dia de operação, trem a trem, por eventos discretos.
//
// - As falhas (material rodante, equipamento fixo, causa comum) são sorteadas no início e entram numa
//   fila de prioridade; cada uma é tratada na ordem do relógio.
// - O movimento dos trens é a recursão max-plus de cada linha-sentido: um trem entra no trecho quando
//   chegou à estação, quando o horário permite, quando o trem da frente deixou o trecho (um trem por
//   trecho e sentido) e respeitado o intervalo mínimo. Um bloqueio impede a entrada e segura quem está
//   dentro do trecho. Depois de cada falha, a linha-sentido afetada é recalculada.
// - Tudo fica no registro: hora, linha, viagem, trecho, sentido, tipo e origem do sorteio.

import type { Contexto, Duracao } from './contexto';
import { reducaoCausaComum } from './contexto';
import { sorteiaOficina } from './frota';
import type { Grafo } from './grafo';
import type { BloqueioOD } from './grafo';
import { avaliaOD, efeitoBloqueio, segmentosBloqueados } from './grafo';
import { Heap } from './heap';
import { hipotese } from './hipoteses';
import type { Politicas } from './politicas';
import type { Fluxo, Rng } from './prng';
import { criaFluxo } from './prng';
import type { LinhaSentido, Viagem } from './rede';
import { estacaoGlobal, trechoFisico } from './rede';
import { sorteiaInstantes } from './taxas';
import type { Sentido } from './tipos';

/** Viagem afetada: atraso no terminal acima de 3 min, cancelada ou encerrada antes (spec 007). */
export const LIMIAR_VIAGEM_AFETADA_S = 180;

export type CausaBloqueio = 'MR' | 'EF' | 'CC';

export type TipoEvento =
  | 'FALHA_TREM'
  | 'FALHA_EF'
  | 'CAUSA_COMUM'
  | 'FIM_INTERRUPCAO'
  | 'RETIRADA'
  | 'DEGRADADA_INICIO'
  | 'DEGRADADA_FIM'
  | 'CANCELAMENTO'
  | 'INJETA_RESERVA'
  | 'SEM_TREM'
  | 'ATRASO';

export interface EventoRegistro {
  t: number; // segundos do dia de operação
  linha: string;
  trem: string | null; // viagem do horário
  trecho: number | null; // trecho físico (entre as estações g e g + 1)
  sentido: Sentido | null;
  tipo: TipoEvento;
  fluxo: Fluxo | 'horario' | 'injetada';
  sorteio: number | null; // posição do sorteio dentro do fluxo
  duracaoS: number | null;
  detalhe: string;
}

export interface FalhaInjetada {
  tipo: CausaBloqueio;
  t: number;
  duracaoS: number;
  linha?: string;
  viagem?: string; // MR: id da viagem; sem ele, sorteia entre as que circulam
  trecho?: number; // EF: trecho físico
  sentidos?: Sentido[]; // EF
  par?: string; // CC: "verde-laranja"
}

export interface Trajetoria {
  viagem: Viagem;
  partida: Float64Array; // simulada, por parada
  chegada: Float64Array;
  ultima: number; // última parada (índice local)
  cancelada: boolean;
}

export interface MetricasLinha {
  minutosServico: number;
  minutosInterrupcao: number;
  minutosPorCausa: Record<CausaBloqueio, number>;
  disponibilidade: number;
  trensHoraPerdidos: number;
  viagensAfetadas: number;
  viagensCanceladas: number;
  viagensRetiradas: number;
  falhas: Record<CausaBloqueio, number>;
  trensNaOficina: number;
  frotaCompleta: boolean;
}

export interface ResultadoDia {
  semente: number;
  porLinha: Record<string, MetricasLinha>;
  rede: {
    minutosInterrupcao: number;
    trensHoraPerdidos: number;
    dispOD: number; // fração da oferta com caminho, média no dia
    extraMin: number; // minutos extras de viagem, média ponderada pela oferta
    minutosParInterrompido: number; // (1 - dispOD) × minutos da janela
  };
  registro: EventoRegistro[];
  hash: string;
  trajetorias?: Record<string, Trajetoria[]>; // chave linha:sentido
  /** Arestas do grafo sem serviço e quando (com `opcoes.bloqueiosOD`; spec 015). */
  bloqueiosOD?: BloqueioOD[];
}

export interface OpcoesDia {
  injetadas?: FalhaInjetada[];
  registrar?: boolean;
  trajetorias?: boolean;
  bloqueiosOD?: boolean;
  /** false: não calcula a disponibilidade origem-destino da rede (a viagem da spec 015 não usa; fica NaN). */
  odDaRede?: boolean;
}

interface Bloqueio {
  ini: number;
  fim: number;
  causa: CausaBloqueio;
}

interface Lento {
  ini: number;
  fim: number;
  fator: number;
}

export interface EstadoSentido {
  ls: LinhaSentido;
  bloqueios: Bloqueio[][]; // por trecho local, em ordem de início
  lentos: Lento[][];
  corte: Int32Array; // última parada de cada viagem (na ordem de circulação)
  cancelada: Uint8Array;
  traj: Trajetoria[] | null;
  mexido: boolean;
}

type Pendente = { tipo: 'MR' | 'EF'; li: number; injetada?: FalhaInjetada } | { tipo: 'CC'; ci: number; injetada?: FalhaInjetada };

/** Simula um dia. Função pura: mesmo contexto, políticas e semente dão o mesmo resultado. */
export function simulaDia(ctx: Contexto, politicas: Politicas, semente: number, opcoes: OpcoesDia = {}): ResultadoDia {
  const { rede, horario, parametros, cenario, grafo } = ctx;
  const registrar = opcoes.registrar ?? true;
  const registro: EventoRegistro[] = [];
  const anota = (e: EventoRegistro) => {
    if (registrar) registro.push(e);
  };
  const fluxos = new Map<string, Rng>();
  const fluxo = (nome: Fluxo, sub: number): Rng => {
    const k = `${nome}:${sub}`;
    let r = fluxos.get(k);
    if (!r) {
      r = criaFluxo(semente, nome, sub);
      fluxos.set(k, r);
    }
    return r;
  };

  // Estado por linha-sentido
  const estados: Record<string, [EstadoSentido, EstadoSentido]> = {};
  for (const linha of rede.ids) {
    const [l0, l1] = horario.porLinha[linha];
    estados[linha] = [novoEstado(l0), novoEstado(l1)];
  }
  const bloqueiosLinha: Record<string, Bloqueio[]> = {};
  const contagem: Record<string, Record<CausaBloqueio, number>> = {};
  for (const linha of rede.ids) {
    bloqueiosLinha[linha] = [];
    contagem[linha] = { MR: 0, EF: 0, CC: 0 };
  }
  const bloqueiosOD: BloqueioOD[] = [];

  // ---------- Frota no início do dia (reserva fria k-de-n) ----------
  const oficinaDia: Record<string, number> = {};
  const frotaCompleta: Record<string, boolean> = {};
  rede.ids.forEach((linha, li) => {
    const of = ctx.oficina[linha];
    const fr = ctx.frota[linha];
    const rng = fluxo('frota', li);
    if (!of || !fr || cenario.semFalhas) {
      oficinaDia[linha] = 0;
      frotaCompleta[linha] = true;
      return;
    }
    const s = politicas.reservaFria ? of.reservas : 0;
    const sorteio = rng.sorteios;
    const i = sorteiaOficina(rng, politicas.reservaFria ? of.comReserva : of.semReserva);
    oficinaDia[linha] = i;
    const deficit = Math.max(0, i - s);
    frotaCompleta[linha] = deficit === 0;
    const t0 = horario.inicioServico[linha];
    if (i > 0 && s > 0)
      anota({ t: t0, linha, trem: null, trecho: null, sentido: null, tipo: 'INJETA_RESERVA', fluxo: 'frota', sorteio, duracaoS: null, detalhe: `${Math.min(i, s)} reserva(s) cobrem ${i} trem(ns) na oficina` });
    if (deficit > 0) cancelaPorFalta(linha, fr.n, deficit, sorteio);
  });

  function cancelaPorFalta(linha: string, n: number, deficit: number, sorteio: number): void {
    const grade = horario.trensPorMinuto[linha];
    let pico = 0;
    for (const x of grade) pico = Math.max(pico, x);
    const capacidade = (pico * (n - deficit)) / n;
    for (const es of estados[linha]) {
      let acc = 0;
      es.ls.viagens.forEach((v, k) => {
        const m = Math.min(grade.length - 1, Math.floor(v.partida[0] / 60));
        const prog = grade[m];
        if (prog <= capacidade) return;
        acc += (prog - capacidade) / prog;
        if (acc >= 1) {
          acc -= 1;
          es.cancelada[k] = 1;
          es.mexido = true;
          es.traj = null;
          anota({ t: v.partida[0], linha, trem: v.id, trecho: null, sentido: es.ls.sentido, tipo: 'CANCELAMENTO', fluxo: 'frota', sorteio, duracaoS: null, detalhe: `falta de ${deficit} trem(ns) de ${n}` });
        }
      });
    }
  }

  // ---------- Sorteio das falhas do dia ----------
  const fila = new Heap<Pendente>();
  if (!cenario.semFalhas) {
    for (const f of ctx.fontes) {
      const rng = fluxo(f.causa === 'MR' ? 'falhas_mr' : 'falhas_ef', f.li);
      for (const t of sorteiaInstantes(rng, f.acum, f.renovacao.forma, f.renovacao.escalaNormalizada)) fila.insere(t, { tipo: f.causa, li: f.li });
    }
    for (const c of ctx.causaComum) {
      const rng = fluxo('causa_comum', c.ci);
      for (const t of sorteiaInstantes(rng, c.acum, 1, 1)) fila.insere(t, { tipo: 'CC', ci: c.ci });
    }
  }
  for (const inj of opcoes.injetadas ?? []) {
    if (inj.tipo === 'CC') {
      const ci = ctx.causaComum.findIndex((c) => c.par === inj.par);
      fila.insere(inj.t, { tipo: 'CC', ci: ci >= 0 ? ctx.causaComum[ci].ci : -1, injetada: inj });
    } else fila.insere(inj.t, { tipo: inj.tipo, li: rede.ids.indexOf(inj.linha ?? ''), injetada: inj });
  }

  const hMin = ctx.intervaloMinimoS;
  const retirar = politicas.retiradaTrem;
  const pRetirada = hipotese('p_retirada', parametros, cenario);
  const tRetirada = hipotese('tempo_retirada_min', parametros, cenario) * 60;
  const tAtivacao = hipotese('tempo_ativacao_degradada_min', parametros, cenario) * 60;
  const fatorLento = hipotese('fator_velocidade_degradada', parametros, cenario);
  const reducaoCC = reducaoCausaComum(ctx, politicas);

  const SEM_DURACAO: Duracao = { pZero: 1, mu: 0, sigma: 1 };
  function duracaoDaFonte(li: number, causa: 'MR' | 'EF'): Duracao {
    return ctx.fontes.find((f) => f.li === li && f.causa === causa)?.duracao ?? SEM_DURACAO;
  }

  function bloqueia(linha: string, s: Sentido, local: number, b: Bloqueio): void {
    const es = estados[linha][s];
    const lista = es.bloqueios[local];
    lista.push(b);
    lista.sort((x, y) => x.ini - y.ini || x.fim - y.fim);
    es.traj = null;
    es.mexido = true;
    bloqueiosLinha[linha].push(b);
  }

  function trajetorias(es: EstadoSentido): Trajetoria[] {
    if (!es.traj) es.traj = calculaTrajetorias(es, hMin);
    return es.traj;
  }

  // ---------- Laço de eventos ----------
  for (let item = fila.retira(); item; item = fila.retira()) {
    const { t, valor: ev } = item;
    if (ev.tipo === 'CC') {
      const inj = ev.injetada;
      const fonte = ctx.causaComum.find((c) => c.ci === ev.ci);
      const linhas = fonte?.linhas ?? inj?.par?.split('-');
      if (!linhas || !linhas.every((l) => rede.linhas[l])) continue;
      let dur: number;
      let fl: EventoRegistro['fluxo'] = 'injetada';
      let sorteio: number | null = null;
      if (inj) dur = inj.duracaoS;
      else {
        const rd = fluxo('duracoes', 100 + ev.ci);
        sorteio = rd.sorteios;
        dur = sorteiaDuracao(rd, fonte?.duracao ?? SEM_DURACAO);
        const u = fluxo('politicas', 100 + ev.ci).uniforme(); // sempre sorteado
        fl = 'causa_comum';
        if (u < reducaoCC) continue; // evento evitado pela alimentação ou controle redundante
      }
      const par = linhas.join('-');
      for (const linha of linhas) {
        contagem[linha].CC++;
        anota({ t, linha, trem: null, trecho: null, sentido: null, tipo: 'CAUSA_COMUM', fluxo: fl, sorteio, duracaoS: dur, detalhe: `par ${par}` });
        if (dur <= 0) continue;
        const n = rede.linhas[linha].n;
        for (const s of [0, 1] as Sentido[]) for (let j = 0; j < n - 1; j++) bloqueia(linha, s, j, { ini: t, fim: t + dur, causa: 'CC' });
        bloqueiosOD.push({ ini: t, fim: t + dur, arestas: grafo.arestasDaLinha.get(linha) ?? [], origem: { causa: 'CC', linha, trecho: null, sentidos: [0, 1] } });
        anota({ t: t + dur, linha, trem: null, trecho: null, sentido: null, tipo: 'FIM_INTERRUPCAO', fluxo: fl, sorteio, duracaoS: dur, detalhe: `causa comum ${par}` });
      }
      continue;
    }

    const linha = rede.ids[ev.li];
    if (!linha) continue;
    const n = rede.linhas[linha].n;
    const inj = ev.injetada;

    if (ev.tipo === 'EF') {
      contagem[linha].EF++;
      let dur: number;
      let g: number;
      let sentidos: Sentido[];
      let fl: EventoRegistro['fluxo'] = 'injetada';
      let sorteio: number | null = null;
      let codigo = '';
      if (inj) {
        dur = inj.duracaoS;
        g = Math.min(Math.max(inj.trecho ?? 0, 0), n - 2);
        sentidos = inj.sentidos ?? (ctx.sentidosEF === 2 ? [0, 1] : [0]);
      } else {
        const rd = fluxo('duracoes', ev.li * 2 + 1);
        sorteio = rd.sorteios;
        dur = sorteiaDuracao(rd, duracaoDaFonte(ev.li, 'EF'));
        const re = fluxo('escolha', 50 + ev.li);
        const [km, cod] = sorteiaLocal(ctx, linha, re.uniforme());
        const uSentido = re.uniforme(); // sempre sorteado
        codigo = cod;
        g = trechoDoKm(ctx, linha, km);
        sentidos = ctx.sentidosEF === 2 ? [0, 1] : [uSentido < 0.5 ? 0 : 1];
        fl = 'falhas_ef';
      }
      const degradada = politicas.operacaoDegradada && dur > tAtivacao;
      const parada = degradada ? tAtivacao : dur;
      anota({ t, linha, trem: null, trecho: g, sentido: sentidos.length === 1 ? sentidos[0] : null, tipo: 'FALHA_EF', fluxo: fl, sorteio, duracaoS: dur, detalhe: codigo ? `local ${codigo}` : `${sentidos.length} sentido(s)` });
      if (parada > 0) {
        for (const s of sentidos) bloqueia(linha, s, trechoFisico(n, s, g), { ini: t, fim: t + parada, causa: 'EF' });
        bloqueiosOD.push({ ini: t, fim: t + parada, arestas: efeitoBloqueio(grafo, linha, g, sentidos, politicas.retornoParcial), origem: { causa: 'EF', linha, trecho: g, sentidos } });
        anota({ t: t + parada, linha, trem: null, trecho: g, sentido: sentidos.length === 1 ? sentidos[0] : null, tipo: 'FIM_INTERRUPCAO', fluxo: fl, sorteio, duracaoS: parada, detalhe: 'equipamento fixo' });
      }
      if (degradada) {
        for (const s of sentidos) {
          const es = estados[linha][s];
          es.lentos[trechoFisico(n, s, g)].push({ ini: t + tAtivacao, fim: t + dur, fator: fatorLento });
          es.traj = null;
          es.mexido = true;
        }
        anota({ t: t + tAtivacao, linha, trem: null, trecho: g, sentido: null, tipo: 'DEGRADADA_INICIO', fluxo: fl, sorteio, duracaoS: dur - tAtivacao, detalhe: `percurso × ${fatorLento}` });
        anota({ t: t + dur, linha, trem: null, trecho: g, sentido: null, tipo: 'DEGRADADA_FIM', fluxo: fl, sorteio, duracaoS: null, detalhe: '' });
      }
      continue;
    }

    // ---------- Falha de material rodante ----------
    contagem[linha].MR++;
    let dur: number;
    let fl: EventoRegistro['fluxo'] = 'injetada';
    let sorteio: number | null = null;
    let uEscolha = 0;
    let uRetirada = 1;
    if (inj) dur = inj.duracaoS;
    else {
      const rd = fluxo('duracoes', ev.li * 2);
      sorteio = rd.sorteios;
      dur = sorteiaDuracao(rd, duracaoDaFonte(ev.li, 'MR'));
      uEscolha = fluxo('escolha', ev.li).uniforme();
      uRetirada = fluxo('politicas', ev.li).uniforme();
      fl = 'falhas_mr';
    }
    // trens em circulação agora, na simulação
    const circulando: { s: Sentido; k: number; tr: Trajetoria }[] = [];
    for (const s of [0, 1] as Sentido[]) {
      const es = estados[linha][s];
      trajetorias(es).forEach((tr, k) => {
        if (tr.cancelada) return;
        const fimViagem = tr.chegada[tr.ultima - tr.viagem.inicio];
        if (tr.chegada[0] <= t && t < fimViagem) circulando.push({ s, k, tr });
      });
    }
    let alvo = circulando[Math.min(circulando.length - 1, Math.floor(uEscolha * circulando.length))];
    if (inj?.viagem) alvo = circulando.find((c) => c.tr.viagem.id === inj.viagem) ?? alvo;
    if (!alvo) {
      anota({ t, linha, trem: null, trecho: null, sentido: null, tipo: 'SEM_TREM', fluxo: fl, sorteio, duracaoS: dur, detalhe: 'nenhum trem em circulação' });
      continue;
    }
    const { s, k, tr } = alvo;
    const es = estados[linha][s];
    const v = tr.viagem;
    // posição: no trecho local j (entre as paradas j e j + 1) ou parado na estação j
    let local = v.inicio;
    let naEstacao = false;
    for (let p = 0; p + v.inicio <= tr.ultima; p++) {
      if (tr.chegada[p] <= t && t < tr.partida[p]) {
        local = v.inicio + p;
        naEstacao = true;
        break;
      }
      if (p + v.inicio < tr.ultima && tr.partida[p] <= t && t < tr.chegada[p + 1]) {
        local = v.inicio + p;
        break;
      }
    }
    const trechoLocal = Math.min(local, n - 2);
    const g = trechoFisico(n, s, trechoLocal);
    const retira = retirar && dur > 0 && uRetirada < pRetirada;
    const parada = retira ? Math.min(dur, tRetirada) : dur;
    anota({ t, linha, trem: v.id, trecho: g, sentido: s, tipo: 'FALHA_TREM', fluxo: fl, sorteio, duracaoS: dur, detalhe: naEstacao ? `parado na estação ${nomeLocal(ctx, linha, s, local)}` : `entre ${nomeLocal(ctx, linha, s, local)} e ${nomeLocal(ctx, linha, s, local + 1)}` });
    if (parada > 0) {
      bloqueia(linha, s, trechoLocal, { ini: t, fim: t + parada, causa: 'MR' });
      bloqueiosOD.push({ ini: t, fim: t + parada, arestas: efeitoBloqueio(grafo, linha, g, [s], politicas.retornoParcial), origem: { causa: 'MR', linha, trecho: g, sentidos: [s] } });
      anota({ t: t + parada, linha, trem: v.id, trecho: g, sentido: s, tipo: 'FIM_INTERRUPCAO', fluxo: fl, sorteio, duracaoS: parada, detalhe: 'material rodante' });
    }
    if (retira) {
      const corte = naEstacao ? local : Math.min(local + 1, v.fim);
      if (corte < es.corte[k]) {
        es.corte[k] = corte;
        es.traj = null;
        es.mexido = true;
      }
      anota({ t: t + parada, linha, trem: v.id, trecho: g, sentido: s, tipo: 'RETIRADA', fluxo: 'politicas', sorteio: null, duracaoS: null, detalhe: `encerra a viagem em ${nomeLocal(ctx, linha, s, corte)}` });
    }
  }

  // ---------- Métricas ----------
  const porLinha: Record<string, MetricasLinha> = {};
  const trajSaida: Record<string, Trajetoria[]> = {};
  let thpRede = 0;
  let minRede = 0;
  for (const linha of rede.ids) {
    const ini = horario.inicioServico[linha];
    const fim = horario.fimServico[linha];
    const minutosServico = Math.max(0, fim - ini) / 60;
    const bl = bloqueiosLinha[linha];
    const minutosInterrupcao = uniao(bl, ini, fim) / 60;
    const minutosPorCausa = {
      MR: uniao(bl.filter((b) => b.causa === 'MR'), ini, fim) / 60,
      EF: uniao(bl.filter((b) => b.causa === 'EF'), ini, fim) / 60,
      CC: uniao(bl.filter((b) => b.causa === 'CC'), ini, fim) / 60,
    };
    let thp = 0;
    let afetadas = 0;
    let canceladas = 0;
    let retiradas = 0;
    for (const es of estados[linha]) {
      if (!es.mexido && !opcoes.trajetorias) continue;
      const tj = trajetorias(es);
      if (opcoes.trajetorias) trajSaida[`${linha}:${es.ls.sentido}`] = tj;
      for (const tr of tj) {
        const v = tr.viagem;
        const ultimaProg = v.chegada[v.chegada.length - 1];
        if (tr.cancelada) {
          thp += (ultimaProg - v.partida[0]) / 3600;
          afetadas++;
          canceladas++;
          continue;
        }
        const p = tr.ultima - v.inicio;
        const atraso = Math.max(0, tr.chegada[p] - v.chegada[p]);
        if (tr.ultima < v.fim) {
          thp += (atraso + ultimaProg - v.chegada[p]) / 3600;
          afetadas++;
          retiradas++;
          continue;
        }
        thp += atraso / 3600;
        if (atraso > LIMIAR_VIAGEM_AFETADA_S) {
          afetadas++;
          anota({ t: tr.chegada[p], linha, trem: v.id, trecho: null, sentido: v.sentido, tipo: 'ATRASO', fluxo: 'horario', sorteio: null, duracaoS: atraso, detalhe: 'atraso no terminal' });
        }
      }
    }
    thpRede += thp;
    minRede += minutosInterrupcao;
    porLinha[linha] = {
      minutosServico,
      minutosInterrupcao,
      minutosPorCausa,
      disponibilidade: minutosServico > 0 ? 1 - minutosInterrupcao / minutosServico : 1,
      trensHoraPerdidos: thp,
      viagensAfetadas: afetadas,
      viagensCanceladas: canceladas,
      viagensRetiradas: retiradas,
      falhas: contagem[linha],
      trensNaOficina: oficinaDia[linha],
      frotaCompleta: frotaCompleta[linha],
    };
  }
  const od = opcoes.odDaRede === false ? { dispOD: NaN, extraMin: NaN, minutosParInterrompido: NaN } : origemDestino(grafo, bloqueiosOD, horario.janelaRede, politicas.rotaAlternativa);
  if (registrar) registro.sort((a, b) => a.t - b.t);
  const resultado: ResultadoDia = {
    semente,
    porLinha,
    rede: { minutosInterrupcao: minRede, trensHoraPerdidos: thpRede, ...od },
    registro,
    hash: hashRegistro(registro),
  };
  if (opcoes.trajetorias) resultado.trajetorias = trajSaida;
  if (opcoes.bloqueiosOD) resultado.bloqueiosOD = bloqueiosOD;
  return resultado;
}

/** Duração da interrupção (s): zero com a massa em zero; senão da amostra observada (ou da lognormal). */
export function sorteiaDuracao(rng: Rng, d: Duracao): number {
  const u = rng.uniforme();
  const z = rng.normal(); // sempre sorteado, para manter o fluxo alinhado entre políticas
  const v = rng.uniforme(); // idem: escolhe a duração na amostra observada
  if (u < d.pZero) return 0;
  if (d.amostra) return d.amostra[Math.min(d.amostra.length - 1, Math.floor(v * d.amostra.length))] * 60;
  return Math.exp(d.mu + d.sigma * z) * 60;
}

export function novoEstado(ls: LinhaSentido): EstadoSentido {
  const trechos = Math.max(ls.n - 1, 0);
  return {
    ls,
    bloqueios: Array.from({ length: trechos }, (): Bloqueio[] => []),
    lentos: Array.from({ length: trechos }, (): Lento[] => []),
    corte: Int32Array.from(ls.viagens.map((v) => v.fim)),
    cancelada: new Uint8Array(ls.viagens.length),
    traj: null,
    mexido: false,
  };
}

/** Recursão max-plus de uma linha-sentido com bloqueios, marcha lenta, cortes e cancelamentos. */
export function calculaTrajetorias(es: EstadoSentido, intervaloMinimoS: number): Trajetoria[] {
  const { ls } = es;
  const trechos = Math.max(ls.n - 1, 0);
  const ultimaEntrada = new Float64Array(trechos).fill(-Infinity);
  const liberaBloco = new Float64Array(trechos).fill(-Infinity);
  const saida: Trajetoria[] = [];
  ls.viagens.forEach((v, k) => {
    const len = v.fim - v.inicio + 1;
    const partida = new Float64Array(len).fill(NaN);
    const chegada = new Float64Array(len).fill(NaN);
    if (es.cancelada[k]) {
      saida.push({ viagem: v, partida, chegada, ultima: v.fim, cancelada: true });
      return;
    }
    const ultima = es.corte[k];
    let a = v.chegada[0];
    chegada[0] = a;
    for (let s = v.inicio; s < ultima; s++) {
      const p = s - v.inicio;
      const parada = Math.max(0, v.partida[p] - v.chegada[p]);
      let d = Math.max(v.partida[p], a + parada, ultimaEntrada[s] + intervaloMinimoS, liberaBloco[s]);
      d = foraDeBloqueio(es.bloqueios[s], d);
      const r = (v.chegada[p + 1] - v.partida[p]) * fatorLento(es.lentos[s], d);
      const c = emTransito(es.bloqueios[s], d, r);
      partida[p] = d;
      chegada[p + 1] = c;
      ultimaEntrada[s] = d;
      if (s > v.inicio) liberaBloco[s - 1] = d;
      a = c;
    }
    partida[ultima - v.inicio] = a;
    if (ultima > v.inicio) liberaBloco[ultima - 1] = a;
    saida.push({ viagem: v, partida, chegada, ultima, cancelada: false });
  });
  return saida;
}

function foraDeBloqueio(lista: Bloqueio[], d: number): number {
  for (const b of lista) if (b.ini <= d && d < b.fim) d = b.fim;
  return d;
}

/** Chegada ao fim do trecho, parando enquanto durar cada bloqueio que começa durante o percurso. */
function emTransito(lista: Bloqueio[], d: number, percurso: number): number {
  let t = d;
  let resta = percurso;
  for (const b of lista) {
    if (b.fim <= t) continue;
    if (b.ini >= t + resta) break;
    if (b.ini > t) {
      resta -= b.ini - t;
      t = b.ini;
    }
    t = Math.max(t, b.fim);
  }
  return t + resta;
}

function fatorLento(lista: Lento[], d: number): number {
  let f = 1;
  for (const l of lista) if (l.ini <= d && d < l.fim) f = Math.max(f, l.fator);
  return f;
}

/** Tamanho da união dos intervalos, recortada em [ini, fim). */
export function uniao(lista: { ini: number; fim: number }[], ini: number, fim: number): number {
  const xs = lista
    .map((b) => [Math.max(b.ini, ini), Math.min(b.fim, fim)] as [number, number])
    .filter(([a, b]) => b > a)
    .sort((x, y) => x[0] - y[0]);
  let total = 0;
  let ca = -Infinity;
  let cb = -Infinity;
  for (const [a, b] of xs) {
    if (a > cb) {
      if (cb > ca) total += cb - ca;
      ca = a;
      cb = b;
    } else cb = Math.max(cb, b);
  }
  if (cb > ca) total += cb - ca;
  return total;
}

/** Disponibilidade origem-destino no dia: varredura no tempo dos conjuntos de arestas bloqueadas. */
function origemDestino(grafo: Grafo, bloqueios: BloqueioOD[], janela: [number, number], rotaAlternativa: boolean) {
  const [ini, fim] = janela;
  const T = Math.max(fim - ini, 1);
  if (bloqueios.length === 0) return { dispOD: 1, extraMin: 0, minutosParInterrompido: 0 };
  let fora = 0;
  let extra = 0;
  for (const { a, b, arestas } of segmentosBloqueados(bloqueios, janela)) {
    const r = avaliaOD(grafo, arestas, rotaAlternativa);
    fora += r.indisponivel * (b - a);
    extra += r.extraMin * (b - a);
  }
  return { dispOD: 1 - fora / T, extraMin: extra / T, minutosParInterrompido: fora / 60 };
}

/** Sorteia o local da falha de equipamento fixo: [km, código]. */
function sorteiaLocal(ctx: Contexto, linha: string, u: number): [number, string] {
  const loc = ctx.locais[linha];
  const comPosicao = loc.pesosAcum.length ? loc.pesosAcum[loc.pesosAcum.length - 1] : 0;
  const total = comPosicao + loc.pesoSemPosicao;
  const x = u * total;
  if (x < comPosicao) {
    let lo = 0;
    while (loc.pesosAcum[lo] <= x) lo++;
    return [loc.kms[lo], loc.codigos[lo]];
  }
  const est = ctx.rede.linhas[linha].estacoes;
  const km0 = est[0].km;
  const km1 = est[est.length - 1].km;
  return [km0 + ((x - comPosicao) / Math.max(loc.pesoSemPosicao, 1e-12)) * (km1 - km0), 'sem posição'];
}

/** Trecho físico que contém o km (uma estação pertence ao trecho que começa nela; a última, ao último). */
function trechoDoKm(ctx: Contexto, linha: string, km: number): number {
  const est = ctx.rede.linhas[linha].estacoes;
  let g = 0;
  for (let i = 0; i < est.length - 1; i++) if (est[i].km <= km) g = i;
  return Math.min(g, est.length - 2);
}

function nomeLocal(ctx: Contexto, linha: string, s: Sentido, local: number): string {
  const l = ctx.rede.linhas[linha];
  const e = l.estacoes[estacaoGlobal(l.n, s, Math.min(Math.max(local, 0), l.n - 1))];
  return e ? e.nome : '?';
}

/** FNV-1a de 32 bits sobre o registro serializado de forma canônica. */
export function hashRegistro(registro: EventoRegistro[]): string {
  let h = 0x811c9dc5;
  const mistura = (s: string) => {
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 0x01000193);
    }
  };
  for (const e of registro) {
    mistura(
      `${e.t.toFixed(3)}|${e.linha}|${e.trem ?? ''}|${e.trecho ?? ''}|${e.sentido ?? ''}|${e.tipo}|${e.fluxo}|${e.sorteio ?? ''}|${e.duracaoS === null ? '' : e.duracaoS.toFixed(3)}|${e.detalhe}\n`,
    );
  }
  return (h >>> 0).toString(16).padStart(8, '0');
}

/** Trens em viagem num instante, a partir das trajetórias simuladas. */
export function trensEmViagem(trajetorias: Trajetoria[], t: number): number {
  let n = 0;
  for (const tr of trajetorias) {
    if (tr.cancelada) continue;
    const fim = tr.chegada[tr.ultima - tr.viagem.inicio];
    if (tr.partida[0] <= t && t < fim) n++;
  }
  return n;
}
