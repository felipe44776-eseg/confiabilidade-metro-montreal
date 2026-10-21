// Mensagens entre a página e os Web Workers do Monte Carlo.

import type { Politicas } from '../motor/politicas';
import type { Cenario, Parametros, RedeJson } from '../motor/tipos';
import type { Rodada } from './rodadas';

export interface PedidoMC {
  redeJson: RedeJson;
  /** Identifica a versão da rede, para o worker não remontar a mesma rede a cada pedido. */
  chaveRede: string;
  parametros: Parametros;
  cenario: Cenario;
  politicas: Politicas;
  /** Variante comparada com números aleatórios comuns (mesma semente por rodada). */
  politicasB?: Politicas;
  sementeBase: number;
  rodadas: number;
}

export type ParaTrabalhador = { tipo: 'roda'; id: number; indices: number[] } & Omit<PedidoMC, 'rodadas'>;

export type DoTrabalhador =
  | { tipo: 'progresso'; id: number; feitas: number }
  | { tipo: 'resultado'; id: number; rodadas: Rodada[] }
  | { tipo: 'erro'; id: number; mensagem: string };
