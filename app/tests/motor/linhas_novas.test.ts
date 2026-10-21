// Spec 016: linhas novas numa viagem, no mesmo dia simulado da rede atual.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { preparaContexto } from '../../src/motor/contexto';
import type { FalhaInjetada } from '../../src/motor/dia';
import { simulaDia } from '../../src/motor/dia';
import { candidataDesenhada } from '../../src/motor/expansao';
import type { FalhaNovaInjetada } from '../../src/motor/linhas_novas';
import { bloqueiosDaVariante, cortesDe, partesDe, preparaVariante } from '../../src/motor/linhas_novas';
import type { Politicas } from '../../src/motor/politicas';
import { NENHUMA_POLITICA, soPolitica } from '../../src/motor/politicas';
import { sementeDaRodada } from '../../src/motor/prng';
import type { AvaliadorViagem } from '../../src/motor/viagem';
import { conexoesDe, mesclaConexoes, metricasVariantesDia, metricasViagemDia, nomesVariantes, nomesViagem, preparaViagem, rodaViagem, simulaDiaViagem } from '../../src/motor/viagem';
import type { CandidatasJson } from '../../src/simulador/candidatas';
import { candidatasDoJson } from '../../src/simulador/candidatas';
import { carregaFixture, carregaRede } from './apoio';

const LONGO = 300_000;
const ATWATER = 'STATION_M134'; // Verde
const UDEM = 'STATION_M536'; // Université-de-Montréal, Azul
const SNOWDON = 'STATION_M236';
const SAINT_MICHEL = 'STATION_M556';
const OITO = 8 * 3600;
const MEIA_HORA = 1800;

const rede = carregaRede();
const p = carregaFixture();
const json = JSON.parse(readFileSync(resolve(__dirname, '../../../dados/derivados/simulador/candidatas.json'), 'utf8')) as CandidatasJson;
const oficiais = candidatasDoJson(json, rede);
const ctxSemFalhas = () => preparaContexto(rede, p, { tipoDia: 'util', semFalhas: true });
const ligacao = () => candidataDesenhada(rede, [ATWATER, UDEM], 0);

function porNome(av: AvaliadorViagem, valores: number[]): Record<string, number> {
  return Object.fromEntries(nomesViagem(av).map((n, i) => [n, valores[i]]));
}

function variante(ctx: ReturnType<typeof ctxSemFalhas>, pol: Politicas, injetadas: FalhaNovaInjetada[] = [], cc = false, cands = [ligacao()]) {
  return preparaVariante(ctx, cands, { politicas: pol, causaComumCompartilhada: cc, injetadas });
}

describe('spec 016: caminho com a linha nova', () => {
  it('a ligação Atwater–Université-de-Montréal vira o caminho de sempre e encurta a viagem', () => {
    const ctx = ctxSemFalhas();
    const base = preparaViagem(ctx, ATWATER, UDEM, false)!;
    const av = preparaViagem(ctx, ATWATER, UDEM, false, variante(ctx, NENHUMA_POLITICA))!;
    expect(base.rota.trechos.map((t) => t.linha)).not.toContain('desenhada1');
    expect(av.rota.trechos.map((t) => t.linha)).toEqual(['desenhada1']);
    expect(av.rota.minutos).toBeLessThan(base.rota.minutos);
    expect(av.tempoSemFalhasMin).toBeLessThan(base.tempoSemFalhasMin);
    // todas as saídas da rede atual chegam também com a linha nova
    expect(av.saidas.length).toBeGreaterThanOrEqual(base.saidas.length * 0.95);
  });

  it('sem falhas: atraso zero e disponibilidade 1 também com a linha nova', () => {
    const ctx = ctxSemFalhas();
    const v = variante(ctx, NENHUMA_POLITICA);
    for (const alt of [false, true]) {
      const av = preparaViagem(ctx, ATWATER, UDEM, alt, v)!;
      const r = simulaDia(ctx, alt ? soPolitica('rotaAlternativa') : NENHUMA_POLITICA, 1, { registrar: false, trajetorias: true, bloqueiosOD: true });
      const m = porNome(av, metricasViagemDia(ctx, av, r));
      expect(m.disp).toBe(1);
      expect(m.atrasoMedioMin).toBe(0);
      expect(m.naoChega).toBe(0);
      expect(m.falhasLinhaNova).toBe(0);
      expect(m.tempoMedioMin).toBeCloseTo(av.tempoSemFalhasMin, 9);
    }
  });
});

describe('spec 016: falhas da linha nova', () => {
  const injetada: FalhaNovaInjetada = { t: OITO, duracaoS: MEIA_HORA, linha: 'desenhada1', trecho: 0, sentidos: [0, 1] };

  it('sem rota alternativa, a falha de 30 min na linha nova tira 30 min do caminho; a rede atual não muda', () => {
    const ctx = ctxSemFalhas();
    const base = preparaViagem(ctx, ATWATER, UDEM, false)!;
    const av = preparaViagem(ctx, ATWATER, UDEM, false, variante(ctx, NENHUMA_POLITICA, [injetada]))!;
    const r = simulaDia(ctx, NENHUMA_POLITICA, 1, { registrar: false, trajetorias: true, bloqueiosOD: true });
    const vals = metricasVariantesDia(ctx, [base, av], r);
    const m = Object.fromEntries(nomesVariantes([base, av]).map((n, i) => [n, vals[i]]));
    const T = av.janela[1] - av.janela[0];
    expect(m.disp).toBe(1);
    expect(m['v1.minSemCaminho']).toBeCloseTo(30, 9);
    expect(m['v1.disp']).toBeCloseTo(1 - MEIA_HORA / T, 12);
    expect(m['d1.disp']).toBeCloseTo(-MEIA_HORA / T, 12);
    // quem sai durante a falha espera a linha nova voltar
    expect(m['v1.atraso5']).toBeGreaterThan(0);
    expect(m['v1.falhasLinhaNova']).toBe(1);
  });

  it('com rota alternativa, a rede atual contorna a falha da linha nova (paralelo)', () => {
    const ctx = ctxSemFalhas();
    const pol = soPolitica('rotaAlternativa');
    const av = preparaViagem(ctx, ATWATER, UDEM, true, variante(ctx, pol, [injetada]))!;
    const r = simulaDia(ctx, pol, 1, { registrar: false, trajetorias: true, bloqueiosOD: true });
    const m = porNome(av, metricasViagemDia(ctx, av, r));
    expect(m.disp).toBe(1);
    expect(m.naoChega).toBe(0);
    // o atraso de quem sai durante a falha é, no máximo, o caminho antigo menos o novo (mais esperas)
    expect(m.atrasoMedioMin).toBeGreaterThan(0);
    expect(m.atraso60).toBe(0);
  });

  it('causa comum compartilhada: o evento nas linhas em que a linha nova encosta também a para', () => {
    const ctx = ctxSemFalhas();
    const pol = soPolitica('rotaAlternativa');
    const inj: FalhaInjetada[] = [{ tipo: 'CC', t: OITO, duracaoS: MEIA_HORA, par: 'verde-laranja' }];
    const r = simulaDia(ctx, pol, 1, { injetadas: inj, registrar: false, trajetorias: true, bloqueiosOD: true });
    const independente = preparaViagem(ctx, ATWATER, UDEM, true, variante(ctx, pol, [], false))!;
    const junto = preparaViagem(ctx, ATWATER, UDEM, true, variante(ctx, pol, [], true))!;
    const mi = porNome(independente, metricasViagemDia(ctx, independente, r));
    const mj = porNome(junto, metricasViagemDia(ctx, junto, r));
    // Atwater só tem a Verde e a linha nova: independente, a linha nova segue; junto, a viagem fica 30 min sem caminho
    expect(mi.disp).toBe(1);
    expect(mj.minSemCaminho).toBeCloseTo(30, 9);
  });
});

describe('spec 016: prolongamento', () => {
  const anjou = () => oficiais.find((c) => c.id === 'azul_anjou')!;

  it('as viagens do horário que chegam a Saint-Michel seguem pelo trecho novo', () => {
    const ctx = ctxSemFalhas();
    const v = variante(ctx, NENHUMA_POLITICA, [], false, [anjou()]);
    const n = rede.linhas.azul.n;
    const [s0] = ctx.horario.porLinha.azul;
    const chegadas = s0.viagens.filter((x) => x.fim === n - 1).map((x) => x.chegada[x.fim - x.inicio]);
    const jE = (v.deslocamento.azul ?? 0) + n - 1;
    const aresta0 = v.g.chaveAresta.get(`azul|${jE}|0`)!;
    const partidas = v.conexoes.dep.filter((_, k) => v.conexoes.aresta[k] === aresta0);
    expect(partidas.length).toBe(chegadas.length);
    expect([...partidas].sort((a, b) => a - b)).toEqual([...chegadas].sort((a, b) => a - b));
  });

  it('sem retorno parcial, a falha no trecho novo para a Azul inteira; com retorno parcial, não alcança Snowdon–Saint-Michel', () => {
    for (const parcial of [false, true]) {
      const ctx = ctxSemFalhas();
      const pol: Politicas = { ...NENHUMA_POLITICA, retornoParcial: parcial };
      const n = rede.linhas.azul.n;
      const inj: FalhaNovaInjetada = { t: OITO, duracaoS: MEIA_HORA, linha: 'azul', trecho: n, sentidos: [0, 1] };
      const v = variante(ctx, pol, [inj], false, [anjou()]);
      const av = preparaViagem(ctx, SNOWDON, SAINT_MICHEL, false, v)!;
      expect(av.rota.trechos.map((t) => t.linha)).toEqual(['azul']);
      const r = simulaDia(ctx, pol, 1, { registrar: false, trajetorias: true, bloqueiosOD: true });
      const m = porNome(av, metricasViagemDia(ctx, av, r));
      if (parcial) expect(m.disp).toBe(1);
      else {
        expect(m.minSemCaminho).toBeCloseTo(30, 9);
        expect(m.atraso5).toBeGreaterThan(0);
      }
    }
  });
});

describe('spec 016: mesmo dia, comparação pareada', () => {
  it(
    'a rede atual mede igual sozinha e junto com as variantes; a rodada é determinística',
    () => {
      const ctx = preparaContexto(rede, p, { tipoDia: 'util' });
      for (const pol of [NENHUMA_POLITICA, soPolitica('rotaAlternativa')]) {
        const base = preparaViagem(ctx, ATWATER, UDEM, pol.rotaAlternativa)!;
        const av = preparaViagem(ctx, ATWATER, UDEM, pol.rotaAlternativa, variante(ctx, pol))!;
        const nb = nomesViagem(base).length;
        for (let i = 0; i < 4; i++) {
          const r = simulaDiaViagem(ctx, pol, sementeDaRodada(20261021, i));
          const so = metricasViagemDia(ctx, base, r);
          const junto = metricasVariantesDia(ctx, [base, av], r);
          expect(junto.slice(0, nb)).toEqual(so);
          expect(junto.length).toBe(nomesVariantes([base, av]).length);
        }
        const a = rodaViagem([0, 1, 2], ctx, pol, 20261021, [base, av]);
        const b = rodaViagem([0, 1, 2], ctx, pol, 20261021, [base, av]);
        expect(a).toEqual(b);
      }
    },
    LONGO,
  );

  it(
    'linha nova independente com rota alternativa nunca tira caminho da viagem',
    () => {
      const ctx = preparaContexto(rede, p, { tipoDia: 'util' });
      const pol = soPolitica('rotaAlternativa');
      const base = preparaViagem(ctx, ATWATER, UDEM, true)!;
      const av = preparaViagem(ctx, ATWATER, UDEM, true, variante(ctx, pol))!;
      const nomes = nomesVariantes([base, av]);
      const iD = nomes.indexOf('d1.disp');
      let falhasNovas = 0;
      for (const rd of rodaViagem(Array.from({ length: 40 }, (_, i) => i), ctx, pol, 20261021, [base, av])) {
        expect(rd.valores[iD]).toBeGreaterThanOrEqual(-1e-12);
        falhasNovas += rd.valores[nomes.indexOf('v1.falhasLinhaNova')];
      }
      // a linha nova falha (taxa por km da média da rede): não é uma linha perfeita
      expect(falhasNovas).toBeGreaterThan(0);
    },
    LONGO,
  );
});

describe('spec 016: conexões intercaladas', () => {
  it(
    'intercalar os trens novos nas conexões da rede atual dá o mesmo que montar tudo no grafo da variante',
    () => {
      const ctx = preparaContexto(rede, p, { tipoDia: 'util' });
      const pol = soPolitica('rotaAlternativa');
      const boisFranc = oficiais.find((c) => c.id === 'laranja_bois_franc')!;
      // prolongamento pelo começo (Côte-Vertu é a primeira estação da Laranja) e uma linha nova juntos
      const v = variante(ctx, pol, [], true, [boisFranc, ligacao()]);
      expect(v.deslocamento.laranja).toBeGreaterThan(0);
      for (let i = 0; i < 3; i++) {
        const r = simulaDiaViagem(ctx, pol, sementeDaRodada(20261021, i));
        const b = bloqueiosDaVariante(ctx, v, r);
        const extra = { deslocamento: v.deslocamento, novas: v.conexoes, cortesAtuais: cortesDe(b.daNova), cortesNovas: cortesDe(b.todos) };
        const cheia = conexoesDe(v.g, rede, r.trajetorias ?? {}, null, extra);
        const mesclada = mesclaConexoes(conexoesDe(ctx.grafo, rede, r.trajetorias ?? {}, null), v, extra);
        expect(mesclada.nViagens).toBe(cheia.nViagens);
        for (const k of ['dep', 'arr', 'de', 'para', 'viagem', 'aresta'] as const) expect(Array.from(mesclada[k]), k).toEqual(Array.from(cheia[k]));
      }
    },
    LONGO,
  );
});

describe('spec 016: linhas incompatíveis', () => {
  it('duas versões da mesma linha não são construídas juntas', () => {
    const ctx = ctxSemFalhas();
    const rosa = oficiais.find((c) => c.id === 'rosa_2017')!;
    const rosaAzul = oficiais.find((c) => c.extras?.length)!;
    expect(() => partesDe(ctx, [rosa, rosaAzul])).toThrow(/mesma linha/);
    // o prolongamento repetido (sozinho e dentro do projeto conjunto) entra uma vez
    expect(partesDe(ctx, [rosaAzul, oficiais.find((c) => c.id === 'azul_anjou')!]).map((x) => x.id).sort()).toEqual(['azul_anjou', rosaAzul.id].sort());
  });
});
