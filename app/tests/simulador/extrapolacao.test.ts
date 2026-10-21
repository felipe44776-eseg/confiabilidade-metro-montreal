// Spec 011: avisos de extrapolação.
import { describe, expect, it } from 'vitest';
import { copia, PADRAO } from '../../src/simulador/cenario';
import { avisosDeExtrapolacao } from '../../src/simulador/extrapolacao';
import { OBSERVADO } from '../../src/simulador/observado';
import { carregaFixture } from '../motor/apoio';

const p = carregaFixture();
const niveis = (e: ReturnType<typeof copia>) => avisosDeExtrapolacao(e, p).map((a) => a.nivel);

describe('avisos de extrapolação', () => {
  it('o cenário padrão não extrapola', () => {
    expect(niveis(copia(PADRAO))).not.toContain('extrapola');
  });

  it('neve no solo em julho: sem dado observado', () => {
    const e = { ...copia(PADRAO), mes: 7, temp: '15a25', neveSolo: '1a10' };
    expect(OBSERVADO['mes|neve_solo']['7|1a10']).toBeUndefined();
    const av = avisosDeExtrapolacao(e, p);
    expect(av.some((a) => a.nivel === 'extrapola' && a.texto.includes('neve no solo'))).toBe(true);
  });

  it('chuva congelante a 25 °C ou mais: extrapolação', () => {
    const e = { ...copia(PADRAO), mes: 7, temp: '25_ou_mais', cond: 'chuva_congelante' };
    const av = avisosDeExtrapolacao(e, p);
    expect(av.some((a) => a.nivel === 'extrapola' && a.texto.includes('chuva congelante'))).toBe(true);
  });

  it('combinação rara vira "poucos dados", não extrapolação', () => {
    // abril com 25 °C ou mais: 4 horas nos dados
    expect(OBSERVADO['mes|temp']['4|25_ou_mais']).toBe(4);
    const e = { ...copia(PADRAO), mes: 4, temp: '25_ou_mais' };
    expect(niveis(e)).toContain('poucos_dados');
  });

  it('hipótese fora da faixa do parametros.json', () => {
    const e = copia(PADRAO);
    e.hipoteses = { reparo_oficina_dias: 6 };
    const av = avisosDeExtrapolacao(e, p);
    expect(av.some((a) => a.nivel === 'extrapola' && a.texto.includes('reparo_oficina_dias'))).toBe(true);
    e.hipoteses = { reparo_oficina_dias: 3 };
    expect(avisosDeExtrapolacao(e, p).some((a) => a.texto.includes('reparo_oficina_dias'))).toBe(false);
  });

  it('feriado em dia útil: nos dados, feriado usa o horário de domingo', () => {
    const e = { ...copia(PADRAO), feriado: true };
    expect(niveis(e)).toContain('extrapola');
    expect(niveis({ ...e, tipoDia: 'domingo' as const })).not.toContain('extrapola');
  });
});
