// Relatório das specs 008 (políticas) e 009 (Monte Carlo) com o parametros.json real do pipeline.
// Roda com: npx vitest run --config vitest.relatorios.config.ts relatorios/politicas.relatorio.ts
// Saídas: ../fontes/verificacao/politicas.md e ../dados/derivados/simulador/politicas.json
import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { it } from 'vitest';
import type { Estimativa, Rodada } from '../src/mc/rodadas';
import { agrega, anualiza, estimativa, nomesMetricas, rodaRodadas, rodadasParaPrecisao } from '../src/mc/rodadas';
import { avisosDoCenario, preparaContexto } from '../src/motor/contexto';
import type { NomePolitica } from '../src/motor/politicas';
import { NENHUMA_POLITICA, NOMES_POLITICAS, soPolitica } from '../src/motor/politicas';
import { TIPOS_DIA } from '../src/motor/tipos';
import { carregaParametrosReais, carregaRede } from '../tests/motor/apoio';

const RAIZ = resolve(__dirname, '../..');
const SEMENTE = 20261021;
const N_POLITICA = 3000; // dias úteis por política e por tempo de reparo
const N_ANO = 4000; // dias por tipo de dia para a comparação anual com o painel
const REPAROS = [0.5, 1, 2, 4];
const POLITICAS = Object.keys(NOMES_POLITICAS) as NomePolitica[];
const fmt = (x: number, c = 1) => x.toLocaleString('pt-BR', { minimumFractionDigits: c, maximumFractionDigits: c });
const ic = (e: Estimativa, c = 1) => `${fmt(e.media, c)} (${fmt(e.ic95[0], c)} a ${fmt(e.ic95[1], c)})`;

/** Diferença pareada (B − A) de uma soma de métricas. */
function difSoma(rodadas: Rodada[], indices: number[]): Estimativa {
  return estimativa(
    rodadas.map((r) => indices.reduce((s, j) => s + ((r.valoresB as number[])[j] - r.valores[j]), 0)),
    SEMENTE,
  );
}

it('relatório das políticas e do Monte Carlo', { timeout: 3_600_000 }, () => {
  const rede = carregaRede();
  const p = carregaParametrosReais();
  const nomes = nomesMetricas(rede.ids);
  const j = (m: string) => nomes.indexOf(m);
  const porCausa = (c: 'MR' | 'EF' | 'CC') => rede.ids.map((l) => j(`${l}.minutos${c}`));
  const saida: Record<string, unknown> = { semente: SEMENTE, rodadas_por_politica: N_POLITICA, rodadas_por_tipo_dia: N_ANO, codigo_parametros: p.codigo_commit };

  // ---- 009: minutos por ano por linha (sem políticas), comparação com o painel, precisão e tempo
  const anual: Record<string, Estimativa> = {};
  const precisao: Record<string, number> = {};
  const t0 = performance.now();
  const porTipo: Record<string, ReturnType<typeof agrega>> = {};
  for (const tipo of TIPOS_DIA) {
    const ctx = preparaContexto(rede, p, { tipoDia: tipo });
    porTipo[tipo] = agrega(rodaRodadas(Array.from({ length: N_ANO }, (_, i) => i), ctx, NENHUMA_POLITICA, SEMENTE), nomes, SEMENTE);
  }
  const segundos = (performance.now() - t0) / 1000;
  for (const l of [...rede.ids, 'rede']) {
    const m = `${l}.minutosInterrupcao`;
    anual[l] = anualiza({ util: porTipo.util.porMetrica[m], sabado: porTipo.sabado.porMetrica[m], domingo: porTipo.domingo.porMetrica[m] });
    if (l !== 'rede') precisao[l] = rodadasParaPrecisao(porTipo.util.porMetrica[m]);
  }
  const ccLaranja = anualiza({
    util: porTipo.util.porMetrica['laranja.minutosCC'],
    sabado: porTipo.sabado.porMetrica['laranja.minutosCC'],
    domingo: porTipo.domingo.porMetrica['laranja.minutosCC'],
  });
  saida.minutos_por_ano = anual;
  saida.minutos_cc_laranja_por_ano = ccLaranja;
  saida.rodadas_para_5pct_dia_util = precisao;
  // tempo de relógio fica só no relatório .md: no JSON versionado, mudaria o hash a cada execução
  const meia50k: Record<string, number> = {};
  for (const l of rede.ids) meia50k[l] = 5 * Math.sqrt(precisao[l] / 50_000); // meia-largura (% da média) esperada com o teto de 50.000 dias
  saida.meia_largura_pct_com_50000_dias = meia50k;
  const disp: Record<string, Estimativa> = {};
  for (const l of rede.ids) disp[l] = porTipo.util.porMetrica[`${l}.disponibilidade`];
  saida.disponibilidade_dia_util = disp;
  saida.disp_od_dia_util = porTipo.util.porMetrica['rede.dispOD'];

  // ---- 008: cada política contra nenhuma, com números aleatórios comuns, para cada tempo de reparo
  const tabela: Record<string, Record<string, Record<string, Estimativa>>> = {};
  for (const reparo of REPAROS) {
    const ctx = preparaContexto(rede, p, { tipoDia: 'util', hipoteses: { reparo_oficina_dias: reparo } });
    tabela[String(reparo)] = {};
    for (const pol of POLITICAS) {
      const rod = rodaRodadas(Array.from({ length: N_POLITICA }, (_, i) => i), ctx, NENHUMA_POLITICA, SEMENTE, soPolitica(pol));
      const ag = agrega(rod, nomes, SEMENTE);
      const dif = ag.diferenca as Record<string, Estimativa>;
      tabela[String(reparo)][pol] = {
        minutos_rede: dif['rede.minutosInterrupcao'],
        trens_hora: dif['rede.trensHoraPerdidos'],
        disp_od_pp: estimativa(rod.map((r) => 100 * ((r.valoresB as number[])[j('rede.dispOD')] - r.valores[j('rede.dispOD')])), SEMENTE),
        par_interrompido_min: dif['rede.minutosParInterrompido'],
        minutos_MR: difSoma(rod, porCausa('MR')),
        minutos_EF: difSoma(rod, porCausa('EF')),
        minutos_CC: difSoma(rod, porCausa('CC')),
        frota_completa_laranja_pp: estimativa(rod.map((r) => 100 * ((r.valoresB as number[])[j('laranja.frotaCompleta')] - r.valores[j('laranja.frotaCompleta')])), SEMENTE),
      };
    }
  }
  saida.politicas = tabela;
  const avisos = avisosDoCenario(preparaContexto(rede, p, { tipoDia: 'util' }), { ...NENHUMA_POLITICA, retornoParcial: true, reservaFria: true });
  saida.avisos = avisos;
  writeFileSync(resolve(RAIZ, 'dados/derivados/simulador/politicas.json'), JSON.stringify(saida, null, 1) + '\n');

  // ---- relatório
  const L: string[] = [
    '# Políticas de tolerância a falhas e Monte Carlo (specs 008 e 009)',
    '',
    `Gerado por \`app/relatorios/politicas.relatorio.ts\` com o motor do simulador e o \`parametros.json\` real (${p.codigo_commit}), semente ${SEMENTE}. ` +
      'Intervalos de 95% pela aproximação normal; diferenças pareadas com números aleatórios comuns (as mesmas falhas nas duas variantes).',
    '',
    '## Minutos de interrupção por ano, sem políticas (spec 009)',
    '',
    `${N_ANO} dias simulados por tipo de dia (útil, sábado, domingo), somados pelo calendário de 251, 52 e 62 dias. Tempo: ${fmt(segundos, 1)} s para ${3 * N_ANO} dias numa thread.`,
    '',
    '| Linha | Minutos por ano (IC 95%) | Disponibilidade no dia útil | Rodadas para 5% de precisão no dia útil | Meia-largura com 50.000 dias (% da média) |',
    '|---|---|---|---|---|',
  ];
  for (const l of rede.ids) L.push(`| ${l} | ${ic(anual[l], 0)} | ${fmt(100 * disp[l].media, 3)}% | ${precisao[l].toLocaleString('pt-BR')} | ${fmt(meia50k[l], 1)} |`);
  L.push(
    `| rede (soma) | ${ic(anual.rede, 0)} | disponibilidade origem-destino ${fmt(100 * porTipo.util.porMetrica['rede.dispOD'].media, 3)}% | |`,
    '',
    `Laranja contra o painel: o painel tem 1.852 min/ano (Monte Carlo) e 1.797 (analítico). O intervalo do motor é ${fmt(anual.laranja.ic95[0], 0)} a ${fmt(anual.laranja.ic95[1], 0)} ` +
      `(${anual.laranja.ic95[0] <= 1852 && 1852 <= anual.laranja.ic95[1] ? 'contém 1.852' : 'não contém 1.852'}; ${anual.laranja.ic95[0] <= 1797 && 1797 <= anual.laranja.ic95[1] ? 'contém 1.797' : 'não contém 1.797'}). ` +
      `Diferenças de definição: o motor soma a causa comum de todos os grupos de linhas que incluem a Laranja (${fmt(ccLaranja.media, 0)} min/ano; 44 dos 45 eventos multilinha), ` +
      'o painel só a Verde–Laranja (31 eventos); o motor usa a taxa de 2025 do modelo da spec 005 e o horário do GTFS, o painel a média de 2019 a 2026; ' +
      'o motor conta a união dos intervalos bloqueados (falhas sobrepostas não somam duas vezes), o painel soma as durações. ' +
      'A duração positiva é sorteada da amostra observada (a média observada era 23% a 29% maior que a da lognormal na Laranja; decisão de 2026-10-21).',
    '',
    '## Cada política contra nenhuma política (spec 008)',
    '',
    `${N_POLITICA} dias úteis por política. Valores negativos = a política reduz. "Minutos" é a soma das quatro linhas por dia útil; MR, EF e CC separam o efeito pela causa da interrupção.`,
    '',
  );
  for (const reparo of REPAROS) {
    L.push(`### Reparo na oficina de ${fmt(reparo, 1)} dia(s) (hipótese)`, '', '| Política | Minutos de interrupção | Material rodante | Equip. fixos | Causa comum | Trens-hora perdidos | Disp. origem-destino (p.p.) | Frota completa na Laranja (p.p.) |', '|---|---|---|---|---|---|---|---|');
    for (const pol of POLITICAS) {
      const x = tabela[String(reparo)][pol];
      L.push(`| ${NOMES_POLITICAS[pol]} | ${ic(x.minutos_rede)} | ${ic(x.minutos_MR)} | ${ic(x.minutos_EF)} | ${ic(x.minutos_CC)} | ${ic(x.trens_hora, 2)} | ${ic(x.disp_od_pp, 3)} | ${ic(x.frota_completa_laranja_pp, 1)} |`);
    }
    L.push('');
  }
  L.push(
    '## Hipóteses e avisos',
    '',
    ...avisos.map((a) => `- ${a}`),
    '- O retorno parcial usa só as pontas de viagem do horário: a posição dos aparelhos de mudança de via não está verificada. O resultado dessa política é hipótese.',
    '- O tempo de reparo na oficina não está em nenhuma fonte (0,5 a 4 dias); a sensibilidade está nas tabelas acima.',
    '',
  );
  writeFileSync(resolve(RAIZ, 'fontes/verificacao/politicas.md'), L.join('\n') + '\n');
});
