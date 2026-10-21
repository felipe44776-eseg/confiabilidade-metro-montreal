// Posição ao longo do traçado real (OpenStreetMap, spec 002). Funções puras.
// O km de cada estação (rede.json) foi medido sobre o mesmo LineString, orientado no sentido 0 do GTFS.

export type Coord = [number, number]; // [lon, lat]

export interface Tracado {
  coords: Coord[];
  acum: Float64Array; // km acumulado até cada vértice
  total: number;
}

const RAIO_KM = 6371.0088;

export function distanciaKm(a: Coord, b: Coord): number {
  const rad = Math.PI / 180;
  const dLat = (b[1] - a[1]) * rad;
  const dLon = (b[0] - a[0]) * rad;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(a[1] * rad) * Math.cos(b[1] * rad) * Math.sin(dLon / 2) ** 2;
  return 2 * RAIO_KM * Math.asin(Math.min(1, Math.sqrt(h)));
}

export function montaTracado(coords: Coord[]): Tracado {
  if (coords.length < 2) throw new Error('traçado precisa de pelo menos dois pontos');
  const acum = new Float64Array(coords.length);
  for (let i = 1; i < coords.length; i++) acum[i] = acum[i - 1] + distanciaKm(coords[i - 1], coords[i]);
  return { coords, acum, total: acum[coords.length - 1] };
}

/** Índice i com acum[i] <= km < acum[i + 1] (busca binária). */
function segmento(t: Tracado, km: number): number {
  let lo = 0;
  let hi = t.acum.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (t.acum[mid] <= km) lo = mid;
    else hi = mid;
  }
  return lo;
}

/** Ponto do traçado no km dado (fora do traçado: a ponta mais próxima). */
export function pontoNoKm(t: Tracado, km: number): Coord {
  if (km <= 0) return t.coords[0];
  if (km >= t.total) return t.coords[t.coords.length - 1];
  const i = segmento(t, km);
  const d = t.acum[i + 1] - t.acum[i];
  const f = d > 0 ? (km - t.acum[i]) / d : 0;
  const a = t.coords[i];
  const b = t.coords[i + 1];
  return [a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])];
}

/** Pedaço do traçado entre dois km (em qualquer ordem), com as pontas interpoladas. */
export function trechoEntre(t: Tracado, kmA: number, kmB: number): Coord[] {
  const a = Math.max(0, Math.min(kmA, kmB));
  const b = Math.min(t.total, Math.max(kmA, kmB));
  const saida: Coord[] = [pontoNoKm(t, a)];
  for (let i = 0; i < t.coords.length; i++) if (t.acum[i] > a && t.acum[i] < b) saida.push(t.coords[i]);
  saida.push(pontoNoKm(t, b));
  return saida;
}

/** km na linha a partir do índice de duas estações consecutivas e da fração percorrida entre elas. */
export function kmEntreEstacoes(kms: readonly number[], a: number, b: number, f: number): number {
  const fr = Math.min(1, Math.max(0, f));
  return kms[a] + fr * (kms[b] - kms[a]);
}
