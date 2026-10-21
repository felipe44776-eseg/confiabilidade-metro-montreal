import { describe, expect, it } from 'vitest';
import { preparaContexto } from '../../src/motor/contexto';
import { simulaDia } from '../../src/motor/dia';
import { NENHUMA_POLITICA } from '../../src/motor/politicas';
import { carregaFixture, carregaRede } from './apoio';

describe('fumaça: um dia útil com falhas sorteadas', () => {
  it('roda e produz métricas finitas', () => {
    const ctx = preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util' });
    let falhas = 0;
    let minutos = 0;
    const N = 200;
    for (let i = 0; i < N; i++) {
      const r = simulaDia(ctx, NENHUMA_POLITICA, 1000 + i);
      for (const m of Object.values(r.porLinha)) {
        expect(Number.isFinite(m.minutosInterrupcao)).toBe(true);
        falhas += m.falhas.MR + m.falhas.EF;
      }
      minutos += r.porLinha.laranja.minutosInterrupcao;
      expect(r.rede.dispOD).toBeGreaterThan(0);
      expect(r.rede.dispOD).toBeLessThanOrEqual(1);
    }
    console.log('falhas por dia', falhas / N, 'minutos laranja por dia', minutos / N);
    expect(falhas / N).toBeGreaterThan(1);
  });
});
