// Gera app/tests/fixtures/parametros_teste.json a partir do painel atual (valores plausíveis, status hipótese).
// Uso (da raiz do repositório): node app/tests/fixtures/gera_parametros_teste.mjs .
import fs from 'node:fs';
const raiz = process.argv[2];
const ler = (p) => JSON.parse(fs.readFileSync(`${raiz}/${p}`, 'utf8'));
const rede = ler('dados/derivados/simulador/rede.json');
const painel = Object.fromEntries(ler('dados/derivados/painel/linhas.json').map((x) => [x.linha, x]));
const cc = ler('dados/derivados/painel/causa_comum.json');
const locais = ler('dados/derivados/geo/locais.json');
const LINHAS = ['verde', 'laranja', 'amarela', 'azul'];
const DIAS = { util: 251, sabado: 52, domingo: 62 };
const DIAS_BASE = 2738; // dias de 2019-01 a 2026-06 no painel
const HORAS_OP = DIAS_BASE * 20;
const P = (valor, extra = {}) => ({ valor, ic95: null, n: null, unidade: '', metodo: 'fixture de teste', fontes: ['dados/derivados/painel'], script: 'app/tests/fixtures (gerada a partir do painel)', status: 'hipótese', ...extra });
const r6 = (x) => Math.round(x * 1e8) / 1e8;
// trem-horas por dia, ponderado pelos tipos de dia
const thDia = {};
for (const l of LINHAS) {
  let tot = 0, dias = 0;
  for (const [tipo, nd] of Object.entries(DIAS)) {
    let th = 0;
    for (const d of ['0', '1']) for (const v of rede.horarios[tipo][l][d]) th += (v.tempos[v.tempos.length - 1][0] - v.tempos[0][1]) / 3600;
    tot += th * nd; dias += nd;
  }
  thDia[l] = tot / dias;
}
const REF = { linha: 'laranja', faixa: 'entrepico', tipo_dia: 'util', estacao: 'outono', temp: '5a15', precip: '0', cond: 'seco_ou_outro', neve_solo: '0', ano: '2019' };
const niveis = {
  faixa: ['abertura', 'pico_manha', 'entrepico', 'pico_tarde', 'noite', 'fim'],
  tipo_dia: ['util', 'sabado', 'domingo'],
  estacao: ['inverno', 'primavera', 'verao', 'outono'],
  temp: ['abaixo_-15', '-15a-5', '-5a5', '5a15', '15a25', '25_ou_mais', 'sem_dado'],
  precip: ['0', 'ate_1mm', 'acima_1mm', 'sem_dado'],
  cond: ['chuva_congelante', 'neve', 'chuva', 'seco_ou_outro', 'sem_dado'],
  neve_solo: ['0', '1a10', 'acima_10', 'sem_dado'],
};
// multiplicadores neutros (1), salvo alguns níveis fora da referência, para testar que o motor os aplica
const especiais = { 'cond=chuva_congelante': 1.8, 'temp=abaixo_-15': 1.4, 'neve_solo=acima_10': 1.2 };
function taxa(causa) {
  const mult = {};
  for (const [f, ns] of Object.entries(niveis)) {
    mult[f] = {};
    for (const nv of ns) mult[f][nv] = P(especiais[`${f}=${nv}`] ?? 1.0, { unidade: 'multiplicador da taxa' });
  }
  for (const ind of ['jogo', 'gp_fds', 'feriado', 'greve']) mult[ind] = { 1: P(1.0, { unidade: 'multiplicador da taxa' }) };
  const base = {};
  for (const l of LINHAS) {
    const falhas = causa === 'MR' ? painel[l].falhas_mr : painel[l].falhas_ef;
    base[l] = P(r6(falhas / DIAS_BASE / thDia[l]), { unidade: 'falhas por trem-hora' });
  }
  return { modelo: 'Poisson', referencia: REF, alpha: P(0), base_por_trem_hora: base, multiplicadores: mult };
}
const SIGMA = 1.0;
const renovacao = {}, ttr = {};
for (const l of LINHAS) {
  const p0 = painel[l].pct_sem_interrupcao;
  const mediaPos = painel[l].mttr_min / (1 - p0);
  for (const c of ['MR', 'EF']) {
    renovacao[`${l}|${c}`] = { forma: P(c === 'MR' ? 0.85 : 0.8), escala: P(1.0), processo: 'renovação Weibull no tempo reescalado (fixture)' };
    ttr[`${l}|${c}`] = { p_zero: P(p0), mu_log: P(r6(Math.log(mediaPos) - SIGMA * SIGMA / 2), { unidade: 'log(minutos)' }), sigma_log: P(SIGMA, { unidade: 'log(minutos)' }) };
  }
}
const causa_comum = {};
for (const x of cc) {
  causa_comum[x.par] = {
    taxa_por_hora_op: P(r6(x.eventos_tecnicos / HORAS_OP), { unidade: 'eventos por hora' }),
    beta_a: P(x.beta_a), beta_b: P(x.beta_b),
    duracao: { p_zero: P(0), mu_log: P(r6(Math.log(x.duracao_media_min) - SIGMA * SIGMA / 2), { unidade: 'log(minutos)' }), sigma_log: P(SIGMA, { unidade: 'log(minutos)' }) },
  };
}
const locais_ef = {}, sem = {};
for (const l of LINHAS) {
  locais_ef[l] = locais.filter((x) => x.linha === l && x.km_linha !== null).map((x) => ({ km: x.km_linha, peso: x.n_tecnicos, codigo: x.codigo, status: x.status }));
  sem[l] = locais.filter((x) => x.linha === l && x.km_linha === null).reduce((a, x) => a + x.n_tecnicos, 0);
}
const frota = {};
for (const l of LINHAS) frota[l] = { trens_necessarios: P(painel[l].trens_dia_util, { unidade: 'trens' }), lambda_trem_dia: P(painel[l].lambda_trem_dia, { unidade: 'falhas por trem-dia' }) };
const H = (v, faixa, unidade = '') => P(v, { faixa, unidade });
const out = {
  versao: 1, codigo_commit: 'fixture', ano_base: 2025, janela_operacao_h: P(20, { unidade: 'h' }),
  taxas: { MR: taxa('MR'), EF: taxa('EF') }, renovacao, ttr, causa_comum, locais_ef, locais_ef_sem_posicao: sem, frota,
  hipoteses: {
    reparo_oficina_dias: H(1.0, [0.5, 4], 'dias'), p_retirada: H(1.0, [0, 1]), reservas_por_linha: H(2, [0, 8], 'trens'),
    intervalo_minimo_s: H(90, [60, 180], 's'), sentidos_bloqueio_ef: H(2, [1, 2], 'sentidos'), fator_velocidade_degradada: H(1.25, [1, 2]),
    duracao_degradada_min: H(30, [0, 120], 'min'), tempo_transferencia_min: H(4, [2, 8], 'min'), reducao_causa_comum: H(0, [0, 1]),
    velocidade_comercial_candidata_kmh: H(36, [30, 45], 'km/h'),
  },
  _nota: 'Fixture de teste do motor: valores plausíveis tirados do painel (dados/derivados/painel), não ajustados. Trem-horas por dia usados na taxa-base: ' + JSON.stringify(Object.fromEntries(Object.entries(thDia).map(([k, v]) => [k, Math.round(v * 10) / 10]))),
};
fs.writeFileSync(`${raiz}/app/tests/fixtures/parametros_teste.json`, JSON.stringify(out, null, 1) + '\n');
console.log('trem-horas/dia', thDia, 'base MR laranja', out.taxas.MR.base_por_trem_hora.laranja.valor);
