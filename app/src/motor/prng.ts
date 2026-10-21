// Gerador pseudoaleatório xoshiro128** com semente, um fluxo independente por fonte de sorteio.
// A mesma semente da rodada gera sempre os mesmos fluxos, em qualquer máquina e com qualquer
// número de workers: é o que torna o registro reprodutível e as comparações de políticas pareadas
// (números aleatórios comuns).

/** Mistura de 32 bits (finalizador do MurmurHash3). */
function fmix32(h: number): number {
  h ^= h >>> 16;
  h = Math.imul(h, 0x85ebca6b);
  h ^= h >>> 13;
  h = Math.imul(h, 0xc2b2ae35);
  h ^= h >>> 16;
  return h >>> 0;
}

/** Combina inteiros numa semente de 32 bits. Ordem importa. */
export function misturaSemente(...partes: number[]): number {
  let h = 0x9e3779b9;
  for (const p of partes) {
    h = fmix32((h ^ fmix32((p | 0) >>> 0)) + 0x7f4a7c15);
  }
  return h >>> 0;
}

/** SplitMix32: espalha uma semente nos quatro registradores do xoshiro. */
function splitmix32(estado: { s: number }): number {
  estado.s = (estado.s + 0x9e3779b9) >>> 0;
  let z = estado.s;
  z = Math.imul(z ^ (z >>> 16), 0x85ebca6b);
  z = Math.imul(z ^ (z >>> 13), 0xc2b2ae35);
  return (z ^ (z >>> 16)) >>> 0;
}

const DOIS_32 = 4294967296;

export class Rng {
  private a: number;
  private b: number;
  private c: number;
  private d: number;
  /** Quantos números já saíram (vai para o registro como origem do sorteio). */
  sorteios = 0;

  constructor(semente: number) {
    const e = { s: semente >>> 0 };
    this.a = splitmix32(e);
    this.b = splitmix32(e);
    this.c = splitmix32(e);
    this.d = splitmix32(e);
    if ((this.a | this.b | this.c | this.d) === 0) this.a = 1;
  }

  /** Inteiro de 32 bits sem sinal (xoshiro128**). */
  proximo(): number {
    const r = Math.imul(rotl(Math.imul(this.b, 5), 7), 9) >>> 0;
    const t = this.b << 9;
    this.c ^= this.a;
    this.d ^= this.b;
    this.b ^= this.c;
    this.a ^= this.d;
    this.c ^= t;
    this.d = rotl(this.d, 11);
    this.sorteios++;
    return r;
  }

  /** Uniforme em [0, 1). */
  uniforme(): number {
    return this.proximo() / DOIS_32;
  }

  /** Uniforme em (0, 1), para logaritmos. */
  uniformeAberto(): number {
    return (this.proximo() + 0.5) / DOIS_32;
  }

  /** Inteiro em [0, n). */
  inteiro(n: number): number {
    return Math.floor(this.uniforme() * n);
  }

  normal(): number {
    // Box-Muller sem guardar o segundo valor: cada chamada gasta dois sorteios, sempre.
    const u = this.uniformeAberto();
    const v = this.uniforme();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }

  exponencial(taxa: number): number {
    return -Math.log(this.uniformeAberto()) / taxa;
  }

  weibull(forma: number, escala: number): number {
    return escala * Math.pow(-Math.log(this.uniformeAberto()), 1 / forma);
  }

  /** Gama(forma, 1) por Marsaglia e Tsang; forma < 1 pelo truque de potência. */
  gama(forma: number): number {
    if (forma < 1) {
      const u = this.uniformeAberto();
      return this.gama(forma + 1) * Math.pow(u, 1 / forma);
    }
    const d = forma - 1 / 3;
    const c = 1 / Math.sqrt(9 * d);
    for (;;) {
      let x: number;
      let v: number;
      do {
        x = this.normal();
        v = 1 + c * x;
      } while (v <= 0);
      v = v * v * v;
      const u = this.uniformeAberto();
      if (u < 1 - 0.0331 * x * x * x * x) return d * v;
      if (Math.log(u) < 0.5 * x * x + d * (1 - v + Math.log(v))) return d * v;
    }
  }
}

function rotl(x: number, k: number): number {
  return ((x << k) | (x >>> (32 - k))) >>> 0;
}

/** Fontes de sorteio. Cada uma vira um fluxo próprio; `sub` separa linhas e pares. */
export const FLUXOS = {
  falhas_mr: 1,
  falhas_ef: 2,
  causa_comum: 3,
  duracoes: 4,
  escolha: 5,
  frota: 6,
  politicas: 7,
  estados: 8,
  linhas_novas: 9, // falhas das linhas novas na viagem (spec 016)
} as const;
export type Fluxo = keyof typeof FLUXOS;

/** Semente da rodada i: depende só da semente-base e do índice (spec 009). */
export function sementeDaRodada(sementeBase: number, indice: number): number {
  return misturaSemente(sementeBase, indice, 0x5eed);
}

export function criaFluxo(sementeRodada: number, fluxo: Fluxo, sub = 0): Rng {
  return new Rng(misturaSemente(sementeRodada, FLUXOS[fluxo], sub));
}

/** Gama completa por Lanczos (g = 7), para a média da Weibull. */
export function gamaFuncao(z: number): number {
  const g = 7;
  const c = [
    0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059,
    12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7,
  ];
  if (z < 0.5) return Math.PI / (Math.sin(Math.PI * z) * gamaFuncao(1 - z));
  z -= 1;
  let x = c[0];
  for (let i = 1; i < g + 2; i++) x += c[i] / (z + i);
  const t = z + g + 0.5;
  return Math.sqrt(2 * Math.PI) * Math.pow(t, z + 0.5) * Math.exp(-t) * x;
}
