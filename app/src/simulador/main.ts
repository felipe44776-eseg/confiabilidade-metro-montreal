// Página /simulador/ (specs 010, 011 e 014): cenário, dia no mapa, Monte Carlo, comparação e expansão.
import './simulador.css';
import type { Local } from '../locais';
import type { ResultadoMC } from '../mc/pool';
import { PoolMC } from '../mc/pool';
import type { Agregado, Estimativa } from '../mc/rodadas';
import { anualiza, DIAS_POR_TIPO_ANO } from '../mc/rodadas';
import { avisosDoCenario, preparaContexto } from '../motor/contexto';
import type { ResultadoDia } from '../motor/dia';
import { simulaDia } from '../motor/dia';
import type { Candidata, ItemRanking } from '../motor/expansao';
import { candidataLivre } from '../motor/expansao';
import { HIPOTESES_PADRAO } from '../motor/hipoteses';
import type { NomePolitica } from '../motor/politicas';
import { NOMES_POLITICAS } from '../motor/politicas';
import { sementeDaRodada } from '../motor/prng';
import type { Rede } from '../motor/rede';
import { montaRede } from '../motor/rede';
import type { Parametro, Parametros, RedeJson, TipoDia } from '../motor/tipos';
import { TIPOS_DIA } from '../motor/tipos';
import { graficoBarras } from '../ui/graficos';
import { casasPara, comIC, comSinal, inteiro, num, pct, pp } from '../ui/formato';
import { montaRodape, REPO } from '../ui/rodape';
import type { Bloco, Ocorrencia } from './animacao';
import { blocosAtivos, blocosDoDia, minutosAte, ocorrenciasDoDia, posicoes, relogio } from './animacao';
import type { CandidatasJson } from './candidatas';
import { candidatasDoJson } from './candidatas';
import type { EstadoCenario, Greve } from './cenario';
import { aplicaGreve, chaveRede, copia, desserializa, estacaoDoMes, JANELAS_GREVE, MESES, NIVEIS, ORDEM_POLITICAS, PADRAO, paraCenarioMotor, ROTULOS, serializa } from './cenario';
import { avisosDeExtrapolacao } from './extrapolacao';
import type { VistaMapa } from './mapa_sim';
import { corDaCandidata, MapaSimulador, VistaSemMapa } from './mapa_sim';
import { PoolAB } from './pool_ab';
import type { PedidoExpansao, RespostaExpansao } from './trabalhador_expansao';

const BASE = import.meta.env.BASE_URL;
const RELATORIOS = `${REPO}/blob/main/fontes/verificacao`;
const FONTE_PARAMETRO: Record<string, string> = {
  'pipeline/modelo_taxa.py': `${RELATORIOS}/modelo_taxa.md`,
  'pipeline/distribuicoes.py': `${RELATORIOS}/distribuicoes.md`,
  'pipeline/parametros.py': `${REPO}/blob/main/pipeline/parametros.py`,
  'pipeline/analise_confiabilidade.py': `${REPO}/blob/main/fontes/FONTES.md`,
};
const OPCOES_RODADAS = [200, 500, 1000, 2000, 5000, 10000];
/** Quanto tempo (s simulados) a falha fica marcada no mapa depois de ocorrer, mesmo sem interrupção. */
const MARCA_FALHA_S = 300;

// ---------- utilidades de DOM ----------
const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
function el<K extends keyof HTMLElementTagNameMap>(tag: K, texto?: string, classe?: string): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (texto !== undefined) e.textContent = texto;
  if (classe) e.className = classe;
  return e;
}
function opcoes(sel: HTMLSelectElement, itens: [string, string][], valor: string): void {
  sel.replaceChildren(...itens.map(([v, t]) => Object.assign(el('option', t), { value: v })));
  sel.value = valor;
}
function linkFonte(p: Parametro): HTMLElement {
  const url = FONTE_PARAMETRO[p.script] ?? `${REPO}/blob/main/${p.script}`;
  const a = el('a', 'fonte');
  a.href = url;
  a.title = `${p.metodo} (${p.script})`;
  return a;
}
function selo(status: string): HTMLElement {
  const classe = { ajustado: 'ajustado', hipótese: 'hipotese', deduzido: 'deduzido', 'não verificado': 'nao-verificado' }[status] ?? '';
  return el('span', status, `selo ${classe}`);
}
function tabela(cabecalho: string[], linhas: (string | Node)[][], classesNumericas: number[] = []): HTMLElement {
  const caixa = el('div', undefined, 'tbl');
  const t = el('table');
  const h = t.createTHead().insertRow();
  cabecalho.forEach((c, i) => {
    const th = el('th', c);
    if (classesNumericas.includes(i)) th.className = 'n';
    h.append(th);
  });
  const b = t.createTBody();
  for (const l of linhas) {
    const r = b.insertRow();
    l.forEach((c, i) => {
      const td = r.insertCell();
      if (classesNumericas.includes(i)) td.className = 'n';
      if (typeof c === 'string') td.textContent = c;
      else td.append(c);
    });
  }
  caixa.append(t);
  return caixa;
}
function mostraErro(e: unknown): void {
  const p = $('erro');
  p.textContent = `Erro: ${e instanceof Error ? e.message : String(e)}`;
  p.hidden = false;
}

async function carrega<T>(caminho: string): Promise<T> {
  const r = await fetch(`${BASE}dados/${caminho}`);
  if (!r.ok) throw new Error(`${caminho}: HTTP ${r.status}`);
  return (await r.json()) as T;
}

// ---------- estado ----------
interface Dados {
  redeJson: RedeJson;
  parametros: Parametros;
  candidatasJson: CandidatasJson;
  linhasGeo: GeoJSON.FeatureCollection;
  estacoesGeo: GeoJSON.FeatureCollection;
  locais: Local[];
}

let dados: Dados;
let estado: EstadoCenario = copia(PADRAO);
let mapa: VistaMapa = new VistaSemMapa();
const redes = new Map<Greve, { json: RedeJson; rede: Rede }>();
let candidatas: Candidata[] = [];

function redeDo(greve: Greve): { json: RedeJson; rede: Rede } {
  let r = redes.get(greve);
  if (!r) {
    const json = aplicaGreve(dados.redeJson, greve);
    r = { json, rede: montaRede(json) };
    redes.set(greve, r);
  }
  return r;
}
/** Rede sem greve: ids e estações são os mesmos com greve. */
const redeBase = () => redeDo('nao').rede;
const nomeLinha = (id: string) => ({ verde: 'Verde', laranja: 'Laranja', amarela: 'Amarela', azul: 'Azul' })[id] ?? id;
const corLinha = (id: string) => dados.redeJson.linhas[id]?.cor ?? '#555555';

// ---------- formulário do cenário ----------
function montaFormulario(): void {
  opcoes($('c-tipo'), TIPOS_DIA.map((t) => [t, ROTULOS[t]]), estado.tipoDia);
  opcoes($('c-mes'), MESES.map((m, i) => [String(i + 1), m]), String(estado.mes));
  opcoes($('c-temp'), NIVEIS.temp.map((n) => [n, ROTULOS[n]]), estado.temp);
  opcoes($('c-precip'), NIVEIS.precip.map((n) => [n, ROTULOS[n]]), estado.precip);
  opcoes($('c-cond'), NIVEIS.cond.map((n) => [n, ROTULOS[n]]), estado.cond);
  opcoes($('c-neve'), NIVEIS.neveSolo.map((n) => [n, ROTULOS[n]]), estado.neveSolo);
  opcoes($('c-greve'), [['nao', 'sem greve'], ...Object.entries(JANELAS_GREVE).map(([k, v]) => [k, v.rotulo] as [string, string])], estado.greve);
  opcoes($('c-rodadas'), OPCOES_RODADAS.map((n) => [String(n), inteiro(n)]), String(estado.rodadas));
  if (!OPCOES_RODADAS.includes(estado.rodadas)) {
    $<HTMLSelectElement>('c-rodadas').append(Object.assign(el('option', inteiro(estado.rodadas)), { value: String(estado.rodadas) }));
    $<HTMLSelectElement>('c-rodadas').value = String(estado.rodadas);
  }
  $<HTMLInputElement>('c-jogo').checked = estado.jogo;
  $<HTMLInputElement>('c-gp').checked = estado.gp;
  $<HTMLInputElement>('c-feriado').checked = estado.feriado;
  $<HTMLInputElement>('c-semente').value = String(estado.semente);
  $<HTMLInputElement>('t-dia').value = String(estado.dia);
  $('c-estacao').textContent = `Estação do ano no modelo: ${{ inverno: 'inverno', primavera: 'primavera', verao: 'verão', outono: 'outono' }[estacaoDoMes(estado.mes)]}.`;
  const pol = $('c-politicas');
  pol.replaceChildren();
  for (const k of ORDEM_POLITICAS) {
    const lab = el('label', undefined, 'caixa');
    const cx = el('input');
    cx.type = 'checkbox';
    cx.checked = estado.politicas[k];
    cx.addEventListener('change', () => {
      estado.politicas[k as NomePolitica] = cx.checked;
      mudou();
    });
    lab.append(cx, NOMES_POLITICAS[k]);
    pol.append(lab);
  }
  montaHipoteses();
}

function montaHipoteses(): void {
  const caixa = $('c-hipoteses');
  caixa.replaceChildren();
  const nomes = [...new Set([...Object.keys(dados.parametros.hipoteses), ...Object.keys(HIPOTESES_PADRAO)])].filter((n) => n !== 'duracao_degradada_min');
  for (const nome of nomes) {
    const p = dados.parametros.hipoteses[nome];
    const padrao = p?.valor ?? HIPOTESES_PADRAO[nome as keyof typeof HIPOTESES_PADRAO];
    const faixa = p?.faixa && p.faixa.length === 2 ? p.faixa : [0, padrao * 2 || 1];
    const valor = estado.hipoteses[nome] ?? padrao;
    const div = el('div', undefined, 'hip');
    const cab = el('div', undefined, 'cab');
    const nomeEl = el('span', nome.replaceAll('_', ' '));
    const valEl = el('output', `${num(valor, valor % 1 ? 2 : 0)}${p?.unidade ? ` ${p.unidade}` : ''}`);
    cab.append(nomeEl, valEl);
    const r = el('input');
    r.type = 'range';
    // a barra vai além da faixa, para a pessoa poder testar extrapolações (que geram aviso)
    const span = faixa[1] - faixa[0];
    r.min = String(Math.max(0, faixa[0] - span * 0.5));
    r.max = String(faixa[1] + span * 0.5);
    r.step = Number.isInteger(padrao) && Number.isInteger(faixa[0]) && Number.isInteger(faixa[1]) ? '1' : String(span / 100);
    r.value = String(valor);
    r.setAttribute('aria-label', nome);
    r.addEventListener('input', () => (valEl.textContent = `${num(Number(r.value), Number(r.value) % 1 ? 2 : 0)}${p?.unidade ? ` ${p.unidade}` : ''}`));
    r.addEventListener('change', () => {
      const v = Number(r.value);
      if (v === padrao) delete estado.hipoteses[nome];
      else estado.hipoteses[nome] = v;
      mudou();
    });
    const nota = el('p', `${p ? p.metodo.replace(/^hipótese do autor, sem dado; ajustável na interface: /, '') : 'criada pelo motor (ainda fora do parametros.json)'}. Faixa: ${num(faixa[0], 2)} a ${num(faixa[1], 2)}.`, 'nota');
    const linhaSelo = el('div');
    linhaSelo.append(selo(p?.status ?? 'hipótese'));
    div.append(cab, r, linhaSelo, nota);
    caixa.append(div);
  }
}

function leFormulario(): void {
  estado.tipoDia = $<HTMLSelectElement>('c-tipo').value as TipoDia;
  estado.mes = Number($<HTMLSelectElement>('c-mes').value);
  estado.temp = $<HTMLSelectElement>('c-temp').value;
  estado.precip = $<HTMLSelectElement>('c-precip').value;
  estado.cond = $<HTMLSelectElement>('c-cond').value;
  estado.neveSolo = $<HTMLSelectElement>('c-neve').value;
  estado.greve = $<HTMLSelectElement>('c-greve').value as Greve;
  estado.jogo = $<HTMLInputElement>('c-jogo').checked;
  estado.gp = $<HTMLInputElement>('c-gp').checked;
  estado.feriado = $<HTMLInputElement>('c-feriado').checked;
  const s = Number($<HTMLInputElement>('c-semente').value);
  if (Number.isInteger(s) && s >= 0) estado.semente = s;
  estado.rodadas = Number($<HTMLSelectElement>('c-rodadas').value);
  const d = Number($<HTMLInputElement>('t-dia').value);
  if (Number.isInteger(d) && d >= 0) estado.dia = d;
}

let esperaDia: ReturnType<typeof setTimeout> | undefined;
function mudou(): void {
  history.replaceState(null, '', `#${serializa(estado)}`);
  $('c-estacao').textContent = `Estação do ano no modelo: ${{ inverno: 'inverno', primavera: 'primavera', verao: 'verão', outono: 'outono' }[estacaoDoMes(estado.mes)]}.`;
  mostraAvisos();
  marcaDesatualizado();
  mostraParametros();
  clearTimeout(esperaDia);
  esperaDia = setTimeout(simulaDiaMostrado, 120);
}

function mostraAvisos(): void {
  const ul = $('avisos');
  ul.replaceChildren();
  const av = avisosDeExtrapolacao(estado, dados.parametros);
  if (estado.feriado && estado.tipoDia !== 'domingo') av.push({ nivel: 'atencao', texto: 'Nos dados, os feriados usam o horário de domingo (spec 004).' });
  if (estado.greve !== 'nao') av.push({ nivel: 'atencao', texto: 'Greve: só circulam as viagens que partem nas faixas com serviço; as faixas vêm da imprensa (status "não verificado").' });
  if (!av.length) ul.append(el('li', 'Nenhum: o cenário está dentro do que os dados observaram.', 'vazio'));
  for (const a of av) ul.append(el('li', a.texto, a.nivel));
}

// ---------- dia no mapa ----------
interface DiaMostrado {
  r: ResultadoDia;
  rede: Rede;
  blocos: Bloco[];
  ocorrencias: Ocorrencia[];
  ini: number;
  fim: number;
  inicioServico: Record<string, number>;
}
let dia: DiaMostrado | null = null;
let tSim = 0;
let tocando = false;

function simulaDiaMostrado(): void {
  try {
    const { rede } = redeDo(estado.greve);
    const ctx = preparaContexto(rede, dados.parametros, paraCenarioMotor(estado));
    const r = simulaDia(ctx, estado.politicas, sementeDaRodada(estado.semente, estado.dia), { registrar: true, trajetorias: true });
    const [ini, fim] = ctx.horario.janelaRede;
    dia = { r, rede, blocos: blocosDoDia(r), ocorrencias: ocorrenciasDoDia(r), ini, fim, inicioServico: ctx.horario.inicioServico };
    const barra = $<HTMLInputElement>('t-barra');
    barra.min = String(Math.floor(ini));
    barra.max = String(Math.ceil(fim));
    barra.step = '30';
    if (!(tSim >= ini && tSim <= fim)) tSim = Math.min(Math.max(7.5 * 3600, ini), fim);
    mostraFalhasDoDia();
    desenhaInstante();
  } catch (e) {
    mostraErro(e);
  }
}

function rotuloOcorrencia(o: Ocorrencia): string {
  const tipo = { FALHA_TREM: 'material rodante', FALHA_EF: 'equipamento fixo', CAUSA_COMUM: 'causa comum' }[o.tipo as 'FALHA_TREM'] ?? o.tipo;
  return `${relogio(o.t)} · ${nomeLinha(o.linha)} · ${tipo} · ${o.duracaoS > 0 ? `${num(o.duracaoS / 60, 0)} min parada` : 'sem interrupção'} · ${o.detalhe}`;
}

function mostraFalhasDoDia(): void {
  if (!dia) return;
  const corpo = $<HTMLTableElement>('tab-falhas').tBodies[0];
  corpo.replaceChildren();
  if (!dia.ocorrencias.length) {
    const r = corpo.insertRow();
    const c = r.insertCell();
    c.colSpan = 5;
    c.textContent = 'Nenhuma falha sorteada neste dia.';
    return;
  }
  for (const o of dia.ocorrencias) {
    const r = corpo.insertRow();
    r.dataset.t = String(o.t);
    r.insertCell().textContent = relogio(o.t);
    const cl = r.insertCell();
    const pt = el('span', undefined, 'ponto');
    pt.style.background = corLinha(o.linha);
    cl.append(pt, ` ${nomeLinha(o.linha)}`);
    r.insertCell().textContent = { FALHA_TREM: 'material rodante', FALHA_EF: 'equipamento fixo', CAUSA_COMUM: 'causa comum' }[o.tipo as 'FALHA_TREM'] ?? o.tipo;
    r.insertCell().textContent = o.duracaoS > 0 ? `${num(o.duracaoS / 60, 1)} min` : 'sem interrupção';
    r.insertCell().textContent = o.detalhe;
    r.style.cursor = 'pointer';
    r.addEventListener('click', () => {
      tSim = Math.max(dia!.ini, o.t - 60);
      desenhaInstante();
    });
  }
}

function desenhaInstante(): void {
  if (!dia) return;
  const pos = posicoes(dia.rede, dia.r.trajetorias ?? {}, tSim);
  mapa.atualizaTrens(pos);
  const ativos = blocosAtivos(dia.blocos, tSim);
  mapa.atualizaBloqueios(ativos);
  const recentes = dia.ocorrencias.filter((o) => o.t <= tSim && tSim < o.t + Math.max(o.duracaoS, MARCA_FALHA_S));
  mapa.atualizaFalhas(recentes, rotuloOcorrencia);
  $<HTMLInputElement>('t-barra').value = String(tSim);
  $('t-relogio').textContent = relogio(tSim);
  const min = minutosAte(dia.rede, dia.inicioServico, dia.blocos, tSim);
  const caixa = $('indicadores');
  const cartoes: [string, string, string?][] = [
    ['Trens em viagem', inteiro(pos.length)],
    ['Bloqueios ativos', inteiro(ativos.length)],
    ['Falhas até agora', inteiro(dia.ocorrencias.filter((o) => o.t <= tSim).length)],
    ...dia.rede.ids.map((l) => [`${nomeLinha(l)}: min parados`, num(min[l], 1), corLinha(l)] as [string, string, string]),
  ];
  if (caixa.children.length !== cartoes.length) {
    caixa.replaceChildren(
      ...cartoes.map(() => {
        const d = el('div', undefined, 'ind');
        d.append(el('div', undefined, 'rot'), el('div', undefined, 'val'));
        return d;
      }),
    );
  }
  cartoes.forEach(([rot, val, cor], i) => {
    const d = caixa.children[i] as HTMLElement;
    const r = d.children[0] as HTMLElement;
    if (r.dataset.t !== rot) {
      r.dataset.t = rot;
      r.replaceChildren();
      if (cor) {
        const p = el('span', undefined, 'ponto');
        p.style.background = cor;
        r.append(p);
      }
      r.append(rot);
    }
    (d.children[1] as HTMLElement).textContent = val;
  });
}

let ultimoQuadro = 0;
let quadros = 0;
let inicioContagem = 0;
function laco(agora: number): void {
  if (!inicioContagem) inicioContagem = agora;
  quadros++;
  if (agora - inicioContagem >= 1000) {
    $('fps').textContent = `${num((quadros * 1000) / (agora - inicioContagem), 0)} fps`;
    quadros = 0;
    inicioContagem = agora;
  }
  if (tocando && dia) {
    const dt = ultimoQuadro ? Math.min(0.25, (agora - ultimoQuadro) / 1000) : 0;
    tSim += dt * Number($<HTMLSelectElement>('t-vel').value);
    if (tSim >= dia.fim) {
      tSim = dia.fim;
      paraDeTocar();
    }
    desenhaInstante();
  }
  ultimoQuadro = agora;
  requestAnimationFrame(laco);
}
function paraDeTocar(): void {
  tocando = false;
  $('b-play').textContent = '▶';
  $('b-play').setAttribute('aria-label', 'Tocar');
}

// ---------- Monte Carlo ----------
const pool = new PoolMC();
let resultadoMC: { estado: string; r: ResultadoMC } | null = null;

function pedidoMC(e: EstadoCenario, tipoDia?: TipoDia) {
  const { json } = redeDo(e.greve);
  const cenario = paraCenarioMotor({ ...e, tipoDia: tipoDia ?? e.tipoDia });
  return { redeJson: json, chaveRede: chaveRede(e.greve), parametros: dados.parametros, cenario, politicas: e.politicas, sementeBase: e.semente, rodadas: e.rodadas };
}

function progresso(idBarra: string, idTexto: string) {
  const barra = $<HTMLProgressElement>(idBarra);
  barra.hidden = false;
  barra.value = 0;
  return (feitas: number, total: number) => {
    barra.max = total;
    barra.value = feitas;
    $(idTexto).textContent = `${inteiro(feitas)} de ${inteiro(total)} dias simulados`;
  };
}

async function rodaMC(): Promise<void> {
  const b = $<HTMLButtonElement>('b-mc');
  const canc = $<HTMLButtonElement>('b-mc-cancela');
  b.disabled = true;
  canc.disabled = false;
  const chave = serializa(estado);
  try {
    const r = await pool.executa(pedidoMC(estado), progresso('p-mc', 's-mc'));
    resultadoMC = { estado: chave, r };
    $('s-mc').textContent = `${inteiro(r.n)} dias em ${num(r.segundos, 1)} s com ${r.workers} worker(s); semente ${r.sementeBase}.`;
    mostraResultadoMC(r);
  } catch (e) {
    if (!(e instanceof Error && e.message === 'cancelado')) mostraErro(e);
    else $('s-mc').textContent = 'Cancelado.';
  } finally {
    b.disabled = false;
    canc.disabled = true;
    $('p-mc').hidden = true;
  }
}

/** Média e IC 95% com as casas que a precisão permite. `escala`: 100 para porcentagens (casas em pontos percentuais). */
function estimativaTexto(e: Estimativa | undefined, f: (x: number, c: number) => string, casasMin = 1, escala = 1): string {
  if (!e) return '—';
  const casas = Math.max(casasMin, casasPara(e.meiaLargura * escala));
  return `${f(e.media, casas)} (${f(e.ic95[0], casas)}–${f(e.ic95[1], casas)})`;
}

function mostraResultadoMC(r: Agregado): void {
  const caixa = $('r-mc');
  caixa.replaceChildren();
  const ids = redeBase().ids;
  const m = r.porMetrica;
  const pctF = (x: number, c: number) => pct(x, Math.min(c, 4));
  caixa.append(el('h3', `Por dia de operação (${ROTULOS[estado.tipoDia]}), média e intervalo de 95%`));
  caixa.append(
    tabela(
      ['Linha', 'Falhas por dia', 'Minutos parados', 'Disponibilidade', 'Trens-hora perdidos', 'Viagens afetadas', 'Frota completa'],
      ids.map((l) => {
        const nome = el('span');
        const p = el('span', undefined, 'ponto');
        p.style.background = corLinha(l);
        nome.append(p, ` ${nomeLinha(l)}`);
        const falhas = (['falhasMR', 'falhasEF', 'falhasCC'] as const).reduce((s, k) => s + (m[`${l}.${k}`]?.media ?? 0), 0);
        return [
          nome,
          num(falhas, 2),
          estimativaTexto(m[`${l}.minutosInterrupcao`], num),
          estimativaTexto(m[`${l}.disponibilidade`], pctF, 1, 100),
          estimativaTexto(m[`${l}.trensHoraPerdidos`], num),
          estimativaTexto(m[`${l}.viagensAfetadas`], num),
          estimativaTexto(m[`${l}.frotaCompleta`], pctF, 0, 100),
        ];
      }),
      [1, 2, 3, 4, 5, 6],
    ),
  );
  caixa.append(
    el(
      'p',
      `Rede: disponibilidade origem-destino (pares de estações ponderados pela oferta) ${estimativaTexto(m['rede.dispOD'], pctF, 1, 100)}; minutos de par interrompido por dia ${estimativaTexto(m['rede.minutosParInterrompido'], num)}; ${inteiro(r.n)} dias, semente ${r.sementeBase}.`,
      'nota',
    ),
  );
  const g1 = el('div');
  graficoBarras(
    g1,
    ids.map((l) => ({ rotulo: nomeLinha(l), valor: m[`${l}.minutosInterrupcao`].media, ic: m[`${l}.minutosInterrupcao`].ic95, cor: corLinha(l) })),
    { titulo: 'Minutos parados por dia, por linha (IC 95%)', formata: (x) => num(x, 1), eixo: 'minutos por dia', colunaValor: 'Minutos' },
  );
  const g2 = el('div');
  graficoBarras(
    g2,
    ids.map((l) => ({ rotulo: nomeLinha(l), valor: m[`${l}.trensHoraPerdidos`].media, ic: m[`${l}.trensHoraPerdidos`].ic95, cor: corLinha(l) })),
    { titulo: 'Trens-hora perdidos por dia (IC 95%)', formata: (x) => num(x, 2), eixo: 'trens-hora por dia', colunaValor: 'Trens-hora' },
  );
  caixa.append(g1, g2);
  const ctx = preparaContexto(redeDo(estado.greve).rede, dados.parametros, paraCenarioMotor(estado));
  const det = el('details');
  det.append(el('summary', 'Hipóteses usadas nesta rodada'));
  const ul = el('ul');
  for (const a of avisosDoCenario(ctx, estado.politicas)) ul.append(el('li', a));
  det.append(ul);
  caixa.append(det);
}

async function estimaAno(): Promise<void> {
  const b = $<HTMLButtonElement>('b-ano');
  b.disabled = true;
  $<HTMLButtonElement>('b-mc-cancela').disabled = false;
  try {
    const porTipo: Partial<Record<TipoDia, Agregado>> = {};
    for (const t of TIPOS_DIA) {
      $('s-mc').textContent = `Simulando ${ROTULOS[t]}…`;
      porTipo[t] = await pool.executa(pedidoMC(estado, t), progresso('p-mc', 's-mc'));
    }
    const ids = redeBase().ids;
    const linhas = ids.map((l) => {
      const anual = anualiza(Object.fromEntries(TIPOS_DIA.map((t) => [t, porTipo[t]!.porMetrica[`${l}.minutosInterrupcao`]])) as Record<TipoDia, Estimativa>);
      const casas = casasPara(anual.meiaLargura, 0);
      return [nomeLinha(l), `${num(anual.media, casas)} (${num(anual.ic95[0], casas)}–${num(anual.ic95[1], casas)})`];
    });
    const caixa = $('r-mc');
    caixa.prepend(
      el('h3', `Minutos parados por ano (${DIAS_POR_TIPO_ANO.util} dias úteis, ${DIAS_POR_TIPO_ANO.sabado} sábados, ${DIAS_POR_TIPO_ANO.domingo} domingos e feriados), IC 95%`),
      tabela(['Linha', 'Minutos por ano'], linhas, [1]),
      el('p', `O painel calcula, com os dados de 2019 a 2026, 1.797 min/ano na Laranja (analítico) e 1.852 (simulação do painel). Clima e mês do cenário valem para o ano inteiro aqui; ${inteiro(estado.rodadas)} dias por tipo, semente ${estado.semente}.`, 'nota'),
    );
    $('s-mc').textContent = 'Ano estimado.';
  } catch (e) {
    if (!(e instanceof Error && e.message === 'cancelado')) mostraErro(e);
    else $('s-mc').textContent = 'Cancelado.';
  } finally {
    b.disabled = false;
    $<HTMLButtonElement>('b-mc-cancela').disabled = true;
    $('p-mc').hidden = true;
  }
}

function marcaDesatualizado(): void {
  if (resultadoMC && resultadoMC.estado !== serializa(estado)) $('s-mc').textContent = 'O cenário mudou: os resultados abaixo são do cenário anterior. Rode de novo.';
}

// ---------- comparação A/B ----------
const poolAB = new PoolAB();
let cenarioA: EstadoCenario | null = null;

function resumoCenario(e: EstadoCenario): string {
  const pol = ORDEM_POLITICAS.filter((k) => e.politicas[k]).map((k) => NOMES_POLITICAS[k].toLowerCase());
  const hs = Object.entries(e.hipoteses).map(([k, v]) => `${k} = ${v}`);
  return `${ROTULOS[e.tipoDia]}, ${MESES[e.mes - 1]}, ${ROTULOS[e.temp]}, precipitação ${ROTULOS[e.precip]}, ${ROTULOS[e.cond]}, neve no solo ${ROTULOS[e.neveSolo]}${e.jogo ? ', jogo' : ''}${e.gp ? ', GP' : ''}${e.feriado ? ', feriado' : ''}${e.greve !== 'nao' ? ', greve' : ''}; políticas: ${pol.length ? pol.join(', ') : 'nenhuma'}${hs.length ? `; hipóteses: ${hs.join(', ')}` : ''}.`;
}

async function compara(): Promise<void> {
  if (!cenarioA) return;
  const b = $<HTMLButtonElement>('b-comparar');
  b.disabled = true;
  $<HTMLButtonElement>('b-cmp-cancela').disabled = false;
  try {
    const A = cenarioA;
    const B = copia(estado);
    const lado = (e: EstadoCenario) => ({ redeJson: redeDo(e.greve).json, chaveRede: chaveRede(e.greve), cenario: paraCenarioMotor(e), politicas: e.politicas });
    const r = await poolAB.executa(dados.parametros, lado(A), lado(B), B.semente, B.rodadas, progresso('p-cmp', 's-cmp'));
    $('s-cmp').textContent = `${inteiro(r.n)} dias pareados em ${num(r.segundos, 1)} s; semente ${r.sementeBase} nas duas versões.`;
    mostraComparacao(r, A, B);
  } catch (e) {
    if (!(e instanceof Error && e.message === 'cancelado')) mostraErro(e);
    else $('s-cmp').textContent = 'Cancelado.';
  } finally {
    b.disabled = !cenarioA;
    $<HTMLButtonElement>('b-cmp-cancela').disabled = true;
    $('p-cmp').hidden = true;
  }
}

function mostraComparacao(r: Agregado, A: EstadoCenario, B: EstadoCenario): void {
  const caixa = $('r-cmp');
  caixa.replaceChildren();
  caixa.append(el('p', `A: ${resumoCenario(A)}`, 'nota'), el('p', `B: ${resumoCenario(B)}`, 'nota'));
  const ids = redeBase().ids;
  const d = r.diferenca!;
  const a = r.porMetrica;
  const bb = r.porMetricaB!;
  const ppF = (x: number) => pp(x, 3);
  const linhas = ids.map((l) => {
    const k = `${l}.minutosInterrupcao`;
    const disp = `${l}.disponibilidade`;
    const thp = `${l}.trensHoraPerdidos`;
    return [
      nomeLinha(l),
      num(a[k].media, 1),
      num(bb[k].media, 1),
      `${comSinal(d[k].media, 1)} (${comSinal(d[k].ic95[0], 1)} a ${comSinal(d[k].ic95[1], 1)})`,
      `${ppF(d[disp].media)} (${ppF(d[disp].ic95[0])} a ${ppF(d[disp].ic95[1])})`,
      `${comSinal(d[thp].media, 2)} (${comSinal(d[thp].ic95[0], 2)} a ${comSinal(d[thp].ic95[1], 2)})`,
    ];
  });
  const od = 'rede.dispOD';
  linhas.push(['Rede (origem-destino)', '', '', '', `${ppF(d[od].media)} (${ppF(d[od].ic95[0])} a ${ppF(d[od].ic95[1])})`, '']);
  caixa.append(tabela(['Linha', 'Min parados/dia em A', 'em B', 'B − A (IC 95%)', 'Disponibilidade B − A', 'Trens-hora perdidos B − A'], linhas, [1, 2, 3, 4, 5]));
  const g = el('div');
  graficoBarras(
    g,
    ids.map((l) => ({ rotulo: nomeLinha(l), valor: d[`${l}.minutosInterrupcao`].media, ic: d[`${l}.minutosInterrupcao`].ic95, cor: corLinha(l), dica: 'negativo: B para menos que A' })),
    { titulo: 'Diferença de minutos parados por dia, B − A (IC 95%)', formata: (x) => comSinal(x, 1), eixo: 'minutos por dia (negativo = B melhor)', colunaValor: 'B − A' },
  );
  caixa.append(g, el('p', 'Intervalo que não cruza o zero: a diferença não é só sorte do sorteio, para estas hipóteses.', 'nota'));
}

// ---------- expansão ----------
function rodaExpansao(pedido: PedidoExpansao): Promise<RespostaExpansao> {
  return new Promise((resolve, reject) => {
    const w = new Worker(new URL('./trabalhador_expansao.ts', import.meta.url), { type: 'module' });
    w.onmessage = (ev: MessageEvent<RespostaExpansao>) => {
      w.terminate();
      if (ev.data.tipo === 'erro') reject(new Error(ev.data.mensagem));
      else resolve(ev.data);
    };
    w.onerror = (e) => {
      w.terminate();
      reject(new Error(e.message));
    };
    w.postMessage(pedido);
  });
}

function opcoesEstados() {
  return {
    amostras: Number($<HTMLSelectElement>('e-amostras').value),
    semente: estado.semente,
    rotaAlternativa: true,
    retornoParcial: estado.politicas.retornoParcial,
    tratamentoCausaComum: estado.politicas.tratamentoCausaComum,
  };
}

function montaCandidatas(): void {
  const caixa = $('lista-candidatas');
  caixa.replaceChildren();
  const porId = new Map(dados.candidatasJson.candidatas.map((c) => [c.id, c]));
  for (const c of candidatas) {
    const j = porId.get(c.id.split('+')[0]);
    const d = el('div', undefined, 'cand');
    const nome = el('div', undefined, 'nome');
    const tr = el('span', undefined, 'traco');
    tr.style.borderTopColor = corDaCandidata(c, redeBase());
    nome.append(tr, c.nome);
    d.append(nome);
    if (j) {
      d.append(el('div', `${j.tipo} · ${j.proponente} · ${j.ano} · ${c.status}`, 'nota'));
      const km = c.extras?.length ? '' : ` · ${num(j.km_reta_total, 1)} km em linha reta`;
      d.append(el('div', `${c.estacoesNovas?.length ?? 0} estações novas${km}`, 'nota'));
      const fontes = el('div', undefined, 'nota');
      j.fontes.slice(0, 3).forEach((f, i) => {
        if (i) fontes.append(' · ');
        const a = el('a', `fonte ${i + 1}`);
        a.href = f;
        fontes.append(a);
      });
      d.append(fontes);
    }
    if (c.extras?.length) d.append(el('div', 'Avaliada junto com o prolongamento da Azul: a Vertières da Rosa vira correspondência.', 'nota'));
    d.addEventListener('mouseenter', () => mapa.mostraCandidatas(candidatas, c.id));
    d.addEventListener('mouseleave', () => mapa.mostraCandidatas(candidatas));
    caixa.append(d);
  }
  const est = redeBase().estacoes.slice().sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
  const itens = est.map((e) => [e.id, e.nome] as [string, string]);
  opcoes($('e-de'), itens, est[0].id);
  opcoes($('e-para'), itens, est[1].id);
}

function mostraRanking(destino: HTMLElement, ranking: ItemRanking[], titulo: string, limite?: number): void {
  destino.replaceChildren();
  const lista = limite ? ranking.slice(0, limite) : ranking;
  if (!lista.length) {
    destino.append(el('p', 'Nenhuma candidata.', 'nota'));
    return;
  }
  const ppF = (x: number) => pp(x, 4);
  destino.append(
    tabela(
      ['Candidata', 'km', 'Ganho de disponibilidade OD (IC 95%)', 'Com causa comum', 'Ganho por km', 'Minutos-par por ano evitados', 'Traçado'],
      lista.map((it) => [
        it.candidata.nome,
        num(it.km, 1),
        `${ppF(it.ganho.media)} (${ppF(it.ganho.ic95[0])} a ${ppF(it.ganho.ic95[1])})`,
        `${ppF(it.ganhoComCausaComum.media)} (${ppF(it.ganhoComCausaComum.ic95[0])} a ${ppF(it.ganhoComCausaComum.ic95[1])})`,
        pp(it.ganhoPorKm, 5),
        `${num(it.minutosParAnoEvitados.media, 0)} (${num(it.minutosParAnoEvitados.ic95[0], 0)} a ${num(it.minutosParAnoEvitados.ic95[1], 0)})`,
        it.candidata.status,
      ]),
      [1, 2, 3, 4, 5],
    ),
  );
  const g = el('div');
  graficoBarras(
    g,
    lista.map((it) => ({ rotulo: it.candidata.nome.length > 26 ? `${it.candidata.nome.slice(0, 25)}…` : it.candidata.nome, valor: it.ganho.media * 100, ic: [it.ganho.ic95[0] * 100, it.ganho.ic95[1] * 100], cor: corDaCandidata(it.candidata, redeBase()), dica: it.candidata.nome })),
    { titulo, formata: (x) => `${comSinal(x, 3)} pp`, eixo: 'pontos percentuais de disponibilidade origem-destino', colunaValor: 'Ganho (pp)' },
  );
  destino.append(g);
  const it0 = lista[0];
  const det = el('details');
  det.append(el('summary', `Método e hipóteses (${inteiro(it0.amostras)} amostras de estado, semente ${it0.semente})`));
  const ul = el('ul');
  for (const h of it0.hipoteses) ul.append(el('li', h));
  ul.append(el('li', 'Disponibilidade dos pares de estações de hoje, ponderados pela oferta (não há passageiros diários). Estações novas não entram como pares.'));
  ul.append(el('li', '"Com causa comum": a candidata para junto quando uma falha de causa comum atinge as linhas em que ela encosta.'));
  det.append(ul);
  destino.append(det);
}

async function avaliaPublicadas(): Promise<void> {
  const b = $<HTMLButtonElement>('b-exp');
  b.disabled = true;
  $('s-exp').textContent = 'Avaliando…';
  try {
    const { json } = redeDo(estado.greve);
    const r = await rodaExpansao({ tipo: 'candidatas', redeJson: json, chaveRede: chaveRede(estado.greve), parametros: dados.parametros, cenario: paraCenarioMotor(estado), candidatas, opcoes: opcoesEstados() });
    if (r.tipo !== 'candidatas') return;
    $('s-exp').textContent = `Pronto em ${num(r.segundos, 1)} s.`;
    mostraRanking($('r-exp'), r.ranking, 'Ganho de disponibilidade origem-destino com cada candidata (IC 95%)');
  } catch (e) {
    mostraErro(e);
  } finally {
    b.disabled = false;
  }
}

async function avaliaLivre(): Promise<void> {
  const de = $<HTMLSelectElement>('e-de').value;
  const para = $<HTMLSelectElement>('e-para').value;
  if (de === para) {
    $('s-busca').textContent = 'Escolha duas estações diferentes.';
    return;
  }
  const { json, rede } = redeDo(estado.greve);
  $('s-busca').textContent = 'Avaliando a ligação livre…';
  try {
    const r = await rodaExpansao({ tipo: 'candidatas', redeJson: json, chaveRede: chaveRede(estado.greve), parametros: dados.parametros, cenario: paraCenarioMotor(estado), candidatas: [candidataLivre(rede, de, para)], opcoes: opcoesEstados() });
    if (r.tipo !== 'candidatas') return;
    $('s-busca').textContent = `Ligação livre avaliada em ${num(r.segundos, 1)} s.`;
    mostraRanking($('r-busca'), r.ranking, 'Ganho com a ligação livre (IC 95%)');
  } catch (e) {
    mostraErro(e);
  }
}

async function busca(): Promise<void> {
  const b = $<HTMLButtonElement>('b-busca');
  b.disabled = true;
  $('s-busca').textContent = 'Buscando… (pode levar alguns minutos com muitas amostras)';
  try {
    const { json } = redeDo(estado.greve);
    const op = { ...opcoesEstados(), amostras: Math.min(20_000, Number($<HTMLSelectElement>('e-amostras').value)) };
    const r = await rodaExpansao({ tipo: 'busca', redeJson: json, chaveRede: chaveRede(estado.greve), parametros: dados.parametros, cenario: paraCenarioMotor(estado), distanciaMaxKm: Number($<HTMLSelectElement>('e-dmax').value), opcoes: op });
    if (r.tipo !== 'busca') return;
    $('s-busca').textContent = `${inteiro(r.porGanho.length)} ligações avaliadas em ${num(r.segundos, 1)} s (${inteiro(op.amostras)} amostras cada).`;
    const caixa = $('r-busca');
    const a = el('div');
    const bk = el('div');
    caixa.replaceChildren(el('h3', 'As 10 de maior ganho'), a, el('h3', 'As 10 de maior ganho por km'), bk);
    mostraRanking(a, r.porGanho, 'Maior ganho (IC 95%)', 10);
    mostraRanking(bk, r.porKm, 'Maior ganho por km (IC 95%)', 10);
  } catch (e) {
    mostraErro(e);
  } finally {
    b.disabled = false;
  }
}

// ---------- parâmetros ----------
function mostraParametros(): void {
  const caixa = $('r-param');
  if (!caixa) return;
  caixa.replaceChildren();
  const p = dados.parametros;
  const ids = redeBase().ids;
  caixa.append(
    el(
      'p',
      `Todos os números do simulador vêm de dados/derivados/simulador/parametros.json (versão ${p.versao}, ano-base ${p.ano_base}, código ${p.codigo_commit}). Cada um tem status: "ajustado" (estimado dos dados, com IC 95%), "deduzido", "hipótese" (sem dado) ou "não verificado".`,
      'nota',
    ),
  );
  const ic = (x: Parametro, casas = 4) => comIC(x.valor, x.ic95 ?? undefined, casas);
  caixa.append(el('h3', 'Taxa-base: falhas por trem-hora nas condições de referência'));
  caixa.append(
    tabela(
      ['Linha', 'Material rodante', 'Equipamentos fixos', 'Status', 'Fonte'],
      ids.map((l) => {
        const mr = p.taxas.MR.base_por_trem_hora[l];
        const ef = p.taxas.EF.base_por_trem_hora[l];
        return [nomeLinha(l), mr ? ic(mr, 5) : '—', ef ? ic(ef, 5) : '—', selo(mr?.status ?? '—'), mr ? linkFonte(mr) : ''];
      }),
      [1, 2],
    ),
  );
  caixa.append(el('h3', 'Multiplicadores do cenário escolhido (1 = condição de referência)'));
  const c = paraCenarioMotor(estado).condicoes ?? {};
  const fatores: [string, string][] = Object.entries(c).filter(([, v]) => v !== '0' || false);
  if (estado.jogo) fatores.push(['jogo', '1']);
  const linhasM = fatores.map(([fator, nivel]) => {
    const mr = p.taxas.MR.multiplicadores[fator]?.[nivel];
    const ef = p.taxas.EF.multiplicadores[fator]?.[nivel];
    return [`${fator} = ${ROTULOS[nivel] ?? nivel}`, mr ? ic(mr, 2) : '1 (referência)', ef ? ic(ef, 2) : '1 (referência)', selo(mr?.status ?? ef?.status ?? 'ajustado'), mr ? linkFonte(mr) : ''];
  });
  caixa.append(tabela(['Fator', 'Material rodante', 'Equipamentos fixos', 'Status', 'Fonte'], linhasM, [1, 2]));
  caixa.append(el('p', 'A faixa do dia (abertura, picos, noite) e o tipo de dia também multiplicam a taxa, hora a hora, pelos coeficientes do mesmo modelo.', 'nota'));
  caixa.append(el('h3', 'Tempo até o serviço voltar'));
  caixa.append(
    el(
      'p',
      'Parte das falhas não interrompe o serviço (massa em zero). Quando interrompe, o simulador sorteia a duração da amostra observada (distribuição empírica); a lognormal ajustada fica como referência, porque subestimava a média.',
      'nota',
    ),
  );
  caixa.append(
    tabela(
      ['Linha e causa', 'Sem interrupção (IC 95%)', 'Duração média se parar (min)', 'Durações observadas', 'Método do sorteio', 'Fonte'],
      Object.entries(p.ttr).map(([k, v]) => {
        const a = v.amostra_positivos;
        return [
          k.replace('|', ' · '),
          comIC(v.p_zero.valor, v.p_zero.ic95 ?? undefined, 1, (x, cs) => pct(x, cs)),
          a ? num(a.media_min, 1) : `${num(Math.exp(v.mu_log.valor + v.sigma_log.valor ** 2 / 2), 1)} (lognormal)`,
          a ? inteiro(a.n) : '—',
          a ? 'distribuição empírica' : 'lognormal',
          linkFonte(v.mu_log),
        ];
      }),
      [1, 2, 3],
    ),
  );
  caixa.append(el('h3', 'Agrupamento das falhas (renovação Weibull no tempo reescalado; forma 1 = Poisson)'));
  caixa.append(
    tabela(
      ['Linha e causa', 'Forma (IC 95%)', 'Processo', 'Fonte'],
      Object.entries(p.renovacao).map(([k, v]) => [k.replace('|', ' · '), ic(v.forma, 3), v.processo ?? '', linkFonte(v.forma)]),
      [1],
    ),
  );
  caixa.append(el('h3', 'Causa comum: eventos que param várias linhas juntas'));
  caixa.append(
    tabela(
      ['Grupo de linhas', 'Eventos por hora de operação (IC 95%)', 'Sem interrupção', 'Duração média se parar (min)', 'Método', 'Fonte'],
      Object.entries(p.causa_comum).map(([k, v]) => [
        (v.linhas ?? k.split('-')).map(nomeLinha).join(' + '),
        comIC(v.taxa_por_hora_op.valor * 1e4, v.taxa_por_hora_op.ic95 ? v.taxa_por_hora_op.ic95.map((x) => x * 1e4) : undefined, 2) + ' × 10⁻⁴',
        pct(v.duracao.p_zero.valor, 0),
        v.duracao.amostra_positivos ? num(v.duracao.amostra_positivos.media_min, 1) : num(Math.exp(v.duracao.mu_log.valor + v.duracao.sigma_log.valor ** 2 / 2), 1),
        v.duracao.amostra_positivos ? 'distribuição empírica' : 'lognormal',
        linkFonte(v.taxa_por_hora_op),
      ]),
      [1, 2, 3],
    ),
  );
  if (p.causa_comum_beta && Object.keys(p.causa_comum_beta).length) {
    caixa.append(el('p', 'Fator β por par de linhas (fração das falhas de cada linha que ocorreu junto com a outra; IC de Clopper-Pearson):', 'nota'));
    caixa.append(
      tabela(
        ['Par', 'Eventos', 'β da 1ª linha', 'β da 2ª linha'],
        Object.entries(p.causa_comum_beta).map(([k, v]) => [k.split('-').map(nomeLinha).join(' e '), inteiro(v.eventos), ic(v.beta_a, 4), ic(v.beta_b, 4)]),
        [1, 2, 3],
      ),
    );
  }
  caixa.append(el('h3', 'Frota (reserva fria k-de-n)'));
  caixa.append(
    tabela(
      ['Linha', 'Trens necessários', 'Falhas de material rodante por trem-dia (IC 95%)', 'Status', 'Fonte'],
      ids.map((l) => {
        const f = p.frota[l];
        return [nomeLinha(l), f ? inteiro(f.trens_necessarios.valor) : '—', f ? ic(f.lambda_trem_dia, 5) : '—', selo(f?.lambda_trem_dia.status ?? '—'), f ? linkFonte(f.lambda_trem_dia) : ''];
      }),
      [1, 2],
    ),
  );
  caixa.append(el('h3', 'Hipóteses'));
  caixa.append(
    tabela(
      ['Hipótese', 'Valor no cenário', 'Padrão', 'Faixa razoável', 'Status'],
      Object.entries(p.hipoteses).map(([k, v]) => [k.replaceAll('_', ' '), num(estado.hipoteses[k] ?? v.valor, 2), num(v.valor, 2), v.faixa ? `${num(v.faixa[0], 2)} a ${num(v.faixa[1], 2)}` : '—', selo(v.status)]),
      [1, 2],
    ),
  );
}

// ---------- abas ----------
function trocaAba(id: string): void {
  for (const b of document.querySelectorAll<HTMLButtonElement>('.abas [role="tab"]')) {
    const ativa = b.id === `tab-${id}`;
    b.setAttribute('aria-selected', String(ativa));
    $(b.getAttribute('aria-controls')!).hidden = !ativa;
  }
  const comMapa = id === 'dia' || id === 'expansao';
  $('mapa-caixa').hidden = !comMapa;
  if (comMapa) requestAnimationFrame(() => mapa.resize());
  mapa.mostraCandidatas(id === 'expansao' ? candidatas : null);
}

// ---------- início ----------
async function inicia(): Promise<void> {
  montaRodape($('rodape'), BASE);
  const [redeJson, parametros, candidatasJson, linhasGeo, estacoesGeo, locais] = await Promise.all([
    carrega<RedeJson>('simulador/rede.json'),
    carrega<Parametros>('simulador/parametros.json'),
    carrega<CandidatasJson>('simulador/candidatas.json'),
    carrega<GeoJSON.FeatureCollection>('geo/linhas.geojson'),
    carrega<GeoJSON.FeatureCollection>('geo/estacoes.geojson'),
    carrega<Local[]>('geo/locais.json'),
  ]);
  dados = { redeJson, parametros, candidatasJson, linhasGeo, estacoesGeo, locais };
  if (location.hash.length > 1) estado = desserializa(location.hash);
  const rede = redeDo('nao').rede;
  candidatas = candidatasDoJson(candidatasJson, rede);
  try {
    mapa = new MapaSimulador('mapa', { linhasGeo, estacoesGeo, locais, rede });
  } catch (e) {
    // sem WebGL (ou o MapLibre não abriu): o resto da página funciona sem o mapa
    const aviso = el('p', `O mapa não abriu neste navegador (${e instanceof Error ? e.message : String(e)}). O resto do simulador funciona.`, 'erro');
    $('mapa').append(aviso);
    mapa = new VistaSemMapa();
  }

  montaFormulario();
  montaCandidatas();
  mostraAvisos();
  mostraParametros();
  history.replaceState(null, '', `#${serializa(estado)}`);

  $('form-cenario').addEventListener('change', (ev) => {
    const alvo = ev.target as HTMLElement;
    if (alvo.closest('#c-politicas') || alvo.closest('#c-hipoteses')) return;
    leFormulario();
    mudou();
  });
  $('t-dia').addEventListener('change', () => {
    leFormulario();
    mudou();
  });
  $('b-padrao').addEventListener('click', () => {
    estado = copia(PADRAO);
    montaFormulario();
    mudou();
  });
  $('b-link').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(location.href);
      $('msg-link').textContent = 'Link copiado. Quem abrir verá o mesmo cenário e os mesmos números.';
    } catch {
      $('msg-link').textContent = `Copie o endereço da barra do navegador: ${location.href}`;
    }
  });
  window.addEventListener('hashchange', () => {
    const novo = desserializa(location.hash);
    if (serializa(novo) === serializa(estado)) return;
    estado = novo;
    montaFormulario();
    mudou();
  });
  for (const b of document.querySelectorAll<HTMLButtonElement>('.abas [role="tab"]')) b.addEventListener('click', () => trocaAba(b.id.replace('tab-', '')));
  $('b-play').addEventListener('click', () => {
    tocando = !tocando;
    if (tocando && dia && tSim >= dia.fim) tSim = dia.ini;
    $('b-play').textContent = tocando ? '❚❚' : '▶';
    $('b-play').setAttribute('aria-label', tocando ? 'Pausar' : 'Tocar');
  });
  $('t-barra').addEventListener('input', () => {
    tSim = Number($<HTMLInputElement>('t-barra').value);
    desenhaInstante();
  });
  $<HTMLInputElement>('t-locais').addEventListener('change', (ev) => mapa.mostraLocais((ev.target as HTMLInputElement).checked));
  $('b-mc').addEventListener('click', rodaMC);
  $('b-ano').addEventListener('click', estimaAno);
  $('b-mc-cancela').addEventListener('click', () => pool.cancela());
  $('b-fixa-a').addEventListener('click', () => {
    cenarioA = copia(estado);
    $('resumo-a').textContent = `A fixado: ${resumoCenario(cenarioA)}`;
    $<HTMLButtonElement>('b-comparar').disabled = false;
  });
  $('b-comparar').addEventListener('click', compara);
  $('b-cmp-cancela').addEventListener('click', () => poolAB.cancela());
  $('b-exp').addEventListener('click', avaliaPublicadas);
  $('b-livre').addEventListener('click', avaliaLivre);
  $('b-busca').addEventListener('click', busca);

  simulaDiaMostrado();
  requestAnimationFrame(laco);
  // o mapa pode demorar (ou não carregar o fundo): quando abrir, desenha o instante atual
  void mapa.pronto.then(() => {
    desenhaInstante();
    trocaAba(document.querySelector('.abas [aria-selected="true"]')?.id.replace('tab-', '') ?? 'dia');
  });
  // cenário padrão já com resultado: rodada curta automática
  void rodaMC();
}

inicia().catch(mostraErro);
