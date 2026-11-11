// Spec 014: método de estados validado contra a camada diária, candidatas e busca exaustiva.
import { describe, expect, it } from 'vitest';
import { agrega, nomesMetricas, rodaRodadas } from '../../src/mc/rodadas';
import { preparaContexto } from '../../src/motor/contexto';
import type { Acumulador, Candidata, Componente } from '../../src/motor/expansao';
import { avaliaCandidatas, avaliaModelo, avaliaRedeAtual, buscaExaustiva, candidataLivre, candidatasDaBusca } from '../../src/motor/expansao';
import type { Grafo, LinhaGrafo } from '../../src/motor/grafo';
import { chave, montaGrafo } from '../../src/motor/grafo';
import { NENHUMA_POLITICA } from '../../src/motor/politicas';
import { haversineKm } from '../../src/motor/rede';
import { carregaFixture, carregaRede } from './apoio';

const LONGO = 600_000;
const SEMENTE = 20261021;
const TOLERANCIA_PP = 0.001; // 0,1 ponto percentual

// Estações da rede atual (parent_station do GTFS)
const ANGRIGNON = 'STATION_M118';
const SNOWDON = 'STATION_M236';
const JEAN_TALON = 'STATION_M272';
const BERRI = 'STATION_M146';

describe('spec 014: validação do método de estados', () => {
  it('rede atual: disponibilidade por linha igual à da camada diária a até 0,1 ponto percentual', () => {
    const rede = carregaRede();
    const p = carregaFixture();
    const cenario = { tipoDia: 'util' as const };
    const ctx = preparaContexto(rede, p, cenario);
    const des = agrega(rodaRodadas(Array.from({ length: 3000 }, (_, i) => i), ctx, NENHUMA_POLITICA, SEMENTE), nomesMetricas(rede.ids), SEMENTE);
    const est = avaliaRedeAtual(rede, p, cenario, { rotaAlternativa: false, semente: SEMENTE });
    const linhas: string[] = [];
    for (const l of rede.ids) {
      const a = des.porMetrica[`${l}.disponibilidade`].media;
      const b = est.dispLinha[l].media;
      linhas.push(`${l}: diária ${(a * 100).toFixed(3)}% estados ${(b * 100).toFixed(3)}% (dif ${((b - a) * 100).toFixed(3)} pp)`);
      expect(Math.abs(a - b), l).toBeLessThan(TOLERANCIA_PP);
    }
    const odA = des.porMetrica['rede.dispOD'].media;
    const odB = est.dispOD.media;
    linhas.push(`OD sem rota alternativa: diária ${(odA * 100).toFixed(3)}% estados ${(odB * 100).toFixed(3)}%`);
    console.log(linhas.join('\n'));
    expect(Math.abs(odA - odB)).toBeLessThan(TOLERANCIA_PP);
  }, LONGO);
});

describe('spec 020 (D62): método de estados contra a enumeração exata', () => {
  it('grafo A–M–B com ligação nova A–B: indisponibilidade sem e com a ligação e ganho iguais aos 8 estados', () => {
    // Três estações, seis pares de peso 1. Linha L1: A–M (s1) e M–B (s2); ligação nova L2: A–B (s3).
    // Cada componente bloqueia o seu trecho nos dois sentidos, com probabilidade p.
    const est = (id: string) => ({ id, nome: id, lat: 0, lon: 0 });
    const L1: LinhaGrafo = { id: 'L1', estacoes: [est('A'), est('M'), est('B')], tempo0: [60, 60], tempo1: [60, 60], km: [1, 1], pontasRetorno: [0, 2] };
    const L2: LinhaGrafo = { id: 'L2', estacoes: [est('A'), est('B')], tempo0: [150], tempo1: [150], km: [2], pontasRetorno: [0, 1], candidata: true };
    const sem = montaGrafo([L1], 30);
    const com = montaGrafo([L1, L2], 30, { pesosDe: sem });
    const trecho = (g: Grafo, linha: string, t: number) => [0, 1].map((s) => g.chaveAresta.get(chave(linha, t, s as 0 | 1)) as number);
    const [p1, p2, p3] = [0.01, 0.01, 0.02];
    const daRede = (g: Grafo): Componente[] => [
      { p: p1, arestas: trecho(g, 'L1', 0), linhas: ['L1'], rotulo: 's1' },
      { p: p2, arestas: trecho(g, 'L1', 1), linhas: ['L1'], rotulo: 's2' },
    ];
    const n = 200_000;
    const accSem = avaliaModelo({ grafo: sem, componentes: daRede(sem), minutosJanela: 1, linhas: ['L1'] }, n, SEMENTE, true);
    const accCom = avaliaModelo({ grafo: com, componentes: daRede(com), minutosJanela: 1, linhas: ['L1'] }, n, SEMENTE, true, {
      comps: [{ p: p3, arestas: trecho(com, 'L2', 0), linhas: ['L2'], rotulo: 's3' }],
      semente: SEMENTE + 1,
    });
    // Enumeração (conta à mão): sem L2, um trecho fora isola M de uma ponta (4 dos 6 pares); os dois, tudo.
    // Com L2, um trecho só nunca corta nada; dois fora isolam uma estação (4 de 6); os três, tudo.
    const q = (p: number) => 1 - p;
    const uSem = (4 / 6) * (p1 * q(p2) + q(p1) * p2) + p1 * p2;
    const uCom = (4 / 6) * (p1 * p2 * q(p3) + p1 * q(p2) * p3 + q(p1) * p2 * p3) + p1 * p2 * p3;
    const estima = (lotes: number[]) => {
      const m = lotes.reduce((a, b) => a + b, 0) / lotes.length;
      const ep = Math.sqrt(lotes.reduce((a, b) => a + (b - m) ** 2, 0) / (lotes.length - 1) / lotes.length);
      return { m, ep };
    };
    const indisp = (acc: Acumulador) => [...acc.od].map((x) => 1 - x);
    const s = estima(indisp(accSem));
    const c = estima(indisp(accCom));
    const g = estima([...accCom.od].map((x, k) => x - accSem.od[k]));
    console.log(`sem: ${s.m.toFixed(6)} (exato ${uSem.toFixed(6)}) | com: ${c.m.toFixed(6)} (exato ${uCom.toFixed(6)}) | ganho ${g.m.toFixed(6)} ± ${g.ep.toFixed(6)} (exato ${(uSem - uCom).toFixed(6)})`);
    expect(Math.abs(s.m - uSem)).toBeLessThan(4 * s.ep);
    expect(Math.abs(c.m - uCom)).toBeLessThan(4 * Math.max(c.ep, 1e-6));
    expect(Math.abs(g.m - (uSem - uCom))).toBeLessThan(4 * g.ep);
  });
});

describe('spec 014: candidatas', () => {
  it('uma ligação livre que fecha um ciclo entre linhas tem ganho positivo, com IC95, rodadas, semente e hipóteses', () => {
    const rede = carregaRede();
    const r = avaliaCandidatas(rede, carregaFixture(), { tipoDia: 'util' }, [candidataLivre(rede, ANGRIGNON, SNOWDON), candidataLivre(rede, JEAN_TALON, BERRI)], { amostras: 100_000, semente: SEMENTE });
    expect(r).toHaveLength(2);
    for (const x of r) {
      expect(x.ganho.ic95[0]).toBeGreaterThan(0);
      expect(x.ganho.n).toBe(100_000);
      expect(x.semente).toBe(SEMENTE);
      expect(x.hipoteses.length).toBeGreaterThan(3);
      expect(x.km).toBeGreaterThan(0);
      expect(x.ganhoPorKm).toBeCloseTo(x.ganho.media / x.km, 12);
      expect(x.minutosParAnoEvitados.media).toBeGreaterThan(0);
      // dividir a causa comum com as linhas em que encosta não pode aumentar o ganho
      expect(x.ganhoComCausaComum.media).toBeLessThanOrEqual(x.ganho.media + 1e-12);
    }
    expect(r[0].ganho.media).toBeGreaterThanOrEqual(r[1].ganho.media);
  }, LONGO);

  it('o km da candidata livre é a linha reta × fator de traçado (hipótese), ou o km informado', () => {
    const rede = carregaRede();
    const a = rede.estacoes.find((e) => e.id === ANGRIGNON);
    const b = rede.estacoes.find((e) => e.id === SNOWDON);
    if (!a || !b) throw new Error('estação');
    const [semKm] = avaliaCandidatas(rede, carregaFixture(), { tipoDia: 'util' }, [candidataLivre(rede, ANGRIGNON, SNOWDON)], { amostras: 2000 });
    expect(semKm.km).toBeCloseTo(haversineKm(a.lat, a.lon, b.lat, b.lon) * 1.2, 9);
    const [comKm] = avaliaCandidatas(rede, carregaFixture(), { tipoDia: 'util' }, [candidataLivre(rede, ANGRIGNON, SNOWDON, 7.5)], { amostras: 2000 });
    expect(comKm.km).toBe(7.5);
  }, LONGO);

  it('prolongamento de linha para estação nova (traçado hipotético) não cria caminho alternativo para os pares de hoje', () => {
    const rede = carregaRede();
    const azul = rede.linhas.azul.estacoes;
    const fim = azul[azul.length - 1];
    const inicio = rede.linhas.verde.estacoes[0];
    const candidatas: Candidata[] = [
      {
        id: 'teste-azul',
        nome: 'Azul + 1 estação (teste)',
        linha: 'azul',
        sequencia: [fim.id, 'NOVA_1'],
        estacoesNovas: [{ id: 'NOVA_1', nome: 'Nova 1', lat: fim.lat + 0.005, lon: fim.lon + 0.01 }],
        status: 'hipótese de traçado',
        fonte: 'teste sintético',
      },
      {
        id: 'teste-verde-inicio',
        nome: 'Verde + 1 estação antes de Angrignon (teste)',
        linha: 'verde',
        sequencia: [inicio.id, 'NOVA_2'],
        estacoesNovas: [{ id: 'NOVA_2', nome: 'Nova 2', lat: inicio.lat - 0.005, lon: inicio.lon - 0.005 }],
        status: 'hipótese de traçado',
      },
    ];
    const r = avaliaCandidatas(rede, carregaFixture(), { tipoDia: 'util' }, candidatas, { amostras: 100_000, semente: SEMENTE });
    for (const x of r) {
      // sem retorno parcial, a falha no trecho novo para a linha inteira: o ganho não pode ser positivo
      expect(x.ganho.media, x.candidata.id).toBeLessThanOrEqual(x.ganho.meiaLargura);
      expect(x.hipoteses.some((h) => h.includes('hipótese de traçado'))).toBe(true);
    }
  }, LONGO);

  it('prolongamento que não sai de um terminal é recusado', () => {
    const rede = carregaRede();
    const meio = rede.linhas.laranja.estacoes[10];
    const c: Candidata = { id: 'x', nome: 'x', linha: 'laranja', sequencia: [meio.id, 'N'], estacoesNovas: [{ id: 'N', nome: 'N', lat: meio.lat, lon: meio.lon + 0.01 }], status: 'livre' };
    expect(() => avaliaCandidatas(rede, carregaFixture(), { tipoDia: 'util' }, [c], { amostras: 100 })).toThrow(/terminal/);
  });
});

describe('spec 014: busca exaustiva', () => {
  it('lista as ligações até a distância máxima, sem as que já existem, e ordena por ganho e por ganho por km', () => {
    const rede = carregaRede();
    const lista = candidatasDaBusca(rede, 1.5, 0.3);
    expect(lista.length).toBeGreaterThan(5);
    const vizinhas = new Set<string>();
    for (const id of rede.ids) {
      const est = rede.linhas[id].estacoes;
      for (let g = 0; g < est.length - 1; g++) vizinhas.add([est[g].id, est[g + 1].id].sort().join('|'));
    }
    for (const c of lista) {
      const [a, b] = c.sequencia;
      expect(vizinhas.has([a, b].sort().join('|'))).toBe(false);
      const ea = rede.estacoes.find((e) => e.id === a);
      const eb = rede.estacoes.find((e) => e.id === b);
      if (!ea || !eb) throw new Error('estação');
      const d = haversineKm(ea.lat, ea.lon, eb.lat, eb.lon);
      expect(d).toBeLessThanOrEqual(1.5);
      expect(d).toBeGreaterThanOrEqual(0.3);
    }
    const t0 = performance.now();
    const { porGanho, porKm } = buscaExaustiva(rede, carregaFixture(), { tipoDia: 'util' }, 1.5, { amostras: 50_000, semente: SEMENTE });
    console.log(`busca exaustiva: ${porGanho.length} candidatas em ${((performance.now() - t0) / 1000).toFixed(1)} s; melhor ${porGanho[0].candidata.nome} (+${(porGanho[0].ganho.media * 100).toFixed(4)} pp); melhor por km ${porKm[0].candidata.nome}`);
    expect(porGanho).toHaveLength(lista.length);
    for (let i = 1; i < porGanho.length; i++) expect(porGanho[i].ganho.media).toBeLessThanOrEqual(porGanho[i - 1].ganho.media);
    for (let i = 1; i < porKm.length; i++) expect(porKm[i].ganhoPorKm).toBeLessThanOrEqual(porKm[i - 1].ganhoPorKm);
  }, LONGO);
});
