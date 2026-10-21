// Spec 015: confiabilidade de uma viagem de uma estação a outra.
import { describe, expect, it } from 'vitest';
import { preparaContexto } from '../../src/motor/contexto';
import type { FalhaInjetada } from '../../src/motor/dia';
import { simulaDia } from '../../src/motor/dia';
import type { Grafo } from '../../src/motor/grafo';
import { segmentosBloqueados } from '../../src/motor/grafo';
import { hipotese } from '../../src/motor/hipoteses';
import { NENHUMA_POLITICA, soPolitica } from '../../src/motor/politicas';
import { sementeDaRodada } from '../../src/motor/prng';
import type { AvaliadorViagem } from '../../src/motor/viagem';
import {
  chegadaMaisCedo,
  conexoesDe,
  indiceEstacao,
  metricasViagemDia,
  nomesViagem,
  preparaViagem,
  rodaViagem,
  rotaDoPar,
  semCaminho,
  simulaDiaViagem,
} from '../../src/motor/viagem';
import { carregaFixture, carregaRede } from './apoio';

const LONGO = 300_000;
const ANGRIGNON = 'STATION_M118';
const LIONEL_GROULX = 'STATION_M132';
const BERRI = 'STATION_M146';
const SAINT_MICHEL = 'STATION_M556';
const OITO = 8 * 3600;
const MEIA_HORA = 1800;

const rede = carregaRede();
const p = carregaFixture();
const ctxSemFalhas = () => preparaContexto(rede, p, { tipoDia: 'util', semFalhas: true });

function porNome(av: AvaliadorViagem, valores: number[]): Record<string, number> {
  return Object.fromEntries(nomesViagem(av).map((n, i) => [n, valores[i]]));
}

/** Atraso (s) da saída t, com as trajetórias do dia, contra o dia sem falhas. */
function atrasoDaSaida(g: Grafo, av: AvaliadorViagem, trajetorias: Parameters<typeof conexoesDe>[2], t: number): number {
  const i = av.saidas.indexOf(t);
  if (i < 0) throw new Error(`saída ${t} fora da grade`);
  const c = chegadaMaisCedo(g, conexoesDe(g, rede, trajetorias), av.rota.origem, av.rota.destino, t, av.transferenciaS, av.permitida);
  return c - av.chegadaSemFalhas[i];
}

describe('spec 015: caminho de sempre', () => {
  it('de Angrignon a Saint-Michel, os trechos se encontram nas baldeações e o tempo soma trechos e baldeações', () => {
    const ctx = ctxSemFalhas();
    const g = ctx.grafo;
    const r = rotaDoPar(g, indiceEstacao(g, ANGRIGNON), indiceEstacao(g, SAINT_MICHEL));
    expect(r).not.toBeNull();
    const rota = r!;
    expect(rota.trechos.length).toBeGreaterThanOrEqual(2);
    expect(rota.trechos[0].linha).toBe('verde');
    expect(rota.trechos[0].deNome).toBe('Angrignon');
    expect(rota.trechos[rota.trechos.length - 1].linha).toBe('azul');
    expect(rota.trechos[rota.trechos.length - 1].ateNome).toBe('Saint-Michel');
    for (let i = 0; i + 1 < rota.trechos.length; i++) expect(rota.trechos[i].ateNome).toBe(rota.trechos[i + 1].deNome);
    const transfer = hipotese('tempo_transferencia_min', p, ctx.cenario);
    const soma = rota.trechos.reduce((s, t) => s + t.minutos, 0) + (rota.trechos.length - 1) * transfer;
    expect(rota.minutos).toBeCloseTo(soma, 6);
  });

  it('a mesma estação, ou uma estação desconhecida, não tem caminho', () => {
    const g = ctxSemFalhas().grafo;
    expect(rotaDoPar(g, indiceEstacao(g, BERRI), indiceEstacao(g, BERRI))).toBeNull();
    expect(indiceEstacao(g, 'nao-existe')).toBe(-1);
    expect(preparaViagem(ctxSemFalhas(), 'nao-existe', BERRI, false)).toBeNull();
  });
});

describe('spec 015: sem falhas', () => {
  it('toda saída chega na hora e o caminho fica disponível o dia todo', () => {
    const ctx = ctxSemFalhas();
    const av = preparaViagem(ctx, ANGRIGNON, SAINT_MICHEL, false)!;
    expect(av.saidas.length).toBeGreaterThan(100);
    const m = porNome(av, metricasViagemDia(ctx, av, simulaDiaViagem(ctx, NENHUMA_POLITICA, 1)));
    expect(m.disp).toBe(1);
    expect(m.minSemCaminho).toBe(0);
    expect(m.atraso5).toBe(0);
    expect(m.atraso15).toBe(0);
    expect(m.naoChega).toBe(0);
    expect(m.atrasoMedioMin).toBe(0);
    for (const t of av.rota.trechos.keys()) expect(m[`disp.trecho.${t}`]).toBe(1);
  });
});

describe('spec 015: interrupção injetada', () => {
  it('meia hora parada na Verde às 08:00: o caminho falta 30 min, quem sai antes não atrasa e quem sai às 08:00 atrasa', () => {
    const ctx = ctxSemFalhas();
    const g = ctx.grafo;
    const av = preparaViagem(ctx, ANGRIGNON, BERRI, false)!;
    expect(av.rota.trechos.map((t) => t.linha)).toEqual(['verde']);
    const trecho = g.arestas[av.rota.trechos[0].arestas[3]].trecho;
    const inj: FalhaInjetada[] = [{ tipo: 'EF', t: OITO, duracaoS: MEIA_HORA, linha: 'verde', trecho, sentidos: [0, 1] }];
    const r = simulaDia(ctx, NENHUMA_POLITICA, 1, { injetadas: inj, trajetorias: true, bloqueiosOD: true });
    const sem = semCaminho(g, av.rota, segmentosBloqueados(r.bloqueiosOD ?? [], av.janela), false);
    expect(sem.total).toBe(MEIA_HORA);
    expect(sem.porTrecho).toEqual([MEIA_HORA]);
    expect(atrasoDaSaida(g, av, r.trajetorias!, 6 * 3600)).toBe(0);
    expect(atrasoDaSaida(g, av, r.trajetorias!, 7 * 3600)).toBe(0);
    expect(atrasoDaSaida(g, av, r.trajetorias!, OITO)).toBeGreaterThan(5 * 60);
    const m = porNome(av, metricasViagemDia(ctx, av, r));
    expect(m.diaComInterrupcao).toBe(1);
    expect(m.minSemCaminho).toBe(30);
    expect(m.atraso5).toBeGreaterThan(0);
    expect(m['atraso5.h6']).toBe(0);
    expect(m['atraso5.h8']).toBeGreaterThan(0);
  });

  it('com rota alternativa, a interrupção no caminho de Lionel-Groulx a Berri-UQAM é contornada pela outra linha', () => {
    const ctx = ctxSemFalhas();
    const g = ctx.grafo;
    const sem = preparaViagem(ctx, LIONEL_GROULX, BERRI, false)!;
    const com = preparaViagem(ctx, LIONEL_GROULX, BERRI, true)!;
    expect(sem.rota.trechos).toHaveLength(1);
    const { linha, arestas } = sem.rota.trechos[0];
    const trecho = g.arestas[arestas[2]].trecho;
    const inj: FalhaInjetada[] = [{ tipo: 'EF', t: OITO, duracaoS: MEIA_HORA, linha, trecho, sentidos: [0, 1] }];
    const pol = soPolitica('rotaAlternativa');
    const r = simulaDia(ctx, pol, 1, { injetadas: inj, trajetorias: true, bloqueiosOD: true });
    const segs = segmentosBloqueados(r.bloqueiosOD ?? [], sem.janela);
    expect(semCaminho(g, sem.rota, segs, false).total).toBe(MEIA_HORA);
    expect(semCaminho(g, com.rota, segs, true).total).toBe(0);
    const t = OITO + 600;
    const atrasoSem = atrasoDaSaida(g, sem, r.trajetorias!, t);
    const atrasoCom = atrasoDaSaida(g, com, r.trajetorias!, t);
    expect(atrasoSem).toBeGreaterThan(5 * 60);
    expect(atrasoCom).toBeLessThan(atrasoSem);
  });
});

describe('spec 015: coerência com a rede', () => {
  /** Primeiro dia sorteado com a rede parcialmente sem caminho. */
  function diaComFalhas(ctx: ReturnType<typeof preparaContexto>, pol: typeof NENHUMA_POLITICA) {
    for (let s = 1; s < 200; s++) {
      const r = simulaDia(ctx, pol, s, { registrar: false, bloqueiosOD: true });
      if (r.rede.dispOD < 0.999) return r;
    }
    throw new Error('nenhum dia com falha');
  }

  for (const rotaAlternativa of [false, true]) {
    it(`ponderada pela oferta, a viagem de cada par reproduz a disponibilidade origem-destino do dia (rota alternativa ${rotaAlternativa ? 'ligada' : 'desligada'})`, () => {
      const ctx = preparaContexto(rede, p, { tipoDia: 'util' });
      const pol = rotaAlternativa ? soPolitica('rotaAlternativa') : NENHUMA_POLITICA;
      const r = diaComFalhas(ctx, pol);
      const g = ctx.grafo;
      const janela = ctx.horario.janelaRede;
      const segs = segmentosBloqueados(r.bloqueiosOD ?? [], janela);
      const N = g.nEstacoesBase;
      let fora = 0;
      for (let o = 0; o < N; o++) {
        for (let d = 0; d < N; d++) {
          const peso = g.pesos[o * N + d];
          if (!peso) continue;
          const rota = rotaDoPar(g, o, d)!;
          fora += (peso * semCaminho(g, rota, segs, rotaAlternativa).total) / (janela[1] - janela[0]);
        }
      }
      expect(1 - fora / g.pesoTotal).toBeCloseTo(r.rede.dispOD, 10);
    }, LONGO);
  }
});

describe('spec 015: rodadas', () => {
  it('a rodada i é o mesmo dia da aba "Muitos dias" e o mesmo pedido dá os mesmos números', () => {
    const ctx = preparaContexto(rede, p, { tipoDia: 'util' });
    const av = preparaViagem(ctx, ANGRIGNON, SAINT_MICHEL, false)!;
    for (const i of [0, 1, 2]) {
      const s = sementeDaRodada(7, i);
      const a = simulaDiaViagem(ctx, NENHUMA_POLITICA, s);
      const b = simulaDia(ctx, NENHUMA_POLITICA, s, { registrar: false });
      expect(a.porLinha).toEqual(b.porLinha);
      expect(a.rede.minutosInterrupcao).toBe(b.rede.minutosInterrupcao);
      expect(a.rede.trensHoraPerdidos).toBe(b.rede.trensHoraPerdidos);
      expect(a.bloqueiosOD?.length ?? 0).toBeGreaterThanOrEqual(0);
    }
    const x = rodaViagem([0, 1, 2, 3], ctx, NENHUMA_POLITICA, 7, av);
    const y = rodaViagem([0, 1, 2, 3], ctx, NENHUMA_POLITICA, 7, av);
    expect(x).toEqual(y);
    for (const r of x) expect(r.valores).toHaveLength(nomesViagem(av).length);
  }, LONGO);
});
