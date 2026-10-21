// Relatório da spec 015 (confiabilidade de uma viagem) com o parametros.json real do pipeline.
// Roda com: npx vitest run --config vitest.relatorios.config.ts relatorios/viagem.relatorio.ts
// Saída: ../fontes/verificacao/viagem.md
import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { it } from 'vitest';
import type { Estimativa } from '../src/mc/rodadas';
import { agrega } from '../src/mc/rodadas';
import { preparaContexto } from '../src/motor/contexto';
import { NENHUMA_POLITICA, soPolitica } from '../src/motor/politicas';
import { LIMIARES_ATRASO_MIN, nomesViagem, preparaViagem, rodaViagem } from '../src/motor/viagem';
import { carregaParametrosReais, carregaRede } from '../tests/motor/apoio';

const RAIZ = resolve(__dirname, '../..');
const SEMENTE = 20261021;
const DIAS = 1000;
/** Viagens representativas: série de três linhas, atalho pela Azul, Amarela com baldeação, par com alternativa, uma linha só. */
const VIAGENS: [string, string][] = [
  ['STATION_M118', 'STATION_M556'], // Angrignon → Saint-Michel
  ['STATION_M222', 'STATION_M288'], // Côte-Vertu → Montmorency
  ['STATION_M454', 'STATION_M236'], // Longueuil → Snowdon
  ['STATION_M132', 'STATION_M146'], // Lionel-Groulx → Berri-UQAM
  ['STATION_M134', 'STATION_M146'], // Atwater → Berri-UQAM
];
const NOME_LINHA: Record<string, string> = { verde: 'Verde', laranja: 'Laranja', amarela: 'Amarela', azul: 'Azul' };
const fmt = (x: number, c = 2) => x.toLocaleString('pt-BR', { minimumFractionDigits: c, maximumFractionDigits: c });
const pc = (x: number, c = 2) => `${fmt(100 * x, c)}%`;
/** Proporção com IC recortado em [0, 1]. */
const pIc = (e: Estimativa, c = 2) => `${pc(e.media, c)} (${pc(Math.max(0, e.ic95[0]), c)} a ${pc(Math.min(1, e.ic95[1]), c)})`;
/** Grandeza que não fica negativa, com o IC recortado em 0. */
const nIc = (e: Estimativa, c = 1) => `${fmt(e.media, c)} (${fmt(Math.max(0, e.ic95[0]), c)} a ${fmt(e.ic95[1], c)})`;

it('relatório da viagem de A a B', { timeout: 3_600_000 }, () => {
  const rede = carregaRede();
  const p = carregaParametrosReais();
  const ctx = preparaContexto(rede, p, { tipoDia: 'util' });
  const nome = (id: string) => rede.estacoes.find((e) => e.id === id)?.nome ?? id;
  const L: string[] = [
    '# Confiabilidade de uma viagem (spec 015)',
    '',
    `Gerado por \`app/relatorios/viagem.relatorio.ts\` com o \`parametros.json\` real (código ${p.codigo_commit}). Cenário padrão (dia útil, condições de referência do modelo), ${DIAS.toLocaleString('pt-BR')} dias por viagem, semente ${SEMENTE}: os mesmos dias da aba "Muitos dias" com essa semente. Média e intervalo de 95%.`,
    '',
    'Disponibilidade: fração da janela de serviço da rede em que o caminho existe, a partir dos bloqueios do dia no grafo das estações (o mesmo método da disponibilidade origem-destino da spec 009). "Produto" é o valor em série, multiplicando as disponibilidades dos trechos como se as linhas falhassem de forma independente. Atraso: saídas a cada 10 minutos; para cada uma, a chegada mais cedo com os trens simulados do dia contra a mesma saída num dia sem falhas.',
    '',
  ];
  const t0 = performance.now();
  for (const [o, d] of VIAGENS) {
    const linhas: string[] = [];
    const res: Record<string, ReturnType<typeof agrega>> = {};
    let caminho = '';
    for (const alt of [false, true]) {
      const av = preparaViagem(ctx, o, d, alt);
      if (!av) throw new Error(`sem caminho de ${o} a ${d}`);
      if (!alt) caminho = av.rota.trechos.map((t) => `${NOME_LINHA[t.linha] ?? t.linha} de ${t.deNome} a ${t.ateNome}`).join(', baldeação, ');
      res[alt ? 'com' : 'sem'] = agrega(rodaViagem(Array.from({ length: DIAS }, (_, i) => i), ctx, alt ? soPolitica('rotaAlternativa') : NENHUMA_POLITICA, SEMENTE, av), nomesViagem(av), SEMENTE);
      if (!alt) {
        const m = res.sem.porMetrica;
        const produto = av.rota.trechos.reduce((s, _, i) => s * m[`disp.trecho.${i}`].media, 1);
        linhas.push(
          `| Trechos | ${av.rota.trechos.map((t, i) => `${NOME_LINHA[t.linha] ?? t.linha} ${pIc(m[`disp.trecho.${i}`])}`).join('; ')} |`,
          `| Produto dos trechos (série) | ${pc(produto)} |`,
          `| Viagem inteira, simulada | ${pIc(m.disp)} |`,
          `| Minutos por dia sem caminho | ${nIc(m.minSemCaminho)} |`,
          `| Dias com ao menos uma interrupção no caminho | ${pIc(m.diaComInterrupcao, 1)} |`,
          ...LIMIARES_ATRASO_MIN.map((l) => `| Chance de chegar mais de ${l} min atrasado | ${pIc(m[`atraso${l}`])} |`),
          `| Chance de não chegar até o fim do serviço | ${pIc(m.naoChega, 4)} |`,
          `| Atraso médio por viagem (min) | ${nIc(m.atrasoMedioMin, 2)} |`,
        );
      } else {
        const m = res.com.porMetrica;
        linhas.push(
          `| Com rota alternativa: viagem inteira | ${pIc(m.disp)} |`,
          `| Com rota alternativa: chance de mais de ${LIMIARES_ATRASO_MIN[0]} min | ${pIc(m[`atraso${LIMIARES_ATRASO_MIN[0]}`])} |`,
          `| Com rota alternativa: atraso médio (min) | ${nIc(m.atrasoMedioMin, 2)} |`,
        );
      }
    }
    L.push(`## ${nome(o)} → ${nome(d)}`, '', `Caminho de sempre: ${caminho}.`, '', '| Medida | Valor (IC 95%) |', '|---|---|', ...linhas, '');
  }
  const minutos = (performance.now() - t0) / 60000;
  L.push(
    '## Como ler',
    '',
    '- Se o produto dos trechos cai dentro do intervalo do simulado, as linhas do caminho falham quase de forma independente: a viagem é um sistema em série.',
    '- Quando a mesma linha aparece em dois trechos (Côte-Vertu → Montmorency usa a Laranja duas vezes), uma falha nela para os dois ao mesmo tempo: os trechos não são independentes e o produto fica abaixo do simulado. Sem a política de retorno parcial, qualquer falha numa linha tira a linha inteira do caminho.',
    '- Com a rota alternativa, a viagem só fica sem caminho quando nenhum caminho está livre (paralelo). A escolha supõe que a pessoa sabe quanto vai durar cada interrupção: é o limite otimista da política.',
    '- O atraso médio é puxado pelas poucas saídas que pegam uma interrupção longa: a amostra de durações da STM tem paradas de horas.',
    '- Não entram ônibus de substituição, caminhada até a plataforma nem lotação.',
    '',
    `Tempo de execução nesta máquina: ${fmt(minutos, 1)} min (um processo).`,
  );
  writeFileSync(resolve(RAIZ, 'fontes/verificacao/viagem.md'), L.join('\n') + '\n');
});
