// Carrega a rede real (dados/derivados/simulador/rede.json) e a fixture de parâmetros para os testes.
// Se o pipeline já gerou dados/derivados/simulador/parametros.json, os testes marcados com
// `comParametrosReais` também rodam com ele.

import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { montaRede } from '../../src/motor/rede';
import type { Rede } from '../../src/motor/rede';
import type { Parametros, RedeJson } from '../../src/motor/tipos';

const RAIZ = resolve(__dirname, '../../..');
export const CAMINHO_REDE = resolve(RAIZ, 'dados/derivados/simulador/rede.json');
export const CAMINHO_PARAMETROS_REAIS = resolve(RAIZ, 'dados/derivados/simulador/parametros.json');
export const CAMINHO_FIXTURE = resolve(__dirname, '../fixtures/parametros_teste.json');

let redeJson: RedeJson | null = null;
let rede: Rede | null = null;

export function carregaRedeJson(): RedeJson {
  redeJson ??= JSON.parse(readFileSync(CAMINHO_REDE, 'utf8')) as RedeJson;
  return redeJson;
}

export function carregaRede(): Rede {
  rede ??= montaRede(carregaRedeJson());
  return rede;
}

export function carregaFixture(): Parametros {
  return JSON.parse(readFileSync(CAMINHO_FIXTURE, 'utf8')) as Parametros;
}

export const temParametrosReais = existsSync(CAMINHO_PARAMETROS_REAIS);

export function carregaParametrosReais(): Parametros {
  return JSON.parse(readFileSync(CAMINHO_PARAMETROS_REAIS, 'utf8')) as Parametros;
}

/** Mediana de uma lista de números. */
export function mediana(xs: number[]): number {
  const o = [...xs].sort((a, b) => a - b);
  return o.length ? o[Math.floor(o.length / 2)] : NaN;
}
