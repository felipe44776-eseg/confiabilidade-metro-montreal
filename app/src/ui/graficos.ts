// Gráfico de barras horizontais com intervalo de 95%, em SVG próprio (sem biblioteca).
// Uma escala só; a cor identifica a linha do metrô (identidade, ordem fixa); textos na cor do texto;
// dica ao passar o mouse ou focar; tabela com os mesmos números logo abaixo.

export interface ItemBarra {
  rotulo: string;
  valor: number;
  ic?: [number, number];
  cor: string;
  dica?: string;
}

export interface OpcoesBarras {
  titulo: string;
  formata: (x: number) => string;
  /** Rótulo do eixo (unidade). */
  eixo: string;
  /** Texto da coluna do valor na tabela. */
  colunaValor?: string;
}

const SVGNS = 'http://www.w3.org/2000/svg';
const ALTURA_LINHA = 30;
const ESPESSURA = 10;
const MARGEM_ROTULO = 128;
const MARGEM_DIREITA = 92;
const LARGURA = 640;

function svg<K extends keyof SVGElementTagNameMap>(tag: K, atributos: Record<string, string | number>): SVGElementTagNameMap[K] {
  const e = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(atributos)) e.setAttribute(k, String(v));
  return e;
}

/** Ticks "redondos" entre a e b. */
export function ticks(a: number, b: number, n = 4): number[] {
  if (!(b > a)) return [a];
  const passoBruto = (b - a) / n;
  const pot = 10 ** Math.floor(Math.log10(passoBruto));
  const passo = [1, 2, 2.5, 5, 10].map((m) => m * pot).find((p) => p >= passoBruto) ?? passoBruto;
  const saida: number[] = [];
  for (let v = Math.ceil(a / passo) * passo; v <= b + passo * 1e-9; v += passo) saida.push(Math.abs(v) < passo * 1e-9 ? 0 : v);
  return saida;
}

/** Barra com a ponta do dado arredondada (4 px) e a base reta, ancorada no zero. */
function caminhoBarra(x0: number, x1: number, y: number, h: number): string {
  const r = Math.min(4, Math.abs(x1 - x0) / 2, h / 2);
  if (x1 >= x0) return `M${x0},${y}H${x1 - r}A${r},${r} 0 0 1 ${x1},${y + r}V${y + h - r}A${r},${r} 0 0 1 ${x1 - r},${y + h}H${x0}Z`;
  return `M${x0},${y}H${x1 + r}A${r},${r} 0 0 0 ${x1},${y + r}V${y + h - r}A${r},${r} 0 0 0 ${x1 + r},${y + h}H${x0}Z`;
}

export function graficoBarras(destino: HTMLElement, itens: readonly ItemBarra[], op: OpcoesBarras): void {
  destino.replaceChildren();
  const fig = document.createElement('figure');
  fig.className = 'grafico';
  const cap = document.createElement('figcaption');
  cap.textContent = op.titulo;
  fig.append(cap);
  if (!itens.length) {
    destino.append(fig);
    return;
  }
  const valores = itens.flatMap((i) => [i.valor, ...(i.ic ?? [])]).filter(Number.isFinite);
  let lo = Math.min(0, ...valores);
  let hi = Math.max(0, ...valores);
  if (hi === lo) hi = lo + 1;
  const folga = (hi - lo) * 0.04;
  if (lo < 0) lo -= folga;
  hi += folga;
  const altura = itens.length * ALTURA_LINHA + 34;
  const s = svg('svg', { viewBox: `0 0 ${LARGURA} ${altura}`, role: 'img', 'aria-label': op.titulo, class: 'grafico-svg' });
  const x = (v: number) => MARGEM_ROTULO + ((v - lo) / (hi - lo)) * (LARGURA - MARGEM_ROTULO - MARGEM_DIREITA);
  const base = itens.length * ALTURA_LINHA;
  for (const t of ticks(lo, hi)) {
    s.append(svg('line', { x1: x(t), x2: x(t), y1: 0, y2: base, class: t === 0 ? 'eixo-zero' : 'grade' }));
    const rot = svg('text', { x: x(t), y: base + 16, 'text-anchor': 'middle', class: 'rotulo-eixo' });
    rot.textContent = op.formata(t);
    s.append(rot);
  }
  const eixo = svg('text', { x: MARGEM_ROTULO + (LARGURA - MARGEM_ROTULO - MARGEM_DIREITA) / 2, y: base + 31, 'text-anchor': 'middle', class: 'rotulo-eixo' });
  eixo.textContent = op.eixo;
  s.append(eixo);
  const dica = document.createElement('div');
  dica.className = 'dica-grafico';
  dica.hidden = true;
  itens.forEach((it, i) => {
    const y = i * ALTURA_LINHA + (ALTURA_LINHA - ESPESSURA) / 2;
    const g = svg('g', { tabindex: 0, class: 'barra' });
    const nome = svg('text', { x: MARGEM_ROTULO - 8, y: y + ESPESSURA - 1, 'text-anchor': 'end', class: 'rotulo-barra' });
    nome.textContent = it.rotulo;
    g.append(nome);
    if (Number.isFinite(it.valor)) g.append(svg('path', { d: caminhoBarra(x(0), x(it.valor), y, ESPESSURA), fill: it.cor, class: 'marca' }));
    if (it.ic && it.ic.every(Number.isFinite)) {
      const yc = y + ESPESSURA / 2;
      g.append(svg('line', { x1: x(it.ic[0]), x2: x(it.ic[1]), y1: yc, y2: yc, class: 'bigode' }));
      for (const v of it.ic) g.append(svg('line', { x1: x(v), x2: x(v), y1: yc - 5, y2: yc + 5, class: 'bigode' }));
    }
    const pontaDireita = Math.max(x(it.valor), it.ic ? x(it.ic[1]) : 0, x(0));
    const val = svg('text', { x: pontaDireita + 6, y: y + ESPESSURA - 1, class: 'valor-barra' });
    val.textContent = op.formata(it.valor);
    g.append(val);
    // área de toque maior que a marca
    const alvo = svg('rect', { x: 0, y: i * ALTURA_LINHA, width: LARGURA, height: ALTURA_LINHA, class: 'alvo' });
    g.append(alvo);
    const texto = `${it.rotulo}: ${op.formata(it.valor)}${it.ic ? ` (IC 95%: ${op.formata(it.ic[0])} a ${op.formata(it.ic[1])})` : ''}${it.dica ? `. ${it.dica}` : ''}`;
    const mostra = (ev: Event) => {
      dica.textContent = texto;
      dica.hidden = false;
      const r = fig.getBoundingClientRect();
      const px = ev instanceof MouseEvent ? ev.clientX - r.left : 16;
      dica.style.left = `${Math.max(0, Math.min(px + 12, r.width - 260))}px`;
      dica.style.top = `${((i + 1) * ALTURA_LINHA * r.width) / LARGURA + 24}px`;
    };
    g.addEventListener('mousemove', mostra);
    g.addEventListener('focus', mostra);
    g.addEventListener('mouseleave', () => (dica.hidden = true));
    g.addEventListener('blur', () => (dica.hidden = true));
    s.append(g);
  });
  fig.append(s, dica);
  // tabela com os mesmos números
  const det = document.createElement('details');
  det.className = 'tabela-grafico';
  const sum = document.createElement('summary');
  sum.textContent = 'Ver como tabela';
  const tab = document.createElement('table');
  const cab = tab.createTHead().insertRow();
  for (const t of ['', op.colunaValor ?? 'Valor', 'IC 95%']) {
    const th = document.createElement('th');
    th.textContent = t;
    cab.append(th);
  }
  const corpo = tab.createTBody();
  for (const it of itens) {
    const r = corpo.insertRow();
    r.insertCell().textContent = it.rotulo;
    r.insertCell().textContent = op.formata(it.valor);
    r.insertCell().textContent = it.ic ? `${op.formata(it.ic[0])} a ${op.formata(it.ic[1])}` : '—';
  }
  det.append(sum, tab);
  destino.append(fig, det);
}
