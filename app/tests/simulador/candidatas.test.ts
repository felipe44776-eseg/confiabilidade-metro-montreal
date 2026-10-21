// Spec 014: conversão de candidatas.json para as candidatas do motor (função pura).
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { avaliaCandidatas } from '../../src/motor/expansao';
import type { CandidatasJson } from '../../src/simulador/candidatas';
import { ID_ROSA_COM_AZUL, candidatasDoJson } from '../../src/simulador/candidatas';
import { carregaFixture, carregaRede } from '../motor/apoio';

const json = JSON.parse(readFileSync(resolve(__dirname, '../../../dados/derivados/simulador/candidatas.json'), 'utf8')) as CandidatasJson;
const SAINT_MICHEL = 'STATION_M556';
const LONGUEUIL = 'STATION_M454';
const COTE_VERTU = 'STATION_M222';
const MONTMORENCY = 'STATION_M288';
const MONT_ROYAL = 'STATION_M264';
const PLACE_DES_ARTS = 'STATION_M142';
const VENDOME = 'STATION_M242';

describe('candidatasDoJson', () => {
  const rede = carregaRede();
  const cs = candidatasDoJson(json, rede);
  const por = new Map(cs.map((c) => [c.id, c]));

  it('converte as 5 candidatas e o projeto conjunto Rosa + Azul', () => {
    expect(cs.map((c) => c.id).sort()).toEqual(['amarela_longueuil', 'azul_anjou', 'laranja_anel_artm_2019', 'laranja_bois_franc', 'rosa_2017', ID_ROSA_COM_AZUL].sort());
    for (const c of cs) {
      expect(c.fonte, c.id).toMatch(/^https?:\/\//);
      expect(c.kmTrechos, c.id).toBeUndefined(); // linha reta × fator_tracado_candidata, calculado no motor
    }
    expect(por.get('azul_anjou')!.status).toBe('em obras (OSM)');
    expect(por.get('rosa_2017')!.status).toBe('hipótese de traçado');
  });

  it('prolongamentos começam no terminal certo de cada linha', () => {
    const azul = por.get('azul_anjou')!;
    expect(azul.linha).toBe('azul');
    expect(azul.sequencia[0]).toBe(SAINT_MICHEL);
    expect(rede.linhas.azul.estacoes.at(-1)!.id).toBe(SAINT_MICHEL); // terminal no fim da linha
    expect(azul.sequencia).toHaveLength(6);
    const amarela = por.get('amarela_longueuil')!;
    expect(amarela.linha).toBe('amarela');
    expect(amarela.sequencia[0]).toBe(LONGUEUIL);
    expect(rede.linhas.amarela.estacoes[0].id).toBe(LONGUEUIL); // terminal no começo da linha
    const bf = por.get('laranja_bois_franc')!;
    expect(bf.linha).toBe('laranja');
    expect(bf.sequencia).toEqual([COTE_VERTU, 'laranja_bois_franc:1', 'laranja_bois_franc:2']);
  });

  it('anel da Laranja é linha nova entre Côte-Vertu e Montmorency, com taxas da Laranja', () => {
    const anel = por.get('laranja_anel_artm_2019')!;
    expect(anel.linha).toBe('laranja_anel');
    expect(anel.herdaTaxasDe).toBe('laranja');
    expect([anel.sequencia[0], anel.sequencia.at(-1)].sort()).toEqual([COTE_VERTU, MONTMORENCY].sort());
    expect(anel.sequencia).toHaveLength(7);
  });

  it('Rosa: linha nova com as estações fundidas no id atual; Vertières simples sem a Azul', () => {
    const rosa = por.get('rosa_2017')!;
    expect(rosa.linha).toBe('rosa');
    expect(rosa.sequencia).toHaveLength(29);
    for (const id of [MONT_ROYAL, PLACE_DES_ARTS, VENDOME]) expect(rosa.sequencia).toContain(id);
    expect(rosa.sequencia).toContain('rosa_2017:7');
    expect(rosa.extras).toBeUndefined();
    expect(rosa.estacoesNovas).toHaveLength(26);
  });

  it('Rosa com a Azul: Vertières vira a da Azul (correspondência) e a Azul entra como extra', () => {
    const conj = por.get(ID_ROSA_COM_AZUL)!;
    expect(conj.sequencia).toContain('azul_anjou:1');
    expect(conj.sequencia).not.toContain('rosa_2017:7');
    expect(conj.extras?.map((e) => e.id)).toEqual(['azul_anjou']);
    expect(conj.estacoesNovas!.some((e) => e.id === 'azul_anjou:1')).toBe(false);
  });

  it('o motor aceita todas: ramais sem ganho de redundância, anel e Rosa com ganho', () => {
    const p = carregaFixture();
    const r = avaliaCandidatas(rede, p, { tipoDia: 'util' }, cs, { amostras: 20_000, semente: 20261021 });
    const g = new Map(r.map((x) => [x.candidata.id, x]));
    for (const ramal of ['azul_anjou', 'amarela_longueuil', 'laranja_bois_franc']) {
      // um ramal não cria caminho alternativo para os pares de hoje e ainda soma trechos que podem falhar:
      // o ganho de redundância não passa de zero (limite superior do IC 95% até o ruído)
      expect(g.get(ramal)!.ganho.ic95[1], ramal).toBeLessThan(1e-4);
    }
    expect(g.get('laranja_anel_artm_2019')!.ganho.media).toBeGreaterThan(0);
    expect(g.get('rosa_2017')!.ganho.media).toBeGreaterThan(0);
    expect(g.get('laranja_anel_artm_2019')!.hipoteses.join(' ')).toContain('herdadas da linha laranja');
  }, 300_000);
});
