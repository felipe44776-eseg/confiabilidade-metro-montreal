// Spec 008: cada política liga e desliga sozinha, a comparação usa números aleatórios comuns e o
// relatório separa falha de trem (MR) de falha de equipamento fixo (EF).
import { describe, expect, it } from 'vitest';
import { agrega, nomesMetricas, rodaRodadas } from '../../src/mc/rodadas';
import { avisosDoCenario, preparaContexto } from '../../src/motor/contexto';
import type { ResultadoDia } from '../../src/motor/dia';
import { simulaDia } from '../../src/motor/dia';
import type { NomePolitica, Politicas } from '../../src/motor/politicas';
import { NENHUMA_POLITICA, NOMES_POLITICAS, soPolitica } from '../../src/motor/politicas';
import { carregaFixture, carregaRede } from './apoio';

const SEMENTES = Array.from({ length: 120 }, (_, i) => 500 + i);
const LONGO = 180_000; // ms: testes com centenas de dias simulados

function ctxUtil(extra: Record<string, number> = {}) {
  return preparaContexto(carregaRede(), carregaFixture(), { tipoDia: 'util', hipoteses: extra });
}

/** Instantes e linhas das falhas sorteadas: têm de ser os mesmos com e sem a política. */
function falhasDoDia(r: ResultadoDia): string[] {
  return r.registro.filter((e) => e.tipo === 'FALHA_TREM' || e.tipo === 'FALHA_EF').map((e) => `${e.tipo}|${e.linha}|${e.t.toFixed(3)}|${e.duracaoS?.toFixed(3)}`);
}

function soma(rs: ResultadoDia[], f: (r: ResultadoDia) => number): number {
  return rs.reduce((a, r) => a + f(r), 0);
}

function rodaPar(pol: Politicas, extra: Record<string, number> = {}) {
  const ctx = ctxUtil(extra);
  const a = SEMENTES.map((s) => simulaDia(ctx, NENHUMA_POLITICA, s));
  const b = SEMENTES.map((s) => simulaDia(ctx, pol, s));
  return { a, b };
}

const minutos = (causa: 'MR' | 'EF' | 'CC') => (r: ResultadoDia) => Object.values(r.porLinha).reduce((x, m) => x + m.minutosPorCausa[causa], 0);

describe('spec 008: políticas', () => {
  it('há seis políticas, todas desligadas em "nenhuma política"', () => {
    expect(Object.keys(NOMES_POLITICAS)).toHaveLength(6);
    expect(Object.values(NENHUMA_POLITICA).every((x) => x === false)).toBe(true);
    for (const nome of Object.keys(NOMES_POLITICAS) as NomePolitica[]) {
      const p = soPolitica(nome);
      expect(Object.entries(p).filter(([, v]) => v).map(([k]) => k)).toEqual([nome]);
    }
  }, LONGO);

  it('números aleatórios comuns: as mesmas falhas acontecem com e sem cada política', () => {
    for (const nome of ['reservaFria', 'retiradaTrem', 'operacaoDegradada', 'retornoParcial', 'rotaAlternativa'] as NomePolitica[]) {
      const { a, b } = rodaPar(soPolitica(nome));
      SEMENTES.forEach((_, i) => expect(falhasDoDia(b[i]), nome).toEqual(falhasDoDia(a[i])));
    }
  }, LONGO);

  it('reserva fria: mais dias com frota completa e menos viagens canceladas', () => {
    const { a, b } = rodaPar(soPolitica('reservaFria'));
    const completas = (rs: ResultadoDia[]) => soma(rs, (r) => Object.values(r.porLinha).filter((m) => m.frotaCompleta).length);
    const canceladas = (rs: ResultadoDia[]) => soma(rs, (r) => Object.values(r.porLinha).reduce((x, m) => x + m.viagensCanceladas, 0));
    expect(completas(b)).toBeGreaterThan(completas(a));
    expect(canceladas(b)).toBeLessThan(canceladas(a));
    expect(b.some((r) => r.registro.some((e) => e.tipo === 'INJETA_RESERVA'))).toBe(true);
  }, LONGO);

  it('retirada do trem falho: reduz só os minutos de material rodante; os de equipamento fixo não mudam', () => {
    const { a, b } = rodaPar(soPolitica('retiradaTrem'));
    expect(soma(b, minutos('MR'))).toBeLessThan(soma(a, minutos('MR')));
    expect(soma(b, minutos('EF'))).toBeCloseTo(soma(a, minutos('EF')), 6);
    expect(b.some((r) => r.registro.some((e) => e.tipo === 'RETIRADA'))).toBe(true);
  }, LONGO);

  it('operação degradada: reduz só os minutos de equipamento fixo e registra a marcha lenta', () => {
    const { a, b } = rodaPar(soPolitica('operacaoDegradada'));
    expect(soma(b, minutos('EF'))).toBeLessThan(soma(a, minutos('EF')));
    expect(soma(b, minutos('MR'))).toBeCloseTo(soma(a, minutos('MR')), 6);
    expect(b.some((r) => r.registro.some((e) => e.tipo === 'DEGRADADA_INICIO'))).toBe(true);
  }, LONGO);

  it('retorno parcial e rota alternativa: mesmos bloqueios, mais pares origem-destino atendidos', () => {
    const { a, b } = rodaPar(soPolitica('retornoParcial'));
    const dispOD = (rs: ResultadoDia[]) => soma(rs, (r) => r.rede.dispOD);
    expect(dispOD(b)).toBeGreaterThan(dispOD(a));
    expect(soma(b, (r) => r.rede.minutosInterrupcao)).toBeCloseTo(soma(a, (r) => r.rede.minutosInterrupcao), 6);
    const rota = rodaPar(soPolitica('rotaAlternativa'));
    expect(dispOD(rota.b)).toBeGreaterThan(dispOD(rota.a));
    expect(soma(rota.b, (r) => r.rede.extraMin)).toBeGreaterThan(0);
  }, LONGO);

  it('tratamento de causa comum: menos eventos de causa comum', () => {
    const { a, b } = rodaPar(soPolitica('tratamentoCausaComum'));
    const cc = (rs: ResultadoDia[]) => soma(rs, (r) => Object.values(r.porLinha).reduce((x, m) => x + m.falhas.CC, 0));
    expect(cc(b)).toBeLessThan(cc(a));
    expect(soma(b, minutos('CC'))).toBeLessThan(soma(a, minutos('CC')));
  }, LONGO);

  it('retorno parcial só usa as pontas de viagem do horário e o resultado leva o aviso de hipótese', () => {
    const rede = carregaRede();
    expect(rede.horarios.util.pontasDeViagem.laranja).toEqual([0, 27, 30]); // Henri-Bourassa recebe viagens curtas
    expect(rede.horarios.util.pontasDeViagem.verde).toEqual([0, 26]);
    const ctx = ctxUtil();
    const avisos = avisosDoCenario(ctx, soPolitica('retornoParcial'));
    expect(avisos.some((x) => x.includes('retorno parcial') && x.includes('não verificados'))).toBe(true);
    const comPontos = preparaContexto(rede, carregaFixture(), { tipoDia: 'util', pontosRetorno: { verde: [14] } });
    expect(comPontos.grafo.linhas.find((l) => l.id === 'verde')?.pontasRetorno).toEqual([0, 14, 26]);
    expect(avisosDoCenario(comPontos, soPolitica('retornoParcial')).some((x) => x.includes('verde 14'))).toBe(true);
  }, LONGO);

  it('comparação contra "nenhuma política" pareada, com intervalo de 95%, separada em MR e EF', () => {
    const ctx = ctxUtil();
    const indices = Array.from({ length: 300 }, (_, i) => i);
    const rod = rodaRodadas(indices, ctx, NENHUMA_POLITICA, 99, soPolitica('retiradaTrem'));
    const ag = agrega(rod, nomesMetricas(ctx.rede.ids), 99);
    const d = ag.diferenca?.['verde.minutosMR'];
    expect(d?.n).toBe(300);
    expect(d?.semente).toBe(99);
    expect(d?.media).toBeLessThan(0);
    expect((d?.ic95[1] ?? 0) - (d?.ic95[0] ?? 0)).toBeGreaterThan(0);
    // o efeito em EF é exatamente zero, rodada a rodada
    expect(ag.diferenca?.['verde.minutosEF'].media).toBe(0);
    expect(ag.diferenca?.['verde.minutosEF'].dp).toBe(0);
    // pareado tem variância menor que a diferença de duas amostras independentes
    const a = ag.porMetrica['verde.minutosMR'];
    const b = ag.porMetricaB?.['verde.minutosMR'];
    expect(d?.ep ?? 1).toBeLessThan(Math.sqrt(a.ep ** 2 + (b?.ep ?? 0) ** 2));
  }, LONGO);

  it('sensibilidade da reserva fria ao tempo de reparo (0,5 a 4 dias)', () => {
    const efeito = [0.5, 1, 2, 4].map((reparo) => {
      const ctx = ctxUtil({ reparo_oficina_dias: reparo });
      const rod = rodaRodadas(
        Array.from({ length: 200 }, (_, i) => i),
        ctx,
        NENHUMA_POLITICA,
        7,
        soPolitica('reservaFria'),
      );
      return agrega(rod, nomesMetricas(ctx.rede.ids), 7).diferenca?.['laranja.viagensCanceladas'].media ?? 0;
    });
    // a reserva evita mais cancelamentos quando o reparo demora
    expect(efeito[3]).toBeLessThan(efeito[0]);
    for (const e of efeito) expect(e).toBeLessThanOrEqual(0);
  }, LONGO);
});
