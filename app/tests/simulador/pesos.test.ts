// Spec 011 (decisão D51): o painel do cenário mostra o peso de cada variável no modelo de taxa e a nota do
// método, com os números dos arquivos gerados (parametros.json e dados/derivados/modelos/taxa_<causa>.json).
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { FAIXAS_HORARIAS } from '../../src/motor/taxas';
import { comIC, inteiro, num } from '../../src/ui/formato';
import { copia, PADRAO } from '../../src/simulador/cenario';
import type { ResumoTaxa, Resumos } from '../../src/simulador/pesos';
import { notaDoMetodo, pesoDoNivel, pesosDoCenario, textoP } from '../../src/simulador/pesos';
import { carregaFixture, carregaParametrosReais } from '../motor/apoio';

const MODELOS = resolve(__dirname, '../../../dados/derivados/modelos');
const resumo = (c: string) => JSON.parse(readFileSync(resolve(MODELOS, `taxa_${c}.json`), 'utf8')) as ResumoTaxa;

describe('peso de cada variável', () => {
  const p = carregaParametrosReais();
  const resumos: Resumos = { MR: resumo('MR'), EF: resumo('EF') };
  const vezes = (x: { valor: number; ic95?: readonly number[] | null }) => `×${comIC(x.valor, x.ic95 ?? undefined, 2)}`;

  it('o peso de um nível é o multiplicador do parametros.json, com o IC, nas duas causas', () => {
    for (const [fator, nivel] of [['neve_solo', 'acima_10'], ['temp', '25_ou_mais'], ['cond', 'chuva_congelante'], ['tipo_dia', 'sabado'], ['estacao', 'inverno'], ['jogo', '1']]) {
      const mr = p.taxas.MR.multiplicadores[fator][nivel];
      const ef = p.taxas.EF.multiplicadores[fator][nivel];
      expect(pesoDoNivel(p, fator, nivel), `${fator}=${nivel}`).toBe(`MR ${vezes(mr)} · EF ${vezes(ef)}`);
    }
  });

  it('a referência e os indicadores desligados valem 1', () => {
    expect(pesoDoNivel(p, 'temp', '5a15')).toBe('1 (referência)');
    expect(pesoDoNivel(p, 'jogo', '0')).toBe('1 (referência)');
    const t = pesosDoCenario(p, PADRAO, resumos);
    for (const campo of ['temp', 'precip', 'cond', 'neve'] as const) expect(t[campo], campo).toBe('Peso: 1 (referência).');
    expect(t.tipo).toMatch(/^Peso: 1 \(referência\)\. O tipo de dia também troca o horário/);
    expect(t.mes).toBe('Estação do ano no modelo: outono; peso: 1 (referência).');
    // caixas desmarcadas mostram o peso de marcar
    expect(t.jogo).toBe(`Se marcado, peso das 18h às 23h: ${pesoDoNivel(p, 'jogo', '1')}.`);
    expect(t.gp.startsWith('Se marcado, peso: MR ×')).toBe(true);
  });

  it('o texto acompanha o cenário escolhido', () => {
    const e = copia(PADRAO);
    e.neveSolo = 'acima_10';
    e.mes = 1;
    e.jogo = true;
    const t = pesosDoCenario(p, e, resumos);
    expect(t.neve).toBe(`Peso: ${pesoDoNivel(p, 'neve_solo', 'acima_10')}.`);
    expect(t.mes).toBe(`Estação do ano no modelo: inverno; peso: ${pesoDoNivel(p, 'estacao', 'inverno')}.`);
    expect(t.jogo.startsWith('Peso das 18h às 23h: MR ×')).toBe(true);
  });

  it('a greve não tem peso na taxa (D42) e mostra o multiplicador medido quando o resumo carregou', () => {
    expect(p.taxas.MR.multiplicadores.greve).toBeUndefined();
    const g = resumos.MR.coeficientes.find((c) => c.termo === 'greve')!;
    const com = pesosDoCenario(p, PADRAO, resumos).greve;
    expect(com).toContain(`MR ×${comIC(g.multiplicador, g.ic95, 2)}`);
    expect(com).toContain('intervalo que contém 1');
    expect(com).toContain('D42');
    expect(pesosDoCenario(p, PADRAO, null).greve).toBe('Sem peso na taxa: a greve entra só pelo horário, com menos trens (decisão D42).');
  });

  it('a nota do método cita os números dos arquivos gerados', () => {
    const n = notaDoMetodo(p, resumos);
    const texto = n.passos.join(' ');
    expect(n.resumo).toContain(`regressão ${p.taxas.MR.modelo}`);
    expect(texto).toContain(`${inteiro(resumos.MR.n_horas)} horas-linha`);
    expect(texto).toContain(`${inteiro(resumos.MR.n_falhas)} de material rodante e ${inteiro(resumos.EF.n_falhas)} de equipamentos fixos`);
    expect(texto).toContain(`α = ${num(p.taxas.MR.alpha.valor, 2)} em MR e ${num(p.taxas.EF.alpha.valor, 2)} em EF`);
    expect(texto).toContain(`MR: ${inteiro(resumos.MR.aic_poisson)} na Poisson contra ${inteiro(resumos.MR.aic_nb)}`);
    expect(texto).toContain(`${inteiro(resumos.MR.bootstrap_b)} reamostras (semente ${resumos.MR.semente})`);
    expect(texto).toContain(`ano de ${p.ano_base}`);
    expect(texto).toContain('Linha Laranja, entrepico, dia útil, outono, 5 a 15 °C, sem precipitação, sem chuva nem neve, sem neve no solo');
  });

  it('a tabela das faixas do dia segue as faixas do motor e marca a referência', () => {
    const { faixas } = notaDoMetodo(p, resumos);
    expect(faixas).toHaveLength(FAIXAS_HORARIAS.length);
    const abertura = faixas[0];
    expect(abertura.horas).toBe('5h–7h');
    expect(abertura.mr).toBe(vezes(p.taxas.MR.multiplicadores.faixa.abertura));
    expect(faixas.find((f) => f.faixa === 'entrepico')?.mr).toBe('1 (referência)');
    expect(faixas[faixas.length - 1].horas).toBe('23h ao fim');
  });

  it('sem o resumo do ajuste, a nota usa só o parametros.json', () => {
    const n = notaDoMetodo(p, null);
    const texto = n.passos.join(' ');
    expect(texto).toContain(`${inteiro(p.taxas.MR.alpha.n as number)} horas-linha`);
    expect(texto).toContain('reamostras');
    expect(texto).not.toContain('semente');
    expect(texto).toContain('a comparação com a Poisson está no relatório do modelo');
    // a fixture dos testes do motor também monta a nota sem erro
    expect(() => notaDoMetodo(carregaFixture(), null)).not.toThrow();
    expect(() => pesosDoCenario(carregaFixture(), PADRAO, null)).not.toThrow();
  });

  it('valor-p muito pequeno vira potência de 10', () => {
    expect(textoP(3.588e-33)).toBe('p < 10⁻³²');
    expect(textoP(4.4e-206)).toBe('p < 10⁻²⁰⁵');
    expect(textoP(0.0123)).toBe(`p = ${num(0.0123, 3)}`);
  });
});
