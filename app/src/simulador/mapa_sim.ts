// Mapa do simulador (spec 010): traçado real, estações, trens animados, trechos bloqueados, falhas,
// locais históricos e linhas candidatas. Só desenha: o estado vem de animacao.ts.

import * as maplibregl from 'maplibre-gl';
import '../ui/maplibre_worker';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { Candidata } from '../motor/expansao';
import type { Rede } from '../motor/rede';
import { type Local, ROTULO_STATUS, ROTULO_TIPO, paraGeoJSON, raio } from '../locais';
import type { Bloco, Ocorrencia, PosicaoTrem } from './animacao';
import type { Coord, Tracado } from './tracado';
import { montaTracado, pontoNoKm, trechoEntre } from './tracado';

const ESTILO = 'https://tiles.openfreemap.org/styles/positron';
const ATRIBUICAO =
  'Traçado © colaboradores do OpenStreetMap (ODbL) · Horário, estações e incidentes: STM, CC BY 4.0 · Fundo: OpenFreeMap';
/** Atraso a partir do qual o trem aparece com contorno vermelho (o mesmo limiar de "viagem afetada" da spec 007). */
const ATRASO_DESTAQUE_S = 180;
/** Cor ilustrativa da Linha Rosa (proposta; não é cor oficial). */
const COR_ROSA = '#d6338a';

export interface DadosMapa {
  linhasGeo: GeoJSON.FeatureCollection;
  estacoesGeo: GeoJSON.FeatureCollection;
  locais: Local[];
  rede: Rede;
}

const VAZIO: GeoJSON.FeatureCollection = { type: 'FeatureCollection', features: [] };

function el<K extends keyof HTMLElementTagNameMap>(tag: K, texto?: string, classe?: string): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (texto !== undefined) e.textContent = texto;
  if (classe) e.className = classe;
  return e;
}

export function corDaCandidata(c: Candidata, rede: Rede): string {
  if (rede.linhas[c.linha]?.cor) return rede.linhas[c.linha].cor as string;
  if (c.herdaTaxasDe && rede.linhas[c.herdaTaxasDe]?.cor) return rede.linhas[c.herdaTaxasDe].cor as string;
  if (c.linha === 'rosa') return COR_ROSA;
  return '#6b6a64';
}

/** O que a página usa do mapa. Sem WebGL, a página segue sem mapa (VistaSemMapa). */
export interface VistaMapa {
  readonly pronto: Promise<void>;
  atualizaTrens(pos: readonly PosicaoTrem[]): void;
  atualizaBloqueios(ativos: readonly Bloco[]): void;
  atualizaFalhas(ocorrencias: readonly Ocorrencia[], rotulo: (o: Ocorrencia) => string): void;
  mostraLocais(ver: boolean): void;
  mostraCandidatas(cands: readonly Candidata[] | null, destaque?: string): void;
  resize(): void;
}

export class VistaSemMapa implements VistaMapa {
  readonly pronto = new Promise<void>(() => {});
  atualizaTrens(): void {}
  atualizaBloqueios(): void {}
  atualizaFalhas(): void {}
  mostraLocais(): void {}
  mostraCandidatas(): void {}
  resize(): void {}
}

export class MapaSimulador implements VistaMapa {
  readonly mapa: maplibregl.Map;
  readonly pronto: Promise<void>;
  private readonly tracados: Record<string, Tracado> = {};
  private chaveBloqueios = '';
  private chaveFalhas = '';

  constructor(
    container: string,
    private readonly dados: DadosMapa,
  ) {
    for (const f of dados.linhasGeo.features) {
      const linha = String((f.properties as Record<string, unknown>).linha);
      this.tracados[linha] = montaTracado((f.geometry as GeoJSON.LineString).coordinates as Coord[]);
    }
    const b = new maplibregl.LngLatBounds();
    for (const t of Object.values(this.tracados)) for (const c of t.coords) b.extend(c);
    this.mapa = new maplibregl.Map({
      container,
      style: ESTILO,
      bounds: b,
      fitBoundsOptions: { padding: 30 },
      attributionControl: { customAttribution: ATRIBUICAO, compact: false },
    });
    this.mapa.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    this.pronto = new Promise((resolve) => this.mapa.on('load', () => (this.montaCamadas(), resolve())));
  }

  /** Ponto do km na linha (traçado do OSM). */
  ponto(linha: string, km: number): Coord {
    const t = this.tracados[linha];
    return t ? pontoNoKm(t, km) : [0, 0];
  }

  private montaCamadas(): void {
    const m = this.mapa;
    const { linhasGeo, estacoesGeo, locais, rede } = this.dados;
    m.addSource('linhas', { type: 'geojson', data: linhasGeo });
    m.addLayer({ id: 'linhas-contorno', type: 'line', source: 'linhas', layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#ffffff', 'line-width': 7 } });
    m.addLayer({ id: 'linhas', type: 'line', source: 'linhas', layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': ['get', 'cor_osm'], 'line-width': 4, 'line-opacity': 0.75 } });
    m.addSource('candidatas', { type: 'geojson', data: VAZIO });
    m.addLayer({ id: 'candidatas', type: 'line', source: 'candidatas', layout: { 'line-cap': 'butt', 'line-join': 'round' }, paint: { 'line-color': ['get', 'cor'], 'line-width': ['case', ['get', 'destaque'], 5, 3], 'line-dasharray': [2, 1.5] } });
    m.addLayer({ id: 'candidatas-estacoes', type: 'circle', source: 'candidatas', filter: ['==', ['geometry-type'], 'Point'], paint: { 'circle-radius': 3.5, 'circle-color': '#ffffff', 'circle-stroke-color': ['get', 'cor'], 'circle-stroke-width': 2 } });
    m.addSource('bloqueios', { type: 'geojson', data: VAZIO });
    m.addLayer({ id: 'bloqueios', type: 'line', source: 'bloqueios', layout: { 'line-cap': 'butt' }, paint: { 'line-color': '#c0262d', 'line-width': 6, 'line-dasharray': [1.2, 0.8] } });
    m.addSource('estacoes', { type: 'geojson', data: estacoesGeo });
    m.addLayer({ id: 'estacoes', type: 'circle', source: 'estacoes', paint: { 'circle-radius': 2.6, 'circle-color': '#ffffff', 'circle-stroke-color': '#1d1d1b', 'circle-stroke-width': 1 } });
    const pontos = paraGeoJSON(locais);
    const nMax = Math.max(...pontos.features.map((f) => Number(f.properties!.n)));
    for (const f of pontos.features) f.properties!.r = raio(Number(f.properties!.n), nMax, 18);
    m.addSource('locais', { type: 'geojson', data: pontos });
    m.addLayer({ id: 'locais', type: 'circle', source: 'locais', layout: { visibility: 'none', 'circle-sort-key': ['-', 0, ['get', 'n']] }, paint: { 'circle-radius': ['get', 'r'], 'circle-color': '#6250d6', 'circle-opacity': 0.35, 'circle-stroke-color': '#ffffff', 'circle-stroke-width': 1 } });
    m.addSource('falhas', { type: 'geojson', data: VAZIO });
    m.addLayer({ id: 'falhas', type: 'circle', source: 'falhas', paint: { 'circle-radius': 8, 'circle-color': '#c0262d', 'circle-opacity': 0.9, 'circle-stroke-color': '#ffffff', 'circle-stroke-width': 2 } });
    m.addSource('trens', { type: 'geojson', data: VAZIO });
    const cores: (string | string[])[] = [];
    for (const id of rede.ids) cores.push(id, rede.linhas[id].cor ?? '#555555');
    m.addLayer({
      id: 'trens',
      type: 'circle',
      source: 'trens',
      paint: {
        'circle-radius': 5,
        'circle-color': ['match', ['get', 'linha'], ...cores, '#555555'] as unknown as maplibregl.ExpressionSpecification,
        'circle-stroke-color': ['case', ['get', 'atrasado'], '#c0262d', '#ffffff'],
        'circle-stroke-width': ['case', ['get', 'atrasado'], 2.5, 1.5],
      },
    });
    const porCodigo = new Map(locais.map((l) => [l.codigo, l]));
    m.on('mouseenter', 'locais', () => (m.getCanvas().style.cursor = 'pointer'));
    m.on('mouseleave', 'locais', () => (m.getCanvas().style.cursor = ''));
    m.on('click', 'locais', (e) => {
      const l = porCodigo.get(String(e.features?.[0]?.properties?.codigo));
      if (l) new maplibregl.Popup({ offset: 10 }).setLngLat(e.lngLat).setDOMContent(popupLocal(l)).addTo(m);
    });
    m.on('click', 'falhas', (e) => {
      const p = e.features?.[0]?.properties;
      if (p) new maplibregl.Popup({ offset: 10 }).setLngLat(e.lngLat).setText(String(p.texto)).addTo(m);
    });
    const dica = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 8 });
    m.on('mousemove', 'estacoes', (e) => dica.setLngLat(e.lngLat).setText(String(e.features?.[0]?.properties?.estacao ?? '')).addTo(m));
    m.on('mouseleave', 'estacoes', () => dica.remove());
  }

  private fonte(id: string): maplibregl.GeoJSONSource | undefined {
    return this.mapa.getSource(id) as maplibregl.GeoJSONSource | undefined;
  }

  atualizaTrens(pos: readonly PosicaoTrem[]): void {
    const src = this.fonte('trens');
    if (!src) return;
    src.setData({
      type: 'FeatureCollection',
      features: pos.map((p) => ({ type: 'Feature', properties: { linha: p.linha, atrasado: p.atrasoS > ATRASO_DESTAQUE_S }, geometry: { type: 'Point', coordinates: this.ponto(p.linha, p.km) } })),
    });
  }

  /** Trechos bloqueados agora; só redesenha quando o conjunto muda. */
  atualizaBloqueios(ativos: readonly Bloco[]): void {
    const src = this.fonte('bloqueios');
    if (!src) return;
    const chave = ativos.map((b) => `${b.linha}:${b.trecho}:${b.ini}`).join('|');
    if (chave === this.chaveBloqueios) return;
    this.chaveBloqueios = chave;
    const feats: GeoJSON.Feature[] = [];
    for (const b of ativos) {
      const t = this.tracados[b.linha];
      if (!t) continue;
      const est = this.dados.rede.linhas[b.linha].estacoes;
      const coords = b.trecho === null ? t.coords : trechoEntre(t, est[b.trecho].km, est[b.trecho + 1].km);
      feats.push({ type: 'Feature', properties: { causa: b.causa }, geometry: { type: 'LineString', coordinates: coords } });
    }
    src.setData({ type: 'FeatureCollection', features: feats });
  }

  /** Marcadores das falhas recentes (no meio do trecho onde ocorreram). */
  atualizaFalhas(ocorrencias: readonly Ocorrencia[], rotulo: (o: Ocorrencia) => string): void {
    const src = this.fonte('falhas');
    if (!src) return;
    const chave = ocorrencias.map((o) => `${o.linha}:${o.t}`).join('|');
    if (chave === this.chaveFalhas) return;
    this.chaveFalhas = chave;
    const feats: GeoJSON.Feature[] = [];
    for (const o of ocorrencias) {
      const est = this.dados.rede.linhas[o.linha]?.estacoes;
      if (!est) continue;
      const km = o.trecho === null ? est[Math.floor(est.length / 2)].km : (est[o.trecho].km + est[o.trecho + 1].km) / 2;
      feats.push({ type: 'Feature', properties: { texto: rotulo(o) }, geometry: { type: 'Point', coordinates: this.ponto(o.linha, km) } });
    }
    src.setData({ type: 'FeatureCollection', features: feats });
  }

  mostraLocais(ver: boolean): void {
    if (this.mapa.getLayer('locais')) this.mapa.setLayoutProperty('locais', 'visibility', ver ? 'visible' : 'none');
  }

  /** Desenha as candidatas (tracejado). `destaque`: id a engrossar. */
  mostraCandidatas(cands: readonly Candidata[] | null, destaque?: string): void {
    const src = this.fonte('candidatas');
    if (!src) return;
    if (!cands) {
      src.setData(VAZIO);
      return;
    }
    const pos = new Map<string, Coord>();
    for (const e of this.dados.rede.estacoes) pos.set(e.id, [e.lon, e.lat]);
    for (const c of cands) for (const p of [c, ...(c.extras ?? [])]) for (const e of p.estacoesNovas ?? []) pos.set(e.id, [e.lon, e.lat]);
    const feats: GeoJSON.Feature[] = [];
    for (const c of cands) {
      if (c.extras?.length) continue; // projeto conjunto: as partes já aparecem sozinhas
      const cor = corDaCandidata(c, this.dados.rede);
      const coords = c.sequencia.map((id) => pos.get(id)).filter((x): x is Coord => !!x);
      feats.push({ type: 'Feature', properties: { cor, destaque: c.id === destaque, id: c.id }, geometry: { type: 'LineString', coordinates: coords } });
      for (const e of c.estacoesNovas ?? []) feats.push({ type: 'Feature', properties: { cor, destaque: false }, geometry: { type: 'Point', coordinates: [e.lon, e.lat] } });
    }
    src.setData({ type: 'FeatureCollection', features: feats });
  }

  resize(): void {
    this.mapa.resize();
  }
}

function popupLocal(l: Local): HTMLElement {
  const div = el('div', undefined, 'pop');
  div.append(el('h3', l.codigo));
  const dl = el('dl');
  const par = (k: string, v: string) => dl.append(el('dt', k), el('dd', v));
  par('Falhas técnicas (2019 a 2026)', new Intl.NumberFormat('pt-BR').format(l.n_tecnicos));
  par('Linha', l.linha);
  par('Tipo', ROTULO_TIPO[l.tipo] ?? l.tipo);
  par('Posição', ROTULO_STATUS[l.status]);
  if (l.estacoes.length) par(l.estacoes.length > 1 ? 'Estações' : 'Estação', l.estacoes.join(' e '));
  div.append(dl, el('p', l.metodo, 'metodo'));
  return div;
}
