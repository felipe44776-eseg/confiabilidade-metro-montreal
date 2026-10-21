// O motor roda com o parametros.json real do pipeline sem mudança de código (contrato
// contratos/parametros.schema.json). Pulado enquanto o pipeline não gerar o arquivo.
import { describe, expect, it } from 'vitest';
import { agrega, nomesMetricas, rodaRodadas } from '../../src/mc/rodadas';
import { avisosDoCenario, preparaContexto } from '../../src/motor/contexto';
import { simulaDia } from '../../src/motor/dia';
import { avaliaRedeAtual } from '../../src/motor/expansao';
import { NENHUMA_POLITICA, soPolitica } from '../../src/motor/politicas';
import type { Parametros } from '../../src/motor/tipos';
import { carregaParametrosReais, carregaRede, temParametrosReais } from './apoio';

const LONGO = 600_000;
const OBRIGATORIAS = ['versao', 'codigo_commit', 'ano_base', 'taxas', 'renovacao', 'ttr', 'causa_comum', 'locais_ef', 'frota', 'hipoteses'] as const;
const STATUS = new Set(['ajustado', 'deduzido', 'hipótese', 'não verificado']);

function parametrosDe(p: Parametros): { caminho: string; status: string }[] {
  const saida: { caminho: string; status: string }[] = [];
  const visita = (x: unknown, caminho: string) => {
    if (x && typeof x === 'object') {
      const o = x as Record<string, unknown>;
      if ('valor' in o && 'status' in o) saida.push({ caminho, status: String(o.status) });
      else for (const [k, v] of Object.entries(o)) visita(v, `${caminho}.${k}`);
    }
  };
  visita(p, '');
  return saida;
}

describe.skipIf(!temParametrosReais)('parametros.json real', () => {
  it('segue o contrato: chaves obrigatórias e todo número com status válido', () => {
    const p = carregaParametrosReais();
    for (const k of OBRIGATORIAS) expect(p, k).toHaveProperty(k);
    for (const l of ['verde', 'laranja', 'amarela', 'azul']) {
      expect(p.taxas.MR.base_por_trem_hora[l].valor).toBeGreaterThan(0);
      expect(p.taxas.EF.base_por_trem_hora[l].valor).toBeGreaterThan(0);
      expect(p.frota[l].trens_necessarios.valor).toBeGreaterThan(0);
    }
    const todos = parametrosDe(p);
    expect(todos.length).toBeGreaterThan(50);
    for (const x of todos) expect(STATUS.has(x.status), x.caminho).toBe(true);
  });

  it('roda dias, Monte Carlo, políticas e o método de estados', () => {
    const rede = carregaRede();
    const p = carregaParametrosReais();
    const ctx = preparaContexto(rede, p, { tipoDia: 'util' });
    const r = simulaDia(ctx, NENHUMA_POLITICA, 1);
    expect(r.hash).toMatch(/^[0-9a-f]{8}$/);
    const ag = agrega(rodaRodadas(Array.from({ length: 500 }, (_, i) => i), ctx, NENHUMA_POLITICA, 11, soPolitica('retiradaTrem')), nomesMetricas(rede.ids), 11);
    const linhas: string[] = [];
    for (const l of rede.ids) {
      const d = ag.porMetrica[`${l}.disponibilidade`];
      expect(d.media).toBeGreaterThan(0.95);
      expect(d.media).toBeLessThanOrEqual(1);
      const f = ag.porMetrica[`${l}.falhasMR`].media + ag.porMetrica[`${l}.falhasEF`].media;
      linhas.push(`${l}: ${f.toFixed(2)} falhas/dia útil, ${ag.porMetrica[`${l}.minutosInterrupcao`].media.toFixed(1)} min/dia, disp ${(d.media * 100).toFixed(3)}%`);
      expect(f).toBeGreaterThan(0.1);
    }
    console.log(['parametros.json real (500 dias úteis):', ...linhas].join('\n'));
    const est = avaliaRedeAtual(rede, p, { tipoDia: 'util' }, { amostras: 50_000 });
    expect(est.dispOD.media).toBeGreaterThan(0.95);
    expect(avisosDoCenario(ctx, NENHUMA_POLITICA).length).toBeGreaterThan(0);
  }, LONGO);
});
