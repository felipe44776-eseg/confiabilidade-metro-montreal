// Página /mapa/: traçado real das linhas (OSM), estações (GTFS) e locais das falhas técnicas (spec 002).
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import './mapa.css';
import { type Local, type Status, ROTULO_STATUS, ROTULO_TIPO, paraGeoJSON, raio, somaPorStatus } from './locais';

const BASE = import.meta.env.BASE_URL;
const ESTILO = 'https://tiles.openfreemap.org/styles/positron';
const STATUS: Status[] = ['verificado', 'deduzido', 'aproximado', 'desconhecido'];
const ATRIBUICAO =
  'Traçado e estações de referência © colaboradores do OpenStreetMap (ODbL) · Incidentes e estações: STM, CC BY 4.0 · Fundo: OpenFreeMap';

function cor(status: Status): string {
  return getComputedStyle(document.documentElement).getPropertyValue(`--st-${status}`).trim();
}

async function carrega<T>(arquivo: string): Promise<T> {
  const resp = await fetch(`${BASE}dados/geo/${arquivo}`);
  if (!resp.ok) throw new Error(`${arquivo}: HTTP ${resp.status}`);
  return (await resp.json()) as T;
}

function el<K extends keyof HTMLElementTagNameMap>(tag: K, texto?: string, classe?: string): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (texto !== undefined) e.textContent = texto;
  if (classe) e.className = classe;
  return e;
}

const fmt = new Intl.NumberFormat('pt-BR');
const fmtPct = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 });
const fmtKm = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 });

function montaLegenda(locais: Local[], aoMudar: (ativos: Status[]) => void): void {
  const soma = somaPorStatus(locais);
  const total = STATUS.reduce((a, s) => a + soma[s], 0);
  const lista = document.getElementById('lista-status')!;
  lista.replaceChildren();
  const ativos = new Set<Status>(['verificado', 'deduzido', 'aproximado']);
  for (const s of STATUS) {
    const li = el('li');
    const rotulo = el('label');
    const caixa = el('input');
    caixa.type = 'checkbox';
    caixa.id = `st-${s}`;
    caixa.checked = s !== 'desconhecido';
    caixa.disabled = s === 'desconhecido';
    const amostra = el('span', undefined, 'amostra');
    amostra.style.background = cor(s);
    const nome = el('span', ROTULO_STATUS[s] + (s === 'desconhecido' ? ' (fora do mapa)' : ''));
    const num = el('span', `${fmt.format(soma[s])} · ${fmtPct.format(soma[s] / total)}`, 'num');
    rotulo.append(caixa, amostra, nome, num);
    if (s === 'desconhecido') rotulo.classList.add('sem-mapa');
    caixa.addEventListener('change', () => {
      if (caixa.checked) ativos.add(s);
      else ativos.delete(s);
      aoMudar([...ativos]);
    });
    li.append(rotulo);
    lista.append(li);
  }
}

function montaLinhas(linhas: GeoJSON.FeatureCollection): void {
  const lista = document.getElementById('lista-linhas')!;
  lista.replaceChildren();
  for (const f of linhas.features) {
    const p = f.properties as Record<string, string | number>;
    const li = el('li');
    const traco = el('span', undefined, 'traco');
    traco.style.background = String(p.cor_osm);
    const nome = String(p.nome_osm).replace(/ vers .*/, '');
    li.append(traco, el('span', nome), el('span', `${fmtKm.format(Number(p.comprimento_km))} / ${fmtKm.format(Number(p.comprimento_oficial_km))} km`, 'num'));
    lista.append(li);
  }
}

function conteudoPopup(l: Local): HTMLElement {
  const div = el('div', undefined, 'pop');
  div.append(el('h3', l.codigo));
  const dl = el('dl');
  const par = (k: string, v: string) => dl.append(el('dt', k), el('dd', v));
  par('Falhas técnicas', fmt.format(l.n_tecnicos));
  par('Linha', l.linha);
  par('Tipo', ROTULO_TIPO[l.tipo] ?? l.tipo);
  par('Posição', ROTULO_STATUS[l.status]);
  if (l.estacoes.length) par(l.estacoes.length > 1 ? 'Estações' : 'Estação', l.estacoes.join(' e '));
  if (l.km_linha !== null) par('Km na linha', fmtKm.format(l.km_linha));
  div.append(dl, el('p', l.metodo, 'metodo'));
  return div;
}

function limites(linhas: GeoJSON.FeatureCollection): maplibregl.LngLatBoundsLike {
  const b = new maplibregl.LngLatBounds();
  for (const f of linhas.features) for (const c of (f.geometry as GeoJSON.LineString).coordinates) b.extend(c as [number, number]);
  return b;
}

async function inicia(): Promise<void> {
  const [linhas, estacoes, locais] = await Promise.all([
    carrega<GeoJSON.FeatureCollection>('linhas.geojson'),
    carrega<GeoJSON.FeatureCollection>('estacoes.geojson'),
    carrega<Local[]>('locais.json'),
  ]);
  montaLinhas(linhas);
  const porCodigo = new Map(locais.map((l) => [l.codigo, l]));
  const pontos = paraGeoJSON(locais);
  const nMax = Math.max(...pontos.features.map((f) => Number(f.properties!.n)));
  for (const f of pontos.features) f.properties!.r = raio(Number(f.properties!.n), nMax);

  const mapa = new maplibregl.Map({
    container: 'mapa',
    style: ESTILO,
    bounds: limites(linhas),
    fitBoundsOptions: { padding: 40 },
    attributionControl: { customAttribution: ATRIBUICAO, compact: false },
  });
  mapa.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

  mapa.on('load', () => {
    mapa.addSource('linhas', { type: 'geojson', data: linhas });
    mapa.addLayer({ id: 'linhas-contorno', type: 'line', source: 'linhas', layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#ffffff', 'line-width': 7 } });
    mapa.addLayer({ id: 'linhas', type: 'line', source: 'linhas', layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': ['get', 'cor_osm'], 'line-width': 4 } });
    mapa.addSource('estacoes', { type: 'geojson', data: estacoes });
    mapa.addLayer({ id: 'estacoes', type: 'circle', source: 'estacoes', paint: { 'circle-radius': 3, 'circle-color': '#ffffff', 'circle-stroke-color': '#1d1d1b', 'circle-stroke-width': 1.2 } });
    mapa.addSource('locais', { type: 'geojson', data: pontos });
    mapa.addLayer({
      id: 'locais',
      type: 'circle',
      source: 'locais',
      layout: { 'circle-sort-key': ['-', 0, ['get', 'n']] },
      paint: {
        'circle-radius': ['get', 'r'],
        'circle-color': ['match', ['get', 'status'], 'verificado', cor('verificado'), 'deduzido', cor('deduzido'), 'aproximado', cor('aproximado'), '#999999'],
        'circle-opacity': 0.55,
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 1,
      },
    });

    const dica = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 8 });
    mapa.on('mousemove', 'estacoes', (e) => {
      const nome = String(e.features?.[0]?.properties?.estacao ?? '');
      dica.setLngLat(e.lngLat).setText(nome).addTo(mapa);
    });
    mapa.on('mouseleave', 'estacoes', () => dica.remove());
    mapa.on('mouseenter', 'locais', () => (mapa.getCanvas().style.cursor = 'pointer'));
    mapa.on('mouseleave', 'locais', () => (mapa.getCanvas().style.cursor = ''));
    mapa.on('click', 'locais', (e) => {
      const l = porCodigo.get(String(e.features?.[0]?.properties?.codigo));
      if (l) new maplibregl.Popup({ offset: 10 }).setLngLat(e.lngLat).setDOMContent(conteudoPopup(l)).addTo(mapa);
    });
  });

  montaLegenda(locais, (ativos) => {
    if (mapa.getLayer('locais')) mapa.setFilter('locais', ['in', ['get', 'status'], ['literal', ativos]]);
  });
}

inicia().catch((erro: unknown) => {
  const p = document.getElementById('erro')!;
  p.textContent = `Não foi possível carregar os dados do mapa: ${erro instanceof Error ? erro.message : String(erro)}`;
  p.hidden = false;
});
