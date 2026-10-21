// API pública do motor do simulador (specs 007, 008, 009 e 014).

export type { Cenario, Condicoes, Parametro, Parametros, RedeJson, Sentido, TipoDia } from './tipos';
export { TIPOS_DIA } from './tipos';
export type { Rede, Viagem } from './rede';
export { montaRede, trechoFisico, estacaoGlobal, trensProgramados, haversineKm } from './rede';
export { HIPOTESES_PADRAO, hipotese } from './hipoteses';
export type { NomeHipotese } from './hipoteses';
export type { Politicas, NomePolitica } from './politicas';
export { NENHUMA_POLITICA, NOMES_POLITICAS, soPolitica } from './politicas';
export type { Contexto } from './contexto';
export { preparaContexto, avisosDoCenario } from './contexto';
export type { EventoRegistro, FalhaInjetada, MetricasLinha, ResultadoDia, Trajetoria, TipoEvento } from './dia';
export { simulaDia, trensEmViagem, hashRegistro, LIMIAR_VIAGEM_AFETADA_S } from './dia';
export { estacionariaFrota, frotaCompletaMarkov, simulaFrota } from './frota';
export type { ParametrosFrota } from './frota';
export { faixaDe, multiplicador, FAIXAS_HORARIAS } from './taxas';
export { sementeDaRodada, misturaSemente, Rng } from './prng';
export type { Candidata, EstacaoNova, ItemRanking, AvaliacaoEstados, OpcoesEstados } from './expansao';
export { avaliaRedeAtual, avaliaCandidatas, buscaExaustiva, candidataLivre, candidatasDaBusca, AMOSTRAS_PADRAO } from './expansao';
