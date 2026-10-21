// Spec 016 (decisão D54): escala para confiabilidade alta.
import { describe, expect, it } from 'vitest';
import { estimativa } from '../../src/mc/rodadas';
import { noves, novesIC, razaoPareada, textoRazao } from '../../src/ui/escala';

const f = (x: number, c: number) => x.toFixed(c);

describe('noves', () => {
  it('99% são 2 noves, 99,9% são 3, 100% é infinito', () => {
    expect(noves(0.99)).toBeCloseTo(2, 12);
    expect(noves(0.999)).toBeCloseTo(3, 12);
    expect(noves(1)).toBe(Infinity);
    expect(noves(0.9954)).toBeCloseTo(2.337, 3);
  });

  it('o intervalo dos noves sai dos extremos do intervalo da disponibilidade, recortado em [0, 1]', () => {
    const r = novesIC({ media: 0.999, ic95: [0.998, 1.0004] });
    expect(r.media).toBeCloseTo(3, 12);
    expect(r.ic95[0]).toBeCloseTo(-Math.log10(0.002), 12);
    expect(r.ic95[1]).toBe(Infinity);
  });
});

describe('razão pareada', () => {
  it('X = 0,1 × Y em todo dia: razão 0,1 sem incerteza', () => {
    const y = [5, 0, 12, 3, 40, 0, 7, 1];
    const x = y.map((v) => 0.1 * v);
    const r = razaoPareada(estimativa(x, 1), estimativa(y, 1), estimativa(x.map((v, i) => v - y[i]), 1))!;
    expect(r.media).toBeCloseTo(0.1, 12);
    expect(r.ic95[1] - r.ic95[0]).toBeLessThan(1e-9);
  });

  it('bate com o método delta escrito por extenso', () => {
    const y = [3, 9, 0, 14, 2, 6, 0, 21, 5, 8];
    const x = [1, 2, 0, 9, 0, 1, 0, 3, 2, 0];
    const ex = estimativa(x, 1);
    const ey = estimativa(y, 1);
    const n = x.length;
    const mx = ex.media;
    const my = ey.media;
    let cov = 0;
    for (let i = 0; i < n; i++) cov += (x[i] - mx) * (y[i] - my);
    cov /= n - 1;
    const R = mx / my;
    const v = (ex.dp ** 2 - 2 * R * cov + R * R * ey.dp ** 2) / (n * my * my);
    const r = razaoPareada(ex, ey, estimativa(x.map((v2, i) => v2 - y[i]), 1))!;
    expect(r.media).toBeCloseTo(R, 12);
    expect(r.ic95[1]).toBeCloseTo(R + 1.959963984540054 * Math.sqrt(v), 10);
  });

  it('sem tempo parado na rede atual, não há razão', () => {
    expect(razaoPareada(estimativa([0, 0], 1), estimativa([0, 0], 1), estimativa([0, 0], 1))).toBeNull();
  });

  it('texto: vezes menos ou mais', () => {
    expect(textoRazao(0.04, f)).toBe('25 vezes menos');
    expect(textoRazao(0.5, f)).toBe('2.0 vezes menos');
    expect(textoRazao(1.3, f)).toBe('1.3 vez mais');
    expect(textoRazao(1, f)).toBe('igual');
    expect(textoRazao(0, f)).toBe('nenhum minuto');
  });
});
