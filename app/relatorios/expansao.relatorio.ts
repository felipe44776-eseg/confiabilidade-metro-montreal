// Relatório da spec 014 (que linha construir) com o motor e o parametros.json real do pipeline.
// Roda com: npx vitest run --config vitest.relatorios.config.ts relatorios/expansao.relatorio.ts
// Saídas: ../fontes/verificacao/expansao.md e ../dados/derivados/simulador/expansao.json
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { it } from 'vitest';
import type { EstimativaSimples, ItemRanking } from '../src/motor/expansao';
import { avaliaCandidatas, avaliaRedeAtual, buscaExaustiva } from '../src/motor/expansao';
import { agrega, nomesMetricas, rodaRodadas } from '../src/mc/rodadas';
import { preparaContexto } from '../src/motor/contexto';
import { NENHUMA_POLITICA } from '../src/motor/politicas';
import { candidatasDoJson, NOMES_CANDIDATAS } from '../src/simulador/candidatas';
import type { CandidatasJson } from '../src/simulador/candidatas';
import { carregaParametrosReais, carregaRede } from '../tests/motor/apoio';

const RAIZ = resolve(__dirname, '../..');
const SEMENTE = 20261021;
const AMOSTRAS = 200_000;
const DIST_MAX_KM = 3;
const pct = (x: number, c = 4) => (100 * x).toLocaleString('pt-BR', { minimumFractionDigits: c, maximumFractionDigits: c });
const num = (x: number, c = 0) => x.toLocaleString('pt-BR', { minimumFractionDigits: c, maximumFractionDigits: c });
const icPct = (e: EstimativaSimples) => `${pct(e.media)} (${pct(e.ic95[0])} a ${pct(e.ic95[1])})`;
const icMin = (e: EstimativaSimples) => `${num(e.media)} (${num(e.ic95[0])} a ${num(e.ic95[1])})`;

function resumo(i: ItemRanking) {
  return {
    id: i.candidata.id, nome: i.candidata.nome, status: i.candidata.status, fonte: i.candidata.fonte, km: i.km,
    ganho: i.ganho, ganho_com_causa_comum: i.ganhoComCausaComum, ganho_por_km: i.ganhoPorKm, minutos_par_ano_evitados: i.minutosParAnoEvitados,
    amostras: i.amostras, semente: i.semente, hipoteses: i.hipoteses,
  };
}

it('relatório da expansão da rede', { timeout: 3_600_000 }, () => {
  const rede = carregaRede();
  const p = carregaParametrosReais();
  const json = JSON.parse(readFileSync(resolve(RAIZ, 'dados/derivados/simulador/candidatas.json'), 'utf8')) as CandidatasJson;
  const candidatas = candidatasDoJson(json, rede);
  const cenario = { tipoDia: 'util' as const };
  const atual = avaliaRedeAtual(rede, p, cenario, { amostras: AMOSTRAS, semente: SEMENTE });
  // Validação da spec 014: método de estados contra a camada diária, mesma rede e mesmos parâmetros
  const diaria = agrega(rodaRodadas(Array.from({ length: 4000 }, (_, i) => i), preparaContexto(rede, p, cenario), NENHUMA_POLITICA, SEMENTE), nomesMetricas(rede.ids), SEMENTE);
  const semRota = avaliaRedeAtual(rede, p, cenario, { amostras: AMOSTRAS, semente: SEMENTE, rotaAlternativa: false });
  const validacao = rede.ids.map((l) => ({ linha: l, diaria: diaria.porMetrica[`${l}.disponibilidade`], estados: semRota.dispLinha[l],
    dif_pp: 100 * (semRota.dispLinha[l].media - diaria.porMetrica[`${l}.disponibilidade`].media) }));
  const variantes = {
    sem_retorno_parcial: avaliaCandidatas(rede, p, cenario, candidatas, { amostras: AMOSTRAS, semente: SEMENTE, retornoParcial: false }),
    com_retorno_parcial: avaliaCandidatas(rede, p, cenario, candidatas, { amostras: AMOSTRAS, semente: SEMENTE, retornoParcial: true }),
  };
  const busca = buscaExaustiva(rede, p, cenario, DIST_MAX_KM, { amostras: AMOSTRAS / 4, semente: SEMENTE });
  const saida = {
    semente: SEMENTE, amostras: AMOSTRAS, codigo_parametros: p.codigo_commit, rede_atual: atual, validacao_contra_camada_diaria: validacao,
    candidatas: Object.fromEntries(Object.entries(variantes).map(([k, v]) => [k, v.map(resumo)])),
    busca_exaustiva: { distancia_max_km: DIST_MAX_KM, amostras: AMOSTRAS / 4, por_ganho: busca.porGanho.slice(0, 15).map(resumo), por_km: busca.porKm.slice(0, 15).map(resumo) },
  };
  writeFileSync(resolve(RAIZ, 'dados/derivados/simulador/expansao.json'), JSON.stringify(saida, null, 1) + '\n');

  const L: string[] = [
    '# Expansão da rede: que linha construir (spec 014)',
    '',
    `Gerado por \`app/relatorios/expansao.relatorio.ts\` com o motor do simulador e o \`parametros.json\` real (${p.codigo_commit}). ` +
      `Método de estados: ${num(AMOSTRAS)} sorteios do estado de cada trecho (aberto ou bloqueado, pela taxa de falha e pela duração), semente ${SEMENTE}, dia útil. ` +
      'A disponibilidade origem-destino é a fração dos pares de estações atuais com caminho, ponderada pela oferta de hoje; o ganho de cada candidata é pareado com a rede atual.',
    '',
    `Rede atual: disponibilidade origem-destino ${icPct(atual.dispOD)}%; minutos de par interrompido por ano ${icMin(atual.minutosParAno)}.`,
    '',
    '## Validação: método de estados contra a camada diária (critério: até 0,1 p.p.)',
    '',
    '| Linha | Camada diária (4.000 dias úteis) | Método de estados | Diferença (p.p.) |',
    '|---|---|---|---|',
    ...validacao.map((v) => `| ${v.linha} | ${pct(v.diaria.media, 3)}% | ${pct(v.estados.media, 3)}% | ${num(v.dif_pp, 3)} |`),
    '',
  ];
  for (const [nome, lista] of Object.entries(variantes)) {
    L.push(
      `## Candidatas oficiais e propostas, ${nome === 'sem_retorno_parcial' ? 'sem retorno parcial (trecho bloqueado para a linha inteira)' : 'com retorno parcial nas pontas de viagem (hipótese)'}`,
      '',
      '| Candidata | Status do traçado | km (aprox.) | Ganho de disponibilidade OD, p.p. (IC 95%) | Com causa comum compartilhada | Ganho por km (p.p./km) | Minutos de par evitados por ano |',
      '|---|---|---|---|---|---|---|',
    );
    for (const i of lista)
      L.push(`| ${NOMES_CANDIDATAS[i.candidata.id] ?? i.candidata.nome} | ${i.candidata.status} | ${num(i.km, 1)} | ${icPct(i.ganho)} | ${icPct(i.ganhoComCausaComum)} | ${pct(i.ganhoPorKm, 5)} | ${icMin(i.minutosParAnoEvitados)} |`);
    L.push('');
  }
  L.push(
    `## Busca exaustiva: ligações diretas entre estações atuais até ${DIST_MAX_KM} km em linha reta`,
    '',
    `${busca.porGanho.length} ligações avaliadas com ${num(AMOSTRAS / 4)} sorteios cada (sem retorno parcial). As 15 melhores por ganho:`,
    '',
    '| Ligação | km (aprox.) | Ganho de disponibilidade OD, p.p. (IC 95%) | Com causa comum | Ganho por km |',
    '|---|---|---|---|---|',
    ...busca.porGanho.slice(0, 15).map((i) => `| ${i.candidata.nome} | ${num(i.km, 1)} | ${icPct(i.ganho)} | ${icPct(i.ganhoComCausaComum)} | ${pct(i.ganhoPorKm, 5)} |`),
    '',
    'As 15 melhores por ganho por km:',
    '',
    '| Ligação | km (aprox.) | Ganho por km (p.p./km) | Ganho (p.p.) |',
    '|---|---|---|---|',
    ...busca.porKm.slice(0, 15).map((i) => `| ${i.candidata.nome} | ${num(i.km, 1)} | ${pct(i.ganhoPorKm, 5)} | ${icPct(i.ganho)} |`),
    '',
    '## Como ler',
    '',
    '- Ganho = disponibilidade origem-destino com a candidata menos a da rede atual, nos pares de estações que já existem. Uma ligação vale pelos caminhos alternativos que cria.',
    '- Um ramal (prolongamento que não fecha ciclo) não cria caminho alternativo e acrescenta trechos que podem falhar. Sem retorno parcial, uma falha no prolongamento para a linha inteira, e por isso o ganho pode ser negativo. A cobertura de bairros novos não entra: não há dado de passageiros.',
    '- "Com causa comum compartilhada": a candidata divide alimentação e controle com as linhas em que encosta e para junto nos eventos de causa comum.',
    `- km: linha reta × fator de traçado (${num(p.hipoteses.fator_tracado_candidata?.valor ?? 1.2, 1)}, hipótese). A busca exaustiva filtra pela distância em linha reta (até ${DIST_MAX_KM} km), por isso aparecem ligações com mais de ${DIST_MAX_KM} km de via.`,
    '- Pesos: cada par de estações pesa pela oferta das linhas que o servem. Como quase todas as viagens percorrem a linha inteira, as estações de uma mesma linha pesam igual, e ligações que unem as mesmas duas linhas dão o mesmo ganho.',
    '- A ligação Atwater (Verde) – Université-de-Montréal (Azul) lidera porque hoje a Azul só se liga ao resto da rede pela Laranja (Snowdon e Jean-Talon): quando a Laranja para, a Azul fica isolada. Uma ligação direta da Azul com outra linha remove esse ponto único de falha.',
    '- Hipóteses: traçado aproximado (linha reta × fator de traçado), velocidade comercial, taxas de falha por km herdadas da linha ou da média da rede. Ver a coluna de hipóteses em `dados/derivados/simulador/expansao.json`.',
    '',
  );
  writeFileSync(resolve(RAIZ, 'fontes/verificacao/expansao.md'), L.join('\n') + '\n');
});
