// Converte dados/derivados/simulador/candidatas.json (pipeline/candidatas.py, spec 014) nas candidatas do motor.
// Função pura: sem DOM nem MapLibre, usada pela página e pelo relatório de expansão.
//
// Regras (registradas em specs/014-expansao-rede/tasks.md):
// - Prolongamento: o caminho da candidata encosta num terminal de uma linha atual (Saint-Michel, Longueuil,
//   Côte-Vertu). A sequência começa nesse terminal, seja ele o primeiro ou o último da linha no rede.json.
// - Linha nova: o caminho encosta em duas estações atuais (anel da Laranja: Côte-Vertu e Montmorency) ou em
//   nenhuma ponta (Rosa). Estação fundida (`funde_com`) usa o id da estação atual. O anel herda as taxas
//   por km da Laranja; a Rosa, a média da rede.
// - Estação que depende de outra candidata (a Vertières da Rosa, `depende_de_candidata`) fica como estação
//   simples da própria candidata. No projeto conjunto (Rosa com a Azul, via `extras`), ela vira a mesma
//   estação da outra candidata e passa a ser correspondência.
// - km: linha reta × fator_tracado_candidata (o motor calcula; `kmTrechos` fica vazio).

import type { Candidata, EstacaoNova } from '../motor/expansao';
import type { Rede } from '../motor/rede';

export interface EstacaoCandidataJson {
  id: string;
  nome: string;
  lat: number;
  lon: number;
  fonte_coord: string;
  status: string;
  funde_com: { linha: string; id: string; nome: string; lat: number; lon: number } | null;
  depende_de_candidata?: string;
}

export interface TrechoCandidataJson {
  de: string;
  para: string;
  linha_existente?: string;
  km_reta: number;
}

export interface CandidataJson {
  id: string;
  tipo: string;
  proponente: string;
  ano: number;
  estacoes: EstacaoCandidataJson[];
  trechos: TrechoCandidataJson[];
  km_reta_total: number;
  fontes: string[];
  status: string[];
}

export interface CandidatasJson {
  fonte: string;
  aviso: string;
  candidatas: CandidataJson[];
}

/** Nome de exibição e id da linha nova de cada candidata conhecida. */
export const NOMES_CANDIDATAS: Record<string, string> = {
  azul_anjou: 'Prolongamento da Azul até Anjou',
  rosa_2017: 'Linha Rosa (proposta de 2017)',
  amarela_longueuil: 'Prolongamento da Amarela em Longueuil',
  laranja_bois_franc: 'Prolongamento da Laranja até Bois-Franc',
  laranja_anel_artm_2019: 'Anel da Laranja (ARTM, 2019)',
};
const LINHA_NOVA: Record<string, string> = { rosa_2017: 'rosa', laranja_anel_artm_2019: 'laranja_anel' };

/** Id do projeto conjunto Rosa + Azul. */
export const ID_ROSA_COM_AZUL = 'rosa_2017+azul_anjou';

function terminais(rede: Rede): Map<string, string> {
  const t = new Map<string, string>();
  for (const id of rede.ids) {
    const est = rede.linhas[id].estacoes;
    t.set(est[0].id, id);
    t.set(est[est.length - 1].id, id);
  }
  return t;
}

/** Caminho do traçado: ordena os nós pelos trechos (grafo em linha). */
function caminho(c: CandidataJson): string[] {
  const viz = new Map<string, string[]>();
  const liga = (a: string, b: string) => {
    if (!viz.has(a)) viz.set(a, []);
    viz.get(a)!.push(b);
  };
  for (const t of c.trechos) {
    liga(t.de, t.para);
    liga(t.para, t.de);
  }
  const pontas = [...viz.entries()].filter(([, v]) => v.length === 1).map(([k]) => k);
  if (pontas.length !== 2) throw new Error(`candidata ${c.id}: o traçado não é uma linha simples (${pontas.length} pontas)`);
  // começa pela ponta que é estação atual, se houver (prolongamento); senão pela primeira estação da candidata
  const ordemCandidata = new Map(c.estacoes.map((e, i) => [e.id, i]));
  pontas.sort((a, b) => (ordemCandidata.get(a) ?? -1) - (ordemCandidata.get(b) ?? -1));
  const seq = [pontas[0]];
  const visto = new Set(seq);
  for (;;) {
    const prox = (viz.get(seq[seq.length - 1]) ?? []).find((x) => !visto.has(x));
    if (!prox) break;
    seq.push(prox);
    visto.add(prox);
  }
  if (seq.length !== viz.size) throw new Error(`candidata ${c.id}: traçado com ciclo ou desconectado`);
  return seq;
}

function primeiraFonte(c: CandidataJson): string | undefined {
  return c.fontes.find((f) => f.startsWith('http'));
}

function statusDe(c: CandidataJson): Candidata['status'] {
  return c.status.length > 0 && c.status.every((s) => s === 'em obras (OSM)') ? 'em obras (OSM)' : 'hipótese de traçado';
}

/** Uma candidata do JSON no formato do motor. `substitui` troca ids de estação (projeto conjunto). */
function converte(c: CandidataJson, rede: Rede, substitui: Map<string, string> = new Map()): Candidata {
  const atuais = new Set(rede.estacoes.map((e) => e.id));
  const term = terminais(rede);
  let seq = caminho(c).map((id) => substitui.get(id) ?? id);
  const novas: EstacaoNova[] = c.estacoes
    .filter((e) => !e.funde_com && !substitui.has(e.id))
    .map((e) => ({ id: e.id, nome: e.nome, lat: e.lat, lon: e.lon }));
  const pontasAtuais = [seq[0], seq[seq.length - 1]].filter((id) => atuais.has(id));
  const base = {
    id: c.id,
    nome: NOMES_CANDIDATAS[c.id] ?? c.id,
    estacoesNovas: novas,
    fonte: primeiraFonte(c),
    status: statusDe(c),
  };
  // prolongamento: exatamente uma ponta numa estação atual, e essa estação é terminal de uma linha
  if (pontasAtuais.length === 1 && term.has(pontasAtuais[0])) {
    if (seq[0] !== pontasAtuais[0]) seq = [...seq].reverse();
    return { ...base, linha: term.get(seq[0])!, sequencia: seq };
  }
  // linha nova (anel com duas pontas na rede, ou linha que só encosta por estações fundidas)
  const linhasPontas = [...new Set(c.trechos.map((t) => t.linha_existente).filter((l): l is string => !!l))];
  return {
    ...base,
    linha: LINHA_NOVA[c.id] ?? c.id,
    sequencia: seq,
    herdaTaxasDe: pontasAtuais.length === 2 && linhasPontas.length === 1 ? linhasPontas[0] : undefined,
  };
}

/**
 * Todas as candidatas do JSON, mais o projeto conjunto Rosa + Azul (quando as duas existem):
 * a Vertières da Rosa vira a Vertières da Azul, que entra como linha extra do mesmo projeto.
 */
export function candidatasDoJson(json: CandidatasJson, rede: Rede): Candidata[] {
  const saida = json.candidatas.map((c) => converte(c, rede));
  for (const c of json.candidatas) {
    const dependentes = c.estacoes.filter((e) => e.depende_de_candidata);
    if (!dependentes.length) continue;
    const subst = new Map<string, string>();
    const extras: Candidata[] = [];
    for (const e of dependentes) {
      const outra = json.candidatas.find((o) => o.id !== c.id && o.estacoes.some((x) => x.nome === e.depende_de_candidata));
      if (!outra) continue;
      const alvo = outra.estacoes.find((x) => x.nome === e.depende_de_candidata)!;
      subst.set(e.id, alvo.id);
      if (!extras.some((x) => x.id === outra.id)) extras.push(converte(outra, rede));
    }
    if (!extras.length) continue;
    const conjunto = converte(c, rede, subst);
    const id = `${c.id}+${extras.map((x) => x.id).join('+')}`;
    saida.push({
      ...conjunto,
      id,
      nome: `${conjunto.nome} com ${extras.map((x) => x.nome.charAt(0).toLowerCase() + x.nome.slice(1)).join(' e ')}`,
      extras,
      status: 'hipótese de traçado',
    });
  }
  return saida;
}
