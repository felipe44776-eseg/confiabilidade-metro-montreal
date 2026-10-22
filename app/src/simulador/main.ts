// Página /simulador/ (specs 010, 011, 014, 015 e 016): cenário, dia no mapa, Monte Carlo, viagem de A a B
// com linhas novas, comparação e expansão.
import './simulador.css';
import type { Local } from '../locais';
import type { ResultadoMC } from '../mc/pool';
import { PoolMC } from '../mc/pool';
import type { Agregado, Estimativa } from '../mc/rodadas';
import { anualiza, DIAS_POR_TIPO_ANO } from '../mc/rodadas';
import type { Contexto } from '../motor/contexto';
import { avisosDoCenario, preparaContexto } from '../motor/contexto';
import type { ResultadoDia } from '../motor/dia';
import { simulaDia } from '../motor/dia';
import type { Candidata, ItemRanking, PontoDesenho } from '../motor/expansao';
import { candidataDesenhada, candidataLivre } from '../motor/expansao';
import { partesDe } from '../motor/linhas_novas';
import { HIPOTESES_PADRAO } from '../motor/hipoteses';
import type { NomePolitica } from '../motor/politicas';
import { NOMES_POLITICAS } from '../motor/politicas';
import { sementeDaRodada } from '../motor/prng';
import type { Rede } from '../motor/rede';
import { haversineKm, montaRede } from '../motor/rede';
import type { Parametro, Parametros, RedeJson, TipoDia } from '../motor/tipos';
import type { AvaliadorViagem, TrechoViagem, VariantePedida } from '../motor/viagem';
import { avaliadoresViagem, LIMIARES_ATRASO_MIN, nomesVariantes, PASSO_SAIDAS_S } from '../motor/viagem';
import { TIPOS_DIA } from '../motor/tipos';
import { noves, novesIC, razaoPareada, textoRazao } from '../ui/escala';
import { graficoBarras, graficoPontosLog } from '../ui/graficos';
import { casasPara, comIC, comSinal, inteiro, num, pct, pp } from '../ui/formato';
import { montaRodape, REPO } from '../ui/rodape';
import type { Bloco, Ocorrencia } from './animacao';
import { blocosAtivos, blocosDoDia, cruzadas, falhasAte, FPS_PARADO, fracaoNaBarra, minutosAte, ocorrenciasDoDia, posicoes, relogio, textoFps, VELOCIDADE_PADRAO, VELOCIDADES } from './animacao';
import type { CandidatasJson } from './candidatas';
import { candidatasDoJson } from './candidatas';
import type { EstadoCenario, Greve } from './cenario';
import { aplicaGreve, chaveCenario, chaveRede, copia, desserializa, itensDoCenario, JANELAS_GREVE, MAX_DESENHADAS, MAX_PONTOS_DESENHO, MESES, NIVEIS, ORDEM_POLITICAS, PADRAO, paraCenarioMotor, ROTULOS, serializa } from './cenario';
import type { Esperado } from './efeito';
import { esperadoPorDia } from './efeito';
import { avisosDeExtrapolacao } from './extrapolacao';
import type { CampoPeso, Resumos, ResumoTaxa } from './pesos';
import { notaDoMetodo, pesosDoCenario } from './pesos';
import type { VistaMapa } from './mapa_sim';
import { corDaCandidata, MapaSimulador, VistaSemMapa } from './mapa_sim';
import { PoolAB } from './pool_ab';
import type { ResultadoViagem } from './pool_viagem';
import { PoolViagem } from './pool_viagem';
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
/** Itens na lista de eventos sobre o mapa. */
const EVENTOS_NA_LISTA = 4;

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
/** Resumos do ajuste da taxa (dados/modelos/taxa_<causa>.json), para a nota do método; null até carregarem. */
let resumos: Resumos = null;

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
  mostraPesos();
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
  const nomes = [...new Set([...Object.keys(dados.parametros.hipoteses), ...Object.keys(HIPOTESES_PADRAO)])];
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

// ---------- peso de cada variável (spec 011, decisão D51) ----------
const ID_PESO: Record<CampoPeso, string> = {
  tipo: 'p-tipo', mes: 'c-estacao', temp: 'p-temp', precip: 'p-precip', cond: 'p-cond',
  neve: 'p-neve', jogo: 'p-jogo', gp: 'p-gp', feriado: 'p-feriado', greve: 'p-greve',
};

function mostraPesos(): void {
  const t = pesosDoCenario(dados.parametros, estado, resumos);
  for (const [campo, id] of Object.entries(ID_PESO)) $(id).textContent = t[campo as CampoPeso];
}

function montaNotaMetodo(): void {
  const n = notaDoMetodo(dados.parametros, resumos);
  $('m-resumo').textContent = n.resumo;
  const ol = el('ol');
  for (const p of n.passos) ol.append(el('li', p));
  const fonte = el('p', undefined, 'nota');
  const rel = el('a', 'relatório do modelo');
  rel.href = FONTE_PARAMETRO['pipeline/modelo_taxa.py'];
  const cod = el('a', 'código');
  cod.href = `${REPO}/blob/main/pipeline/modelo_taxa.py`;
  const dec = el('a', 'decisões D19, D20 e D42');
  dec.href = `${BASE}decisoes/`;
  fonte.append('Todos os coeficientes, resíduos e testes: ', rel, ' e ', cod, '; por que assim: ', dec, '. A aba "Parâmetros" mostra os pesos do cenário escolhido e a taxa-base de cada linha.');
  $('m-corpo').replaceChildren(
    ol,
    tabela(
      ['Faixa do dia', 'MR', 'EF'],
      n.faixas.map((f) => {
        const c = el('span');
        c.append(f.faixa, el('br'), el('span', f.horas, 'horas'));
        return [c, f.mr, f.ef];
      }),
      [1, 2],
    ),
    fonte,
  );
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
  mostraPesos();
  mostraAvisos();
  marcaDesatualizado();
  mostraParametros();
  clearTimeout(esperaDia);
  esperaDia = setTimeout(() => {
    simulaDiaMostrado();
    aplicado();
    mostraRotaViagem();
  }, 120);
}

// ---------- cenário aplicado (spec 011, decisão D50) ----------
/** Contexto do cenário atual, guardado: emendar os dias só sorteia o dia novo (3 ms), sem refazer o cenário (22 ms). */
let ctxCenario: { chave: string; ctx: Contexto; esperado: Esperado } | null = null;
let esperadoNoPadrao: Esperado | null = null;
/** Dias completos tocados no mapa desde a última mudança de cenário, e as falhas sorteadas neles. */
let placar = { dias: 0, falhas: 0 };

function contextoDoCenario(): { ctx: Contexto; esperado: Esperado } {
  const chave = chaveCenario({ ...estado, semente: 0, rodadas: 0 });
  if (ctxCenario?.chave !== chave) {
    const ctx = preparaContexto(redeDo(estado.greve).rede, dados.parametros, paraCenarioMotor(estado));
    ctxCenario = { chave, ctx, esperado: esperadoPorDia(ctx, estado.politicas) };
  }
  return ctxCenario;
}

function esperadoPadrao(): Esperado {
  esperadoNoPadrao ??= esperadoPorDia(preparaContexto(redeDo(PADRAO.greve).rede, dados.parametros, paraCenarioMotor(PADRAO)), PADRAO.politicas);
  return esperadoNoPadrao;
}

/** Chamada quando o cenário muda: zera o placar, mostra a hora e pisca a faixa. */
function aplicado(abertura = false): void {
  placar = { dias: 0, falhas: 0 };
  const hora = new Date().toLocaleTimeString('pt-BR');
  $('aplicado-quando').textContent = abertura ? `aplicado às ${hora}` : `aplicado às ${hora}; o dia no mapa foi sorteado de novo com este cenário`;
  if (!abertura) {
    const caixa = $('aplicado');
    caixa.classList.remove('piscou');
    void caixa.offsetWidth; // reinicia a animação
    caixa.classList.add('piscou');
  }
  mostraAplicado();
}

function mostraAplicado(): void {
  if (!ctxCenario) return;
  const ul = $('aplicado-itens');
  ul.replaceChildren(
    ...itensDoCenario(estado, NOMES_POLITICAS).map((it) => {
      const li = el('li', undefined, it.mudou ? 'mudou' : '');
      li.append(el('span', `${it.rotulo}: `, 'rot'), it.texto);
      if (it.mudou) li.title = 'Diferente do cenário padrão';
      return li;
    }),
  );
  const esp = ctxCenario.esperado;
  const pad = esperadoPadrao();
  const razao = pad.total > 0 ? esp.total / pad.total : 1;
  const ef = $('aplicado-efeito');
  ef.replaceChildren(
    'Falhas esperadas por dia neste cenário: ',
    el('strong', num(esp.total, 2)),
    ` (cenário padrão: ${num(pad.total, 2)}; `,
    el('strong', `×${num(razao, 2)}`),
    '). Por linha: ',
  );
  redeBase().ids.forEach((l, i) => {
    const p = el('span', undefined, 'ponto');
    p.style.background = corLinha(l);
    ef.append(i ? ' · ' : '', p, ` ${nomeLinha(l)} ${num(esp.porLinha[l].total, 2)}`);
  });
  ef.append('. O clima e os eventos multiplicam a taxa por trem-hora; o tipo de dia e a greve mudam quantos trens circulam. Das políticas, só o tratamento da causa comum muda quantas falhas ocorrem; as outras mudam quanto a falha para a linha.');
  $('aplicado-placar').textContent = placar.dias
    ? `No mapa: ${inteiro(placar.dias)} dia(s) completo(s) deste cenário, ${inteiro(placar.falhas)} falhas sorteadas, ${num(placar.falhas / placar.dias, 2)} por dia (esperado: ${num(esp.total, 2)}). Com mais dias, a média se aproxima do esperado.`
    : 'Toque o dia no mapa a 1 h/s ou mais rápido: a cada dia completo, a contagem de falhas sorteadas aparece aqui, para comparar com o esperado.';
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

/** Sorteia o dia `estado.dia` do cenário. `doInicio`: a animação recomeça na abertura do serviço (dia emendado). */
function simulaDiaMostrado(doInicio = false): void {
  try {
    const { ctx } = contextoDoCenario();
    const rede = ctx.rede;
    const r = simulaDia(ctx, estado.politicas, sementeDaRodada(estado.semente, estado.dia), { registrar: true, trajetorias: true });
    const [ini, fim] = ctx.horario.janelaRede;
    dia = { r, rede, blocos: blocosDoDia(r), ocorrencias: ocorrenciasDoDia(r), ini, fim, inicioServico: ctx.horario.inicioServico };
    const barra = $<HTMLInputElement>('t-barra');
    barra.min = String(Math.floor(ini));
    barra.max = String(Math.ceil(fim));
    barra.step = '30';
    if (doInicio) tSim = ini;
    else if (!(tSim >= ini && tSim <= fim)) tSim = Math.min(Math.max(7.5 * 3600, ini), fim);
    mostraFalhasDoDia();
    desenhaInstante();
  } catch (e) {
    mostraErro(e);
  }
}

/** Fim do dia com a animação tocando: conta o dia no placar e emenda o próximo dia sorteado. */
function emendaDia(): void {
  if (!dia) return;
  placar = { dias: placar.dias + 1, falhas: placar.falhas + dia.ocorrencias.length };
  estado.dia += 1;
  $<HTMLInputElement>('t-dia').value = String(estado.dia);
  history.replaceState(null, '', `#${serializa(estado)}`);
  simulaDiaMostrado(true);
  mostraAplicado();
}

const tipoDaFalha = (o: Ocorrencia) => ({ FALHA_TREM: 'material rodante', FALHA_EF: 'equipamento fixo', CAUSA_COMUM: 'causa comum' })[o.tipo as 'FALHA_TREM'] ?? o.tipo;

/** Evento vermelho: pulso no local e item na lista sobre o mapa. */
function anunciaFalha(o: Ocorrencia): void {
  mapa.pulsa(o);
  const lista = $('eventos');
  const li = el('li', undefined, 'novo');
  const p = el('span', undefined, 'ponto');
  p.style.background = corLinha(o.linha);
  li.append(p, ` Dia ${estado.dia} · ${relogio(o.t)} · ${nomeLinha(o.linha)} · ${tipoDaFalha(o)} · ${o.duracaoS > 0 ? `${num(o.duracaoS / 60, 0)} min parada` : 'sem interrupção'}`);
  lista.prepend(li);
  while (lista.children.length > EVENTOS_NA_LISTA) lista.lastElementChild!.remove();
  lista.hidden = false;
}

/** Riscos vermelhos na barra de tempo, um por falha do dia. */
function marcaBarra(): void {
  if (!dia) return;
  const caixa = $('t-marcas');
  caixa.replaceChildren(
    ...dia.ocorrencias.map((o) => {
      const i = el('i', undefined, o.duracaoS > 0 ? 'para' : '');
      i.style.left = `${(fracaoNaBarra(o.t, dia!.ini, dia!.fim) * 100).toFixed(2)}%`;
      i.title = rotuloOcorrencia(o);
      return i;
    }),
  );
  ocorridasMarcadas = -1;
}

function rotuloOcorrencia(o: Ocorrencia): string {
  return `${relogio(o.t)} · ${nomeLinha(o.linha)} · ${tipoDaFalha(o)} · ${o.duracaoS > 0 ? `${num(o.duracaoS / 60, 0)} min parada` : 'sem interrupção'} · ${o.detalhe}`;
}

function mostraFalhasDoDia(): void {
  if (!dia) return;
  marcaBarra();
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
    r.insertCell().textContent = tipoDaFalha(o);
    r.insertCell().textContent = o.duracaoS > 0 ? `${num(o.duracaoS / 60, 1)} min` : 'sem interrupção';
    r.insertCell().textContent = o.detalhe;
    r.style.cursor = 'pointer';
    r.title = 'Ir para esta falha no mapa';
    r.addEventListener('click', () => {
      tSim = Math.max(dia!.ini, o.t - 60);
      desenhaInstante();
      mapa.pulsa(o);
    });
  }
}

/** Quantas falhas do dia já estavam marcadas como ocorridas na barra e na tabela (só remarca quando muda). */
let ocorridasMarcadas = -1;
function marcaOcorridas(n: number): void {
  if (n === ocorridasMarcadas) return;
  ocorridasMarcadas = n;
  $('t-marcas')
    .querySelectorAll('i')
    .forEach((i, k) => i.classList.toggle('passou', k < n));
  const linhas = $<HTMLTableElement>('tab-falhas').tBodies[0].rows;
  if (dia?.ocorrencias.length) for (let k = 0; k < linhas.length; k++) linhas[k].classList.toggle('futura', k >= n);
}

function desenhaInstante(): void {
  if (!dia) return;
  const pos = posicoes(dia.rede, dia.r.trajetorias ?? {}, tSim);
  mapa.atualizaTrens(pos);
  const ativos = blocosAtivos(dia.blocos, tSim);
  mapa.atualizaBloqueios(ativos);
  const ocorridas = falhasAte(dia.ocorrencias, tSim);
  mapa.atualizaFalhas(ocorridas, rotuloOcorrencia);
  marcaOcorridas(ocorridas.length);
  $<HTMLInputElement>('t-barra').value = String(tSim);
  $('t-relogio').textContent = relogio(tSim);
  const min = minutosAte(dia.rede, dia.inicioServico, dia.blocos, tSim);
  const caixa = $('indicadores');
  const cartoes: [string, string, string?][] = [
    ['Trens em viagem', inteiro(pos.length)],
    ['Bloqueios ativos', inteiro(ativos.length)],
    ['Falhas até agora', inteiro(ocorridas.length)],
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
  if (!tocando) {
    // parada, a página ainda pede quadros; a taxa não seria da animação
    quadros = 0;
    inicioContagem = agora;
    if ($('fps').textContent !== FPS_PARADO) $('fps').textContent = textoFps(false, 0, 0);
  } else {
    if (!inicioContagem) inicioContagem = agora;
    quadros++;
    if (agora - inicioContagem >= 1000) {
      $('fps').textContent = textoFps(true, quadros, agora - inicioContagem);
      quadros = 0;
      inicioContagem = agora;
    }
  }
  if (tocando && dia) {
    const dt = ultimoQuadro ? Math.min(0.25, (agora - ultimoQuadro) / 1000) : 0;
    const antes = tSim;
    tSim = Math.min(dia.fim, tSim + dt * Number($<HTMLSelectElement>('t-vel').value));
    // em alta velocidade um quadro cruza várias falhas: todas viram evento vermelho
    for (const o of cruzadas(dia.ocorrencias, antes, tSim)) anunciaFalha(o);
    desenhaInstante();
    if (tSim >= dia.fim) {
      if ($<HTMLInputElement>('t-emenda').checked) emendaDia();
      else paraDeTocar();
    }
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
  const chave = chaveCenario(estado);
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
  caixa.append(el('p', `Cenário desta rodada: ${resumoCenario(estado)}`, 'nota'));
  const esperado = contextoDoCenario().esperado;
  caixa.append(
    tabela(
      ['Linha', 'Falhas por dia', 'Esperado pelo modelo', 'Minutos parados', 'Disponibilidade', 'Noves', 'Trens-hora perdidos', 'Viagens afetadas', 'Frota completa'],
      ids.map((l) => {
        const nome = el('span');
        const p = el('span', undefined, 'ponto');
        p.style.background = corLinha(l);
        nome.append(p, ` ${nomeLinha(l)}`);
        const falhas = (['falhasMR', 'falhasEF', 'falhasCC'] as const).reduce((s, k) => s + (m[`${l}.${k}`]?.media ?? 0), 0);
        return [
          nome,
          num(falhas, 2),
          num(esperado.porLinha[l].total, 2),
          estimativaTexto(m[`${l}.minutosInterrupcao`], num),
          estimativaTexto(m[`${l}.disponibilidade`], pctF, 1, 100),
          novesTexto(m[`${l}.disponibilidade`]),
          estimativaTexto(m[`${l}.trensHoraPerdidos`], num),
          estimativaTexto(m[`${l}.viagensAfetadas`], num),
          estimativaTexto(m[`${l}.frotaCompleta`], pctF, 0, 100),
        ];
      }),
      [1, 2, 3, 4, 5, 6, 7, 8],
    ),
  );
  caixa.append(el('p', '"Noves": −log₁₀ da indisponibilidade (99% são 2 noves, 99,9% são 3), a escala que separa valores perto de 100%.', 'nota'));
  caixa.append(el('p', '"Esperado pelo modelo" é a taxa do cenário somada no dia, a mesma que o sorteio usa; a média dos dias simulados fica perto dela, e a diferença é a variação do sorteio.', 'nota'));
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
  // trocar o dia mostrado não muda o cenário (chaveCenario ignora o dia)
  if (resultadoMC && resultadoMC.estado !== chaveCenario(estado)) $('s-mc').textContent = 'O cenário mudou: os resultados abaixo são do cenário anterior. Rode de novo.';
}

// ---------- viagem de A a B (specs 015 e 016) ----------
const poolViagem = new PoolViagem();
/** Avaliadores da viagem: a rede atual (primeiro) e uma versão da rede por linha nova escolhida. */
interface Avaliacao {
  avs: AvaliadorViagem[];
  variantes: VariantePedida[];
  /** Por que a versão com todas juntas ficou de fora (linhas incompatíveis). */
  aviso: string | null;
}
let resultadoViagem: { chave: string; r: ResultadoViagem; aval: Avaliacao; estado: EstadoCenario } | null = null;
let avaliacaoGuardada: { chave: string; aval: Avaliacao | null; erro: string | null } | null = null;
/** Linha em desenho no mapa (spec 016); null fora do modo de desenho. */
let desenho: PontoDesenho[] | null = null;

const chaveViagem = () =>
  `${chaveCenario(estado)}|${estado.viagemDe}|${estado.viagemPara}|${estado.linhasNovas.join(',')}|${JSON.stringify(estado.linhasDesenhadas)}|${estado.ccNova ? 1 : 0}`;
const nomeDaEstacao = (id: string) => redeBase().estacoes.find((e) => e.id === id)?.nome ?? id;
const relogioMin = (s: number) => `${String(Math.floor(s / 3600) % 24).padStart(2, '0')}:${String(Math.floor((s % 3600) / 60)).padStart(2, '0')}`;
const abaViagemAtiva = () => $('tab-viagem').getAttribute('aria-selected') === 'true';
/** Número com dois algarismos significativos (eixo e valores do gráfico em escala logarítmica). */
function numSig(x: number): string {
  if (!(x > 0)) return '0';
  return num(x, Math.max(0, Math.min(4, 1 - Math.floor(Math.log10(x)))));
}
function novesTexto(e: Estimativa | undefined): string {
  if (!e) return '—';
  const n = novesIC(e);
  const f = (x: number) => (Number.isFinite(x) ? num(x, 2) : '∞');
  return `${f(n.media)} (${f(n.ic95[0])}–${f(n.ic95[1])})`;
}
function difTexto(e: Estimativa | undefined, f: (x: number, c: number) => string, escala = 1): string {
  if (!e) return '—';
  const c = Math.max(1, casasPara(e.meiaLargura * escala));
  return `${f(e.media, c)} (${f(e.ic95[0], c)} a ${f(e.ic95[1], c)})`;
}

/** Linhas novas escolhidas para a viagem: as propostas marcadas e as desenhadas (spec 016). */
function linhasDaViagem(): Candidata[] {
  const rede = redeBase();
  const saida = estado.linhasNovas.map((id) => candidatas.find((c) => c.id === id)).filter((c): c is Candidata => !!c);
  estado.linhasDesenhadas.forEach((pts, i) => {
    try {
      saida.push(candidataDesenhada(rede, pts, i));
    } catch {
      // ponto do link que não existe mais na rede: a linha fica de fora (a lista mostra o motivo)
    }
  });
  return saida;
}

/** Uma versão da rede por linha nova e, com duas ou mais, todas juntas. */
function variantesDaViagem(ctx: Contexto): { variantes: VariantePedida[]; aviso: string | null } {
  const linhas = linhasDaViagem();
  const variantes: VariantePedida[] = linhas.map((c) => ({ id: c.id, nome: c.nome, linhas: [c] }));
  let aviso: string | null = null;
  if (linhas.length > 1) {
    try {
      partesDe(ctx, linhas);
      variantes.push({ id: 'todas', nome: 'Todas as linhas novas juntas', linhas });
    } catch (e) {
      aviso = `Sem a versão com todas juntas: ${e instanceof Error ? e.message : String(e)}.`;
    }
  }
  return { variantes, aviso };
}

/** Avaliadores da viagem no cenário atual, guardados: preparar custa dezenas de ms por versão da rede. */
function avaliacaoAtual(): { aval: Avaliacao | null; erro: string | null } {
  const chave = chaveViagem();
  if (avaliacaoGuardada?.chave !== chave) {
    let aval: Avaliacao | null = null;
    let erro: string | null = null;
    if (estado.viagemDe !== estado.viagemPara) {
      const ctx = contextoDoCenario().ctx;
      const { variantes, aviso } = variantesDaViagem(ctx);
      try {
        aval = { avs: avaliadoresViagem(ctx, estado.viagemDe, estado.viagemPara, estado.politicas, variantes, estado.ccNova), variantes, aviso };
      } catch (e) {
        erro = e instanceof Error ? e.message : String(e);
        try {
          // a rede atual sozinha, para a aba seguir útil
          aval = { avs: avaliadoresViagem(ctx, estado.viagemDe, estado.viagemPara, estado.politicas, [], false), variantes: [], aviso: null };
        } catch {
          aval = null;
        }
      }
    }
    avaliacaoGuardada = { chave, aval, erro };
  }
  return avaliacaoGuardada;
}

function montaViagem(): void {
  const itens: [string, string][] = [...redeBase().estacoes]
    .sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'))
    .map((e) => [e.id, `${e.nome} (${[...new Set(e.plataformas.map((p) => nomeLinha(p.linha)))].join(', ')})`]);
  for (const [id, campo] of [['v-de', 'viagemDe'], ['v-para', 'viagemPara']] as const) {
    const sel = $<HTMLSelectElement>(id);
    opcoes(sel, itens, estado[campo]);
    if (sel.value !== estado[campo]) {
      // id do link que não existe na rede: volta ao padrão
      estado[campo] = PADRAO[campo];
      sel.value = estado[campo];
    }
  }
  opcoes($('v-desenho-est'), itens, itens[0][0]);
  montaLinhasNovas();
  mostraRotaViagem();
}

// ----- linhas novas (spec 016) -----
function linhasMudaram(): void {
  history.replaceState(null, '', `#${serializa(estado)}`);
  mostraDesenhadas();
  mostraRotaViagem();
}

function tracoDe(c: Candidata): HTMLElement {
  const t = el('span', undefined, 'traco-linha');
  t.style.borderTopColor = corDaCandidata(c, redeBase());
  return t;
}

function montaLinhasNovas(): void {
  const caixa = $('v-cands');
  caixa.replaceChildren();
  for (const c of candidatas) {
    const lab = el('label', undefined, 'caixa');
    const cx = el('input');
    cx.type = 'checkbox';
    cx.checked = estado.linhasNovas.includes(c.id);
    cx.addEventListener('change', () => {
      const marcadas = new Set(estado.linhasNovas);
      if (cx.checked) marcadas.add(c.id);
      else marcadas.delete(c.id);
      estado.linhasNovas = candidatas.map((x) => x.id).filter((id) => marcadas.has(id));
      linhasMudaram();
    });
    lab.append(cx, tracoDe(c), c.nome);
    caixa.append(lab);
  }
  $<HTMLInputElement>('v-cc').checked = estado.ccNova;
  mostraDesenhadas();
}

const nomePonto = (p: PontoDesenho) => (typeof p === 'string' ? nomeDaEstacao(p) : 'estação nova');

function mostraDesenhadas(): void {
  const ul = $('v-desenhadas');
  ul.replaceChildren();
  const rede = redeBase();
  estado.linhasDesenhadas.forEach((pts, i) => {
    const li = el('li');
    try {
      const c = candidataDesenhada(rede, pts, i);
      const coord = (id: string) => rede.estacoes.find((e) => e.id === id) ?? c.estacoesNovas?.find((e) => e.id === id);
      let km = 0;
      for (let k = 1; k < c.sequencia.length; k++) {
        const a = coord(c.sequencia[k - 1])!;
        const b = coord(c.sequencia[k])!;
        km += haversineKm(a.lat, a.lon, b.lat, b.lon);
      }
      li.append(tracoDe(c), `Linha desenhada ${i + 1}: ${pts.map(nomePonto).join(' – ')} (${num(km, 1)} km em linha reta)`);
    } catch (e) {
      li.append(`Linha desenhada ${i + 1}: fora da avaliação (${e instanceof Error ? e.message : String(e)})`);
    }
    const b = el('button', '✕', 'secundario');
    b.type = 'button';
    b.title = 'Remover esta linha';
    b.setAttribute('aria-label', `Remover a linha desenhada ${i + 1}`);
    b.addEventListener('click', () => {
      estado.linhasDesenhadas.splice(i, 1);
      linhasMudaram();
    });
    li.append(b);
    ul.append(li);
  });
  $<HTMLButtonElement>('b-desenha').disabled = desenho !== null || estado.linhasDesenhadas.length >= MAX_DESENHADAS;
}

function coordsDoDesenho(): [number, number][] {
  const rede = redeBase();
  return (desenho ?? []).map((p) => {
    if (typeof p !== 'string') return [p.lon, p.lat];
    const e = rede.estacoes.find((x) => x.id === p)!;
    return [e.lon, e.lat];
  });
}

/** Linhas novas e a linha em desenho no mapa, só na aba da viagem. */
function mostraLinhasNovasNoMapa(): void {
  if (!abaViagemAtiva()) return;
  // o projeto conjunto (Rosa com a Azul) aparece pelas partes: o mapa pula candidatas com extras
  mapa.mostraCandidatas(linhasDaViagem().flatMap((c) => [{ ...c, extras: undefined }, ...(c.extras ?? [])]));
  mapa.mostraDesenho(desenho ? coordsDoDesenho() : null);
}

function comecaDesenho(): void {
  desenho = [];
  $('v-desenho').hidden = false;
  mapa.aoClicar((c) => acrescentaAoDesenho('estacao' in c ? c.estacao : { lat: Math.round(c.lat * 1e5) / 1e5, lon: Math.round(c.lon * 1e5) / 1e5 }));
  atualizaDesenho();
  mostraDesenhadas();
}

function terminaDesenho(salva: boolean): void {
  if (salva && desenho && desenho.length >= 2 && estado.linhasDesenhadas.length < MAX_DESENHADAS) estado.linhasDesenhadas.push(desenho);
  desenho = null;
  $('v-desenho').hidden = true;
  mapa.aoClicar(null);
  mapa.mostraDesenho(null);
  linhasMudaram();
}

function acrescentaAoDesenho(p: PontoDesenho): void {
  if (!desenho || desenho.length >= MAX_PONTOS_DESENHO) return;
  if (typeof p === 'string' && desenho.includes(p)) return; // a linha não passa duas vezes pela mesma estação
  desenho.push(p);
  atualizaDesenho();
}

function atualizaDesenho(): void {
  if (!desenho) return;
  const n = desenho.length;
  $('v-desenho-txt').textContent = n
    ? `Linha em desenho: ${desenho.map(nomePonto).join(' → ')} (${n} ${n === 1 ? 'estação' : 'estações'}${n >= MAX_PONTOS_DESENHO ? ', o máximo' : ''}).`
    : 'Linha em desenho: escolha a primeira estação no mapa ou na lista.';
  $<HTMLButtonElement>('b-desenho-ok').disabled = n < 2;
  $<HTMLButtonElement>('b-desenho-volta').disabled = n === 0;
  mapa.mostraDesenho(coordsDoDesenho());
}

// ----- caminho -----
/** Nome, cor e sentido de uma linha do caminho, também das linhas novas. */
function nomeNaRota(av: AvaliadorViagem, linha: string): string {
  if (redeBase().linhas[linha]) return nomeLinha(linha);
  return av.variante?.partes.find((p) => p.linha === linha)?.nome ?? linha;
}
function corNaRota(av: AvaliadorViagem, linha: string): string {
  const parte = av.variante?.partes.find((p) => p.linha === linha);
  return redeBase().linhas[linha] ? corLinha(linha) : parte ? corDaCandidata(parte, redeBase()) : '#6b6a64';
}
function sentidoNaRota(av: AvaliadorViagem, t: TrechoViagem): string {
  const est = av.g.linhas.find((l) => l.id === t.linha)!.estacoes;
  return (t.ate > t.de ? est[est.length - 1] : est[0]).nome;
}
const textoRota = (av: AvaliadorViagem) => av.rota.trechos.map((t) => `${nomeNaRota(av, t.linha)} até ${t.ateNome}`).join(', ');
const mesmaRota = (a: AvaliadorViagem, b: AvaliadorViagem) => textoRota(a) === textoRota(b);

function listaDaRota(av: AvaliadorViagem): HTMLElement {
  const ul = el('ul');
  av.rota.trechos.forEach((t, i) => {
    if (i > 0) ul.append(el('li', `Baldeação em ${t.deNome}: ${num(av.transferenciaS / 60, 0)} min (hipótese tempo_transferencia_min)`, 'baldeacao'));
    const li = el('li');
    const p = el('span', undefined, 'ponto');
    p.style.background = corNaRota(av, t.linha);
    li.append(p, ` ${nomeNaRota(av, t.linha)}, sentido ${sentidoNaRota(av, t)}: ${t.deNome} → ${t.ateNome} (${t.paradas} ${t.paradas === 1 ? 'trecho' : 'trechos'}, ${num(t.minutos, 0)} min)`);
    ul.append(li);
  });
  return ul;
}

function mostraRotaViagem(): void {
  const caixa = $('v-rota');
  if (!caixa) return;
  caixa.replaceChildren();
  const ativa = abaViagemAtiva();
  mostraLinhasNovasNoMapa();
  if (estado.viagemDe === estado.viagemPara) {
    caixa.append(el('p', 'Escolha duas estações diferentes.', 'nota'));
    if (ativa) mapa.mostraRota(null);
    return;
  }
  const { aval, erro } = avaliacaoAtual();
  if (!aval) {
    caixa.append(el('p', erro && !erro.startsWith('não há caminho') ? `Erro: ${erro}` : 'Não há caminho entre essas estações no horário deste tipo de dia.', 'nota'));
    if (ativa) mapa.mostraRota(null);
    return;
  }
  const av = aval.avs[0];
  caixa.append(el('h3', `Caminho de sempre (o mais rápido sem falhas, ${ROTULOS[estado.tipoDia]})`), listaDaRota(av));
  const ini = av.saidas[0];
  const fim = av.saidas[av.saidas.length - 1];
  caixa.append(
    el(
      'p',
      `Tempo de percurso: ${num(av.rota.minutos, 0)} min (percurso mediano do horário mais as baldeações, sem a espera na plataforma). Saídas simuladas: a cada ${PASSO_SAIDAS_S / 60} min, das ${relogioMin(ini)} às ${relogioMin(fim)} (${inteiro(av.saidas.length)} por dia).` +
        (estado.politicas.rotaAlternativa ? ' Rota alternativa ligada: a pessoa pode usar qualquer caminho livre.' : ' Rota alternativa desligada: a pessoa usa só este caminho e espera a linha voltar.'),
      'nota',
    ),
  );
  if (aval.avs.length > 1) {
    caixa.append(el('h3', 'Com as linhas novas'));
    const ul = el('ul', undefined, 'variantes');
    aval.avs.slice(1).forEach((x, k) => {
      const li = el('li');
      li.append(el('strong', `${aval.variantes[k].nome}: `));
      if (!mesmaRota(av, x)) li.append(`o caminho de sempre passa a ser ${textoRota(x)} (${num(x.rota.minutos, 0)} min, ${comSinal(x.rota.minutos - av.rota.minutos, 0)} min).`);
      else
        li.append(
          `o caminho de sempre não muda (${num(x.rota.minutos, 0)} min)` +
            (estado.politicas.rotaAlternativa ? '; a linha nova vale como caminho alternativo.' : '; sem a rota alternativa, a linha nova só pesa pelas falhas que causa nas linhas do caminho.'),
        );
      ul.append(li);
    });
    caixa.append(ul);
    if (aval.aviso) caixa.append(el('p', aval.aviso, 'nota'));
  }
  if (erro) caixa.append(el('p', `Linhas novas fora da avaliação: ${erro}.`, 'erro'));
  if (ativa) mapa.mostraRota(av.rota.trechos.map((t) => ({ linha: t.linha, de: t.de, ate: t.ate })));
  if (resultadoViagem && resultadoViagem.chave !== chaveViagem()) $('s-viagem').textContent = 'A viagem, as linhas novas ou o cenário mudaram: o resultado abaixo é do anterior. Avalie de novo.';
}

async function avaliaViagem(): Promise<void> {
  const { aval } = avaliacaoAtual();
  if (!aval) {
    mostraRotaViagem();
    return;
  }
  const b = $<HTMLButtonElement>('b-viagem');
  const canc = $<HTMLButtonElement>('b-viagem-cancela');
  b.disabled = true;
  canc.disabled = false;
  const chave = chaveViagem();
  const congelado = copia(estado);
  try {
    const { json } = redeDo(estado.greve);
    const r = await poolViagem.executa(
      {
        redeJson: json,
        chaveRede: chaveRede(estado.greve),
        parametros: dados.parametros,
        cenario: paraCenarioMotor(estado),
        politicas: estado.politicas,
        sementeBase: estado.semente,
        rodadas: estado.rodadas,
        origem: estado.viagemDe,
        destino: estado.viagemPara,
        variantes: aval.variantes,
        causaComumNova: estado.ccNova,
      },
      nomesVariantes(aval.avs),
      progresso('p-viagem', 's-viagem'),
    );
    resultadoViagem = { chave, r, aval, estado: congelado };
    $('s-viagem').textContent = `${inteiro(r.n)} dias em ${num(r.segundos, 1)} s com ${r.workers} worker(s); semente ${r.sementeBase}${aval.avs.length > 1 ? `; ${aval.avs.length} versões da rede medidas em cada dia` : ''}.`;
    mostraResultadoViagem(r, aval, congelado);
  } catch (e) {
    if (!(e instanceof Error && e.message === 'cancelado')) mostraErro(e);
    else $('s-viagem').textContent = 'Cancelado.';
  } finally {
    b.disabled = false;
    canc.disabled = true;
    $('p-viagem').hidden = true;
  }
}

/** Medidas que não ficam negativas e não têm teto 1 (as demais são proporções). */
const SEM_TETO = new Set(['minSemCaminho', 'atrasoMedioMin', 'tempoMedioMin', 'falhasLinhaNova']);

/** O intervalo normal perto de 0 (ou de 1, nas proporções) passa da faixa possível: mostra recortado. Diferenças ficam como estão. */
function recortado(porMetrica: Record<string, Estimativa>): Record<string, Estimativa> {
  return Object.fromEntries(
    Object.entries(porMetrica).map(([k, x]) => {
      if (/^d\d+\./.test(k)) return [k, x];
      const teto = SEM_TETO.has(k.replace(/^v\d+\./, '')) ? Infinity : 1;
      return [k, { ...x, ic95: [Math.max(0, x.ic95[0]), Math.min(teto, x.ic95[1])] as [number, number] }];
    }),
  );
}

function mostraResultadoViagem(r: Agregado, aval: Avaliacao, e: EstadoCenario): void {
  const caixa = $('r-viagem');
  caixa.replaceChildren();
  const m = recortado(r.porMetrica);
  const av = aval.avs[0];
  const pctF = (x: number, c: number) => pct(x, Math.min(c, 4));
  const trechos = av.rota.trechos;
  caixa.append(el('h3', `${nomeDaEstacao(e.viagemDe)} → ${nomeDaEstacao(e.viagemPara)}: ${inteiro(r.n)} dias (${ROTULOS[e.tipoDia]}), média e intervalo de 95%`));
  caixa.append(el('p', `Cenário desta rodada: ${resumoCenario(e)} Os dias são os mesmos da aba "Muitos dias" (semente ${r.sementeBase}).`, 'nota'));
  if (aval.avs.length > 1) {
    mostraComparacaoViagem(caixa, r, m, aval, e);
    caixa.append(el('h4', 'Rede atual em detalhe'));
  }

  caixa.append(el('h4', 'Disponibilidade do caminho: fração do horário de serviço com caminho livre'));
  const T = Math.max(av.janela[1] - av.janela[0], 1);
  const minDe = (x: Estimativa): Estimativa => ({ ...x, media: ((1 - x.media) * T) / 60, ic95: [((1 - x.ic95[1]) * T) / 60, ((1 - x.ic95[0]) * T) / 60], meiaLargura: (x.meiaLargura * T) / 60 });
  const linhas: (string | Node)[][] = trechos.map((t, i) => {
    const nome = el('span');
    const p = el('span', undefined, 'ponto');
    p.style.background = corLinha(t.linha);
    nome.append(p, ` ${nomeLinha(t.linha)}: ${t.deNome} → ${t.ateNome}`);
    const d = m[`disp.trecho.${i}`];
    return [nome, estimativaTexto(d, pctF, 2, 100), estimativaTexto(minDe(d), num), novesTexto(d)];
  });
  const produto = trechos.reduce((s, _, i) => s * (m[`disp.trecho.${i}`]?.media ?? 1), 1);
  if (trechos.length > 1) linhas.push(['Produto dos trechos (em série, se as linhas falhassem de forma independente)', pct(produto, 2), num(((1 - produto) * T) / 60, 1), num(noves(produto), 2)]);
  linhas.push([el('strong', 'Viagem inteira (simulada)'), estimativaTexto(m.disp, pctF, 2, 100), estimativaTexto(m.minSemCaminho, num), novesTexto(m.disp)]);
  caixa.append(tabela(['Parte da viagem', 'Disponibilidade (IC 95%)', 'Minutos por dia sem caminho', 'Noves'], linhas, [1, 2, 3]));

  const d = m.disp;
  const repetidas = [...new Set(trechos.map((t) => t.linha).filter((l, i, xs) => xs.indexOf(l) !== i))].map(nomeLinha);
  let leitura: string;
  if (trechos.length === 1) leitura = 'Uma linha só: a disponibilidade da viagem é a do trecho.';
  else if (repetidas.length && !e.politicas.rotaAlternativa)
    leitura = `A ${repetidas.join(' e a ')} aparece em mais de um trecho: uma falha nela para esses trechos ao mesmo tempo, então eles não são independentes, e o produto dos trechos (${pct(produto, 2)}) fica abaixo do simulado (${pct(d.media, 2)}). Sem a política de retorno parcial, qualquer falha numa linha tira a linha inteira do caminho.`;
  else if (e.politicas.rotaAlternativa)
    leitura =
      d.ic95[0] > produto
        ? `Com a rota alternativa, a viagem só fica sem caminho quando nenhum caminho está livre: os caminhos ficam em paralelo, e a disponibilidade simulada (${pct(d.media, 2)}) passa o produto dos trechos do caminho de sempre (${pct(produto, 2)}).`
        : `Com a rota alternativa, a viagem só fica sem caminho quando nenhum caminho está livre; aqui a alternativa quase não muda o resultado (simulado ${pct(d.media, 2)}, produto dos trechos ${pct(produto, 2)}), porque não há caminho que evite as linhas paradas.`;
  else if (produto >= d.ic95[0] && produto <= d.ic95[1])
    leitura = `O produto dos trechos (${pct(produto, 2)}) cai dentro do intervalo do simulado: as linhas do caminho falham quase de forma independente, e a viagem se comporta como um sistema em série.`;
  else if (produto < d.ic95[0])
    leitura = `O simulado (${pct(d.media, 2)}) fica acima do produto dos trechos (${pct(produto, 2)}): as interrupções de linhas diferentes coincidem no tempo mais do que se fossem independentes (a causa comum para várias linhas juntas), e o tempo total sem caminho é menor que a soma das partes.`;
  else leitura = `O simulado (${pct(d.media, 2)}) fica abaixo do produto dos trechos (${pct(produto, 2)}).`;
  caixa.append(el('p', `${leitura} Em ${estimativaTexto(m.diaComInterrupcao, pctF, 0, 100)} dos dias houve ao menos uma interrupção no caminho.`, 'nota'));
  // escala logarítmica: os trechos e a viagem inteira lado a lado, mesmo quando todos passam de 99%
  const gl = el('div', undefined, 'grafico-estreito');
  graficoPontosLog(
    gl,
    [
      ...trechos.map((t, i) => {
        const x = minDe(m[`disp.trecho.${i}`]);
        return { rotulo: `${nomeLinha(t.linha)} (trecho ${i + 1})`, valor: x.media, ic: x.ic95, cor: corLinha(t.linha), dica: `${t.deNome} → ${t.ateNome}` };
      }),
      { rotulo: 'Viagem inteira', valor: m.minSemCaminho.media, ic: m.minSemCaminho.ic95, cor: corTinta(), dica: 'simulada' },
    ],
    { titulo: 'Minutos por dia sem caminho, por trecho e na viagem inteira (escala logarítmica, IC 95%)', formata: numSig, eixo: 'minutos por dia (cada marca é 10 vezes a anterior)', colunaValor: 'Minutos por dia' },
  );
  caixa.append(gl);
  caixa.append(
    el(
      'p',
      'Escala: perto de 100%, a disponibilidade esconde as diferenças (99,5% e 99,9% parecem iguais, mas o tempo sem caminho cai 5 vezes). Por isso a tabela mostra também os minutos sem caminho e o número de noves (−log₁₀ da indisponibilidade: 99% são 2 noves, 99,9% são 3), e o gráfico usa escala logarítmica.',
      'nota',
    ),
  );

  caixa.append(el('h4', `Atraso de quem viaja (saídas a cada ${PASSO_SAIDAS_S / 60} min, com os trens simulados do dia)`));
  const l1 = LIMIARES_ATRASO_MIN[0];
  const lMax = LIMIARES_ATRASO_MIN[LIMIARES_ATRASO_MIN.length - 1];
  caixa.append(
    tabela(
      ['Medida', 'Valor (IC 95%)'],
      [
        ...LIMIARES_ATRASO_MIN.map((l) => [`Chance de chegar mais de ${l} min depois do programado`, estimativaTexto(m[`atraso${l}`], pctF, 2, 100)]),
        ['Chance de não chegar até o fim do serviço', estimativaTexto(m.naoChega, pctF, 2, 100)],
        ['Atraso médio por viagem (minutos)', estimativaTexto(m.atrasoMedioMin, num, 2)],
        ['Tempo médio da saída à chegada, com a espera na plataforma (minutos)', estimativaTexto(m.tempoMedioMin, num, 1)],
      ],
      [1],
    ),
  );
  caixa.append(
    el(
      'p',
      `O atraso médio inclui as saídas sem atraso e é puxado pelas poucas que pegam uma interrupção longa (${pct(m[`atraso${lMax}`].media, 2)} das saídas atrasam mais de ${lMax} min): a amostra de durações da STM tem paradas de horas, e ` +
        (e.politicas.rotaAlternativa ? 'mesmo com a rota alternativa há trechos sem outro caminho.' : 'sem a rota alternativa a pessoa espera a linha voltar.'),
      'nota',
    ),
  );
  // 20 barras: na largura natural do gráfico (640 px), sem esticar
  const g = el('div', undefined, 'grafico-estreito');
  const cor = getComputedStyle(document.documentElement).getPropertyValue('--destaque').trim() || '#2a5bd7';
  graficoBarras(
    g,
    av.horas.map((h) => {
      const x = m[`atraso${l1}.h${h}`];
      return { rotulo: `${relogioMin(h * 3600)}–${relogioMin((h + 1) * 3600)}`, valor: x.media * 100, ic: [x.ic95[0] * 100, x.ic95[1] * 100] as [number, number], cor };
    }),
    { titulo: `Chance de atraso de mais de ${l1} min, por hora de saída (IC 95%)`, formata: (x) => `${num(x, 2)}%`, eixo: '% das saídas', colunaValor: '% das saídas' },
  );
  caixa.append(g);
  caixa.append(
    el(
      'p',
      'Como se mede: a disponibilidade vem dos bloqueios do dia no grafo das estações, o mesmo método da disponibilidade origem-destino da rede. ' +
        'O atraso compara, para cada saída, a chegada mais cedo ao destino com os trens simulados (inclusive esperar a linha voltar e o atraso dos trens depois) com a mesma saída num dia sem falhas. ' +
        'Com a rota alternativa, a pessoa escolhe o caminho sabendo quanto vai durar cada interrupção: é o limite otimista da política. ' +
        `Não entram ônibus de substituição, caminhada até a plataforma nem lotação. Limiares de ${LIMIARES_ATRASO_MIN.join(', ').replace(/, (\d+)$/, ' e $1')} min: escolha de apresentação (spec 015).`,
      'nota',
    ),
  );
}

const corTinta = () => getComputedStyle(document.documentElement).getPropertyValue('--tinta').trim() || '#1d1d1b';

/** Rede atual contra cada versão com linhas novas, no mesmo dia simulado (spec 016). */
function mostraComparacaoViagem(caixa: HTMLElement, r: Agregado, m: Record<string, Estimativa>, aval: Avaliacao, e: EstadoCenario): void {
  const ms = r.porMetrica;
  const pctF = (x: number, c: number) => pct(x, Math.min(c, 4));
  const pre = (k: number) => (k === 0 ? '' : `v${k}.`);
  const nomeRede = (k: number) => (k === 0 ? 'Rede atual' : aval.variantes[k - 1].nome);
  const corRede = (k: number) => {
    if (k === 0) return getComputedStyle(document.documentElement).getPropertyValue('--tinta-3').trim() || '#77766f';
    const v = aval.variantes[k - 1];
    return v.linhas.length === 1 ? corDaCandidata(v.linhas[0], redeBase()) : corTinta();
  };
  const nomeComCor = (k: number) => {
    const s = el('span');
    const p = el('span', undefined, 'ponto');
    p.style.background = corRede(k);
    s.append(p, ` ${nomeRede(k)}`);
    return s;
  };
  const razaoDe = (k: number) => razaoPareada(ms[`v${k}.minSemCaminho`], ms.minSemCaminho, ms[`d${k}.minSemCaminho`]);
  /** Nome no meio da frase ("Com todas as linhas novas juntas"). */
  const nomeNaFrase = (k: number) => (aval.variantes[k - 1].id === 'todas' ? 'todas as linhas novas juntas' : nomeRede(k));
  caixa.append(el('h4', `Com as linhas novas: os mesmos ${inteiro(r.n)} dias, com e sem cada linha`));
  const av0 = aval.avs[0];
  const larga = (t: HTMLElement) => {
    t.classList.add('larga');
    return t;
  };
  caixa.append(
    larga(tabela(
      ['Rede', 'Tempo programado', 'Disponibilidade (IC 95%)', 'Minutos por dia sem caminho', 'Noves', 'Sem caminho ÷ rede atual', 'Atraso de mais de 5 min', 'Tempo médio da viagem (min)'],
      aval.avs.map((av, k) => {
        const rz = k ? razaoDe(k) : null;
        const cr = rz ? Math.max(2, casasPara((rz.ic95[1] - rz.ic95[0]) / 2)) : 2;
        return [
          nomeComCor(k),
          `${num(av.rota.minutos, 0)} min${k && !mesmaRota(av0, av) ? ' (caminho novo)' : ''}`,
          estimativaTexto(m[`${pre(k)}disp`], pctF, 2, 100),
          estimativaTexto(m[`${pre(k)}minSemCaminho`], num),
          novesTexto(m[`${pre(k)}disp`]),
          k === 0 ? '1' : rz ? `${num(rz.media, cr)} (${num(rz.ic95[0], cr)}–${num(rz.ic95[1], cr)})` : '—',
          estimativaTexto(m[`${pre(k)}atraso${LIMIARES_ATRASO_MIN[0]}`], pctF, 2, 100),
          estimativaTexto(m[`${pre(k)}tempoMedioMin`], num),
        ];
      }),
      [1, 2, 3, 4, 5, 6, 7],
    )),
  );
  const g = el('div', undefined, 'grafico-estreito');
  graficoPontosLog(
    g,
    aval.avs.map((_, k) => {
      const x = m[`${pre(k)}minSemCaminho`];
      const nome = nomeRede(k);
      return { rotulo: nome.length > 22 ? `${nome.slice(0, 21)}…` : nome, valor: x.media, ic: x.ic95, cor: corRede(k), dica: nome };
    }),
    { titulo: 'Minutos por dia sem caminho, com e sem as linhas novas (escala logarítmica, IC 95%)', formata: numSig, eixo: 'minutos por dia (cada marca é 10 vezes a anterior)', colunaValor: 'Minutos por dia' },
  );
  caixa.append(g);
  caixa.append(el('p', 'Ganho medido dia a dia: com a linha nova menos a rede atual, no mesmo dia simulado. As falhas da rede atual são as mesmas nas duas medidas, então o intervalo do ganho é bem mais estreito que o de cada valor; intervalo que não cruza o zero é diferença que não vem da sorte do sorteio, para estas hipóteses.', 'nota'));
  caixa.append(
    larga(tabela(
      ['Linha nova', 'Disponibilidade', 'Minutos por dia sem caminho', 'Atraso de mais de 5 min', 'Atraso médio (min)', 'Tempo médio da viagem (min)'],
      aval.avs.slice(1).map((_, i) => {
        const k = i + 1;
        const dd = (n: string) => ms[`d${k}.${n}`];
        return [
          nomeComCor(k),
          difTexto(dd('disp'), (x, c) => pp(x, Math.min(c, 4)), 100),
          difTexto(dd('minSemCaminho'), comSinal),
          difTexto(dd(`atraso${LIMIARES_ATRASO_MIN[0]}`), (x, c) => pp(x, Math.min(c, 4)), 100),
          difTexto(dd('atrasoMedioMin'), comSinal),
          difTexto(dd('tempoMedioMin'), comSinal),
        ];
      }),
      [1, 2, 3, 4, 5],
    )),
  );
  // leitura: cada linha nova, com o motivo
  const ul = el('ul', undefined, 'leituras');
  aval.avs.slice(1).forEach((av, i) => {
    const k = i + 1;
    const dd = ms[`d${k}.disp`];
    const x = m[`v${k}.minSemCaminho`].media;
    const y = m.minSemCaminho.media;
    const rz = razaoDe(k);
    const muda = !mesmaRota(av0, av);
    const nb = noves(m.disp.media);
    const nv = noves(m[`v${k}.disp`].media);
    const fN = (n: number) => (Number.isFinite(n) ? num(n, 2) : '∞');
    const tempo = ms[`d${k}.tempoMedioMin`];
    const tempoTxt = tempo && tempo.ic95[1] < 0 ? ` A viagem também fica ${num(-tempo.media, 1)} min mais curta em média, com as falhas.` : '';
    let t: string;
    const porque = muda ? 'O caminho de sempre passa pela linha nova.' : 'O caminho de sempre não muda: a linha nova vale como caminho alternativo.';
    const nadaMuda = !muda && Math.abs(dd.media) < 1e-12 && dd.meiaLargura < 1e-12;
    if (nadaMuda) t = `Com ${nomeNaFrase(k)}, nada muda nesta viagem: o caminho de sempre é o mesmo e nenhuma falha da linha nova alcança as linhas dele.`;
    else if (dd.ic95[0] > 0 && !(x > 0))
      t = `Com ${nomeNaFrase(k)}, a viagem não ficou sem caminho em nenhum dos ${inteiro(r.n)} dias simulados (na rede atual, ${numSig(y)} min por dia; ${fN(nb)} noves). Com mais dias, o tempo sem caminho fica mensurável. ${porque}`;
    else if (dd.ic95[0] > 0)
      t = `Com ${nomeNaFrase(k)}, a viagem fica sem caminho ${numSig(x)} min por dia em vez de ${numSig(y)} (${rz ? textoRazao(rz.media, num) : 'menos'}; de ${fN(nb)} para ${fN(nv)} noves). ${porque}`;
    else if (dd.ic95[1] < 0)
      t =
        `Com ${nomeNaFrase(k)}, a viagem piora: ${numSig(x)} min por dia sem caminho em vez de ${numSig(y)}. ` +
        (muda
          ? 'O caminho de sempre passa pela linha nova, que também falha (taxas por km herdadas das linhas atuais) e, sem retorno parcial, para inteira com uma falha em qualquer trecho.'
          : 'A viagem não usa o trecho novo, mas ele prolonga uma linha do caminho: sem retorno parcial, a falha no trecho novo para a linha inteira.');
    else
      t = `Com ${nomeNaFrase(k)}, a diferença de disponibilidade (${pp(dd.media, 3)}) não se separa do zero com ${inteiro(r.n)} dias.` + (muda ? ' O caminho de sempre passa pela linha nova: ela tira as falhas das linhas antigas do caminho, mas traz as próprias.' : '');
    if (!e.politicas.rotaAlternativa && !muda && dd.ic95[0] <= 0) t += ' Sem a rota alternativa, a linha nova só conta se entrar no caminho de sempre; ligue a política "Rota alternativa de passageiros" no painel para ver o efeito em paralelo.';
    ul.append(el('li', t + tempoTxt));
  });
  caixa.append(ul);
  const det = el('details');
  det.append(el('summary', 'Hipóteses das linhas novas'));
  const lh = el('ul');
  const vistas = new Set<string>();
  for (const av of aval.avs.slice(1)) {
    for (const h of av.variante?.hipoteses ?? []) {
      if (vistas.has(h)) continue;
      vistas.add(h);
      lh.append(el('li', h));
    }
  }
  lh.append(el('li', 'Cada linha nova tem um fluxo de sorteio próprio: as falhas da rede atual e as de cada linha são as mesmas em todas as versões. Estações novas não entram como origem ou destino.'));
  det.append(lh);
  caixa.append(det);
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
  const comMapa = id === 'dia' || id === 'expansao' || id === 'viagem';
  $('mapa-caixa').hidden = !comMapa;
  if (comMapa) requestAnimationFrame(() => mapa.resize());
  if (id !== 'viagem' && desenho) terminaDesenho(false);
  mapa.mostraCandidatas(id === 'expansao' ? candidatas : null);
  mapa.mostraDesenho(null);
  if (id === 'viagem') mostraRotaViagem();
  else mapa.mostraRota(null);
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
  // o resumo do ajuste só enriquece a nota do método (contagens, AIC, semente); sem ele a nota usa o parametros.json
  Promise.all([carrega<ResumoTaxa>('modelos/taxa_MR.json'), carrega<ResumoTaxa>('modelos/taxa_EF.json')])
    .then(([MR, EF]) => {
      resumos = { MR, EF };
      montaNotaMetodo();
      mostraPesos();
    })
    .catch(() => undefined);
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
  montaNotaMetodo();
  opcoes(
    $('t-vel'),
    VELOCIDADES.map((v) => [String(v.valor), v.rotulo]),
    String(VELOCIDADE_PADRAO),
  );
  montaCandidatas();
  montaViagem();
  mostraAvisos();
  mostraParametros();
  history.replaceState(null, '', `#${serializa(estado)}`);

  $('form-cenario').addEventListener('change', (ev) => {
    const alvo = ev.target as HTMLElement;
    if (alvo.closest('#c-politicas') || alvo.closest('#c-hipoteses')) return;
    leFormulario();
    mudou();
  });
  // trocar o dia mostrado sorteia outro dia do mesmo cenário: não é mudança de cenário
  $('t-dia').addEventListener('change', () => {
    leFormulario();
    history.replaceState(null, '', `#${serializa(estado)}`);
    simulaDiaMostrado();
  });
  $('b-padrao').addEventListener('click', () => {
    estado = copia(PADRAO);
    montaFormulario();
    montaViagem();
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
    montaViagem();
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
  for (const [id, campo] of [['v-de', 'viagemDe'], ['v-para', 'viagemPara']] as const) {
    $(id).addEventListener('change', () => {
      estado[campo] = $<HTMLSelectElement>(id).value;
      history.replaceState(null, '', `#${serializa(estado)}`);
      mostraRotaViagem();
    });
  }
  $('b-inverte').addEventListener('click', () => {
    [estado.viagemDe, estado.viagemPara] = [estado.viagemPara, estado.viagemDe];
    $<HTMLSelectElement>('v-de').value = estado.viagemDe;
    $<HTMLSelectElement>('v-para').value = estado.viagemPara;
    history.replaceState(null, '', `#${serializa(estado)}`);
    mostraRotaViagem();
  });
  $('b-viagem').addEventListener('click', avaliaViagem);
  $('b-viagem-cancela').addEventListener('click', () => poolViagem.cancela());
  $('b-desenha').addEventListener('click', comecaDesenho);
  $('b-desenho-add').addEventListener('click', () => acrescentaAoDesenho($<HTMLSelectElement>('v-desenho-est').value));
  $('b-desenho-volta').addEventListener('click', () => {
    desenho?.pop();
    atualizaDesenho();
  });
  $('b-desenho-ok').addEventListener('click', () => terminaDesenho(true));
  $('b-desenho-cancela').addEventListener('click', () => terminaDesenho(false));
  $('v-cc').addEventListener('change', () => {
    estado.ccNova = $<HTMLInputElement>('v-cc').checked;
    linhasMudaram();
  });

  simulaDiaMostrado();
  aplicado(true);
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
