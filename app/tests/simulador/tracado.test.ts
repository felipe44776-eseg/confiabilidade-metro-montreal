// Spec 010: posição ao longo do traçado real (funções puras).
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import type { Coord } from '../../src/simulador/tracado';
import { distanciaKm, kmEntreEstacoes, montaTracado, pontoNoKm, trechoEntre } from '../../src/simulador/tracado';
import { carregaRedeJson } from '../motor/apoio';

describe('traçado sintético', () => {
  // três pontos sobre o equador: 0°, 0,01° e 0,03° de longitude
  const t = montaTracado([
    [0, 0],
    [0.01, 0],
    [0.03, 0],
  ]);
  const grau = distanciaKm([0, 0], [1, 0]);

  it('comprimento acumulado', () => {
    expect(t.total).toBeCloseTo(0.03 * grau, 6);
    expect(t.acum[1]).toBeCloseTo(0.01 * grau, 6);
  });

  it('interpola dentro do segmento e prende nas pontas', () => {
    const [lon, lat] = pontoNoKm(t, 0.02 * grau);
    expect(lon).toBeCloseTo(0.02, 9);
    expect(lat).toBeCloseTo(0, 9);
    expect(pontoNoKm(t, -5)).toEqual([0, 0]);
    expect(pontoNoKm(t, 1e6)).toEqual([0.03, 0]);
  });

  it('pedaço entre dois km, em qualquer ordem, com os vértices do meio', () => {
    const p = trechoEntre(t, 0.025 * grau, 0.005 * grau);
    expect(p[0][0]).toBeCloseTo(0.005, 9);
    expect(p[1]).toEqual([0.01, 0]);
    expect(p[p.length - 1][0]).toBeCloseTo(0.025, 9);
  });

  it('km entre estações pela fração percorrida', () => {
    expect(kmEntreEstacoes([0, 1, 3], 1, 2, 0.5)).toBe(2);
    expect(kmEntreEstacoes([0, 1, 3], 2, 1, 0.25)).toBe(2.5); // sentido 1: do km 3 para o km 1
    expect(kmEntreEstacoes([0, 1, 3], 1, 2, 2)).toBe(3);
  });
});

describe('traçado real (OSM) e estações (GTFS)', () => {
  const linhas = JSON.parse(readFileSync(resolve(__dirname, '../../../dados/derivados/geo/linhas.geojson'), 'utf8')) as GeoJSON.FeatureCollection;
  const rede = carregaRedeJson();

  it('cada estação, posta no traçado pelo seu km, fica a menos de 150 m da coordenada do GTFS', () => {
    let pior = 0;
    for (const f of linhas.features) {
      const linha = String((f.properties as Record<string, unknown>).linha);
      const t = montaTracado((f.geometry as GeoJSON.LineString).coordinates as Coord[]);
      for (const e of rede.linhas[linha].estacoes) {
        const d = distanciaKm(pontoNoKm(t, e.km), [e.lon, e.lat]) * 1000;
        pior = Math.max(pior, d);
        expect(d, `${linha} ${e.nome}`).toBeLessThan(150);
      }
    }
    console.log(`maior distância estação–traçado: ${pior.toFixed(1)} m`);
  });
});
