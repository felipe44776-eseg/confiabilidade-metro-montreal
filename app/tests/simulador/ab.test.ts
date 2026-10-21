// Spec 011: comparação A/B com números aleatórios comuns.
import { describe, expect, it } from 'vitest';
import { agrega, nomesMetricas, rodaRodadas } from '../../src/mc/rodadas';
import { preparaContexto } from '../../src/motor/contexto';
import { NENHUMA_POLITICA, soPolitica } from '../../src/motor/politicas';
import { sementeDaRodada } from '../../src/motor/prng';
import { rodaRodadasAB } from '../../src/simulador/ab';
import { copia, PADRAO, paraCenarioMotor } from '../../src/simulador/cenario';
import { carregaFixture, carregaRede } from '../motor/apoio';

const BASE = 20261021;
const indices = Array.from({ length: 60 }, (_, i) => i);

describe('comparação A/B', () => {
  const rede = carregaRede();
  const p = carregaFixture();
  const ctxA = preparaContexto(rede, p, paraCenarioMotor(PADRAO));

  it('A e B usam a mesma semente em cada rodada', () => {
    const r = rodaRodadasAB(indices.slice(0, 5), ctxA, NENHUMA_POLITICA, ctxA, soPolitica('reservaFria'), BASE);
    r.forEach((x, i) => expect(x.semente).toBe(sementeDaRodada(BASE, i)));
  });

  it('cenários iguais: diferença exatamente zero em todas as métricas', () => {
    const r = rodaRodadasAB(indices, ctxA, NENHUMA_POLITICA, ctxA, NENHUMA_POLITICA, BASE);
    const ag = agrega(r, nomesMetricas(rede.ids), BASE);
    for (const e of Object.values(ag.diferenca!)) {
      expect(e.media).toBe(0);
      expect(e.ic95).toEqual([0, 0]);
    }
  });

  it('o lado A é o mesmo de uma rodada sozinha (B não interfere)', () => {
    const inverno = { ...copia(PADRAO), mes: 1, temp: 'abaixo_-15', cond: 'chuva_congelante' };
    const ctxB = preparaContexto(rede, p, paraCenarioMotor(inverno));
    const ab = rodaRodadasAB(indices, ctxA, NENHUMA_POLITICA, ctxB, NENHUMA_POLITICA, BASE);
    const so = rodaRodadas(indices, ctxA, NENHUMA_POLITICA, BASE);
    expect(ab.map((x) => x.valores)).toEqual(so.map((x) => x.valores));
    const soB = rodaRodadas(indices, ctxB, NENHUMA_POLITICA, BASE);
    expect(ab.map((x) => x.valoresB)).toEqual(soB.map((x) => x.valores));
  });
});
