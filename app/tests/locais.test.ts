import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { type Local, paraGeoJSON, raio, somaPorStatus } from '../src/locais';

const locais: Local[] = JSON.parse(readFileSync(resolve(__dirname, '../../dados/derivados/geo/locais.json'), 'utf-8'));

describe('locais dos incidentes (spec 002)', () => {
  it('soma exatamente as 8.530 falhas técnicas de uma linha', () => {
    const s = somaPorStatus(locais);
    expect(s.verificado + s.deduzido + s.aproximado + s.desconhecido).toBe(8530);
  });

  it('nunca põe local sem posição em (0, 0)', () => {
    const g = paraGeoJSON(locais);
    const semPosicao = locais.filter((l) => l.lat === null).length;
    expect(g.features.length).toBe(locais.length - semPosicao);
    for (const f of g.features) {
      expect(Math.abs(f.geometry.coordinates[0])).toBeGreaterThan(73);
      expect(f.geometry.coordinates[1]).toBeGreaterThan(45);
    }
  });

  it('todo local com posição tem status diferente de desconhecido', () => {
    for (const l of locais) if (l.lat !== null) expect(l.status).not.toBe('desconhecido');
  });
});

describe('raio', () => {
  it('cresce com a raiz do número de falhas e respeita os limites', () => {
    expect(raio(0, 100)).toBe(0);
    expect(raio(100, 100)).toBe(22);
    expect(raio(25, 100)).toBeCloseTo(3 + 19 * 0.5);
  });
});
