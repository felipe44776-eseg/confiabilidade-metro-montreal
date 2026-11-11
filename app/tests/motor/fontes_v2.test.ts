// Spec 019, passo 2: contrato v2 com várias fontes por linha.
import { describe, expect, it } from 'vitest';
import { familiaNaLinha, preparaContexto } from '../../src/motor/contexto';
import { simulaDia } from '../../src/motor/dia';
import { NENHUMA_POLITICA } from '../../src/motor/politicas';
import type { Causa, FonteParam, Parametros } from '../../src/motor/tipos';
import { carregaFixture, carregaRede } from './apoio';

const LINHAS = ['verde', 'laranja', 'amarela', 'azul'];

/** Contrato v2 a partir da fixture v1: cada família vira fontes que dividem a taxa-base nas frações dadas. */
function v2(p: Parametros, divisao: Record<Causa, Record<string, number>>): Parametros {
  const fontes: FonteParam[] = [];
  for (const causa of ['MR', 'EF'] as Causa[]) {
    const t = p.taxas[causa];
    for (const [id, fracao] of Object.entries(divisao[causa])) {
      const linhas: FonteParam['linhas'] = {};
      for (const l of LINHAS) {
        linhas[l] = {
          base_por_trem_hora: { ...t.base_por_trem_hora[l], valor: t.base_por_trem_hora[l].valor * fracao },
          renovacao: p.renovacao[`${l}|${causa}`],
          ttr: p.ttr[`${l}|${causa}`],
          ...(causa === 'EF' ? { locais: p.locais_ef[l], locais_sem_posicao: p.locais_ef_sem_posicao?.[l] ?? 0 } : {}),
        };
      }
      fontes.push({ id, familia: causa, rotulo: id, status_rotulo: 'teste', modelo: 'teste', n_falhas: 0, alpha: t.alpha, referencia: t.referencia, multiplicadores: t.multiplicadores, linhas });
    }
  }
  return { ...p, versao: 2, fontes };
}

const DIVISAO = { MR: { mr73: 0.7, mpm10: 0.3 }, EF: { via: 0.5, controle: 0.3, energia: 0.2 } };

describe('spec 019: fontes do contrato v2', () => {
  it('cada linha tem as fontes do arquivo, com a família e os locais próprios', () => {
    const ctx = preparaContexto(carregaRede(), v2(carregaFixture(), DIVISAO), { tipoDia: 'util' });
    expect(ctx.fontes.length).toBe(LINHAS.length * 5);
    const verde = ctx.fontes.filter((f) => f.linha === 'verde');
    expect(verde.map((f) => f.id)).toEqual(['mr73', 'mpm10', 'via', 'controle', 'energia']);
    expect(verde.filter((f) => f.causa === 'EF').every((f) => f.locais !== undefined)).toBe(true);
    expect(new Set(ctx.fontes.map((f) => `${f.linha}|${f.subInstantes}`)).size).toBe(ctx.fontes.length);
  });

  it('a soma das fontes de cada família reproduz a taxa da família do v1', () => {
    const rede = carregaRede();
    const p = carregaFixture();
    const c1 = preparaContexto(rede, p, { tipoDia: 'util' });
    const c2 = preparaContexto(rede, v2(p, DIVISAO), { tipoDia: 'util' });
    for (const l of LINHAS)
      for (const causa of ['MR', 'EF'] as Causa[]) {
        const a = familiaNaLinha(c1, l, causa)!.acum;
        const b = familiaNaLinha(c2, l, causa)!.acum;
        expect(b[b.length - 1]).toBeCloseTo(a[a.length - 1], 9);
      }
  });

  it('acrescentar uma fonte não muda os instantes das outras (sub-fluxo pelo nome da linha e da fonte)', () => {
    const rede = carregaRede();
    const p = carregaFixture();
    const sem = preparaContexto(rede, v2(p, { MR: { mr73: 0.7 }, EF: { via: 0.5 } }), { tipoDia: 'util' });
    const com = preparaContexto(rede, v2(p, { MR: { mr73: 0.7, mpm10: 0.3 }, EF: { via: 0.5, energia: 0.2 } }), { tipoDia: 'util' });
    for (let s = 1; s <= 5; s++) {
      const ra = simulaDia(sem, NENHUMA_POLITICA, s);
      const rb = simulaDia(com, NENHUMA_POLITICA, s);
      for (const l of LINHAS) {
        expect(rb.porLinha[l].falhasPorFonte.mr73 ?? 0).toBe(ra.porLinha[l].falhasPorFonte.mr73 ?? 0);
        expect(rb.porLinha[l].falhasPorFonte.via ?? 0).toBe(ra.porLinha[l].falhasPorFonte.via ?? 0);
      }
    }
  });

  it('falhas e minutos por fonte e por classe de gravidade somam os da família', () => {
    const ctx = preparaContexto(carregaRede(), v2(carregaFixture(), DIVISAO), { tipoDia: 'util' });
    for (let s = 1; s <= 10; s++) {
      const r = simulaDia(ctx, NENHUMA_POLITICA, s);
      for (const l of LINHAS) {
        const m = r.porLinha[l];
        const f = m.falhasPorFonte;
        expect((f.mr73 ?? 0) + (f.mpm10 ?? 0)).toBe(m.falhas.MR);
        expect((f.via ?? 0) + (f.controle ?? 0) + (f.energia ?? 0)).toBe(m.falhas.EF);
        expect(Object.values(m.falhasPorClasse).reduce((a, b) => a + b, 0)).toBe(m.falhas.MR + m.falhas.EF + m.falhas.CC);
      }
    }
  });

  it('fonte sem duração ou sem renovação é erro, não valor padrão', () => {
    const p = v2(carregaFixture(), DIVISAO);
    const semTtr = structuredClone(p);
    delete (semTtr.fontes![0].linhas.verde as { ttr?: unknown }).ttr;
    expect(() => preparaContexto(carregaRede(), semTtr, { tipoDia: 'util' })).toThrow(/duração/);
    const semRenov = structuredClone(p);
    delete (semRenov.fontes![0].linhas.verde as { renovacao?: unknown }).renovacao;
    expect(() => preparaContexto(carregaRede(), semRenov, { tipoDia: 'util' })).toThrow(/renovação/);
  });
});
