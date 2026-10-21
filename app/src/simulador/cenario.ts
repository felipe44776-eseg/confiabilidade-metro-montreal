// Cenário da página (spec 011): o que a pessoa escolhe, como vira o cenário do motor e como vai para o link.
// Funções puras: o mesmo link dá o mesmo cenário, e o mesmo cenário com a mesma semente dá os mesmos números.

import type { NomePolitica, Politicas } from '../motor/politicas';
import { NENHUMA_POLITICA } from '../motor/politicas';
import type { Cenario, Condicoes, RedeJson, TipoDia } from '../motor/tipos';
import { TIPOS_DIA } from '../motor/tipos';

export type Greve = 'nao' | 'set_out_2025' | 'jun_2025';

export interface EstadoCenario {
  tipoDia: TipoDia;
  mes: number; // 1 a 12
  temp: string; // níveis do modelo da spec 005
  precip: string;
  cond: string;
  neveSolo: string;
  jogo: boolean;
  gp: boolean;
  feriado: boolean;
  greve: Greve;
  politicas: Politicas;
  /** Só as hipóteses que a pessoa mudou; as demais ficam no valor do parametros.json. */
  hipoteses: Record<string, number>;
  semente: number;
  rodadas: number;
  dia: number; // índice da rodada mostrada no mapa (a rodada i do Monte Carlo)
  /** Viagem da aba "Viagem de A a B" (spec 015): ids das estações. Não muda o cenário. */
  viagemDe: string;
  viagemPara: string;
}

export const ORDEM_POLITICAS: readonly NomePolitica[] = ['reservaFria', 'retiradaTrem', 'operacaoDegradada', 'retornoParcial', 'rotaAlternativa', 'tratamentoCausaComum'];

/** Níveis oferecidos na página (os "sem_dado" do ajuste não são cenário). */
export const NIVEIS = {
  temp: ['abaixo_-15', '-15a-5', '-5a5', '5a15', '15a25', '25_ou_mais'],
  precip: ['0', 'ate_1mm', 'acima_1mm'],
  cond: ['seco_ou_outro', 'chuva', 'neve', 'chuva_congelante'],
  neveSolo: ['0', '1a10', 'acima_10'],
} as const;

export const ROTULOS: Record<string, string> = {
  'abaixo_-15': 'abaixo de −15 °C',
  '-15a-5': '−15 a −5 °C',
  '-5a5': '−5 a 5 °C',
  '5a15': '5 a 15 °C',
  '15a25': '15 a 25 °C',
  '25_ou_mais': '25 °C ou mais',
  '0': 'nenhuma',
  ate_1mm: 'até 1 mm/h',
  acima_1mm: 'acima de 1 mm/h',
  seco_ou_outro: 'seco ou outra',
  chuva: 'chuva',
  neve: 'neve',
  chuva_congelante: 'chuva congelante',
  '1a10': '1 a 10 cm',
  acima_10: 'mais de 10 cm',
  util: 'dia útil',
  sabado: 'sábado',
  domingo: 'domingo',
};

/** Faixas com serviço das greves de 2025 (dados/manuais/greves_stm.csv; fonte: imprensa, status "não verificado"). */
export const JANELAS_GREVE: Record<Exclude<Greve, 'nao'>, { rotulo: string; janelas: [number, number][] }> = {
  set_out_2025: { rotulo: 'greve com faixas (set.–out. de 2025: 06:30–09:30, 14:45–17:45, 23:00–01:15)', janelas: [[6.5 * 3600, 9.5 * 3600], [14.75 * 3600, 17.75 * 3600], [23 * 3600, 25.25 * 3600]] },
  jun_2025: { rotulo: 'greve com faixas (junho de 2025: 06:30–09:38, 14:45–17:48, 23:00–01:00)', janelas: [[6.5 * 3600, 9 * 3600 + 38 * 60], [14.75 * 3600, 17 * 3600 + 48 * 60], [23 * 3600, 25 * 3600]] },
};

/** Jogo do Canadiens às 19h: o pipeline marca de 1 h antes a 3 h 30 depois do início (horas 18 a 22). */
export const HORAS_JOGO = [18, 19, 20, 21, 22];

export const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

export function estacaoDoMes(mes: number): string {
  if (mes === 12 || mes <= 2) return 'inverno';
  if (mes <= 5) return 'primavera';
  if (mes <= 8) return 'verao';
  return 'outono';
}

/** Cenário padrão: as condições de referência do modelo (multiplicadores iguais a 1), em outubro. */
export const PADRAO: EstadoCenario = {
  tipoDia: 'util',
  mes: 10,
  temp: '5a15',
  precip: '0',
  cond: 'seco_ou_outro',
  neveSolo: '0',
  jogo: false,
  gp: false,
  feriado: false,
  greve: 'nao',
  politicas: { ...NENHUMA_POLITICA },
  hipoteses: {},
  semente: 20261021,
  rodadas: 1000,
  dia: 0,
  // Angrignon (Verde) a Saint-Michel (Azul): três linhas em série
  viagemDe: 'STATION_M118',
  viagemPara: 'STATION_M556',
};

export function copia(e: EstadoCenario): EstadoCenario {
  return { ...e, politicas: { ...e.politicas }, hipoteses: { ...e.hipoteses } };
}

/** Cenário do motor. O clima muda a taxa só pelos multiplicadores da spec 005 (parametros.json). */
export function paraCenarioMotor(e: EstadoCenario): Cenario {
  const condicoes: Condicoes = {
    estacao: estacaoDoMes(e.mes),
    temp: e.temp,
    precip: e.precip,
    cond: e.cond,
    neve_solo: e.neveSolo,
    gp_fds: e.gp ? '1' : '0',
    feriado: e.feriado ? '1' : '0',
    greve: e.greve !== 'nao' ? '1' : '0',
    jogo: '0',
  };
  const cenario: Cenario = { tipoDia: e.tipoDia, condicoes };
  if (e.jogo) {
    cenario.condicoesPorHora = {};
    for (const h of HORAS_JOGO) cenario.condicoesPorHora[h] = { jogo: '1' };
  }
  if (Object.keys(e.hipoteses).length) cenario.hipoteses = { ...e.hipoteses };
  return cenario;
}

/**
 * Horário de greve: só as viagens que partem dentro das faixas com serviço (a viagem que já partiu termina).
 * A oferta menor entra no motor pelo próprio horário, como a exposição da spec 004.
 */
export function aplicaGreve(rede: RedeJson, greve: Greve): RedeJson {
  if (greve === 'nao') return rede;
  const janelas = JANELAS_GREVE[greve].janelas;
  const dentro = (t: number) => janelas.some(([a, b]) => t >= a && t < b);
  const horarios = {} as RedeJson['horarios'];
  for (const tipo of TIPOS_DIA) {
    horarios[tipo] = {};
    for (const [linha, sentidos] of Object.entries(rede.horarios[tipo])) {
      horarios[tipo][linha] = { '0': sentidos['0'].filter((v) => dentro(v.tempos[0][1])), '1': sentidos['1'].filter((v) => dentro(v.tempos[0][1])) };
    }
  }
  return { ...rede, horarios };
}

/** Chave da versão da rede (o worker só remonta a rede quando ela muda). */
export function chaveRede(greve: Greve): string {
  return `rede:${greve}`;
}

// ---------- link compartilhável ----------

const CODIGO_GREVE: Record<Greve, string> = { nao: '0', set_out_2025: 's', jun_2025: 'j' };

export function serializa(e: EstadoCenario): string {
  const p = new URLSearchParams();
  p.set('d', e.tipoDia);
  p.set('m', String(e.mes));
  p.set('t', e.temp);
  p.set('p', e.precip);
  p.set('c', e.cond);
  p.set('n', e.neveSolo);
  p.set('ev', `${e.jogo ? 1 : 0}${e.gp ? 1 : 0}${e.feriado ? 1 : 0}`);
  p.set('gr', CODIGO_GREVE[e.greve]);
  p.set('pol', ORDEM_POLITICAS.map((k) => (e.politicas[k] ? '1' : '0')).join(''));
  const hs = Object.entries(e.hipoteses).sort(([a], [b]) => a.localeCompare(b));
  if (hs.length) p.set('h', hs.map(([k, v]) => `${k}:${v}`).join(','));
  p.set('s', String(e.semente));
  p.set('r', String(e.rodadas));
  p.set('dia', String(e.dia));
  p.set('vo', e.viagemDe);
  p.set('vd', e.viagemPara);
  return p.toString();
}

function inteiro(v: string | null, padrao: number, min: number, max: number): number {
  const n = v === null ? NaN : Number(v);
  return Number.isInteger(n) && n >= min && n <= max ? n : padrao;
}

function nivel<T extends string>(v: string | null, validos: readonly T[], padrao: T): T {
  return v !== null && (validos as readonly string[]).includes(v) ? (v as T) : padrao;
}

/** Lê o link. Valor inválido ou ausente volta ao padrão (o link nunca quebra a página). */
export function desserializa(texto: string): EstadoCenario {
  const p = new URLSearchParams(texto.replace(/^#/, ''));
  const e = copia(PADRAO);
  e.tipoDia = nivel(p.get('d'), TIPOS_DIA, PADRAO.tipoDia);
  e.mes = inteiro(p.get('m'), PADRAO.mes, 1, 12);
  e.temp = nivel(p.get('t'), NIVEIS.temp, PADRAO.temp);
  e.precip = nivel(p.get('p'), NIVEIS.precip, PADRAO.precip);
  e.cond = nivel(p.get('c'), NIVEIS.cond, PADRAO.cond);
  e.neveSolo = nivel(p.get('n'), NIVEIS.neveSolo, PADRAO.neveSolo);
  const ev = p.get('ev') ?? '000';
  e.jogo = ev[0] === '1';
  e.gp = ev[1] === '1';
  e.feriado = ev[2] === '1';
  const gr = p.get('gr');
  e.greve = (Object.entries(CODIGO_GREVE).find(([, c]) => c === gr)?.[0] as Greve | undefined) ?? 'nao';
  const pol = p.get('pol') ?? '';
  ORDEM_POLITICAS.forEach((k, i) => (e.politicas[k] = pol[i] === '1'));
  for (const par of (p.get('h') ?? '').split(',').filter(Boolean)) {
    const [k, v] = par.split(':');
    const n = Number(v);
    if (k && /^[a-z_]+$/.test(k) && Number.isFinite(n)) e.hipoteses[k] = n;
  }
  e.semente = inteiro(p.get('s'), PADRAO.semente, 0, 2 ** 32 - 1);
  e.rodadas = inteiro(p.get('r'), PADRAO.rodadas, 10, 50_000);
  e.dia = inteiro(p.get('dia'), PADRAO.dia, 0, 49_999);
  const id = (v: string | null, padrao: string) => (v !== null && /^[A-Za-z0-9_]{1,40}$/.test(v) ? v : padrao);
  e.viagemDe = id(p.get('vo'), PADRAO.viagemDe);
  e.viagemPara = id(p.get('vd'), PADRAO.viagemPara);
  return e;
}

/** Chave do cenário sem o dia mostrado e sem a viagem: trocar de dia ou de viagem não muda o cenário nem o resultado do Monte Carlo. */
export function chaveCenario(e: EstadoCenario): string {
  return serializa({ ...e, dia: 0, viagemDe: PADRAO.viagemDe, viagemPara: PADRAO.viagemPara });
}

const NOMES_ESTACAO: Record<string, string> = { inverno: 'inverno', primavera: 'primavera', verao: 'verão', outono: 'outono' };

/**
 * O que está valendo no cenário, item a item, com `mudou` quando difere do padrão (spec 011, decisão D50).
 * `politicas` recebe os nomes legíveis das políticas ligadas.
 */
export function itensDoCenario(e: EstadoCenario, nomesPoliticas: Record<NomePolitica, string>): { rotulo: string; texto: string; mudou: boolean }[] {
  const eventos = [e.jogo && 'jogo do Canadiens', e.gp && 'GP do Canadá', e.feriado && 'feriado'].filter(Boolean) as string[];
  const pol = ORDEM_POLITICAS.filter((k) => e.politicas[k]).map((k) => nomesPoliticas[k].toLowerCase());
  const hs = Object.entries(e.hipoteses).sort(([a], [b]) => a.localeCompare(b));
  return [
    { rotulo: 'Dia', texto: ROTULOS[e.tipoDia], mudou: e.tipoDia !== PADRAO.tipoDia },
    { rotulo: 'Mês', texto: `${MESES[e.mes - 1]} (${NOMES_ESTACAO[estacaoDoMes(e.mes)]})`, mudou: e.mes !== PADRAO.mes },
    { rotulo: 'Temperatura', texto: ROTULOS[e.temp], mudou: e.temp !== PADRAO.temp },
    { rotulo: 'Precipitação', texto: ROTULOS[e.precip], mudou: e.precip !== PADRAO.precip },
    { rotulo: 'Condição', texto: ROTULOS[e.cond], mudou: e.cond !== PADRAO.cond },
    { rotulo: 'Neve no solo', texto: ROTULOS[e.neveSolo], mudou: e.neveSolo !== PADRAO.neveSolo },
    { rotulo: 'Eventos', texto: eventos.length ? eventos.join(', ') : 'nenhum', mudou: eventos.length > 0 },
    { rotulo: 'Greve', texto: e.greve === 'nao' ? 'não' : JANELAS_GREVE[e.greve].rotulo, mudou: e.greve !== 'nao' },
    { rotulo: 'Políticas', texto: pol.length ? pol.join(', ') : 'nenhuma', mudou: pol.length > 0 },
    { rotulo: 'Hipóteses', texto: hs.length ? hs.map(([k, v]) => `${k.replaceAll('_', ' ')} = ${v}`).join(', ') : 'valores do parametros.json', mudou: hs.length > 0 },
  ];
}

export function politicasIguais(a: Politicas, b: Politicas): boolean {
  return ORDEM_POLITICAS.every((k) => a[k] === b[k]);
}
