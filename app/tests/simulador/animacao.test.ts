// Spec 010: estado do dia simulado num instante (trens, bloqueios, indicadores) e custo por quadro.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { preparaContexto } from '../../src/motor/contexto';
import { simulaDia, trensEmViagem } from '../../src/motor/dia';
import { NENHUMA_POLITICA } from '../../src/motor/politicas';
import { blocosAtivos, blocosDoDia, FPS_PARADO, minutosAte, ocorrenciasDoDia, posicoes, relogio, textoFps } from '../../src/simulador/animacao';
import type { Coord } from '../../src/simulador/tracado';
import { montaTracado, pontoNoKm } from '../../src/simulador/tracado';
import { carregaFixture, carregaRede } from '../motor/apoio';

const OITO = 8 * 3600;

describe('animação do dia', () => {
  const rede = carregaRede();
  const p = carregaFixture();

  it('às 08:00 sem falhas, os trens desenhados são os do motor (26, 31, 2 e 9)', () => {
    const ctx = preparaContexto(rede, p, { tipoDia: 'util', semFalhas: true });
    const r = simulaDia(ctx, NENHUMA_POLITICA, 1, { trajetorias: true });
    const pos = posicoes(rede, r.trajetorias!, OITO);
    const porLinha: Record<string, number> = {};
    for (const x of pos) porLinha[x.linha] = (porLinha[x.linha] ?? 0) + 1;
    for (const l of rede.ids) {
      const motor = trensEmViagem([...r.trajetorias![`${l}:0`], ...r.trajetorias![`${l}:1`]], OITO);
      expect(porLinha[l] ?? 0, l).toBe(motor);
    }
    expect([porLinha.verde, porLinha.laranja, porLinha.amarela, porLinha.azul]).toEqual([26, 31, 2, 9]);
    for (const x of pos) {
      const est = rede.linhas[x.linha].estacoes;
      expect(x.km).toBeGreaterThanOrEqual(Math.min(est[0].km, est[est.length - 1].km) - 1e-9);
      expect(x.km).toBeLessThanOrEqual(Math.max(est[0].km, est[est.length - 1].km) + 1e-9);
      expect(x.atrasoS).toBe(0);
    }
  });

  it('falha injetada: o trecho fica bloqueado do início até a retomada e os minutos batem com o motor', () => {
    const ctx = preparaContexto(rede, p, { tipoDia: 'util', semFalhas: true });
    const r = simulaDia(ctx, NENHUMA_POLITICA, 7, { trajetorias: true, injetadas: [{ tipo: 'EF', t: OITO, duracaoS: 900, linha: 'laranja', trecho: 10, sentidos: [0, 1] }] });
    const blocos = blocosDoDia(r);
    expect(blocos).toHaveLength(1); // um bloqueio nos dois sentidos (sentido null)
    expect(blocos[0]).toMatchObject({ linha: 'laranja', trecho: 10, sentido: null, ini: OITO, fim: OITO + 900, causa: 'EF' });
    expect(blocosAtivos(blocos, OITO - 1)).toHaveLength(0);
    expect(blocosAtivos(blocos, OITO + 450)).toHaveLength(1);
    expect(blocosAtivos(blocos, OITO + 900)).toHaveLength(0);
    expect(ocorrenciasDoDia(r)).toHaveLength(1);
    const fim = ctx.horario.janelaRede[1];
    const min = minutosAte(rede, ctx.horario.inicioServico, blocos, fim + 3600);
    expect(min.laranja).toBeCloseTo(r.porLinha.laranja.minutosInterrupcao, 9);
    expect(min.laranja).toBeCloseTo(15, 9);
    expect(minutosAte(rede, ctx.horario.inicioServico, blocos, OITO + 300).laranja).toBeCloseTo(5, 9);
  });

  it('relógio do dia de operação', () => {
    expect(relogio(25 * 3600 + 15 * 60)).toBe('01:15');
    expect(relogio(OITO + 59)).toBe('08:00');
  });

  it('custo por quadro: posições de todos os trens no pico, no traçado real', () => {
    const linhas = JSON.parse(readFileSync(resolve(__dirname, '../../../dados/derivados/geo/linhas.geojson'), 'utf8')) as GeoJSON.FeatureCollection;
    const tracados: Record<string, ReturnType<typeof montaTracado>> = {};
    for (const f of linhas.features) tracados[String((f.properties as Record<string, unknown>).linha)] = montaTracado((f.geometry as GeoJSON.LineString).coordinates as Coord[]);
    const ctx = preparaContexto(rede, p, { tipoDia: 'util' });
    const r = simulaDia(ctx, NENHUMA_POLITICA, 3, { trajetorias: true });
    const blocos = blocosDoDia(r);
    const N = 2000;
    let soma = 0;
    const t0 = performance.now();
    for (let i = 0; i < N; i++) {
      const t = OITO + i * 0.5; // meia hora de pico em passos de 0,5 s simulado
      for (const x of posicoes(rede, r.trajetorias!, t)) soma += pontoNoKm(tracados[x.linha], x.km)[0];
      soma += blocosAtivos(blocos, t).length;
    }
    const msPorQuadro = (performance.now() - t0) / N;
    console.log(`custo por quadro (posições + pontos no traçado + bloqueios): ${msPorQuadro.toFixed(3)} ms`);
    expect(Number.isFinite(soma)).toBe(true);
    expect(msPorQuadro).toBeLessThan(5); // folga para 30 fps (33 ms por quadro) com o desenho do MapLibre
  });
});

describe('contador de quadros', () => {
  it('mostra "parado" quando a animação não toca, e a taxa só quando toca (achado 7, rodada 3)', () => {
    expect(textoFps(false, 60, 1000)).toBe(FPS_PARADO);
    expect(textoFps(true, 33, 1000)).toBe('33 fps');
    expect(textoFps(true, 0, 0)).toBe('— fps');
  });
});
