// Referência do motor antes da revisão de 2026-11 (spec 019, passo 1). Grava o resultado exato de dias
// simulados, de viagens com linhas novas e da avaliação de expansão com os parâmetros de hoje. Enquanto o
// motor for só reorganizado (fontes em lista, mesmos sub-fluxos), tudo aqui deve sair igual, bit a bit.
// Para gravar de novo: GRAVA_REFERENCIA=1 npx vitest run tests/motor/referencia_v1.test.ts
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { metricasDoDia } from '../../src/mc/rodadas';
import { preparaContexto } from '../../src/motor/contexto';
import { simulaDia } from '../../src/motor/dia';
import { avaliaCandidatas, candidataDesenhada, candidataLivre } from '../../src/motor/expansao';
import type { Politicas } from '../../src/motor/politicas';
import { NENHUMA_POLITICA } from '../../src/motor/politicas';
import type { Cenario, Parametros, TipoDia } from '../../src/motor/tipos';
import { avaliadoresViagem, rodaViagem } from '../../src/motor/viagem';
import { CAMINHO_PARAMETROS_REAIS, carregaFixture, carregaParametrosReais, carregaRede, temParametrosReais } from './apoio';

const ARQUIVO = resolve(__dirname, '../fixtures/referencia_v1.json');
const GRAVA = process.env.GRAVA_REFERENCIA === '1';
const LONGO = 600_000;

const TODAS: Politicas = { reservaFria: true, retiradaTrem: true, operacaoDegradada: true, retornoParcial: true, rotaAlternativa: true, tratamentoCausaComum: true };
const ATWATER = 'STATION_M134';
const UDEM = 'STATION_M536';
const ANGRIGNON = 'STATION_M118';
const SNOWDON = 'STATION_M236';

const sha = (x: unknown) => createHash('sha256').update(JSON.stringify(x)).digest('hex').slice(0, 24);

/** Último nível de cada fator do modelo de taxa: um dia com todas as condições fora da referência. */
function condicoesExtremas(p: Parametros): Record<string, string> {
  return Object.fromEntries(Object.entries(p.taxas.MR.multiplicadores).map(([f, niveis]) => [f, Object.keys(niveis).at(-1) as string]));
}

/** Hash do parametros.json real: os casos com ele só valem enquanto o arquivo for o mesmo da gravação. */
function shaReais(): string {
  return temParametrosReais ? createHash('sha256').update(readFileSync(CAMINHO_PARAMETROS_REAIS)).digest('hex').slice(0, 24) : '';
}

function conjuntos(): { nome: string; p: Parametros }[] {
  const c = [{ nome: 'fixture', p: carregaFixture() }];
  if (temParametrosReais) {
    const p = carregaParametrosReais();
    if (p.versao === 1) c.push({ nome: 'reais', p });
  }
  return c;
}

function calcula(): Record<string, string> {
  const rede = carregaRede();
  const saida: Record<string, string> = {};
  for (const { nome, p } of conjuntos()) {
    for (const tipoDia of ['util', 'sabado', 'domingo'] as TipoDia[]) {
      for (const [nc, cond] of [['ref', undefined], ['extremo', condicoesExtremas(p)]] as const) {
        const cenario: Cenario = { tipoDia, ...(cond ? { condicoes: cond } : {}) };
        const ctx = preparaContexto(rede, p, cenario);
        for (const [np, pol] of [['nenhuma', NENHUMA_POLITICA], ['todas', TODAS]] as const) {
          for (let s = 1; s <= 8; s++) {
            const r = simulaDia(ctx, pol, 1000 + s, { bloqueiosOD: true });
            saida[`dia|${nome}|${tipoDia}|${nc}|${np}|${s}`] = `${r.hash}|${sha({ m: metricasDoDia(r, rede.ids), rede: r.rede, b: r.bloqueiosOD })}`;
          }
        }
      }
    }
    const ctx = preparaContexto(rede, p, { tipoDia: 'util' });
    for (const [np, pol] of [['nenhuma', NENHUMA_POLITICA], ['todas', TODAS]] as const) {
      const variantes = [
        { id: 'lig', nome: 'ligação', linhas: [candidataDesenhada(rede, [ATWATER, UDEM], 0)] },
        { id: 'ang', nome: 'Angrignon–Snowdon', linhas: [candidataDesenhada(rede, [ANGRIGNON, SNOWDON], 1)] },
      ];
      const avs = avaliadoresViagem(ctx, ATWATER, UDEM, pol, variantes, np === 'todas');
      saida[`viagem|${nome}|${np}`] = sha(rodaViagem([0, 1, 2, 3, 4, 5], ctx, pol, 20261021, avs));
    }
    const ranking = avaliaCandidatas(rede, p, { tipoDia: 'util' }, [candidataLivre(rede, ANGRIGNON, SNOWDON), candidataLivre(rede, ATWATER, UDEM)], { amostras: 3000, semente: 7 });
    saida[`expansao|${nome}`] = sha(ranking);
  }
  return saida;
}

describe('referência do motor antes da revisão (spec 019, passo 1)', () => {
  it(
    'dias, viagens e expansão saem iguais à referência gravada',
    () => {
      const atual = calcula();
      if (GRAVA || !existsSync(ARQUIVO)) {
        writeFileSync(ARQUIVO, JSON.stringify({ parametros_reais_sha: shaReais(), ...atual }, null, 1) + '\n');
        return;
      }
      const ref = JSON.parse(readFileSync(ARQUIVO, 'utf8')) as Record<string, string>;
      // a fixture vale sempre; os parâmetros reais só se o arquivo for o mesmo da gravação (o pipeline pode tê-lo refeito)
      const reaisIguais = ref.parametros_reais_sha === shaReais();
      const chaves = Object.keys(ref).filter((k) => k !== 'parametros_reais_sha' && k in atual && (reaisIguais || !k.includes('|reais')));
      expect(chaves.filter((k) => k.includes('|fixture')).length).toBe(99);
      for (const k of chaves) expect(atual[k], k).toBe(ref[k]);
    },
    LONGO,
  );
});
