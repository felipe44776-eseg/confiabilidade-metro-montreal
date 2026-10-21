// Constituição, princípio 6: dado ausente nunca vira zero.
import { describe, expect, it } from 'vitest';
import { taxaAcumulada } from '../../src/motor/taxas';
import type { Parametros } from '../../src/motor/tipos';
import { carregaFixture, carregaRede } from './apoio';

describe('spec 007: taxa-base ausente no contrato', () => {
  it('linha sem taxa-base é erro, não taxa zero (linha que nunca falharia)', () => {
    const p = carregaFixture();
    const rede = carregaRede();
    const linha = rede.ids[0];
    const semTaxa: Parametros = { ...p, taxas: { ...p.taxas, MR: { ...p.taxas.MR, base_por_trem_hora: {} } } };
    expect(() => taxaAcumulada(semTaxa, rede.horarios.util, { tipoDia: 'util' }, linha, 'MR')).toThrow(/taxa-base/);
    expect(taxaAcumulada(p, rede.horarios.util, { tipoDia: 'util' }, linha, 'MR').at(-1)).toBeGreaterThan(0);
  });
});
