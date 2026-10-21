// Avisos de extrapolação (spec 011): o cenário sai do que os dados observaram?
// Combinações de condições: contagem de horas de 2019 a 2026-06 (observado.ts). Hipóteses: a `faixa` do parametros.json.

import type { Parametros } from '../motor/tipos';
import type { EstadoCenario } from './cenario';
import { MESES, ROTULOS, estacaoDoMes } from './cenario';
import { OBSERVADO } from './observado';

export type NivelAviso = 'extrapola' | 'poucos_dados' | 'atencao';

export interface Aviso {
  nivel: NivelAviso;
  texto: string;
}

/** Abaixo disso, a combinação existe nos dados mas com poucas horas. */
export const MIN_HORAS = 30;
/** Intervalo de 95% do multiplicador mais largo que esta razão (alto ÷ baixo) merece aviso. */
export const RAZAO_IC_LARGO = 3;

const rot = (v: string) => ROTULOS[v] ?? v;
const mes = (m: number) => MESES[m - 1];

function horas(par: string, a: string, b: string): number {
  return OBSERVADO[par]?.[`${a}|${b}`] ?? 0;
}

function confere(par: string, a: string, b: string, descricao: string, saida: Aviso[]): void {
  const n = horas(par, a, b);
  if (n === 0) saida.push({ nivel: 'extrapola', texto: `Extrapolação: nenhuma hora com ${descricao} nos dados de 2019 a 2026.` });
  else if (n < MIN_HORAS) saida.push({ nivel: 'poucos_dados', texto: `Poucos dados: só ${n} horas com ${descricao} de 2019 a 2026.` });
}

export function avisosDeExtrapolacao(e: EstadoCenario, parametros: Parametros): Aviso[] {
  const saida: Aviso[] = [];
  const m = String(e.mes);
  confere('mes|temp', m, e.temp, `${rot(e.temp)} em ${mes(e.mes)}`, saida);
  confere('temp|cond', e.temp, e.cond, `${rot(e.cond)} a ${rot(e.temp)}`, saida);
  confere('mes|cond', m, e.cond, `${rot(e.cond)} em ${mes(e.mes)}`, saida);
  confere('cond|precip', e.cond, e.precip, `${rot(e.cond)} e precipitação ${rot(e.precip)}`, saida);
  // neve no solo: de abril a novembro a estação muitas vezes não mede, e o pipeline grava "sem dado" (não zero).
  // "Nenhuma" é o nível de referência e o estado esperado fora do inverno: só os níveis com neve são conferidos.
  if (e.neveSolo !== '0') {
    const medidas = ['0', '1a10', 'acima_10'].reduce((s, n) => s + horas('mes|neve_solo', m, n), 0);
    if (medidas === 0) saida.push({ nivel: 'extrapola', texto: `Extrapolação: não há medição de neve no solo em ${mes(e.mes)} nos dados.` });
    else confere('mes|neve_solo', m, e.neveSolo, `neve no solo ${rot(e.neveSolo)} em ${mes(e.mes)}`, saida);
  }
  if (e.feriado) confere('tipo_dia|feriado', e.tipoDia, '1', `feriado em ${rot(e.tipoDia)} (nos dados, feriado usa o horário de domingo)`, saida);
  if (e.jogo) confere('tipo_dia|jogo', e.tipoDia, '1', `jogo do Canadiens em ${rot(e.tipoDia)}`, saida);
  if (e.gp) confere('tipo_dia|gp_fds', e.tipoDia, '1', `fim de semana do GP em ${rot(e.tipoDia)}`, saida);
  if (e.greve !== 'nao') confere('tipo_dia|greve', e.tipoDia, '1', `greve em ${rot(e.tipoDia)}`, saida);
  if (e.gp && estacaoDoMes(e.mes) !== 'verao' && e.mes !== 5) saida.push({ nivel: 'atencao', texto: `O GP do Canadá acontece em maio ou junho; em ${mes(e.mes)} o multiplicador vem de outro mês.` });

  // hipóteses fora da faixa declarada
  for (const [nome, valor] of Object.entries(e.hipoteses)) {
    const p = parametros.hipoteses[nome];
    if (!p) continue;
    const f = p.faixa;
    if (f && f.length === 2 && (valor < f[0] || valor > f[1])) saida.push({ nivel: 'extrapola', texto: `Extrapolação: ${nome} = ${valor} fora da faixa razoável (${f[0]} a ${f[1]}).` });
  }

  // multiplicadores com intervalo muito largo nos níveis escolhidos
  const escolhidos: [string, string][] = [
    ['temp', e.temp],
    ['precip', e.precip],
    ['cond', e.cond],
    ['neve_solo', e.neveSolo],
    ['estacao', estacaoDoMes(e.mes)],
  ];
  if (e.jogo) escolhidos.push(['jogo', '1']);
  if (e.gp) escolhidos.push(['gp_fds', '1']);
  if (e.feriado) escolhidos.push(['feriado', '1']);
  if (e.greve !== 'nao') escolhidos.push(['greve', '1']);
  for (const causa of ['MR', 'EF'] as const) {
    for (const [fator, nivel] of escolhidos) {
      const p = parametros.taxas[causa].multiplicadores[fator]?.[nivel];
      const ic = p?.ic95;
      if (p && ic && ic.length === 2 && ic[0] > 0 && ic[1] / ic[0] > RAZAO_IC_LARGO)
        saida.push({ nivel: 'atencao', texto: `Incerteza alta: multiplicador de ${fator} = ${rot(nivel)} (${causa}) tem IC 95% de ${ic[0].toFixed(2)} a ${ic[1].toFixed(2)}.` });
    }
  }
  return saida;
}
