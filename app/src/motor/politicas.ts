// Políticas de tolerância a falhas (spec 008). Cada uma liga e desliga sozinha; "nenhuma política"
// é a operação como os dados a registram.

export interface Politicas {
  /** Reserva fria k-de-n: reservas_por_linha trens parados cobrem os que estão na oficina. */
  reservaFria: boolean;
  /** Retirada do trem falho: com probabilidade p_retirada, o trem sai da via em tempo_retirada_min e encerra a viagem na estação seguinte. */
  retiradaTrem: boolean;
  /** Operação degradada: após tempo_ativacao_degradada_min, o trecho com falha de equipamento fixo reabre em marcha lenta até o fim do reparo. */
  operacaoDegradada: boolean;
  /** Retorno parcial antes do trecho bloqueado: só nas pontas de viagem do horário e nos pontos do cenário (hipótese). */
  retornoParcial: boolean;
  /** Rota alternativa de passageiros: o par origem-destino vale por qualquer caminho livre na rede. */
  rotaAlternativa: boolean;
  /** Tratamento de causa comum: alimentação ou controle redundante reduz a taxa de causa comum. */
  tratamentoCausaComum: boolean;
}

export type NomePolitica = keyof Politicas;

export const NENHUMA_POLITICA: Politicas = {
  reservaFria: false,
  retiradaTrem: false,
  operacaoDegradada: false,
  retornoParcial: false,
  rotaAlternativa: false,
  tratamentoCausaComum: false,
};

export const NOMES_POLITICAS: Record<NomePolitica, string> = {
  reservaFria: 'Reserva fria k-de-n',
  retiradaTrem: 'Retirada do trem falho',
  operacaoDegradada: 'Operação degradada (marcha lenta)',
  retornoParcial: 'Retorno parcial antes do trecho bloqueado',
  rotaAlternativa: 'Rota alternativa de passageiros',
  tratamentoCausaComum: 'Tratamento de causa comum',
};

/** Só a política indicada ligada. */
export function soPolitica(nome: NomePolitica): Politicas {
  return { ...NENHUMA_POLITICA, [nome]: true };
}
