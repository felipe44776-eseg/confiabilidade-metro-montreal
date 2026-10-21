// Tipos de entrada do motor. Espelham dados/derivados/simulador/rede.json e o contrato
// contratos/parametros.schema.json (fronteira entre o pipeline Python e o simulador).

export type TipoDia = 'util' | 'sabado' | 'domingo';
export const TIPOS_DIA: readonly TipoDia[] = ['util', 'sabado', 'domingo'];
export type Sentido = 0 | 1;
export type Causa = 'MR' | 'EF';
export const CAUSAS: readonly Causa[] = ['MR', 'EF'];

// ---------- rede.json ----------

export interface EstacaoJson {
  id: string; // parent_station do GTFS; a mesma estação de correspondência aparece em mais de uma linha
  nome: string;
  km: number; // posição ao longo do traçado no sentido 0 (spec 002)
  lat: number;
  lon: number;
}

/**
 * Viagem do horário. `inicio` e as paradas estão no referencial do próprio sentido:
 * a parada i fica no índice local `inicio + i`. No sentido 0 o índice local é o índice em
 * `estacoes`; no sentido 1 o índice local L corresponde a `estacoes[n - 1 - L]`
 * (pipeline/horario_simulador.py: `passos = [n-1-i for i in idx]`).
 */
export interface ViagemJson {
  inicio: number;
  tempos: [number, number][]; // [chegada, partida] em segundos desde a meia-noite do dia de operação
}

export interface RedeJson {
  fonte?: unknown;
  linhas: Record<string, { cor?: string; estacoes: EstacaoJson[] }>;
  correspondencias: { estacao: string; id: string; linhas: string[] }[];
  horarios: Record<TipoDia, Record<string, Record<'0' | '1', ViagemJson[]>>>;
}

// ---------- parametros.json ----------

export type StatusParametro = 'ajustado' | 'deduzido' | 'hipótese' | 'não verificado';

export interface Parametro {
  valor: number;
  ic95?: [number, number] | number[] | null;
  n?: number | null;
  unidade?: string;
  metodo: string;
  fontes: string[];
  script: string;
  status: StatusParametro;
  faixa?: number[];
}

export interface Taxa {
  modelo: string;
  alpha: Parametro;
  base_por_trem_hora: Record<string, Parametro>;
  multiplicadores: Record<string, Record<string, Parametro>>;
  referencia?: Record<string, string>;
}

export interface Lognormal {
  p_zero: Parametro;
  mu_log: Parametro;
  sigma_log: Parametro;
  /** Durações positivas observadas (minutos, ordenadas). Com ela, o sorteio é pela distribuição empírica. */
  amostra_positivos?: { minutos: number[]; n: number; media_min: number; metodo?: string; status?: string };
}

export interface Renovacao {
  forma: Parametro;
  escala: Parametro;
  processo?: string;
}

export interface CausaComumParam {
  /** Linhas paradas juntas (grupo). Sem ele, as linhas vêm da chave separada por '-'. */
  linhas?: string[];
  taxa_por_hora_op: Parametro;
  beta_a?: Parametro;
  beta_b?: Parametro;
  duracao: Lognormal;
}

export interface LocalEF {
  km: number;
  peso: number;
  codigo: string;
  status: string;
}

export interface FrotaParam {
  trens_necessarios: Parametro;
  lambda_trem_dia: Parametro;
}

export interface Parametros {
  versao: number;
  codigo_commit: string;
  ano_base: number;
  janela_operacao_h?: Parametro;
  taxas: { MR: Taxa; EF: Taxa };
  renovacao: Record<string, Renovacao>; // chave "linha|causa"
  ttr: Record<string, Lognormal>; // chave "linha|causa"
  causa_comum: Record<string, CausaComumParam>; // chave: grupo de linhas em ordem alfabética, unidas por '-'
  /** Fator β por par de linhas (relatório, não é fonte de sorteio). */
  causa_comum_beta?: Record<string, { eventos: number; beta_a: Parametro; beta_b: Parametro }>;
  locais_ef: Record<string, LocalEF[]>;
  locais_ef_sem_posicao?: Record<string, number>;
  frota: Record<string, FrotaParam>;
  hipoteses: Record<string, Parametro>;
}

// ---------- cenário ----------

/** Condições de um fator do modelo de taxa (spec 005): fator -> nível. Indicadores usam "1" ou "0". */
export type Condicoes = Record<string, string>;

export interface Cenario {
  tipoDia: TipoDia;
  /** Condições do dia inteiro. Fator ausente fica no nível de referência do modelo. */
  condicoes?: Condicoes;
  /** Condições por hora de serviço (5 a 27), sobrepostas às do dia. */
  condicoesPorHora?: Record<number, Condicoes>;
  /** Valores que substituem parametros.hipoteses (controles da interface). */
  hipoteses?: Record<string, number>;
  /** Estações (índice no sentido 0) onde se supõe retorno parcial, além das pontas de viagem do horário. Hipótese. */
  pontosRetorno?: Record<string, number[]>;
  /** Desliga todas as falhas sorteadas (as injetadas continuam). */
  semFalhas?: boolean;
}
