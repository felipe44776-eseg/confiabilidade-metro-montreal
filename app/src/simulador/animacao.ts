// Estado do dia simulado num instante: posição dos trens, trechos bloqueados e indicadores (spec 010).
// Funções puras sobre o resultado de simulaDia (com registro e trajetórias).

import type { EventoRegistro, ResultadoDia, Trajetoria } from '../motor/dia';
import { uniao } from '../motor/dia';
import type { Rede } from '../motor/rede';
import { estacaoGlobal } from '../motor/rede';
import type { Sentido } from '../motor/tipos';
import { kmEntreEstacoes } from './tracado';

export interface PosicaoTrem {
  id: string;
  linha: string;
  sentido: Sentido;
  km: number;
  parado: boolean;
  atrasoS: number; // atraso em relação ao horário, no ponto atual
}

/** Posição de uma trajetória no instante t, ou null se o trem não está em viagem. */
export function posicaoDaTrajetoria(rede: Rede, tr: Trajetoria, t: number): PosicaoTrem | null {
  if (tr.cancelada) return null;
  const v = tr.viagem;
  const ultimo = tr.ultima - v.inicio;
  if (t < tr.partida[0] || t >= tr.chegada[ultimo]) return null;
  const l = rede.linhas[v.linha];
  const kms = l.estacoes.map((e) => e.km);
  const g = (local: number) => estacaoGlobal(l.n, v.sentido, local);
  for (let p = 0; p <= ultimo; p++) {
    if (tr.chegada[p] <= t && t < tr.partida[p]) {
      return { id: v.id, linha: v.linha, sentido: v.sentido, km: kms[g(v.inicio + p)], parado: true, atrasoS: Math.max(0, tr.partida[p] - v.partida[p]) };
    }
    if (p < ultimo && tr.partida[p] <= t && t < tr.chegada[p + 1]) {
      const dur = tr.chegada[p + 1] - tr.partida[p];
      const f = dur > 0 ? (t - tr.partida[p]) / dur : 1;
      return {
        id: v.id,
        linha: v.linha,
        sentido: v.sentido,
        km: kmEntreEstacoes(kms, g(v.inicio + p), g(v.inicio + p + 1), f),
        parado: false,
        atrasoS: Math.max(0, tr.partida[p] - v.partida[p]),
      };
    }
  }
  return null;
}

/** Trens em viagem no instante t, com km na linha. */
export function posicoes(rede: Rede, trajetorias: Record<string, Trajetoria[]>, t: number): PosicaoTrem[] {
  const saida: PosicaoTrem[] = [];
  for (const lista of Object.values(trajetorias)) {
    for (const tr of lista) {
      const p = posicaoDaTrajetoria(rede, tr, t);
      if (p) saida.push(p);
    }
  }
  return saida;
}

export type CausaBloco = 'MR' | 'EF' | 'CC';

export interface Bloco {
  ini: number;
  fim: number;
  linha: string;
  trecho: number | null; // trecho físico; null = a linha inteira (causa comum)
  sentido: Sentido | null; // null = os dois
  causa: CausaBloco;
  detalhe: string;
}

export interface Ocorrencia {
  t: number;
  linha: string;
  trecho: number | null;
  tipo: EventoRegistro['tipo'];
  duracaoS: number;
  detalhe: string;
}

function causaDoFim(e: EventoRegistro): CausaBloco {
  if (e.detalhe.startsWith('causa comum')) return 'CC';
  if (e.detalhe === 'equipamento fixo') return 'EF';
  return 'MR';
}

/** Intervalos de bloqueio do dia, a partir dos eventos FIM_INTERRUPCAO (duração = tempo parado de fato). */
export function blocosDoDia(r: ResultadoDia): Bloco[] {
  return r.registro
    .filter((e) => e.tipo === 'FIM_INTERRUPCAO' && (e.duracaoS ?? 0) > 0)
    .map((e) => ({ ini: e.t - (e.duracaoS as number), fim: e.t, linha: e.linha, trecho: e.trecho, sentido: e.sentido, causa: causaDoFim(e), detalhe: e.detalhe }))
    .sort((a, b) => a.ini - b.ini);
}

/** Falhas do dia (com ou sem interrupção), para a lista e os marcadores. */
export function ocorrenciasDoDia(r: ResultadoDia): Ocorrencia[] {
  return r.registro
    .filter((e) => e.tipo === 'FALHA_TREM' || e.tipo === 'FALHA_EF' || e.tipo === 'CAUSA_COMUM')
    .map((e) => ({ t: e.t, linha: e.linha, trecho: e.trecho, tipo: e.tipo, duracaoS: e.duracaoS ?? 0, detalhe: e.detalhe }));
}

export function blocosAtivos(blocos: readonly Bloco[], t: number): Bloco[] {
  return blocos.filter((b) => b.ini <= t && t < b.fim);
}

/** Minutos de interrupção por linha do início do serviço até t (união dos bloqueios, como no motor). */
export function minutosAte(rede: Rede, inicioServico: Record<string, number>, blocos: readonly Bloco[], t: number): Record<string, number> {
  const saida: Record<string, number> = {};
  for (const l of rede.ids) {
    const ini = inicioServico[l];
    saida[l] = t > ini ? uniao(blocos.filter((b) => b.linha === l), ini, t) / 60 : 0;
  }
  return saida;
}

/** Relógio do dia de operação: 25:15 vira 01:15. */
export function relogio(t: number): string {
  const h = Math.floor(t / 3600);
  const m = Math.floor((t % 3600) / 60);
  return `${String(h % 24).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}
