// Hipóteses do motor: parâmetros sem dado, ajustáveis na interface, sempre com status "hipótese".
// O valor vem, nesta ordem: do cenário (controle da interface), de parametros.hipoteses e, por
// último, do padrão abaixo. As cinco últimas foram criadas pelo motor e ainda não estão no
// parametros.json gerado por pipeline/parametros.py.

import type { Cenario, Parametros } from './tipos';

export const HIPOTESES_PADRAO = {
  reparo_oficina_dias: 1, // tempo médio de reparo de um trem retirado (0,5 a 4)
  p_retirada: 1, // parcela das falhas de material rodante que retira o trem de serviço
  reservas_por_linha: 2, // trens de reserva por linha, com a política de reserva fria
  intervalo_minimo_s: 90, // separação mínima entre trens que entram no mesmo trecho
  sentidos_bloqueio_ef: 2, // falha de equipamento fixo bloqueia 1 ou 2 sentidos
  fator_velocidade_degradada: 1.25, // multiplica o tempo de percurso na operação degradada
  duracao_degradada_min: 30, // não usado pelo motor (ver specs/008-politicas/plan.md)
  tempo_transferencia_min: 4, // transferência nas estações de correspondência
  reducao_causa_comum: 0, // redução da taxa de causa comum com alimentação ou controle redundante
  velocidade_comercial_candidata_kmh: 36, // linha candidata da spec 014
  // Criadas pelo motor:
  tempo_retirada_min: 10, // política de retirada: tempo-alvo para tirar o trem falho da via (5 a 30)
  tempo_ativacao_degradada_min: 5, // política de operação degradada: parada antes da marcha lenta (2 a 15)
  reducao_causa_comum_politica: 0.5, // usada pela política de causa comum quando reducao_causa_comum é 0
  fator_tracado_candidata: 1.2, // km de via / distância em linha reta, para candidatas sem km informado
  km_minimo_candidata: 0.3, // ligação candidata mais curta aceita na busca exaustiva
} as const;

export type NomeHipotese = keyof typeof HIPOTESES_PADRAO;

export function hipotese(nome: NomeHipotese, parametros: Parametros, cenario?: Cenario): number {
  const doCenario = cenario?.hipoteses?.[nome];
  if (doCenario !== undefined) return doCenario;
  const doArquivo = parametros.hipoteses?.[nome]?.valor;
  if (doArquivo !== undefined) return doArquivo;
  return HIPOTESES_PADRAO[nome];
}
