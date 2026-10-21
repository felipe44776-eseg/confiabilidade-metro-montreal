// Spec 011 (decisão D50): a página mostra o efeito do cenário nas falhas esperadas por dia,
// e a média sorteada pelo motor fica perto desse número.
import { describe, expect, it } from 'vitest';
import { agrega, nomesMetricas, rodaRodadas } from '../../src/mc/rodadas';
import { preparaContexto } from '../../src/motor/contexto';
import { NENHUMA_POLITICA, soPolitica } from '../../src/motor/politicas';
import { chaveCenario, copia, itensDoCenario, PADRAO, paraCenarioMotor } from '../../src/simulador/cenario';
import { esperadoPorDia } from '../../src/simulador/efeito';
import { NOMES_POLITICAS } from '../../src/motor/politicas';
import { carregaFixture, carregaRede } from '../motor/apoio';

/** 2.000 dias levam cerca de 5 s sozinhos e mais com os outros testes em paralelo. */
const LONGO = 120_000;

describe('falhas esperadas por dia', () => {
  const rede = carregaRede();
  const p = carregaFixture();

  it('a média de 2.000 dias sorteados fica perto do esperado, por linha e na rede', () => {
    const ctx = preparaContexto(rede, p, paraCenarioMotor(PADRAO));
    const esp = esperadoPorDia(ctx, NENHUMA_POLITICA);
    const ag = agrega(rodaRodadas(Array.from({ length: 2000 }, (_, i) => i), ctx, NENHUMA_POLITICA, 3), nomesMetricas(rede.ids), 3);
    let soma = 0;
    for (const l of rede.ids) {
      const m = (['falhasMR', 'falhasEF', 'falhasCC'] as const).reduce((s, k) => s + ag.porMetrica[`${l}.${k}`].media, 0);
      soma += m;
      // tolerância: 4 erros-padrão da média, mais 0,02 para as linhas com poucas falhas
      const ep = Math.sqrt(Math.max(esp.porLinha[l].total, 0.01) / 2000) * 2.5;
      expect(Math.abs(m - esp.porLinha[l].total), l).toBeLessThan(4 * ep + 0.02);
    }
    expect(Math.abs(soma - esp.total) / esp.total).toBeLessThan(0.05);
  }, LONGO);

  it('chuva congelante e muita neve no solo aumentam o esperado pelo produto dos multiplicadores', () => {
    const base = esperadoPorDia(preparaContexto(rede, p, paraCenarioMotor(PADRAO)), NENHUMA_POLITICA);
    const e = copia(PADRAO);
    e.cond = 'chuva_congelante';
    e.neveSolo = 'acima_10';
    const ruim = esperadoPorDia(preparaContexto(rede, p, paraCenarioMotor(e)), NENHUMA_POLITICA);
    // a fixture tem 1,8 e 1,2 nos dois tipos de falha; a causa comum não depende do clima
    const semCC = (x: typeof base) => Object.values(x.porLinha).reduce((s, v) => s + v.MR + v.EF, 0);
    expect(semCC(ruim) / semCC(base)).toBeCloseTo(1.8 * 1.2, 6);
  });

  it('o tratamento da causa comum reduz só a parte de causa comum', () => {
    const ctx = preparaContexto(rede, p, paraCenarioMotor(PADRAO));
    const sem = esperadoPorDia(ctx, NENHUMA_POLITICA);
    const com = esperadoPorDia(ctx, soPolitica('tratamentoCausaComum'));
    for (const l of rede.ids) {
      expect(com.porLinha[l].MR).toBe(sem.porLinha[l].MR);
      expect(com.porLinha[l].CC).toBeLessThanOrEqual(sem.porLinha[l].CC);
    }
    expect(com.total).toBeLessThan(sem.total);
  });
});

describe('o que está valendo no cenário', () => {
  it('no padrão nada aparece como mudado; cada mudança marca só o seu item', () => {
    expect(itensDoCenario(PADRAO, NOMES_POLITICAS).filter((i) => i.mudou)).toEqual([]);
    const e = copia(PADRAO);
    e.cond = 'neve';
    e.politicas.reservaFria = true;
    const mudados = itensDoCenario(e, NOMES_POLITICAS).filter((i) => i.mudou);
    expect(mudados.map((i) => i.rotulo)).toEqual(['Condição', 'Políticas']);
    expect(mudados[0].texto).toBe('neve');
  });

  it('a chave do cenário ignora o dia mostrado', () => {
    const e = copia(PADRAO);
    e.dia = 17;
    expect(chaveCenario(e)).toBe(chaveCenario(PADRAO));
    e.cond = 'chuva';
    expect(chaveCenario(e)).not.toBe(chaveCenario(PADRAO));
  });
});
