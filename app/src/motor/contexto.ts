// Preparação de um cenário: tudo o que não muda entre rodadas (taxas acumuladas, distribuições,
// locais de falha, frota, grafo origem-destino). Uma rodada só sorteia em cima disto.

import { estacionariaFrota } from './frota';
import type { Grafo } from './grafo';
import { linhasDoHorario, montaGrafo } from './grafo';
import { hipotese } from './hipoteses';
import type { Politicas } from './politicas';
import type { Fluxo } from './prng';
import { gamaFuncao, hash30 } from './prng';
import type { HorarioDia, Rede } from './rede';
import type { Renovacao01 } from './taxas';
import { renovacaoDaFonte, renovacaoDe, taxaAcumulada, taxaAcumuladaConstante, taxaAcumuladaFonte } from './taxas';
import type { Causa, Cenario, LocalEF, Lognormal, Parametros } from './tipos';
import { CAUSAS } from './tipos';

export interface Duracao {
  pZero: number;
  mu: number; // log(minutos)
  sigma: number;
  /** Durações positivas observadas (minutos). Quando existe, substitui a lognormal no sorteio (decisão de 2026-10-21, spec 009). */
  amostra?: Float64Array;
}

/**
 * Uma fonte de falha de uma linha (spec 019). A família (`causa`) decide o efeito: MR para o trem no sentido, EF
 * bloqueia um trecho. Cada fonte tem os seus sub-fluxos de sorteio; no contrato v1, as duas fontes de cada linha
 * (MR e EF) usam os sub-fluxos de antes da revisão, então os números não mudam.
 */
export interface FonteFalha {
  /** Identificador da fonte na linha (contrato v1: a própria família, "MR" ou "EF"). */
  id: string;
  /** Posição em ctx.fontes. */
  fi: number;
  linha: string;
  li: number; // índice da linha
  causa: Causa; // família
  acum: Float64Array;
  renovacao: Renovacao01;
  duracao: Duracao;
  fluxoInstantes: Fluxo;
  subInstantes: number;
  subDuracao: number;
  subEscolha: number;
  subPolitica: number;
  /** Locais da fonte; sem eles, os da linha (equipamento fixo). */
  locais?: LocaisLinha;
}

/** Sub-fluxos de sorteio do contrato v1, idênticos aos do motor antes da revisão de 2026-11. */
function subFluxosV1(li: number, causa: Causa): Pick<FonteFalha, 'fluxoInstantes' | 'subInstantes' | 'subDuracao' | 'subEscolha' | 'subPolitica'> {
  return causa === 'MR'
    ? { fluxoInstantes: 'falhas_mr', subInstantes: li, subDuracao: li * 2, subEscolha: li, subPolitica: li }
    : { fluxoInstantes: 'falhas_ef', subInstantes: li, subDuracao: li * 2 + 1, subEscolha: 50 + li, subPolitica: li };
}

export interface FonteCausaComum {
  par: string;
  ci: number;
  linhas: string[]; // 2 a 4 linhas paradas juntas pelo mesmo evento
  acum: Float64Array;
  duracao: Duracao;
}

export interface LocaisLinha {
  kms: number[];
  pesosAcum: number[]; // soma acumulada dos pesos dos locais com posição
  pesoSemPosicao: number; // falhas sem posição: sorteadas uniformes ao longo da linha
  codigos: string[];
}

export interface Contexto {
  rede: Rede;
  parametros: Parametros;
  cenario: Cenario;
  horario: HorarioDia;
  grafo: Grafo;
  intervaloMinimoS: number;
  sentidosEF: 1 | 2;
  fontes: FonteFalha[];
  causaComum: FonteCausaComum[];
  locais: Record<string, LocaisLinha>;
  frota: Record<string, { n: number; lambdaDia: number }>;
  /** Distribuição estacionária de trens na oficina, sem e com reserva. */
  oficina: Record<string, { semReserva: Float64Array; comReserva: Float64Array; reservas: number }>;
}

export function duracaoDe(l: Lognormal | undefined): Duracao {
  if (!l) return { pZero: 1, mu: 0, sigma: 1 };
  const a = l.amostra_positivos?.minutos;
  return { pZero: l.p_zero.valor, mu: l.mu_log.valor, sigma: l.sigma_log.valor, amostra: a && a.length ? Float64Array.from(a) : undefined };
}

/** Duração média em minutos (com a massa em zero). */
export function duracaoMediaMin(d: Duracao): number {
  if (d.amostra) {
    let s = 0;
    for (const x of d.amostra) s += x;
    return (1 - d.pZero) * (s / d.amostra.length);
  }
  return (1 - d.pZero) * Math.exp(d.mu + (d.sigma * d.sigma) / 2);
}

/** Locais de falha de equipamento fixo (km com peso; o resto uniforme ao longo da linha). */
function montaLocais(lista0: LocalEF[] | undefined, semPosicao: number): LocaisLinha {
  const lista = (lista0 ?? []).filter((x) => Number.isFinite(x.km) && x.peso > 0);
  const pesosAcum: number[] = [];
  let acc = 0;
  for (const x of lista) {
    acc += x.peso;
    pesosAcum.push(acc);
  }
  // sem nenhum local com posição, todas as falhas ficam uniformes ao longo da linha
  return { kms: lista.map((x) => x.km), pesosAcum, pesoSemPosicao: lista.length ? semPosicao : 1, codigos: lista.map((x) => x.codigo) };
}

/** Sub-fluxo de uma fonte do contrato v2: depende só do nome da linha e da fonte (acrescentar uma fonte não mexe nas outras). */
export function subFluxoDaFonte(linha: string, id: string): number {
  return 1000 + (hash30(`${linha}|${id}`) % 1_000_000_000);
}

export function preparaContexto(rede: Rede, parametros: Parametros, cenario: Cenario, grafo?: Grafo): Contexto {
  const horario = rede.horarios[cenario.tipoDia];
  const fontes: FonteFalha[] = [];
  const v2 = parametros.versao >= 2 && (parametros.fontes?.length ?? 0) > 0;
  rede.ids.forEach((linha, li) => {
    if (v2) {
      // contrato v2 (spec 019): as fontes do arquivo, na ordem do arquivo, em cada linha em que existem
      for (const fp of parametros.fontes ?? []) {
        const fl = fp.linhas[linha];
        if (!fl) continue;
        if (!fl.ttr) throw new Error(`parametros.json sem duração da fonte ${fp.id} na linha ${linha}`);
        const sub = subFluxoDaFonte(linha, fp.id);
        fontes.push({
          id: fp.id,
          fi: fontes.length,
          linha,
          li,
          causa: fp.familia,
          acum: taxaAcumuladaFonte(fp, horario, cenario, linha),
          renovacao: renovacaoDaFonte(fp, linha),
          duracao: duracaoDe(fl.ttr),
          fluxoInstantes: fp.familia === 'MR' ? 'falhas_mr' : 'falhas_ef',
          subInstantes: sub,
          subDuracao: sub,
          subEscolha: sub,
          subPolitica: sub,
          locais: fp.familia === 'EF' ? montaLocais(fl.locais, fl.locais_sem_posicao ?? 0) : undefined,
        });
      }
      return;
    }
    for (const causa of CAUSAS) {
      fontes.push({
        id: causa,
        fi: fontes.length,
        linha,
        li,
        causa,
        acum: taxaAcumulada(parametros, horario, cenario, linha, causa),
        renovacao: renovacaoDe(parametros, linha, causa),
        duracao: duracaoDe(parametros.ttr[`${linha}|${causa}`]),
        ...subFluxosV1(li, causa),
      });
    }
  });
  const causaComum: FonteCausaComum[] = [];
  Object.entries(parametros.causa_comum).forEach(([par, cc], ci) => {
    // grupo de linhas atingidas juntas (chave "a-b" ou "a-b-c..."); cada evento histórico está num grupo só
    const linhas = cc.linhas ?? par.split('-');
    if (linhas.length < 2 || !linhas.every((l) => rede.linhas[l])) return;
    const ini = Math.max(...linhas.map((l) => horario.inicioServico[l]));
    const fim = Math.min(...linhas.map((l) => horario.fimServico[l]));
    causaComum.push({ par, ci, linhas, acum: taxaAcumuladaConstante(cc.taxa_por_hora_op.valor, ini, fim), duracao: duracaoDe(cc.duracao) });
  });
  const locais: Record<string, LocaisLinha> = {};
  for (const linha of rede.ids) locais[linha] = montaLocais(parametros.locais_ef[linha], parametros.locais_ef_sem_posicao?.[linha] ?? 0);
  const frota: Contexto['frota'] = {};
  const oficina: Contexto['oficina'] = {};
  const reparo = hipotese('reparo_oficina_dias', parametros, cenario);
  const pRet = hipotese('p_retirada', parametros, cenario);
  const reservas = Math.round(hipotese('reservas_por_linha', parametros, cenario));
  for (const linha of rede.ids) {
    const f = parametros.frota[linha];
    if (!f) continue;
    const n = Math.round(f.trens_necessarios.valor);
    const lambdaDia = f.lambda_trem_dia.valor * pRet;
    frota[linha] = { n, lambdaDia };
    oficina[linha] = {
      semReserva: estacionariaFrota({ n, s: 0, lambdaDia, reparoDias: reparo }),
      comReserva: estacionariaFrota({ n, s: reservas, lambdaDia, reparoDias: reparo }),
      reservas,
    };
  }
  const transferenciaS = hipotese('tempo_transferencia_min', parametros, cenario) * 60;
  const g = grafo ?? montaGrafo(linhasDoHorario(rede, horario, cenario.pontosRetorno), transferenciaS, { rede, horario });
  return {
    rede,
    parametros,
    cenario,
    horario,
    grafo: g,
    intervaloMinimoS: hipotese('intervalo_minimo_s', parametros, cenario),
    sentidosEF: hipotese('sentidos_bloqueio_ef', parametros, cenario) >= 2 ? 2 : 1,
    fontes,
    causaComum,
    locais,
    frota,
    oficina,
  };
}

/** Uma família (MR ou EF) numa linha, somando as fontes dela: taxa acumulada, mistura das durações pesada pelas
 * falhas esperadas e forma média da renovação. Com uma fonte só (contrato v1), é a própria fonte. */
export interface FamiliaLinha {
  acum: Float64Array;
  duracoes: { peso: number; d: Duracao }[];
  forma: number;
  escala: number; // normalizada: média 1 no tempo reescalado
}

export function familiaNaLinha(ctx: Contexto, linha: string, causa: Causa): FamiliaLinha | null {
  const fs = ctx.fontes.filter((f) => f.linha === linha && f.causa === causa);
  if (!fs.length) return null;
  if (fs.length === 1) return { acum: fs[0].acum, duracoes: [{ peso: 1, d: fs[0].duracao }], forma: fs[0].renovacao.forma, escala: fs[0].renovacao.escalaNormalizada };
  const acum = new Float64Array(fs[0].acum.length);
  const duracoes: FamiliaLinha['duracoes'] = [];
  let total = 0;
  let forma = 0;
  for (const f of fs) {
    for (let i = 0; i < acum.length; i++) acum[i] += f.acum[i];
    const peso = f.acum[f.acum.length - 1];
    total += peso;
    forma += peso * f.renovacao.forma;
    duracoes.push({ peso, d: f.duracao });
  }
  forma = total > 0 ? forma / total : 1;
  return { acum, duracoes, forma, escala: 1 / gamaFuncao(1 + 1 / forma) };
}

/** Duração média de uma mistura de durações (minutos, com a massa em zero). */
export function duracaoMediaMistura(ds: { peso: number; d: Duracao }[]): number {
  let s = 0;
  let p = 0;
  for (const x of ds) {
    s += x.peso * duracaoMediaMin(x.d);
    p += x.peso;
  }
  return p > 0 ? s / p : 0;
}

/** Redução da taxa de causa comum com a política ligada. */
export function reducaoCausaComum(ctx: Contexto, politicas: Politicas): number {
  if (!politicas.tratamentoCausaComum) return 0;
  const r = hipotese('reducao_causa_comum', ctx.parametros, ctx.cenario);
  return r > 0 ? r : hipotese('reducao_causa_comum_politica', ctx.parametros, ctx.cenario);
}

/** Hipóteses ativas num cenário com estas políticas, para acompanhar cada resultado publicado. */
export function avisosDoCenario(ctx: Contexto, politicas: Politicas): string[] {
  const h = (nome: Parameters<typeof hipotese>[0], unidade = '') => `${nome} = ${hipotese(nome, ctx.parametros, ctx.cenario)}${unidade}`;
  const avisos = [h('intervalo_minimo_s', ' s'), h('sentidos_bloqueio_ef'), h('tempo_transferencia_min', ' min'), 'um trem por trecho e sentido (simplificação da spec 007)'];
  if (politicas.reservaFria) avisos.push(h('reservas_por_linha'), h('reparo_oficina_dias', ' dias'), h('p_retirada'));
  else avisos.push(h('reparo_oficina_dias', ' dias'), h('p_retirada'));
  if (politicas.retiradaTrem) avisos.push(h('tempo_retirada_min', ' min'));
  if (politicas.operacaoDegradada) avisos.push(h('tempo_ativacao_degradada_min', ' min'), h('fator_velocidade_degradada'));
  if (politicas.retornoParcial) {
    const extras = Object.entries(ctx.cenario.pontosRetorno ?? {}).filter(([, v]) => v.length);
    avisos.push(
      'retorno parcial: só nas pontas de viagem do horário (aparelhos de mudança de via não verificados)' +
        (extras.length ? `; pontos extras do cenário (hipótese): ${extras.map(([l, v]) => `${l} ${v.join(',')}`).join('; ')}` : ''),
    );
  }
  if (politicas.tratamentoCausaComum) avisos.push(`redução da causa comum = ${reducaoCausaComum(ctx, politicas)}`);
  for (const [nome, p] of Object.entries(ctx.parametros.hipoteses ?? {})) if (p.status !== 'hipótese') avisos.push(`atenção: ${nome} com status ${p.status}`);
  return avisos;
}
