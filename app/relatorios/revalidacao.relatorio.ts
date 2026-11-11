// Spec 020: o simulador revisto reproduz o histórico de cada linha × família? Compara com o observado e com a v1.1.0.
// Roda com: npx vitest run --config vitest.relatorios.config.ts relatorios/revalidacao.relatorio.ts
// Saídas: ../fontes/verificacao/revalidacao.md e ../dados/derivados/simulador/revalidacao.json
// Critério da spec 020, declarado antes: média simulada dentro do IC 95% por blocos semanais do observado em 2025 (o
// ano-base dos parâmetros); ao lado, a tolerância de 15% da spec 009 e a dispersão diária (variância ÷ média).
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { gunzipSync } from 'node:zlib';
import { it } from 'vitest';
import { preparaContexto } from '../src/motor/contexto';
import type { Grafo as GrafoOD } from '../src/motor/grafo';
import { CLASSES_GRAVIDADE, simulaDia } from '../src/motor/dia';
import { NENHUMA_POLITICA } from '../src/motor/politicas';
import { sementeDaRodada } from '../src/motor/prng';
import type { Condicoes, Parametros, TipoDia } from '../src/motor/tipos';
import { carregaParametrosReais, carregaRede } from '../tests/motor/apoio';

const RAIZ = resolve(__dirname, '../..');
const SEMENTE = 20261110;
const K = 6; // simulações de cada dia de 2025
type Grafo = { tipoDia: TipoDia; g: GrafoOD };
const LINHAS = ['verde', 'laranja', 'amarela', 'azul'];
const FAMILIAS = ['MR', 'EF', 'CC'] as const;
const TOLERANCIA = 0.15;
// Indicador publicado pela STM (todas as causas): relatórios anuais 2019–2022 e "Principaux indicateurs et résultats au 2025-12-31"
const STM_PUBLICADO: Record<string, number> = { '2019': 10.6, '2020': 9.2, '2021': 9.4, '2022': 10.4, '2023': 13.2, '2024': 13.0, '2025': 11.66 };
const fmt = (x: number, c = 1) => (Number.isFinite(x) ? x.toLocaleString('pt-BR', { minimumFractionDigits: c, maximumFractionDigits: c }) : '—');

function csv(caminho: string): Record<string, string>[] {
  const [cab, ...linhas] = readFileSync(caminho, 'utf8').trim().split(/\r?\n/);
  const nomes = cab.split(';');
  return linhas.map((l) => Object.fromEntries(l.split(';').map((v, i) => [nomes[i], v])));
}

interface Simulado {
  ano: Record<string, Record<string, number>>; // linha -> métrica -> por ano
  dispersao: Record<string, Record<string, number>>; // linha -> família -> variância ÷ média das falhas por dia (dia útil)
}

/** Condições de cada hora de serviço de 2025 (clima, estação, eventos, tipo de dia), tiradas do painel do modelo. */
function condicoes2025(): { data: string; tipoDia: TipoDia; porHora: Record<number, Condicoes> }[] {
  const texto = gunzipSync(readFileSync(resolve(RAIZ, 'dados/derivados/modelos/painel_modelo.csv.gz'))).toString('utf8');
  const [cab, ...linhas] = texto.trim().split(/\r?\n/);
  const n = cab.split(';');
  const i = (c: string) => n.indexOf(c);
  const dias = new Map<string, { tipoDia: TipoDia; porHora: Record<number, Condicoes> }>();
  for (const s of linhas) {
    const v = s.split(';');
    if (!v[i('data_servico')].startsWith('2025') || v[i('linha')] !== 'laranja') continue; // as condições são as mesmas em todas as linhas
    const d = v[i('data_servico')];
    const dia = dias.get(d) ?? { tipoDia: v[i('tipo_dia')] as TipoDia, porHora: {} };
    dia.porHora[Number(v[i('hora')])] = Object.fromEntries(
      ['estacao', 'temp', 'precip', 'cond', 'neve_solo', 'jogo', 'gp_fds', 'feriado'].map((c) => [c, v[i(c)]]),
    );
    dias.set(d, dia);
  }
  return [...dias.entries()].map(([data, x]) => ({ data, ...x }));
}

/** Cada dia de 2025 com as suas condições, K vezes (sementes diferentes); greves não entram (serviço normal). */
function simula(p: Parametros, dias: ReturnType<typeof condicoes2025>): Simulado {
  const rede = carregaRede();
  const ano: Simulado['ano'] = Object.fromEntries(LINHAS.map((l) => [l, {} as Record<string, number>]));
  const dispersao: Simulado['dispersao'] = Object.fromEntries(LINHAS.map((l) => [l, {} as Record<string, number>]));
  const diarios: Record<string, Record<string, number[]>> = Object.fromEntries(LINHAS.map((l) => [l, { MR: [], EF: [], CC: [] }]));
  let grafo: Grafo | undefined;
  dias.forEach((dia, di) => {
    const ctx = preparaContexto(rede, p, { tipoDia: dia.tipoDia, condicoesPorHora: dia.porHora }, grafo?.tipoDia === dia.tipoDia ? grafo.g : undefined);
    grafo = { tipoDia: dia.tipoDia, g: ctx.grafo };
    for (let k = 0; k < K; k++) {
      const r = simulaDia(ctx, NENHUMA_POLITICA, sementeDaRodada(SEMENTE, di * K + k), { registrar: false, odDaRede: false });
      for (const l of LINHAS) {
        const m = r.porLinha[l];
        const add = (c: string, v: number) => (ano[l][c] = (ano[l][c] ?? 0) + v / K);
        for (const f of FAMILIAS) {
          add(`falhas_${f}`, m.falhas[f]);
          add(`minutos_${f}`, m.minutosPorCausa[f]);
          if (dia.tipoDia === 'util') diarios[l][f].push(m.falhas[f]);
        }
        add('minutos', m.minutosInterrupcao);
        add('falhas_5_ou_mais', m.falhasPorClasse['5_a_10'] + m.falhasPorClasse['10_a_30'] + m.falhasPorClasse['30_ou_mais']);
        for (const c of CLASSES_GRAVIDADE) add(`falhas_${c}`, m.falhasPorClasse[c]);
      }
    }
  });
  for (const l of LINHAS)
    for (const f of FAMILIAS) {
      const xs = diarios[l][f];
      const media = xs.reduce((a, b) => a + b, 0) / xs.length;
      const vari = xs.reduce((a, b) => a + (b - media) ** 2, 0) / (xs.length - 1);
      dispersao[l][f] = media > 0 ? vari / media : NaN;
    }
  return { ano, dispersao };
}

/** Observado por ano, por linha × família, com IC por blocos semanais: no ano-base do simulador (2025) e na média de 2019 a 2025. */
function observado(anos: string[]) {
  const ev = csv(resolve(RAIZ, 'dados/derivados/eventos/eventos_tecnicos.csv'));
  const cc = csv(resolve(RAIZ, 'dados/derivados/eventos/eventos_causa_comum.csv'));
  const semana = (d: string) => {
    const t = new Date(`${d}T12:00:00Z`);
    const dia = (t.getUTCDay() + 6) % 7;
    t.setUTCDate(t.getUTCDate() - dia + 3);
    const ini = new Date(Date.UTC(t.getUTCFullYear(), 0, 4));
    return `${t.getUTCFullYear()}-${String(1 + Math.round((+t - +ini) / 864e5 / 7)).padStart(2, '0')}`;
  };
  // contagens por semana (para o bootstrap) e por dia útil (para a dispersão)
  const porSemana = new Map<string, Record<string, number>>();
  const porDia = new Map<string, Record<string, number>>();
  const soma = (mapa: Map<string, Record<string, number>>, chave: string, k: string, v: number) => {
    const o = mapa.get(chave) ?? {};
    o[k] = (o[k] ?? 0) + v;
    mapa.set(chave, o);
  };
  for (const e of ev) {
    if (!anos.includes(e.data_servico.slice(0, 4))) continue;
    const s = semana(e.data_servico);
    soma(porSemana, s, `${e.linha}|falhas_${e.causa}`, 1);
    soma(porSemana, s, `${e.linha}|minutos_${e.causa}`, Number(e.duracao_min));
    if (Number(e.duracao_min) >= 5) soma(porSemana, s, `${e.linha}|falhas_5_ou_mais`, 1);
    soma(porDia, e.data_servico, `${e.linha}|${e.causa}`, 1);
  }
  for (const e of cc) {
    if (!anos.includes(e.data_servico.slice(0, 4))) continue;
    for (const l of e.linhas.split(',')) {
      soma(porSemana, semana(e.data_servico), `${l}|falhas_CC`, 1);
      soma(porSemana, semana(e.data_servico), `${l}|minutos_CC`, Number(e.duracao_min));
      if (Number(e.duracao_min) >= 5) soma(porSemana, semana(e.data_servico), `${l}|falhas_5_ou_mais`, 1);
      soma(porDia, e.data_servico, `${l}|CC`, 1);
    }
  }
  const semanas = [...porSemana.keys()];
  const nAnos = anos.length;
  const chaves = new Set<string>();
  for (const o of porSemana.values()) for (const k of Object.keys(o)) chaves.add(k);
  const media: Record<string, number> = {};
  const ic: Record<string, [number, number]> = {};
  let x = 12345;
  const aleatorio = () => ((x = (Math.imul(x, 1103515245) + 12345) >>> 0) / 2 ** 32);
  const reamostras: Record<string, number[]> = {};
  for (let b = 0; b < 1000; b++) {
    const tot: Record<string, number> = {};
    for (let i = 0; i < semanas.length; i++) {
      const o = porSemana.get(semanas[Math.floor(aleatorio() * semanas.length)])!;
      for (const [k, v] of Object.entries(o)) tot[k] = (tot[k] ?? 0) + v;
    }
    for (const k of chaves) (reamostras[k] ??= []).push((tot[k] ?? 0) / nAnos);
  }
  for (const k of chaves) {
    let t = 0;
    for (const o of porSemana.values()) t += o[k] ?? 0;
    media[k] = t / nAnos;
    const r = reamostras[k].sort((a, b) => a - b);
    ic[k] = [r[25], r[974]];
  }
  // dispersão: dias úteis de 2025, variância ÷ média por linha × família
  const dias25 = [...new Set(ev.filter((e) => e.data_servico.startsWith('2025')).map((e) => e.data_servico))];
  const util = (d: string) => [1, 2, 3, 4, 5].includes(new Date(`${d}T12:00:00Z`).getUTCDay());
  const todosDias: string[] = [];
  for (let t = Date.UTC(2025, 0, 1); t <= Date.UTC(2025, 11, 31); t += 864e5) {
    const d = new Date(t).toISOString().slice(0, 10);
    if (util(d)) todosDias.push(d);
  }
  const vm = (xs: number[]) => {
    const m = xs.reduce((a, b) => a + b, 0) / xs.length;
    return m > 0 ? xs.reduce((a, b) => a + (b - m) ** 2, 0) / (xs.length - 1) / m : NaN;
  };
  const dispersao: Record<string, number> = {};
  for (const l of LINHAS) for (const f of FAMILIAS) dispersao[`${l}|${f}`] = vm(todosDias.map((d) => porDia.get(d)?.[`${l}|${f}`] ?? 0));
  // IC 95% da dispersão observada por blocos semanais (spec 019): as semanas de dias úteis são sorteadas com reposição
  const porSemanaUtil = new Map<string, string[]>();
  for (const d of todosDias) porSemanaUtil.set(semana(d), [...(porSemanaUtil.get(semana(d)) ?? []), d]);
  const blocos = [...porSemanaUtil.values()];
  const dispersaoIC: Record<string, [number, number]> = {};
  for (const l of LINHAS)
    for (const f of FAMILIAS) {
      const k = `${l}|${f}`;
      const rs: number[] = [];
      for (let b = 0; b < 1000; b++) {
        const xs: number[] = [];
        for (let i = 0; i < blocos.length; i++) for (const d of blocos[Math.floor(aleatorio() * blocos.length)]) xs.push(porDia.get(d)?.[k] ?? 0);
        rs.push(vm(xs));
      }
      const ok = rs.filter(Number.isFinite).sort((a, b) => a - b);
      dispersaoIC[k] = ok.length ? [ok[Math.floor(0.025 * ok.length)], ok[Math.ceil(0.975 * ok.length) - 1]] : [NaN, NaN];
    }
  return { media, ic, dispersao, dispersaoIC, dias25: dias25.length };
}

it('revalidação do simulador contra o histórico (spec 020)', { timeout: 3_600_000 }, () => {
  const revisto = carregaParametrosReais();
  const v1 = JSON.parse(execFileSync('git', ['show', 'v1.1.0:dados/derivados/simulador/parametros.json'], { cwd: RAIZ, maxBuffer: 1 << 28 }).toString('utf8')) as Parametros;
  const dias = condicoes2025();
  const simR = simula(revisto, dias);
  const simV1 = simula(v1, dias);
  const obs = observado(['2025']);
  const obsPeriodo = observado(['2019', '2020', '2021', '2022', '2023', '2024', '2025']);
  const metricas = ['falhas_MR', 'falhas_EF', 'falhas_CC', 'minutos_MR', 'minutos_EF', 'minutos_CC', 'falhas_5_ou_mais'];
  const comparacoes: Record<string, unknown>[] = [];
  for (const l of LINHAS)
    for (const m of metricas) {
      const k = `${l}|${m}`;
      const o = obs.media[k] ?? 0;
      const r = simR.ano[l][m];
      const a = simV1.ano[l][m];
      comparacoes.push({ linha: l, metrica: m, observado: o, ic95_observado: obs.ic[k] ?? [0, 0], media_2019_2025: obsPeriodo.media[k] ?? 0, revisto: r, v1: a, dentro_15pct: o > 0 ? Math.abs(r - o) / o <= TOLERANCIA : r === 0, dentro_ic: obs.ic[k] ? r >= obs.ic[k][0] && r <= obs.ic[k][1] : false, v1_dentro_ic: obs.ic[k] ? a >= obs.ic[k][0] && a <= obs.ic[k][1] : false });
    }
  const dispComp = LINHAS.flatMap((l) =>
    FAMILIAS.map((f) => {
      const k = `${l}|${f}`;
      const ic95 = obs.dispersaoIC[k];
      const r = simR.dispersao[l][f];
      const a = simV1.dispersao[l][f];
      return { linha: l, familia: f, observado: obs.dispersao[k], ic95, revisto: r, v1: a, dentro: r >= ic95[0] && r <= ic95[1], abaixo: r < ic95[0], v1_dentro: a >= ic95[0] && a <= ic95[1] };
    }),
  );
  const dispNoIC = dispComp.filter((c) => c.dentro).length;
  const dentro = comparacoes.filter((c) => c.dentro_15pct).length;
  const noIC = comparacoes.filter((c) => c.dentro_ic).length;
  const noICv1 = comparacoes.filter((c) => c.v1_dentro_ic).length;
  // indicador de 5 min por milhão de km-carro, só falhas técnicas e causa comum, com o km de 2025
  const frota = csv(resolve(RAIZ, 'dados/derivados/exposicao/frota_mensal.csv'));
  const km25 = frota.filter((r) => r.mes.startsWith('2025') && r.km_carro).reduce((s, r) => s + Number(r.km_carro), 0) / 1e6;
  const cincoSim = LINHAS.reduce((s, l) => s + simR.ano[l].falhas_5_ou_mais, 0);
  const cincoObs25 = csv(resolve(RAIZ, 'dados/derivados/eventos/eventos_tecnicos.csv')).filter((e) => e.data_servico.startsWith('2025') && e.classe_faixa_oficial !== 'menos_de_5').length;
  // por ano: dados abertos (todas as causas e só técnicas, faixa oficial; normaliza.py) contra o publicado, com o km-carro do ano
  const resumo = JSON.parse(readFileSync(resolve(RAIZ, 'dados/derivados/eventos/resumo_normalizacao.json'), 'utf8'));
  const cincoAno = resumo.cinco_ou_mais_faixa_oficial_por_ano as { todas_as_causas: Record<string, number>; tecnicas: Record<string, number> };
  const kmAno = (a: string) => frota.filter((r) => r.mes.startsWith(a) && r.km_carro).reduce((s, r) => s + Number(r.km_carro), 0) / 1e6;
  const porAno = Object.keys(STM_PUBLICADO).map((a) => {
    const km = kmAno(a);
    const todas = (cincoAno.todas_as_causas[a] ?? 0) / km;
    return { ano: a, km_carro_milhoes: km, todas_as_causas: todas, tecnicas: (cincoAno.tecnicas[a] ?? 0) / km, publicado: STM_PUBLICADO[a], razao: todas / STM_PUBLICADO[a] };
  });
  const razoes = porAno.map((r) => r.razao);
  const L = [
    '# Revalidação do simulador contra o histórico (spec 020)',
    '',
    `Gerado por \`app/relatorios/revalidacao.relatorio.ts\`: cada um dos ${dias.length} dias de 2025 simulado ${K} vezes (semente ${SEMENTE}), sem políticas, com o tipo de dia, a estação, o clima e os eventos de cada hora daquele dia (painel do modelo, spec 005) e a taxa-base do ano 2025. As greves não entram: o simulador roda o serviço normal nesses dias. ` +
      `Parâmetros revistos: \`${revisto.codigo_commit}\` (contrato v${revisto.versao}); v1.1.0: \`${v1.codigo_commit}\`. Observado: o ano de 2025 (o ano-base dos parâmetros), com IC 95% por blocos semanais (1.000 reamostras); a média de 2019 a 2025 fica como contexto, porque a mistura de frotas mudou (a Verde tinha 61% de MR-73 em 2019 e 15% em 2025). ` +
      `Tolerância declarada antes: até ${100 * TOLERANCIA}% da média observada (a da spec 009). O IC do observado aparece para dar a escala da variação de um ano.`,
    '',
    `**Critério da spec 020 (dentro do IC 95% do observado em 2025):** revisto ${noIC} de ${comparacoes.length}; v1.1.0 ${noICv1} de ${comparacoes.length}. **A até ${100 * TOLERANCIA}% do observado (critério da spec 009):** revisto ${dentro} de ${comparacoes.length}.`,
    '',
    '| Linha | Medida por ano | Observado em 2025 (IC 95%) | Média 2019–2025 | Revisto | v1.1.0 | Revisto no IC | v1.1.0 no IC | Revisto a até 15% |',
    '|---|---|---|---|---|---|---|---|---|',
    ...comparacoes.map((c) => {
      const ic = c.ic95_observado as [number, number];
      return `| ${c.linha} | ${c.metrica} | ${fmt(c.observado as number)} (${fmt(ic[0])}–${fmt(ic[1])}) | ${fmt(c.media_2019_2025 as number)} | ${fmt(c.revisto as number)} | ${fmt(c.v1 as number)} | ${c.dentro_ic ? 'sim' : 'não'} | ${c.v1_dentro_ic ? 'sim' : 'não'} | ${c.dentro_15pct ? 'sim' : 'não'} |`;
    }),
    '',
    '## Dispersão das falhas por dia (dias úteis)',
    '',
    'Variância ÷ média das falhas por dia de cada linha × família. Poisson dá 1; o histórico tem agrupamento (spec 006). Somar fontes independentes tende a dar dispersão menor que a observada. ' +
      'Critério da spec 019: a simulada dentro do IC 95% da observada, por blocos semanais (1.000 reamostras das semanas de dias úteis de 2025); abaixo dele, o critério pede um fator diário comum por família. A dispersão por mês (12 meses num ano) não foi calculada.',
    '',
    `**Revisto dentro do IC:** ${dispNoIC} de ${dispComp.length} (abaixo: ${dispComp.filter((c) => c.abaixo).map((c) => `${c.linha} ${c.familia}`).join(', ') || 'nenhum'}). **v1.1.0 dentro do IC:** ${dispComp.filter((c) => c.v1_dentro).length} de ${dispComp.length}.`,
    '',
    '| Linha | Família | Observado (dias úteis de 2025; IC 95%) | Revisto | v1.1.0 | Revisto no IC |',
    '|---|---|---|---|---|---|',
    ...dispComp.map((c) => `| ${c.linha} | ${c.familia} | ${fmt(c.observado, 2)} (${fmt(c.ic95[0], 2)}–${fmt(c.ic95[1], 2)}) | ${fmt(c.revisto, 2)} | ${fmt(c.v1, 2)} | ${c.dentro ? 'sim' : c.abaixo ? 'não, abaixo' : 'não, acima'} |`),
    '',
    '## Indicador de 5 minutos ou mais por milhão de km-carro',
    '',
    `Só falhas técnicas e causa comum (o indicador da STM conta todas as causas, inclusive clientela). Km-carro de 2025: ${fmt(km25, 1)} milhões.`,
    '',
    `- Simulado (revisto): ${fmt(cincoSim / km25, 2)} por milhão de km-carro (${fmt(cincoSim, 0)} por ano).`,
    `- Dados abertos de 2025, faixa oficial: ${fmt(cincoObs25 / km25, 2)} (${cincoObs25} falhas técnicas de uma linha).`,
    `- Publicado pela STM, todas as causas: ${Object.entries(STM_PUBLICADO).map(([a, v]) => `${a}: ${fmt(v, 2)}`).join('; ')}.`,
    '',
    '### Por ano: dados abertos contra o publicado',
    '',
    'Incidentes de 5 min ou mais pela faixa oficial ("Incident en minutes") do CSV de incidentes, por ano civil, divididos pelo km-carro do km real no mesmo ano. A STM não publica a regra de contagem do indicador; a diferença que sobra fica declarada como exceção da spec 020, sem explicação da STM (D65).',
    '',
    '| Ano | Km-carro (milhões) | Dados abertos, todas as causas | Dados abertos, só técnicas | Publicado pela STM | Dados abertos ÷ publicado |',
    '|---|---|---|---|---|---|',
    ...porAno.map((r) => `| ${r.ano} | ${fmt(r.km_carro_milhoes, 1)} | ${fmt(r.todas_as_causas, 2)} | ${fmt(r.tecnicas, 2)} | ${fmt(r.publicado, 2)} | ${fmt(r.razao, 3)} |`),
    '',
    `Razão entre os dados abertos de todas as causas e o publicado: de ${fmt(Math.min(...razoes), 3)} a ${fmt(Math.max(...razoes), 3)}. As falhas técnicas são de ${fmt(Math.min(...porAno.map((r) => r.tecnicas / r.todas_as_causas)) * 100, 0)}% a ${fmt(Math.max(...porAno.map((r) => r.tecnicas / r.todas_as_causas)) * 100, 0)}% dos incidentes de 5 min ou mais.`,
  ];
  writeFileSync(resolve(RAIZ, 'fontes/verificacao/revalidacao.md'), L.join('\n') + '\n');
  writeFileSync(resolve(RAIZ, 'dados/derivados/simulador/revalidacao.json'), JSON.stringify({ semente: SEMENTE, dias_2025: dias.length, simulacoes_por_dia: K, comparacoes, dispersao: { observado: obs.dispersao, ic95_observado: obs.dispersaoIC, revisto: simR.dispersao, v1: simV1.dispersao, comparacoes: dispComp }, indicador: { km_carro_2025_milhoes: km25, simulado: cincoSim / km25, dados_abertos_2025: cincoObs25 / km25, stm_publicado: STM_PUBLICADO, por_ano: porAno } }, null, 1) + '\n');
});
