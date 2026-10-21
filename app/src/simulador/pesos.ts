// Peso de cada variável do cenário no modelo de taxa (spec 005) e a nota do método no painel do cenário
// (spec 011, decisão D51). Todo número vem de parametros.json ou de dados/modelos/taxa_<causa>.json,
// gerados por pipeline/modelo_taxa.py e pipeline/parametros.py.

import { FAIXAS_HORARIAS } from '../motor/taxas';
import type { Parametros } from '../motor/tipos';
import { comIC, inteiro, num } from '../ui/formato';
import type { EstadoCenario } from './cenario';
import { estacaoDoMes, HORAS_JOGO, ROTULOS } from './cenario';

/** Campos do resumo do ajuste em dados/modelos/taxa_<causa>.json que a nota usa. */
export interface ResumoTaxa {
  causa: string;
  n_horas: number;
  n_falhas: number;
  modelo_escolhido: string;
  aic_poisson: number;
  aic_nb: number;
  alpha_nb: number;
  p_lr_dispersao: number;
  bootstrap_b: number;
  semente: number;
  ano_base: string;
  coeficientes: { termo: string; multiplicador: number; ic95: number[] | null }[];
}
/** Resumos das duas causas; null enquanto não carregaram (a nota usa só o parametros.json). */
export type Resumos = { MR: ResumoTaxa; EF: ResumoTaxa } | null;

export type CampoPeso = 'tipo' | 'mes' | 'temp' | 'precip' | 'cond' | 'neve' | 'jogo' | 'gp' | 'feriado' | 'greve';

export const NOMES_ESTACAO: Record<string, string> = { inverno: 'inverno', primavera: 'primavera', verao: 'verão', outono: 'outono' };
const NOMES_FAIXA: Record<string, string> = {
  abertura: 'abertura',
  pico_manha: 'pico da manhã',
  entrepico: 'entrepico',
  pico_tarde: 'pico da tarde',
  noite: 'noite',
  fim: 'fim da noite',
};
const REFERENCIA = '1 (referência)';

const contem1 = (ic: readonly number[] | null | undefined) => !!ic && ic.length === 2 && ic[0] <= 1 && 1 <= ic[1];
const vezes = (valor: number, ic: readonly number[] | null | undefined) => `×${comIC(valor, ic ?? undefined, 2)}`;
const horas = (a: number, b: number) => `das ${a % 24}h às ${b % 24}h`;
const capitaliza = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

/** Peso de um nível nas duas causas: "MR ×1,37 (1,10–1,67) · EF ×1,38 (1,10–1,70)", ou "1 (referência)". */
export function pesoDoNivel(p: Parametros, fator: string, nivel: string): string {
  const mr = p.taxas.MR.multiplicadores[fator]?.[nivel];
  const ef = p.taxas.EF.multiplicadores[fator]?.[nivel];
  if ((!mr && !ef) || p.taxas.MR.referencia?.[fator] === nivel) return REFERENCIA;
  return `MR ${mr ? vezes(mr.valor, mr.ic95) : '×1'} · EF ${ef ? vezes(ef.valor, ef.ic95) : '×1'}`;
}

function textoGreve(resumos: Resumos): string {
  const fim = 'a greve entra só pelo horário, com menos trens (decisão D42)';
  const g = resumos ? [resumos.MR, resumos.EF].map((r) => r.coeficientes.find((c) => c.termo === 'greve')) : [];
  const [mr, ef] = g;
  if (!mr || !ef) return `Sem peso na taxa: ${fim}.`;
  const comUm = contem1(mr.ic95) && contem1(ef.ic95) ? ', com intervalo que contém 1' : '';
  return `Sem peso na taxa: o multiplicador medido foi MR ${vezes(mr.multiplicador, mr.ic95)} · EF ${vezes(ef.multiplicador, ef.ic95)}${comUm}, e ${fim}.`;
}

/** Texto embaixo de cada campo do painel: o peso do valor escolhido (ou, nas caixas desmarcadas, o de marcar). */
export function pesosDoCenario(p: Parametros, e: EstadoCenario, resumos: Resumos): Record<CampoPeso, string> {
  const est = estacaoDoMes(e.mes);
  const caixa = (ligada: boolean, fator: string, quando = '') => `${ligada ? 'Peso' : 'Se marcado, peso'}${quando}: ${pesoDoNivel(p, fator, '1')}.`;
  return {
    tipo: `Peso: ${pesoDoNivel(p, 'tipo_dia', e.tipoDia)}. O tipo de dia também troca o horário (quantos trens circulam).`,
    mes: `Estação do ano no modelo: ${NOMES_ESTACAO[est] ?? est}; peso: ${pesoDoNivel(p, 'estacao', est)}.`,
    temp: `Peso: ${pesoDoNivel(p, 'temp', e.temp)}.`,
    precip: `Peso: ${pesoDoNivel(p, 'precip', e.precip)}.`,
    cond: `Peso: ${pesoDoNivel(p, 'cond', e.cond)}.`,
    neve: `Peso: ${pesoDoNivel(p, 'neve_solo', e.neveSolo)}.`,
    jogo: caixa(e.jogo, 'jogo', ` ${horas(HORAS_JOGO[0], HORAS_JOGO[HORAS_JOGO.length - 1] + 1)}`),
    gp: caixa(e.gp, 'gp_fds'),
    feriado: caixa(e.feriado, 'feriado'),
    greve: textoGreve(resumos),
  };
}

function referenciaEmTexto(ref: Record<string, string> | undefined): string {
  if (!ref) return 'a condição de referência do modelo';
  const partes: string[] = [];
  for (const [f, v] of Object.entries(ref)) {
    if (f === 'ano') continue; // a taxa-base já vem projetada para o ano-base
    if (f === 'linha') partes.push(`Linha ${capitaliza(v)}`);
    else if (f === 'faixa') partes.push(NOMES_FAIXA[v] ?? v);
    else if (f === 'estacao') partes.push(NOMES_ESTACAO[v] ?? v);
    else if (f === 'precip') partes.push(v === '0' ? 'sem precipitação' : `precipitação ${ROTULOS[v] ?? v}`);
    else if (f === 'cond') partes.push(v === 'seco_ou_outro' ? 'sem chuva nem neve' : (ROTULOS[v] ?? v));
    else if (f === 'neve_solo') partes.push(v === '0' ? 'sem neve no solo' : `neve no solo ${ROTULOS[v] ?? v}`);
    else partes.push(ROTULOS[v] ?? v);
  }
  return partes.join(', ');
}

const SOBRESCRITO: Record<string, string> = { '-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹' };
/** "p < 10⁻³²" para p muito pequeno; "p = 0,012" nos outros casos. */
export function textoP(p: number): string {
  if (!(p > 0)) return 'p ≈ 0';
  if (p >= 0.001) return `p = ${num(p, 3)}`;
  const e = String(Math.ceil(Math.log10(p)));
  return `p < 10${[...e].map((c) => SOBRESCRITO[c] ?? c).join('')}`;
}

export interface NotaMetodo {
  /** Parágrafo sempre visível no painel. */
  resumo: string;
  /** Passos do método, em ordem. */
  passos: string[];
  /** Peso de cada faixa do dia, que muda hora a hora e não tem campo no painel. */
  faixas: { faixa: string; horas: string; mr: string; ef: string }[];
}

export function notaDoMetodo(p: Parametros, resumos: Resumos): NotaMetodo {
  const { MR, EF } = p.taxas;
  const modelo = MR.modelo === EF.modelo ? MR.modelo : `${MR.modelo} (MR) e ${EF.modelo} (EF)`;
  const nHoras = resumos?.MR.n_horas ?? MR.alpha.n ?? null;
  const b = resumos?.MR.bootstrap_b ?? Number(/B=(\d+)/.exec(Object.values(MR.base_por_trem_hora)[0]?.metodo ?? '')?.[1] ?? NaN);
  const passos: string[] = [];

  passos.push(
    `Base: ${nHoras ? `${inteiro(nHoras)} horas-linha` : 'as horas-linha'} (cada hora de serviço de cada linha), de 2019 a junho de 2026, com as falhas técnicas daquela hora` +
      (resumos ? ` (${inteiro(resumos.MR.n_falhas)} de material rodante e ${inteiro(resumos.EF.n_falhas)} de equipamentos fixos)` : '') +
      ', os trens-hora do horário (GTFS), o clima da hora (ECCC) e os eventos do dia.',
  );
  passos.push(
    'Um modelo para cada causa: log(falhas esperadas na hora) = log(trens-hora) + constante + soma dos coeficientes dos níveis daquela hora. ' +
      'O log(trens-hora) entra com coeficiente fixo em 1 (deslocamento): o peso mede falhas por trem em circulação, e uma hora com mais trens não conta como efeito da variável.',
  );
  passos.push(
    `Peso = exp(coeficiente): a razão entre a taxa naquele nível e a taxa na referência (${referenciaEmTexto(MR.referencia)}). ` +
      'Como as variáveis entram juntas, cada peso vale com as outras fixas. Variáveis que andam juntas nos dados, como inverno, frio e neve no solo, repartem o efeito entre si; o efeito do conjunto aparece em "Cenário aplicado".',
  );
  const dispersao = `há mais horas com várias falhas do que a Poisson prevê (sobredispersão α = ${num(MR.alpha.valor, 2)} em MR e ${num(EF.alpha.valor, 2)} em EF, por máxima verossimilhança)`;
  passos.push(
    resumos
      ? `Por que ${modelo}: ${dispersao}. Ela ganhou da Poisson nas duas causas pelo AIC (menor é melhor; MR: ${inteiro(resumos.MR.aic_poisson)} na Poisson contra ${inteiro(resumos.MR.aic_nb)}; EF: ${inteiro(resumos.EF.aic_poisson)} contra ${inteiro(resumos.EF.aic_nb)}) e pela razão de verossimilhança (${textoP(Math.max(resumos.MR.p_lr_dispersao, resumos.EF.p_lr_dispersao))}).`
      : `Por que ${modelo}: ${dispersao}; a comparação com a Poisson está no relatório do modelo.`,
  );
  passos.push(
    `Intervalo de 95%: bootstrap em blocos semanais${Number.isFinite(b) ? `, com ${inteiro(b)} reamostras` : ''}${resumos ? ` (semente ${resumos.MR.semente})` : ''}. ` +
      'Cada reamostra sorteia semanas inteiras, porque falhas em horas próximas não são independentes. Quando o intervalo contém 1, os dados não distinguem o efeito de nenhum efeito; o simulador usa o valor estimado mesmo assim, e os Avisos apontam os intervalos largos.',
  );
  passos.push(
    `No simulador: falhas esperadas por minuto = taxa-base da linha × produto dos pesos daquela hora × trens em circulação. A taxa-base de cada linha já inclui o efeito da linha e do ano de ${p.ano_base}. ` +
      `O mês entra pela estação do ano, o jogo vale ${horas(HORAS_JOGO[0], HORAS_JOGO[HORAS_JOGO.length - 1] + 1)}, o tipo de dia muda o peso e o horário, e a greve muda só o horário (decisão D42). ` +
      'A faixa do dia não tem campo aqui: o peso dela muda hora a hora, como na tabela abaixo.',
  );

  const faixas = FAIXAS_HORARIAS.map(([a, fimH, nome]) => {
    const mr = MR.multiplicadores.faixa?.[nome];
    const ef = EF.multiplicadores.faixa?.[nome];
    const ref = MR.referencia?.faixa === nome;
    return {
      faixa: NOMES_FAIXA[nome] ?? nome,
      horas: fimH >= 29 ? `${a}h ao fim` : `${a % 24}h–${(fimH + 1) % 24}h`,
      mr: ref || !mr ? REFERENCIA : vezes(mr.valor, mr.ic95),
      ef: ref || !ef ? REFERENCIA : vezes(ef.valor, ef.ic95),
    };
  });

  return {
    resumo:
      `Cada variável pesa como um multiplicador da taxa de falha por trem em circulação, estimado dos incidentes da STM por regressão ${modelo}, com todas as variáveis no mesmo modelo. ` +
      '1 é a condição de referência; ×1,30 quer dizer 30% mais falhas por trem-hora, com o resto igual. ' +
      'Embaixo de cada campo está o peso do valor escolhido, para material rodante (MR) e equipamentos fixos (EF), com o intervalo de 95%.',
    passos,
    faixas,
  };
}
