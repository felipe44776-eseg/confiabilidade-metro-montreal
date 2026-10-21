// Camada de frota (spec 008, reserva fria k-de-n): processo de longo prazo em tempo contínuo.
// n trens necessários e s de reserva. Cada trem em serviço sai para a oficina a λ × p_retirada por dia;
// a reserva parada não falha (reserva fria). Cada trem na oficina volta a 1 / reparo por dia,
// sem fila de oficina. Estado i = trens na oficina.

import type { Rng } from './prng';

export interface ParametrosFrota {
  n: number;
  s: number;
  lambdaDia: number; // saídas para a oficina por trem em serviço por dia (λ × p_retirada)
  reparoDias: number;
}

function taxaSaida(p: ParametrosFrota, i: number): number {
  return Math.min(p.n, p.n + p.s - i) * p.lambdaDia;
}

/** Distribuição estacionária do nascimento-morte: pi[i] = P(i trens na oficina). */
export function estacionariaFrota(p: ParametrosFrota): Float64Array {
  const total = p.n + p.s;
  const pi = new Float64Array(total + 1);
  pi[0] = 1;
  let soma = 1;
  for (let i = 0; i < total; i++) {
    pi[i + 1] = (pi[i] * taxaSaida(p, i)) / ((i + 1) / p.reparoDias);
    soma += pi[i + 1];
  }
  for (let i = 0; i <= total; i++) pi[i] /= soma;
  return pi;
}

/** P(frota completa) = P(pelo menos n disponíveis) = P(i <= s), pelo Markov. */
export function frotaCompletaMarkov(p: ParametrosFrota): number {
  const pi = estacionariaFrota(p);
  let acc = 0;
  for (let i = 0; i <= p.s; i++) acc += pi[i];
  return acc;
}

export interface ResultadoFrotaSimulada {
  pFrotaCompleta: number;
  trensNaOficinaMedio: number;
  saidas: number;
  dias: number;
}

/** Simulação do mesmo processo por eventos (Gillespie), para conferir com o Markov. */
export function simulaFrota(rng: Rng, p: ParametrosFrota, dias: number): ResultadoFrotaSimulada {
  let t = 0;
  let i = 0;
  let tempoCompleta = 0;
  let integral = 0;
  let saidas = 0;
  while (t < dias) {
    const sai = taxaSaida(p, i);
    const volta = i / p.reparoDias;
    const total = sai + volta;
    const dt = Math.min(rng.exponencial(total), dias - t);
    if (i <= p.s) tempoCompleta += dt;
    integral += i * dt;
    t += dt;
    if (t >= dias) break;
    if (rng.uniforme() * total < sai) {
      i++;
      saidas++;
    } else i--;
  }
  return { pFrotaCompleta: tempoCompleta / dias, trensNaOficinaMedio: integral / dias, saidas, dias };
}

/** Trens na oficina no início de um dia sorteado da operação estacionária. */
export function sorteiaOficina(rng: Rng, pi: Float64Array): number {
  const u = rng.uniforme();
  let acc = 0;
  for (let i = 0; i < pi.length; i++) {
    acc += pi[i];
    if (u < acc) return i;
  }
  return pi.length - 1;
}
