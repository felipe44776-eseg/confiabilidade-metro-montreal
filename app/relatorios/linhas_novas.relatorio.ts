// Relatório da spec 016 (linhas novas numa viagem) com o parametros.json real do pipeline.
// Roda com: npx vitest run --config vitest.relatorios.config.ts relatorios/linhas_novas.relatorio.ts
// Saída: ../fontes/verificacao/linhas_novas.md (DIAS_RELATORIO=200 roda mais curto, sem gravar).
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { it } from 'vitest';
import type { Estimativa } from '../src/mc/rodadas';
import { agrega } from '../src/mc/rodadas';
import { preparaContexto } from '../src/motor/contexto';
import type { Candidata } from '../src/motor/expansao';
import { candidataDesenhada } from '../src/motor/expansao';
import { preparaVariante } from '../src/motor/linhas_novas';
import type { Politicas } from '../src/motor/politicas';
import { NENHUMA_POLITICA } from '../src/motor/politicas';
import type { AvaliadorViagem } from '../src/motor/viagem';
import { nomesVariantes, preparaViagem, rodaViagem } from '../src/motor/viagem';
import type { CandidatasJson } from '../src/simulador/candidatas';
import { candidatasDoJson } from '../src/simulador/candidatas';
import { noves, novesIC, razaoPareada } from '../src/ui/escala';
import { carregaParametrosReais, carregaRede } from '../tests/motor/apoio';

const RAIZ = resolve(__dirname, '../..');
const SEMENTE = 20261021;
const DIAS = Number(process.env.DIAS_RELATORIO ?? 1000);
const GRAVA = DIAS === 1000;
const NOME_LINHA: Record<string, string> = { verde: 'Verde', laranja: 'Laranja', amarela: 'Amarela', azul: 'Azul' };
const fmt = (x: number, c = 2) => (Number.isFinite(x) ? x.toLocaleString('pt-BR', { minimumFractionDigits: c, maximumFractionDigits: c }) : x > 0 ? '∞' : '—');
const pc = (x: number, c = 2) => `${fmt(100 * x, c)}%`;
const sinal = (x: number, c: number) => `${x > 0 ? '+' : ''}${fmt(x, c)}`;
const ic = (e: Estimativa, f: (x: number) => string, min = -Infinity, max = Infinity) => `${f(e.media)} (${f(Math.max(min, e.ic95[0]))} a ${f(Math.min(max, e.ic95[1]))})`;
const dif = (e: Estimativa, f: (x: number) => string) => `${f(e.media)} (${f(e.ic95[0])} a ${f(e.ic95[1])})`;

interface Caso {
  titulo: string;
  de: string;
  para: string;
  linhas: () => Candidata[];
  politicas: Politicas[];
  causaComum?: boolean[];
  nota: string;
}

it('relatório das linhas novas numa viagem', { timeout: 3_600_000 }, () => {
  const rede = carregaRede();
  const p = carregaParametrosReais();
  const json = JSON.parse(readFileSync(resolve(RAIZ, 'dados/derivados/simulador/candidatas.json'), 'utf8')) as CandidatasJson;
  const oficiais = candidatasDoJson(json, rede);
  const oficial = (id: string) => () => [oficiais.find((c) => c.id === id)!];
  const desenhada = (a: string, b: string) => () => [candidataDesenhada(rede, [a, b], 0)];
  const nomeEst = (id: string) => rede.estacoes.find((e) => e.id === id)?.nome ?? id;
  const rota = { ...NENHUMA_POLITICA, rotaAlternativa: true };
  const parcial = { ...NENHUMA_POLITICA, retornoParcial: true };
  const CASOS: Caso[] = [
    {
      titulo: 'Atwater → Université-de-Montréal, com uma ligação desenhada entre as duas',
      de: 'STATION_M134',
      para: 'STATION_M536',
      linhas: desenhada('STATION_M134', 'STATION_M536'),
      politicas: [NENHUMA_POLITICA, rota],
      causaComum: [false, true],
      nota: 'A melhor ligação nova da busca da spec 014 (a Azul hoje só se liga à rede pela Laranja). A ligação vira o caminho de sempre: uma linha só, no lugar de Verde, Laranja e Azul.',
    },
    {
      titulo: 'Côte-Vertu → Montmorency, com o anel da Laranja (ARTM, 2019)',
      de: 'STATION_M222',
      para: 'STATION_M288',
      linhas: oficial('laranja_anel_artm_2019'),
      politicas: [NENHUMA_POLITICA, rota],
      nota: 'Hoje a viagem dá a volta pela Laranja inteira; o anel liga as duas pontas por Laval.',
    },
    {
      titulo: 'Vendôme → Place-des-Arts, com a Linha Rosa (proposta de 2017)',
      de: 'STATION_M242',
      para: 'STATION_M142',
      linhas: oficial('rosa_2017'),
      politicas: [NENHUMA_POLITICA, rota],
      nota: 'A Rosa encosta na Laranja em Vendôme e em Mont-Royal e na Verde em Place-des-Arts.',
    },
    {
      titulo: 'Angrignon → Saint-Michel (a viagem padrão), com uma ligação desenhada Angrignon–Snowdon',
      de: 'STATION_M118',
      para: 'STATION_M556',
      linhas: desenhada('STATION_M118', 'STATION_M236'),
      politicas: [NENHUMA_POLITICA, rota],
      nota: 'A ligação troca três linhas em série (Verde, Laranja, Azul) por duas (a ligação e a Azul).',
    },
    {
      titulo: 'Snowdon → Saint-Michel, com o prolongamento da Azul até Anjou',
      de: 'STATION_M236',
      para: 'STATION_M556',
      linhas: oficial('azul_anjou'),
      politicas: [NENHUMA_POLITICA, parcial],
      nota: 'A viagem não usa o trecho novo. Sem retorno parcial, uma falha no prolongamento para a Azul inteira; com retorno parcial, Saint-Michel continua ponto de retorno.',
    },
  ];
  const L: string[] = [
    '# Linhas novas numa viagem (spec 016)',
    '',
    `Gerado por \`app/relatorios/linhas_novas.relatorio.ts\` com o \`parametros.json\` real (código ${p.codigo_commit}). Cenário padrão (dia útil, condições de referência do modelo), ${DIAS.toLocaleString('pt-BR')} dias por caso, semente ${SEMENTE}: os mesmos dias da aba "Muitos dias" com essa semente. Média e intervalo de 95%.`,
    '',
    'Cada dia é simulado uma vez e medido duas vezes: na rede atual e na rede com a linha nova. A linha nova tem falhas e trens próprios, num fluxo de sorteio separado; as falhas da rede atual são as mesmas nas duas medidas. Por isso a diferença tem intervalo pareado, mais estreito que o de cada valor.',
    '',
    'Escala: perto de 100%, a disponibilidade esconde as diferenças. Ao lado dela vão o tempo sem caminho por dia, o número de noves (−log₁₀ da indisponibilidade: 99% são 2 noves, 99,9% são 3) e a razão do tempo sem caminho contra a rede atual.',
    '',
  ];
  const t0 = performance.now();
  for (const caso of CASOS) {
    L.push(`## ${caso.titulo}`, '', caso.nota, '');
    for (const pol of caso.politicas) {
      for (const cc of caso.causaComum ?? [false]) {
        const ctx = preparaContexto(rede, p, { tipoDia: 'util' });
        const base = preparaViagem(ctx, caso.de, caso.para, pol.rotaAlternativa)!;
        const v = preparaVariante(ctx, caso.linhas(), { politicas: pol, causaComumCompartilhada: cc });
        const av = preparaViagem(ctx, caso.de, caso.para, pol.rotaAlternativa, v)!;
        const avs: AvaliadorViagem[] = [base, av];
        const t1 = performance.now();
        const ag = agrega(rodaViagem(Array.from({ length: DIAS }, (_, i) => i), ctx, pol, SEMENTE, avs), nomesVariantes(avs), SEMENTE);
        const seg = (performance.now() - t1) / 1000;
        const m = ag.porMetrica;
        const rotulo = [
          pol.rotaAlternativa ? 'com rota alternativa' : 'sem rota alternativa',
          pol.retornoParcial ? 'com retorno parcial' : '',
          caso.causaComum ? (cc ? 'linha nova divide a causa comum com as linhas em que encosta' : 'linha nova independente') : '',
        ].filter(Boolean);
        const nomeNaRota = (a: AvaliadorViagem, l: string) => NOME_LINHA[l] ?? (l.startsWith('desenhada') ? 'linha desenhada' : (a.variante?.partes.find((x) => x.linha === l)?.nome ?? l));
        const caminho = (a: AvaliadorViagem) => a.rota.trechos.map((t) => `${nomeNaRota(a, t.linha)} até ${t.ateNome}`).join(', ');
        const razao = razaoPareada(m['v1.minSemCaminho'], m.minSemCaminho, m['d1.minSemCaminho']);
        const nb = novesIC(m.disp);
        const nv = novesIC(m['v1.disp']);
        L.push(
          `### ${rotulo.join('; ')}`,
          '',
          `| Medida | Rede atual | Com ${v.nome} | Com − atual (IC 95%, mesmo dia) |`,
          '|---|---|---|---|',
          `| Caminho de sempre | ${caminho(base)} | ${caminho(av)} | |`,
          `| Tempo programado do caminho (min) | ${fmt(base.rota.minutos, 1)} | ${fmt(av.rota.minutos, 1)} | ${sinal(av.rota.minutos - base.rota.minutos, 1)} |`,
          `| Disponibilidade da viagem | ${ic(m.disp, (x) => pc(x, 3), 0, 1)} | ${ic(m['v1.disp'], (x) => pc(x, 3), 0, 1)} | ${dif(m['d1.disp'], (x) => `${sinal(100 * x, 3)} pp`)} |`,
          `| Tempo sem caminho (min por dia) | ${ic(m.minSemCaminho, (x) => fmt(x, 2), 0)} | ${ic(m['v1.minSemCaminho'], (x) => fmt(x, 2), 0)} | ${dif(m['d1.minSemCaminho'], (x) => sinal(x, 2))} |`,
          `| Noves (−log₁₀ da indisponibilidade) | ${fmt(nb.media, 2)} (${fmt(nb.ic95[0], 2)} a ${fmt(nb.ic95[1], 2)}) | ${fmt(nv.media, 2)} (${fmt(nv.ic95[0], 2)} a ${fmt(nv.ic95[1], 2)}) | ${sinal(noves(m['v1.disp'].media) - noves(m.disp.media), 2)} |`,
          `| Tempo sem caminho com a linha nova ÷ rede atual | | | ${razao ? `${fmt(razao.media, 3)} (${fmt(razao.ic95[0], 3)} a ${fmt(razao.ic95[1], 3)})` : '—'} |`,
          `| Chance de chegar mais de 5 min atrasado | ${ic(m.atraso5, (x) => pc(x, 2), 0, 1)} | ${ic(m['v1.atraso5'], (x) => pc(x, 2), 0, 1)} | ${dif(m['d1.atraso5'], (x) => `${sinal(100 * x, 2)} pp`)} |`,
          `| Atraso médio por viagem (min) | ${ic(m.atrasoMedioMin, (x) => fmt(x, 2), 0)} | ${ic(m['v1.atrasoMedioMin'], (x) => fmt(x, 2), 0)} | ${dif(m['d1.atrasoMedioMin'], (x) => sinal(x, 2))} |`,
          `| Tempo médio da saída à chegada, com as falhas (min) | ${ic(m.tempoMedioMin, (x) => fmt(x, 1), 0)} | ${ic(m['v1.tempoMedioMin'], (x) => fmt(x, 1), 0)} | ${dif(m['d1.tempoMedioMin'], (x) => sinal(x, 2))} |`,
          `| Falhas da linha nova por dia | | ${ic(m['v1.falhasLinhaNova'], (x) => fmt(x, 3), 0)} | |`,
          '',
          `${fmt(seg, 1)} s para ${DIAS.toLocaleString('pt-BR')} dias nesta máquina (um processo). Hipóteses: ${v.hipoteses.join('; ')}.`,
          '',
        );
      }
    }
  }
  const minutos = (performance.now() - t0) / 60000;
  L.push(
    '## Como ler',
    '',
    '- A linha nova ajuda de dois jeitos: quando vira o caminho de sempre (menos linhas em série, viagem mais curta) e, com a rota alternativa, como caminho em paralelo.',
    '- Sem a rota alternativa, a pessoa usa só o caminho de sempre: se ele passa pela linha nova, a viagem passa a depender das falhas dela.',
    '- Um prolongamento que a viagem não usa não ajuda e, sem retorno parcial, piora: a falha no trecho novo para a linha inteira.',
    '- A linha nova herda as taxas por km e as durações das linhas atuais: não é mais confiável que elas por hipótese.',
    '',
    `Tempo de execução total: ${fmt(minutos, 1)} min (um processo).`,
  );
  const texto = L.join('\n') + '\n';
  if (GRAVA) writeFileSync(resolve(RAIZ, 'fontes/verificacao/linhas_novas.md'), texto);
  else if (process.env.SAIDA_RELATORIO) writeFileSync(process.env.SAIDA_RELATORIO, texto);
});
