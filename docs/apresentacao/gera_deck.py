# Gera docs/apresentacao/index.html (deck autocontido). Uso, da raiz: python -I docs/apresentacao/gera_deck.py
# Le linhas.json e metro_sequencias.csv direto do repositorio; os demais numeros
# foram copiados dos arquivos citados no rodape de cada slide.
# PDF: Chrome -> Imprimir -> Salvar como PDF, margens "Nenhuma", graficos de plano de fundo ligados.
import csv, json, math, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # raiz do repositorio
OUT = os.path.join(REPO, "docs", "apresentacao", "index.html")
_MAN = json.load(open(os.path.join(REPO, "fontes", "fontes_manifesto.json"), encoding="utf-8"))
_REL = [r.replace("dados-", "") for r in _MAN.get("releases", [_MAN["release"]])]
VERSAO_DADOS = (", ".join(_REL[:-1]) + " e " + _REL[-1]) if len(_REL) > 1 else _REL[0]  # versão dos dados (spec 013)

LINHAS = json.load(open(os.path.join(REPO, "dados", "derivados", "painel", "linhas.json"), encoding="utf-8"))
L = {d["linha"]: d for d in LINHAS}
ORDEM = ["verde", "laranja", "amarela", "azul"]
NOME = {"verde": "Verde", "laranja": "Laranja", "amarela": "Amarela", "azul": "Azul"}
COR = {"verde": "#008E4F", "laranja": "#EF8122", "amarela": "#FFD900", "azul": "#0076BE"}
BORDA_AMARELA = "#A38B00"

# ---------------------------------------------------------------- formatacao
def br(x, d=0, sinal=False):
    s = f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if x < 0:
        s = "\u2212" + s
    elif sinal and x > 0:
        s = "+" + s
    return s

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def sn(x, d):
    """Com sinal; "0" quando arredonda para zero."""
    return "0" if round(abs(x), d) == 0 else br(x, d, True)

# ---------------------------------------------------------------- números lidos dos arquivos gerados (revisão de 2026-11)
def _json(*partes):
    return json.load(open(os.path.join(REPO, *partes), encoding="utf-8"))

def _json_v1(caminho):
    """O mesmo arquivo na versão congelada v1.1.0 (resultado oficial da spec 012)."""
    import subprocess
    return json.loads(subprocess.run(["git", "show", f"v1.1.0:{caminho}"], cwd=REPO, capture_output=True, check=True, timeout=60).stdout.decode("utf-8"))

TAXA = {c: _json("dados", "derivados", "modelos", f"taxa_{c}.json") for c in ("MR", "EF")}
COEF = {c: {x["termo"]: x for x in TAXA[c]["coeficientes"]} for c in TAXA}
DIST = _json("dados", "derivados", "modelos", "distribuicoes.json")
POL = _json("dados", "derivados", "simulador", "politicas.json")
EXP = _json("dados", "derivados", "simulador", "expansao.json")
BT = _json("dados", "derivados", "modelos", "backtest.json")
BT_V1 = _json_v1("dados/derivados/modelos/backtest.json")
REVAL = _json("dados", "derivados", "simulador", "revalidacao.json")
TF = _json("dados", "derivados", "modelos", "taxa_fontes.json")
NORM = _json("dados", "derivados", "eventos", "resumo_normalizacao.json")
NORM_V1 = _json_v1("dados/derivados/eventos/resumo_normalizacao.json")
L_V1 = {d["linha"]: d for d in _json_v1("dados/derivados/painel/linhas.json")}

def stroke_amarela(linha, w=1.25):
    return f' stroke="{BORDA_AMARELA}" stroke-width="{w}"' if linha == "amarela" else ""

def barra_h(x0, y, w, h, cor, r=4, extra=""):
    """Barra horizontal com ponta de dado arredondada (4px) e base reta."""
    if w <= 0:
        return ""
    r = min(r, w, h / 2)
    return (f'<path d="M{x0:.1f},{y:.1f} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r:.1f} '
            f'a{r},{r} 0 0 1 {-r},{r} h{-(w - r):.1f} z" fill="{cor}"{extra}/>')

def barra_h_esq(x0, y, w, h, cor, r=4, extra=""):
    """Barra que cresce para a esquerda a partir de x0 (valores negativos)."""
    if w <= 0:
        return ""
    r = min(r, w, h / 2)
    return (f'<path d="M{x0:.1f},{y:.1f} h{-(w - r):.1f} a{r},{r} 0 0 0 {-r},{r} v{h - 2 * r:.1f} '
            f'a{r},{r} 0 0 0 {r},{r} h{w - r:.1f} z" fill="{cor}"{extra}/>')

# ---------------------------------------------------------------- mapa (GTFS)
SEQ = {}
with open(os.path.join(REPO, "dados", "derivados", "gtfs", "metro_sequencias.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f, delimiter=";"):
        if r["direction_id"] != "0":
            continue
        nome = r["estacao"].replace("STATION", "").strip()
        SEQ.setdefault(r["route_id"], []).append((int(r["ordem"]), nome, float(r["lat"]), float(r["lon"])))
for k in SEQ:
    SEQ[k].sort()
ROTA = {"verde": "1", "laranja": "2", "amarela": "4", "azul": "5"}
assert [len(SEQ[ROTA[l]]) for l in ORDEM] == [27, 31, 3, 12], "sequencia do GTFS mudou"

ROTULO = {
    "ANGRIGNON": "Angrignon", "HONORÉ-BEAUGRAND": "Honoré-Beaugrand", "CÔTE-VERTU": "Côte-Vertu",
    "MONTMORENCY": "Montmorency", "SNOWDON": "Snowdon", "JEAN-TALON": "Jean-Talon",
    "LIONEL-GROULX": "Lionel-Groulx", "BERRI-UQAM": "Berri-UQAM", "SAINT-MICHEL": "Saint-Michel",
    "LONGUEUIL- U. de SHERBROOKE": "Longueuil", "ATWATER": "Atwater",
    "UNIVERSITÉ DE MONTREAL": "Université-de-Montréal",
}
CORRESP = {"LIONEL-GROULX", "BERRI-UQAM", "SNOWDON", "JEAN-TALON"}

def mapa_svg(w, h, modo, pad=(24, 96, 24, 96)):
    """modo: 'titulo', 'corredor' ou 'expansao'. pad = (topo, direita, baixo, esquerda)."""
    pts = [(la, lo) for l in ORDEM for (_, _, la, lo) in SEQ[ROTA[l]]]
    lat_max = max(p[0] for p in pts); lat_min = min(p[0] for p in pts)
    lon_min = min(p[1] for p in pts); lon_max = max(p[1] for p in pts)
    kx = math.cos(math.radians((lat_max + lat_min) / 2))
    rx = (lon_max - lon_min) * kx; ry = lat_max - lat_min
    t, d, b, e = pad
    s = min((w - e - d) / rx, (h - t - b) / ry)
    ox = e + ((w - e - d) - rx * s) / 2; oy = t + ((h - t - b) - ry * s) / 2
    def P(la, lo):
        return ox + (lo - lon_min) * kx * s, oy + (lat_max - la) * s
    pos = {}
    for l in ORDEM:
        for (_, n, la, lo) in SEQ[ROTA[l]]:
            pos[n] = P(la, lo)
    out = [f'<svg class="mapa" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
           f'aria-label="Mapa das quatro linhas do metrô de Montreal, posições das estações do GTFS">']
    def segs(l, de=None, ate=None):
        nomes = [n for (_, n, _, _) in SEQ[ROTA[l]]]
        if de is not None:
            i, j = nomes.index(de), nomes.index(ate)
            i, j = min(i, j), max(i, j)
            nomes = nomes[i:j + 1]
        return " ".join(f"{pos[n][0]:.1f},{pos[n][1]:.1f}" for n in nomes)
    sw = 7
    fade = modo in ("corredor", "expansao")
    for l in ORDEM:
        op = ""
        if modo == "corredor":
            op = ' opacity="0.28"'
        elif modo == "expansao" and l in ("verde", "amarela"):
            op = ' opacity="0.35"'
        if l == "amarela":
            out.append(f'<polyline points="{segs(l)}" fill="none" stroke="{BORDA_AMARELA}" stroke-width="{sw + 2.5}" stroke-linecap="round" stroke-linejoin="round"{op}/>')
        out.append(f'<polyline points="{segs(l)}" fill="none" stroke="{COR[l]}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{op}><title>Linha {NOME[l]}</title></polyline>')
    if modo == "corredor":
        for l in ("verde", "laranja"):
            out.append(f'<polyline points="{segs(l, "LIONEL-GROULX", "BERRI-UQAM")}" fill="none" stroke="{COR[l]}" stroke-width="{sw + 2}" stroke-linecap="round" stroke-linejoin="round"/>')
    if modo == "expansao":
        a, u = pos["ATWATER"], pos["UNIVERSITÉ DE MONTREAL"]
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{u[0]:.1f}" y2="{u[1]:.1f}" stroke="var(--accent)" stroke-width="5" stroke-dasharray="9 6" stroke-linecap="round"><title>Ligação nova Atwater – Université-de-Montréal (hipótese de traçado)</title></line>')
    # estacoes comuns
    for l in ORDEM:
        for (_, n, _, _) in SEQ[ROTA[l]]:
            if n in CORRESP:
                continue
            x, y = pos[n]
            op = ' opacity="0.5"' if (modo == "corredor") else ""
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.9" fill="#fff"{op}/>')
    for n in sorted(CORRESP):  # conjunto: sem ordenar, a ordem muda a cada execução (hash aleatório) e o arquivo deixa de ser reprodutível
        x, y = pos[n]
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="#fff" stroke="var(--ink)" stroke-width="2.2"><title>{ROTULO[n]} (correspondência)</title></circle>')
    if modo == "expansao":
        for n in ("ATWATER", "UNIVERSITÉ DE MONTREAL"):
            x, y = pos[n]
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="#fff" stroke="var(--accent)" stroke-width="2.4"/>')
    # rotulos
    lab = {
        "titulo": {"ANGRIGNON": (-11, 5, "end"), "HONORÉ-BEAUGRAND": (-11, 4, "end"), "CÔTE-VERTU": (-11, 5, "end"),
                   "MONTMORENCY": (0, -14, "middle"), "SNOWDON": (-12, 5, "end"), "JEAN-TALON": (-12, 2, "end"),
                   "LIONEL-GROULX": (-12, 16, "end"), "BERRI-UQAM": (12, 14, "start"), "SAINT-MICHEL": (10, -6, "start"),
                   "LONGUEUIL- U. de SHERBROOKE": (0, -14, "middle")},
        "corredor": {"LIONEL-GROULX": (-12, 16, "end"), "BERRI-UQAM": (12, 14, "start"), "SNOWDON": (-12, 5, "end"),
                     "JEAN-TALON": (-12, 2, "end")},
        "expansao": {"SNOWDON": (-12, 5, "end"), "JEAN-TALON": (-12, 2, "end"), "LIONEL-GROULX": (-2, 22, "middle"),
                     "BERRI-UQAM": (12, 14, "start"), "ATWATER": (12, 2, "start"),
                     "UNIVERSITÉ DE MONTREAL": (-12, -4, "end")},
    }[modo]
    for n, (dx, dy, anc) in lab.items():
        x, y = pos[n]
        cls = "m-lab"
        if modo == "corredor" and n in ("SNOWDON", "JEAN-TALON"):
            cls = "m-lab m-fraco"
        if modo == "expansao" and n in ("ATWATER", "UNIVERSITÉ DE MONTREAL"):
            cls = "m-lab m-acc"
        out.append(f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anc}" class="{cls}">{ROTULO[n]}</text>')
    out.append("</svg>")
    return "".join(out), pos

def legenda_linhas(extra=""):
    itens = "".join(f'<span class="lg"><i style="background:{COR[l]}"{" class=am" if l=="amarela" else ""}></i>{NOME[l]}</span>' for l in ORDEM)
    return f'<div class="legenda">{itens}{extra}</div>'

# ---------------------------------------------------------------- slide 5: barras pequenas
def painel_barras(chave, fmt, w=356):
    vals = [L[l][chave] for l in ORDEM]
    vmax = max(vals)
    lx = 84; vx_pad = 8; vw = 78
    bw_max = w - lx - vw - vx_pad
    rh = 40; bh = 22; h = rh * 4 + 4
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    out.append(f'<line x1="{lx}" y1="0" x2="{lx}" y2="{h}" class="eixo"/>')
    for i, l in enumerate(ORDEM):
        v = L[l][chave]; y = i * rh + (rh - bh) / 2 + 2
        bw = bw_max * v / vmax
        out.append(f'<text x="{lx - 10}" y="{y + bh / 2 + 5:.1f}" text-anchor="end" class="c-lab">{NOME[l]}</text>')
        out.append(barra_h(lx + 1, y, bw, bh, COR[l], extra=stroke_amarela(l)).replace("/>", f"><title>{NOME[l]}: {fmt(v)}</title></path>"))
        out.append(f'<text x="{lx + 1 + bw + vx_pad:.1f}" y="{y + bh / 2 + 6:.1f}" class="c-val">{fmt(v)}</text>')
    out.append("</svg>")
    return "".join(out)

# ---------------------------------------------------------------- slide 6: floresta (multiplicadores)
def mult(c, termo):
    x = COEF[c][termo]
    return (x["multiplicador"], x["ic95"][0], x["ic95"][1])

FATORES = [(nome, mult("MR", t), mult("EF", t)) for nome, t in (  # dados/derivados/modelos/taxa_MR.json e taxa_EF.json
    ("Abertura do serviço (5 a 6 h)", "faixa=abertura"),
    ("Pico da manhã", "faixa=pico_manha"),
    ("Mais de 10 cm de neve no solo", "neve_solo=acima_10"),
    ("25 °C ou mais", "temp=25_ou_mais"),
    ("Abaixo de −15 °C", "temp=abaixo_-15"),
    ("Dia de greve (por trem-hora)", "greve"),
)]
contem_1 = lambda m: m[1] <= 1 <= m[2]

def floresta():
    w = 1152; x0 = 290; x1 = 790; lo, hi = math.log(0.45), math.log(4.5)
    def X(v):
        return x0 + (math.log(v) - lo) / (hi - lo) * (x1 - x0)
    top = 34; rh = 44; n = len(FATORES); h = top + rh * n + 30
    cMR, cEF = 850, 1012
    o = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Multiplicadores da taxa de falha com intervalo de 95%">']
    o.append(f'<text x="0" y="18" class="c-head">Fator</text>')
    o.append(f'<text x="{x0}" y="18" class="c-head">Multiplicador da taxa por trem-hora (IC 95%, escala log)</text>')
    o.append(f'<circle cx="{cMR + 6}" cy="13" r="6" fill="var(--ink)"/><text x="{cMR + 17}" y="18" class="c-head2">Material rodante</text>')
    o.append(f'<rect x="{cEF}" y="7" width="12" height="12" fill="var(--accent)"/><text x="{cEF + 18}" y="18" class="c-head2">Equip. fixos</text>')
    for v in (0.5, 1, 2, 3, 4):
        cls = "ref" if v == 1 else "grade"
        o.append(f'<line x1="{X(v):.1f}" y1="{top - 6}" x2="{X(v):.1f}" y2="{top + rh * n}" class="{cls}"/>')
        o.append(f'<text x="{X(v):.1f}" y="{top + rh * n + 20}" text-anchor="middle" class="c-tick">{br(v, 1) if v < 1 else br(v)}</text>')
    o.append(f'<text x="{X(1) + 6:.1f}" y="{top + rh * n + 20}" class="c-tick">= sem efeito</text>')
    for i, (nome, mr, ef) in enumerate(FATORES):
        yc = top + i * rh + rh / 2
        if i % 2 == 0:
            o.append(f'<rect x="0" y="{top + i * rh}" width="{w}" height="{rh}" fill="var(--zebra)"/>')
        o.append(f'<text x="0" y="{yc + 6:.1f}" class="c-lab">{esc(nome)}</text>')
        for (val, a, b), dy, forma, cor, cx in ((mr, -9, "c", "var(--ink)", cMR), (ef, 9, "q", "var(--accent)", cEF)):
            y = yc + dy
            sig = not (a <= 1 <= b)
            o.append(f'<line x1="{X(a):.1f}" y1="{y:.1f}" x2="{X(b):.1f}" y2="{y:.1f}" stroke="{cor}" stroke-width="2"/>')
            fill = cor if sig else "var(--surface)"
            tt = f"{br(val, 2)} ({br(a, 2)}–{br(b, 2)})"
            if forma == "c":
                o.append(f'<circle cx="{X(val):.1f}" cy="{y:.1f}" r="6" fill="{fill}" stroke="{cor}" stroke-width="2"><title>Material rodante: {tt}</title></circle>')
            else:
                o.append(f'<rect x="{X(val) - 6:.1f}" y="{y - 6:.1f}" width="12" height="12" fill="{fill}" stroke="{cor}" stroke-width="2"><title>Equipamentos fixos: {tt}</title></rect>')
            cls = "c-num" if sig else "c-num c-fraco"
            o.append(f'<text x="{cx}" y="{yc + 5:.1f}" class="{cls}">{tt}</text>')
    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------------- slide 7: forma da Weibull
FORMA = {l: tuple(DIST["reescala"][f"{l}|{c}"]["weibull_reescalado"]["forma"] for c in ("MR", "EF")) for l in ORDEM}  # distribuicoes.json

def pontos_weibull():
    w = 700; lx = 100; x0 = lx + 14; x1 = 560; lo, hi = 0.3, 1.1
    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    top = 44; rh = 56; h = top + rh * 4 + 40
    cMR, cEF = 600, 660
    o = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Forma da Weibull no tempo reescalado por linha e causa">']
    o.append(f'<rect x="{X(lo):.1f}" y="{top - 8}" width="{X(1) - X(lo):.1f}" height="{rh * 4 + 8}" fill="var(--accent-soft)"/>')
    o.append(f'<text x="{X(lo) + 8:.1f}" y="{top + 8}" class="c-acc">forma &lt; 1: agrupamento</text>')
    for v in (0.4, 0.6, 0.8, 1.0):
        cls = "ref" if v == 1.0 else "grade"
        o.append(f'<line x1="{X(v):.1f}" y1="{top - 8}" x2="{X(v):.1f}" y2="{top + rh * 4}" class="{cls}"/>')
        o.append(f'<text x="{X(v):.1f}" y="{top + rh * 4 + 20}" text-anchor="middle" class="c-tick">{br(v, 1)}</text>')
    o.append(f'<text x="{X(1) + 8:.1f}" y="{top + 8}" class="c-tick">1 = sem memória</text>')
    o.append(f'<text x="{X(1) + 8:.1f}" y="{top + 26}" class="c-tick">(Poisson)</text>')
    o.append(f'<text x="{cMR}" y="22" text-anchor="middle" class="c-head">MR</text><text x="{cEF}" y="22" text-anchor="middle" class="c-head">EF</text>')
    for i, l in enumerate(ORDEM):
        yc = top + i * rh + rh / 2 + 6
        mr, ef = FORMA[l]
        o.append(f'<text x="{lx}" y="{yc + 5:.1f}" text-anchor="end" class="c-lab">{NOME[l]}</text>')
        o.append(f'<line x1="{X(min(mr, ef)):.1f}" y1="{yc:.1f}" x2="{X(max(mr, ef)):.1f}" y2="{yc:.1f}" class="grade"/>')
        st = stroke_amarela(l, 1.5)
        o.append(f'<circle cx="{X(mr):.1f}" cy="{yc:.1f}" r="8" fill="{COR[l]}" stroke="var(--surface)" stroke-width="2"/>')
        if l == "amarela":
            o.append(f'<circle cx="{X(mr):.1f}" cy="{yc:.1f}" r="7" fill="none"{st}/>')
        o.append(f'<circle cx="{X(mr):.1f}" cy="{yc:.1f}" r="12" fill="transparent"><title>{NOME[l]}, material rodante: {br(mr, 2)}</title></circle>')
        o.append(f'<rect x="{X(ef) - 7.5:.1f}" y="{yc - 7.5:.1f}" width="15" height="15" fill="{COR[l]}" stroke="var(--surface)" stroke-width="2"><title>{NOME[l]}, equipamentos fixos: {br(ef, 2)}</title></rect>')
        if l == "amarela":
            o.append(f'<rect x="{X(ef) - 6.5:.1f}" y="{yc - 6.5:.1f}" width="13" height="13" fill="none"{st}/>')
        o.append(f'<text x="{cMR}" y="{yc + 5:.1f}" text-anchor="middle" class="c-num">{br(mr, 2)}</text>')
        o.append(f'<text x="{cEF}" y="{yc + 5:.1f}" text-anchor="middle" class="c-num">{br(ef, 2)}</text>')
    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------------- slide 8: grupos de causa comum
GRUPOS = sorted(((tuple(l for l in ORDEM if l in g["linhas"]), g["eventos"]) for g in DIST["causa_comum_grupos"].values()),
                key=lambda t: (-t[1], len(t[0])))  # distribuicoes.json, grupos usados pelo simulador
CC_DUR_MEDIA = DIST["causa_comum_duracao_conjunta"]["media_min"]
BETA_VL_EF = DIST["causa_comum_beta_familia"]["verde-laranja|EF"]  # β com o denominador da família (spec 018)
BETA_VL_V1 = DIST["causa_comum"]["verde-laranja"]  # β com o denominador de todas as falhas (v1.1.0, spec 006)
EXPO = _json("dados", "derivados", "exposicao", "resumo_exposicao.json")
REV_NO_IC = sum(c["dentro_ic"] for c in REVAL["comparacoes"])  # revalidacao.json (spec 020)
V1_NO_IC = sum(c["v1_dentro_ic"] for c in REVAL["comparacoes"])
N_COMP = len(REVAL["comparacoes"])
N_RECALC = 38  # verifica_fontes.py --recalcula em 2026-11-10: 38 números, 0 diferenças (25 até a v1.1.0; 13 novos da spec 017)
assert sum(n for _, n in GRUPOS) == 45
assert sum(n for g, n in GRUPOS if "verde" in g and "laranja" in g) == 31
assert sum(n for g, n in GRUPOS if "laranja" in g) == 44

def barras_grupos():
    w = 570; lx = 110; bx = 330; bw_max = 190; rh = 38; bh = 20; top = 4
    h = top + rh * len(GRUPOS) + 4
    o = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Eventos de causa comum por grupo de linhas">']
    o.append(f'<line x1="{bx}" y1="0" x2="{bx}" y2="{h}" class="eixo"/>')
    for i, (g, n) in enumerate(GRUPOS):
        y = top + i * rh
        yc = y + rh / 2
        for j, l in enumerate(ORDEM):
            cx = 12 + j * 22
            if l in g:
                o.append(f'<circle cx="{cx}" cy="{yc:.1f}" r="8" fill="{COR[l]}"{stroke_amarela(l)}/>')
            else:
                o.append(f'<circle cx="{cx}" cy="{yc:.1f}" r="7" fill="none" stroke="var(--rule)" stroke-width="1.5"/>')
        nomes = " + ".join(NOME[l] for l in g) if len(g) < 4 else "as quatro linhas"
        o.append(f'<text x="{lx}" y="{yc + 5:.1f}" class="c-lab c-sm">{nomes}</text>')
        vl = "verde" in g and "laranja" in g
        cor = "var(--accent)" if vl else "var(--bar)"
        bwid = bw_max * n / 12
        o.append(barra_h(bx + 1, yc - bh / 2, bwid, bh, cor).replace("/>", f"><title>{nomes}: {n} eventos</title></path>"))
        o.append(f'<text x="{bx + 1 + bwid + 8:.1f}" y="{yc + 6:.1f}" class="c-val">{n}</text>')
    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------------- slide 9: faixa de validacao
_CORR = {c["cenario"]: c for c in _json("dados", "derivados", "painel", "corredor.json")}
LAR_SIM = POL["minutos_por_ano"]["laranja"]  # politicas.json (simulador, ano-base)
LAR_ANA, LAR_PAINEL = _CORR["so_laranja"]["min_ano_analitico"], _CORR["so_laranja"]["sim_min_ano"]  # painel (2019 a 2026)
LAR_DENTRO = LAR_SIM["ic95"][0] <= LAR_ANA <= LAR_SIM["ic95"][1] and LAR_SIM["ic95"][0] <= LAR_PAINEL <= LAR_SIM["ic95"][1]

def faixa_laranja():
    s, (a, b) = LAR_SIM["media"], LAR_SIM["ic95"]
    lo = 100 * math.floor((min(a, LAR_ANA, LAR_PAINEL) - 60) / 100); hi = 100 * math.ceil((max(b, LAR_ANA, LAR_PAINEL) + 220) / 100)  # folga para o rótulo da direita
    w = 540; h = 118; x0 = 20; x1 = 520
    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    y = 64
    o = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Laranja: minutos parados por ano, simulador contra painel">']
    for v in range(lo + 100, hi, 100):
        o.append(f'<line x1="{X(v):.1f}" y1="{y - 26}" x2="{X(v):.1f}" y2="{y + 22}" class="grade"/>')
        o.append(f'<text x="{X(v):.1f}" y="{y + 42}" text-anchor="middle" class="c-tick">{br(v)}</text>')
    o.append(f'<rect x="{X(a):.1f}" y="{y - 9}" width="{X(b) - X(a):.1f}" height="18" rx="4" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.2"><title>IC 95% do simulador: {br(a)} a {br(b)}</title></rect>')
    o.append(f'<circle cx="{X(s):.1f}" cy="{y}" r="7" fill="var(--accent)" stroke="var(--surface)" stroke-width="2"/>')
    o.append(f'<text x="{X(s):.1f}" y="{y - 18}" text-anchor="middle" class="c-num c-acc-t">simulador {br(s)}</text>')
    for v in (LAR_ANA, LAR_PAINEL):
        o.append(f'<path d="M{X(v):.1f},{y - 8} l7,8 l-7,8 l-7,-8 z" fill="var(--ink)" stroke="var(--surface)" stroke-width="1.5"/>')
    esq, dir_ = sorted((("analítico", LAR_ANA), ("painel", LAR_PAINEL)), key=lambda t: t[1])
    o.append(f'<text x="{X(esq[1]) - 4:.1f}" y="{y + 30}" text-anchor="end" class="c-sm-t">{esq[0]} {br(esq[1])}</text>')
    o.append(f'<text x="{X(dir_[1]) + 10:.1f}" y="{y - 14}" class="c-sm-t">{dir_[0]} {br(dir_[1])}</text>')
    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------------- slide 10: politicas
def _pol(chave, nome, sub):  # politicas.json, reparo de 1,0 dia
    p = POL["politicas"]["1"][chave]
    m = p["minutos_rede"]
    th = p["trens_hora"]["media"]
    return (nome, sub, (-m["media"], -m["ic95"][1], -m["ic95"][0]), sn(th, 1 if abs(th) >= 10 else 2),
            sn(p["disp_od_pp"]["media"], 2), sn(p["frota_completa_laranja_pp"]["media"], 1), chave == "operacaoDegradada")

POLITICAS = [_pol(*x) for x in (
    ("operacaoDegradada", "Operação degradada", "marcha lenta após falha de equipamento fixo"),
    ("retiradaTrem", "Retirada do trem falho", "só material rodante"),
    ("tratamentoCausaComum", "Tratamento de causa comum", "redução de 50% (hipótese)"),
    ("reservaFria", "Reserva fria", "2 trens por linha"),
    ("retornoParcial", "Retorno parcial", "nas pontas de viagem (hipótese)"),
    ("rotaAlternativa", "Rota alternativa", "de passageiros"),
)]
P1, P4 = POL["politicas"]["1"], POL["politicas"]["4"]

def barra_politica(v, a, b, dest):
    w = 250; h = 30; x0 = 2; esc_ = (w - 64) / 10
    o = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    o.append(f'<line x1="{x0}" y1="0" x2="{x0}" y2="{h}" class="eixo"/>')
    cor = "var(--accent)" if dest else "var(--bar)"
    if v > 0:
        o.append(barra_h(x0 + 1, 5, v * esc_, 20, cor))
        o.append(f'<line x1="{x0 + 1 + a * esc_:.1f}" y1="15" x2="{x0 + 1 + b * esc_:.1f}" y2="15" stroke="var(--ink)" stroke-width="2"/>')
        o.append(f'<line x1="{x0 + 1 + a * esc_:.1f}" y1="10" x2="{x0 + 1 + a * esc_:.1f}" y2="20" stroke="var(--ink)" stroke-width="2"/>')
        o.append(f'<line x1="{x0 + 1 + b * esc_:.1f}" y1="10" x2="{x0 + 1 + b * esc_:.1f}" y2="20" stroke="var(--ink)" stroke-width="2"/>')
        o.append(f'<text x="{x0 + 1 + b * esc_ + 8:.1f}" y="21" class="c-val">\u2212{br(v, 1)}</text>')
    else:
        o.append(f'<text x="{x0 + 10}" y="21" class="c-val c-fraco">0</text>')
    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------------- slide 11: ganhos de expansao
_CAND = {c["id"]: c for c in EXP["candidatas"]["sem_retorno_parcial"]}  # expansao.json, sem retorno parcial
_RP = {c["id"]: c["ganho"]["media"] * 100 for c in EXP["candidatas"]["com_retorno_parcial"]}
_MELHOR = EXP["busca_exaustiva"]["por_ganho"][0]
N_LIGACOES = int(re.search(r"(\d+) ligações avaliadas", open(os.path.join(REPO, "fontes", "verificacao", "expansao.md"), encoding="utf-8").read()).group(1))
DISP_OD_ATUAL = EXP["rede_atual"]["dispOD"]["media"] * 100

def _rot(g):
    return sn(g, 4 if abs(g) < 0.001 else 3)

def _ganho(cid, nome, sub):
    c = _CAND[cid]
    g, (a, b) = c["ganho"]["media"] * 100, (x * 100 for x in c["ganho"]["ic95"])
    sub = f"{br(c['km'], 1)} km" + (" · ramal" if sub == "ramal" else "") + (" · IC cruza zero" if a < 0 < b else "")
    return (nome, sub, g, _rot(g), False, "cand")

GANHOS = [("Atwater – Université-de-Montréal", f"ligação direta, {br(_MELHOR['km'], 1)} km", _MELHOR["ganho"]["media"] * 100,
           _rot(_MELHOR["ganho"]["media"] * 100), True, "busca")] + sorted((_ganho(*x) for x in (
    ("rosa_2017", "Linha Rosa", ""),
    ("rosa_2017+azul_anjou", "Rosa + Azul até Anjou", ""),
    ("laranja_anel_artm_2019", "Anel da Laranja (ARTM, 2019)", ""),
    ("amarela_longueuil", "Amarela em Longueuil", "ramal"),
    ("laranja_bois_franc", "Laranja até Bois-Franc", "ramal"),
    ("azul_anjou", "Azul até Anjou (em obras)", "ramal"),
)), key=lambda t: -t[2])  # candidatas na ordem do ganho
assert "Atwater" in _MELHOR["nome"], _MELHOR["nome"]

def barras_ganho():
    w = 640; lx = 262; x0 = 290; x1 = 560; lo, hi = -0.08, 0.09
    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    rh = 40; top = 30; sep = 26
    h = top + rh * len(GANHOS) + sep + 30
    o = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Ganho de disponibilidade origem-destino por candidata">']
    o.append(f'<text x="0" y="16" class="c-head">Busca exaustiva (298 ligações até 3 km)</text>')
    zx = X(0)
    yb = top + rh * len(GANHOS) + sep
    o.append(f'<line x1="{zx:.1f}" y1="{top - 6}" x2="{zx:.1f}" y2="{yb}" class="ref"/>')
    for v in (-0.05, 0.05):
        o.append(f'<line x1="{X(v):.1f}" y1="{top - 6}" x2="{X(v):.1f}" y2="{yb}" class="grade"/>')
        o.append(f'<text x="{X(v):.1f}" y="{yb + 18}" text-anchor="middle" class="c-tick">{br(v, 2, True)}</text>')
    o.append(f'<text x="{zx:.1f}" y="{yb + 18}" text-anchor="middle" class="c-tick">0</text>')
    o.append(f'<text x="{x1 + 8}" y="{yb + 18}" class="c-tick">p.p.</text>')
    for i, (nome, sub, v, rot, dest, grupo) in enumerate(GANHOS):
        y = top + i * rh + (sep if i >= 1 else 0)
        if i == 1:
            o.append(f'<text x="0" y="{y - 6}" class="c-head">Candidatas oficiais e propostas</text>')
        yc = y + rh / 2
        o.append(f'<text x="{lx}" y="{yc - 2:.1f}" text-anchor="end" class="c-lab c-sm">{esc(nome)}</text>')
        o.append(f'<text x="{lx}" y="{yc + 16:.1f}" text-anchor="end" class="c-tick">{esc(sub)}</text>')
        cor = "var(--accent)" if dest else "var(--bar)"
        bw = abs(X(v) - zx)
        if v >= 0:
            o.append(barra_h(zx + 1, yc - 10, max(bw, 1.5), 20, cor, r=4 if bw > 6 else 0).replace("/>", f"><title>{esc(nome)}: {rot} p.p.</title></path>"))
            tx = max(zx + bw + 8, zx + 8)
            o.append(f'<text x="{tx:.1f}" y="{yc + 6:.1f}" class="c-val">{rot}</text>')
        else:
            o.append(barra_h_esq(zx - 1, yc - 10, bw, 20, cor).replace("/>", f"><title>{esc(nome)}: {rot} p.p.</title></path>"))
            o.append(f'<text x="{zx + 8:.1f}" y="{yc + 6:.1f}" class="c-val">{rot}</text>')
    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------------- slide 12: cobertura do backtest
def _cob(bt, k):
    c = bt[k]["cobertura_total"]
    return 100 * c["cobertura"], 100 * c["ic95"][0], 100 * c["ic95"][1]

# resultado oficial da spec 012: backtest.json da v1.1.0 (git show); o refeito após a revisão é o do disco (pós-hoc)
VERSOES = [(k, d, s, *_cob(BT_V1, k), pre) for k, d, s, pre in (
    ("A", "Treino até 2024-12, efeito do ano de 2024", "pré-registrada · resultado oficial", True),
    ("B", "Treino até 2023-09, só exposição medida", "pré-registrada", True),
    ("C", "Treino até 2024-12, efeito do ano sorteado", "definida depois de ver A", False),
    ("D", "Regra C em outro período (teste 2023-01 a 2024-06)", "definida depois de ver A", False),
)]
POS_HOC = {k: _cob(BT, k) for k in "ABCD"}
_BT_FAM = {k: {c: 100 * BT[k]["cobertura_por_familia"][c]["cobertura"] for c in ("MR", "EF")} for k in "ABCD"}

def cobertura():
    w = 1152; lx = 470; x0 = 500; x1 = 940; lo, hi = 50, 100
    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    top = 34; rh = 58; n = len(VERSOES); yb = top + rh * n
    h = yb + 34
    o = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Cobertura do intervalo de predição de 90% por versão do backtest">']
    o.append(f'<rect x="{X(80):.1f}" y="{top - 10}" width="{X(98) - X(80):.1f}" height="{rh * n + 10}" fill="var(--accent-soft)"/>')
    o.append(f'<text x="{(X(80) + X(98)) / 2:.1f}" y="{top - 16}" text-anchor="middle" class="c-acc">faixa exigida: 80% a 98%</text>')
    for v in (50, 60, 70, 80, 90, 100):
        o.append(f'<line x1="{X(v):.1f}" y1="{top - 10}" x2="{X(v):.1f}" y2="{yb}" class="grade"/>')
        o.append(f'<text x="{X(v):.1f}" y="{yb + 20}" text-anchor="middle" class="c-tick">{v}%</text>')
    o.append(f'<text x="{x1 + 30}" y="{top - 16}" class="c-head">Cobertura (IC 95%)</text>')
    for i, (k, desc, status, v, a, b, pre) in enumerate(VERSOES):
        yc = top + i * rh + rh / 2
        o.append(f'<text x="0" y="{yc - 2:.1f}" class="c-lab"><tspan class="c-k">{k}</tspan><tspan x="26">{esc(desc)}</tspan></text>')
        o.append(f'<text x="26" y="{yc + 18:.1f}" class="c-tick">{status}</text>')
        o.append(f'<line x1="{X(a):.1f}" y1="{yc:.1f}" x2="{X(b):.1f}" y2="{yc:.1f}" stroke="var(--ink)" stroke-width="2"/>')
        for e in (a, b):
            o.append(f'<line x1="{X(e):.1f}" y1="{yc - 6:.1f}" x2="{X(e):.1f}" y2="{yc + 6:.1f}" stroke="var(--ink)" stroke-width="2"/>')
        fill = "var(--ink)" if pre else "var(--surface)"
        o.append(f'<circle cx="{X(v):.1f}" cy="{yc:.1f}" r="8" fill="{fill}" stroke="var(--ink)" stroke-width="2.5"><title>{k}: {br(v, 1)}% ({br(a, 1)}–{br(b, 1)})</title></circle>')
        cls = "c-num c-forte" if k == "A" else "c-num"
        o.append(f'<text x="{x1 + 30}" y="{yc + 6:.1f}" class="{cls}">{br(v, 1)}% ({br(a, 1)}–{br(b, 1)})</text>')
    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------------- funil (slide 4)
def funil():
    w = 520; h = 150; bw = 400; x0 = 0
    itens = [(45785, "incidentes registrados"), (8619, "falhas técnicas"), (8530, "falhas técnicas de uma linha só")]
    o = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Dos incidentes às falhas técnicas">']
    for i, (n, rot) in enumerate(itens):
        y = i * 50
        wd = bw * n / 45785
        cor = "var(--accent)" if i == 2 else "var(--bar)"
        o.append(barra_h(x0, y + 4, wd, 24, cor))
        o.append(f'<text x="{x0 + wd + 10:.1f}" y="{y + 23}" class="c-val">{br(n)}</text>')
        o.append(f'<text x="{x0 + wd + 76:.1f}" y="{y + 23}" class="c-lab c-sm">{rot}</text>' if i else
                 f'<text x="{x0 + 10}" y="{y + 22}" class="c-in">{rot}</text>')
    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------------- montagem
def chip(l):
    return f'<i class="chip{" am" if l == "amarela" else ""}" style="background:{COR[l]}"></i>'

mapa_titulo, _ = mapa_svg(470, 470, "titulo", pad=(26, 100, 22, 92))
mapa_corr, _ = mapa_svg(520, 380, "corredor", pad=(12, 110, 12, 110))
mapa_exp, _ = mapa_svg(440, 360, "expansao", pad=(16, 70, 16, 120))

def f2(v): return br(v, 2)
def f2h(v): return br(v, 2) + " h"
def f2m(v): return br(v, 2) + " min"

tiles_disp = "".join(
    f'<div class="tile-l">{chip(l)}<div><div class="tile-v">{br(L[l]["disponibilidade"] * 100, 2)}%</div>'
    f'<div class="tile-s">{br(L[l]["min_fora_ano"])} min por ano parada</div></div></div>' for l in ORDEM)

por_linha = " · ".join(f'{chip(l)}{NOME[l]} <b>{br(L[l]["falhas"])}</b>' for l in ORDEM)
R = L["rede"]
assert R["falhas"] == 8530 and R["falhas_mr"] == 3982 and R["falhas_ef"] == 4548

SLIDES = []

def slide(eyebrow, titulo, corpo, fonte, notas, classe=""):
    SLIDES.append(dict(eyebrow=eyebrow, titulo=titulo, corpo=corpo, fonte=fonte, notas=notas, classe=classe))

# 1 ---------------------------------------------------------------
slide("", "", f"""
<div class="capa">
  <div class="capa-txt">
    <div class="eyebrow">Sistemas Tolerantes a Falhas · Engenharia de Produção · ESEG · 2026</div>
    <h1>Confiabilidade e tolerância a falhas do metrô de Montreal</h1>
    <p class="lede">Dados públicos, modelos e simulação</p>
    <div class="equipe">
      <div class="label">Equipe</div>
      <p>Ana Paula Duanetti · Felipe Marins<br>Lorena Feitosa de Freitas · Sophia Braz</p>
    </div>
    <p class="url">felipe44776-eseg.github.io/confiabilidade-metro-montreal</p>
  </div>
  <figure class="capa-mapa">{mapa_titulo}{legenda_linhas()}
    <figcaption>Posição das estações no GTFS da STM; linhas ligadas em linha reta entre estações.</figcaption>
  </figure>
</div>""",
"docs/equipe.json; dados/derivados/gtfs/metro_sequencias.csv (mapa)",
"""<p>Apresentar a equipe e o tema em uma frase: medimos a confiabilidade do metrô de Montreal só com dados públicos e simulamos políticas de tolerância a falhas.</p>
<p>Avisar que todo número da apresentação tem a fonte no rodapé e pode ser refeito por qualquer pessoa.</p>
<p><b>Tempo:</b> 30 s.</p>""", "capa-slide")

# 2 ---------------------------------------------------------------
slide("A pergunta", "Quanto o metrô falha, por quê, e o que deixaria a rede mais tolerante a falhas", """
<div class="cols c-60-40">
  <div>
    <ol class="perguntas">
      <li><b>Quanto cada linha falha</b> e por quanto tempo fica parada? Sob quais condições: hora, clima, eventos?</li>
      <li><b>As falhas são independentes</b> ou se agrupam? Quanto pesa a causa comum, que para duas linhas ao mesmo tempo?</li>
      <li><b>Que políticas</b> de tolerância a falhas mais reduzem a indisponibilidade?</li>
      <li><b>Que nova ligação</b> deixaria a rede mais confiável como sistema?</li>
    </ol>
  </div>
  <div class="caixa">
    <div class="label">Por que Montreal</div>
    <ul class="lista">
      <li>A STM publica cada incidente do metrô em dados abertos (CC BY 4.0).</li>
      <li>Cada registro tem hora do incidente e da retomada, causa, linha e local.</li>
      <li>São <b>45.785 incidentes</b>, de 2019-01-01 a 2026-06-30.</li>
      <li>Também procuramos bases de São Paulo (Metrô SP, ARTESP): nenhuma tinha série de falhas utilizável.</li>
    </ul>
  </div>
</div>
<div class="faixa">
  <div><span class="label">Componentes</span> trens (material rodante) e infraestrutura: via, sinalização, energia, portas (equipamentos fixos)</div>
  <div><span class="label">Redundâncias</span> trens de reserva na garagem (k-de-n fria) e caminhos alternativos entre estações (rota)</div>
</div>""",
"docs/relatorio/relatorio.md §1 e §3.1; fontes/FONTES.md §1 e §3",
"""<p>As quatro perguntas organizam a apresentação: medir, entender o agrupamento, testar políticas, escolher expansão.</p>
<p>Por que Montreal: é raro achar uma base pública com hora de início e de retomada, causa, linha e local de cada falha. Também procuramos bases de São Paulo e não havia série de falhas utilizável.</p>
<p>Fechar com a leitura de sistema tolerante a falhas: os componentes são trens e equipamentos fixos; as redundâncias são a reserva de trens e os caminhos alternativos.</p>
<p><b>Tempo:</b> 1 min.</p>""")

# 3 ---------------------------------------------------------------
slide("Antes dos resultados", "Nenhum número sem fonte: qualquer pessoa pode refazer cada conta", f"""
<div class="cards c3">
  <div class="card"><div class="card-k">1</div><h3>Cópia exata dos dados</h3><p>Três Releases no GitHub (<code>dados-2026-10-20</code>, <code>dados-2026-10-21</code> e <code>dados-2026-11</code>, o km real republicado pela STM), com o SHA-256 de cada arquivo no manifesto.</p></div>
  <div class="card"><div class="card-k">2</div><h3>Segunda implementação</h3><p><code>verifica_fontes.py</code>, em Python puro e sem usar o pipeline, recalcula <b>{N_RECALC} números</b> publicados direto dos dados brutos. Diferença: <b>zero</b>.</p></div>
  <div class="card"><div class="card-k">3</div><h3>Publicação bloqueada por erro</h3><p>Cada publicação baixa a Release, confere os hashes, recalcula e roda os testes. Um erro impede o site de ir ao ar.</p></div>
  <div class="card"><div class="card-k">4</div><h3>Auditoria independente</h3><p>Um agente sem acesso aos scripts tentou refutar os números com código próprio. Nenhuma divergência numérica; as 6 ressalvas de apresentação foram corrigidas.</p></div>
  <div class="card"><div class="card-k">5</div><h3>Reprodução do zero</h3><p><code>reproduz.yml</code> refaz o pipeline numa máquina limpa e compara com o publicado. <span class="tag">passou em 2026-10-21 (commit ba19e74): 48 arquivos idênticos byte a byte, 5 dentro da tolerância, 0 fora</span></p></div>
  <div class="card"><div class="card-k">6</div><h3>Decisões com data (SDD)</h3><p>Critério de aceite escrito antes do código. Se o resultado não atende, vira exceção registrada: o critério não é afrouxado.</p></div>
</div>
<p class="nota">Verificação na origem: em 2026-10-20, 26 das 27 fontes baixadas de novo vieram idênticas byte a byte; a 27ª (mobilidade do Google, 98 MB) foi conferida pelo tamanho.</p>""",
"docs/relatorio/relatorio.md §3.2; fontes/FONTES.md (resultado local, §5); specs/constitution.md; specs/013-publicacao/spec.md (Resultado) e tasks.md",
f"""<p>Este slide vem antes dos resultados de propósito: a equipe quis que ninguém precisasse confiar em quem fez as contas.</p>
<p>Destacar o item 2: um segundo programa, escrito à parte, refaz {N_RECALC} números direto dos dados brutos e chega ao mesmo valor. E o item 3: o site não publica se essa conferência falhar.</p>
<p>Item 5: a reprodução do zero rodou no GitHub Actions em 2026-10-21. A primeira execução reproduziu todos os resultados e só acusou metadados (commit e tempo de execução gravados nos relatórios); depois da correção, a segunda deu 45 arquivos idênticos byte a byte, 8 dentro da tolerância e nenhum fora. No commit ba19e74, com o hash do código também comparado, a execução 39556506384 deu 48 idênticos, 5 dentro da tolerância e 0 fora.</p>
<p><b>Tempo:</b> 1 min 30 s.</p>""")

# 4 ---------------------------------------------------------------
slide("Dados · 2019-01-01 a 2026-06-30", "45.785 incidentes da STM viram 8.530 falhas técnicas, ligadas a oferta, clima e eventos", f"""
<div class="cols c-50-50">
  <div>
    <div class="label">Dos incidentes às falhas técnicas</div>
    {funil()}
    <p class="corpo-sm"><b>{br(R["falhas_mr"])}</b> de material rodante · <b>{br(R["falhas_ef"])}</b> de equipamentos fixos</p>
    <p class="corpo-sm">{por_linha}</p>
    <p class="corpo-sm muted">Fora das métricas por linha, mas declaradas: 45 em várias linhas (viram causa comum) e 44 sem linha.</p>
    <p class="corpo-sm"><span class="tag">após a revisão</span> 9 fontes de falha: frota do trem (MR-73, MPM-10, outros) e setor do equipamento fixo, nas etiquetas da STM (via, "Service aux trains", estações, TCPE), dividido pelo sintoma.</p>
  </div>
  <div>
    <table class="tab">
      <thead><tr><th>Fonte</th><th>O que entra</th></tr></thead>
      <tbody>
        <tr><td><b>Oferta</b><br><span class="muted">GTFS da STM, versão 20261007130000_26N</span></td><td>Trens em viagem às 08:00: 26, 31, 2 e 9. Calibrada pelo km real da STM, republicado em 2026-10-23: {br(EXPO["km_carro_total_milhoes"], 2)} milhões de km-carro (2019-01 a 2026-09; na v1.1.0, 411,63 milhões até 2023-09); erro mensal mediano de {br(100 * EXPO["erro_abs_mediano"], 2)}%.</td></tr>
        <tr><td><b>Clima horário</b><br><span class="muted">ECCC, 3 estações</span></td><td>65.717 horas; precipitação em 99,99% das horas de operação.</td></tr>
        <tr><td><b>Eventos externos</b><br><span class="muted">NHL, Jolpica, imprensa</span></td><td>348 eventos (jogos do Canadiens, GP do Canadá, greves de 2025), cada um com URL e status.</td></tr>
        <tr><td><b>Rede</b><br><span class="muted">OpenStreetMap, Wikidata</span></td><td>4 linhas e 73 estações, todas casadas; traçado a até 3% do comprimento oficial.</td></tr>
      </tbody>
    </table>
    <p class="nota">Base do modelo de taxa: 226.658 horas-linha com serviço.</p>
  </div>
</div>""",
"docs/relatorio/relatorio.md §3; fontes/FONTES.md §1; dados/derivados/painel/linhas.json; fontes/verificacao/exposicao.md; fontes/verificacao/validacao_geo.md; fontes/verificacao/modelo_taxa.md",
"""<p>Falha técnica, aqui, é o incidente que a STM atribui a material rodante (o trem) ou a equipamentos fixos (via, sinalização, energia, portas). Os demais incidentes, de passageiros ou operação, ficam fora dos modelos.</p>
<p>Cada falha foi ligada à oferta de trens daquela hora, ao clima da hora e aos eventos do dia. É isso que permite medir taxa por trem-hora, e não por hora de relógio.</p>
<p>Nada foi descartado em silêncio: os 45 eventos multilinha viram causa comum e os 44 sem linha ficam registrados.</p>
<p><b>Tempo:</b> 1 min.</p>""")

# 5 ---------------------------------------------------------------
MAIS_PARADA = max(ORDEM, key=lambda l: L[l]["min_fora_ano"])
assert MAIS_PARADA in ("verde", "laranja") and L["azul"]["min_fora_ano"] < L["laranja"]["min_fora_ano"], "revisar o título do slide 5"
slide("Indicadores por linha · 2019-01 a 2026-06 · após a revisão", "Verde e Laranja falham mais e ficam mais tempo paradas; a Azul parava metade do que parecia", f"""
<div class="multiplos">
  <div><h3>Falhas por dia</h3><p class="sub">falhas técnicas de uma linha</p>{painel_barras("falhas_por_dia", f2)}</div>
  <div><h3>MTBF</h3><p class="sub">horas de operação entre falhas</p>{painel_barras("mtbf_op_h", f2h)}</div>
  <div><h3>MTTR</h3><p class="sub">minutos até o serviço voltar</p>{painel_barras("mttr_min", f2m)}</div>
</div>
<div class="disp">
  <div class="disp-t"><div class="label">Disponibilidade</div><p class="sub">A = MTBF / (MTBF + MTTR)</p></div>
  {tiles_disp}
</div>
<p class="nota">MTBF em horas de operação (janela de 20 h por dia, 05:00 a 01:00). MTTR é o tempo até o serviço voltar, não o reparo na oficina, e inclui as falhas sem interrupção. <span class="tag">após a revisão</span> A duração segue a faixa oficial da STM quando a calculada pelos horários a contradiz (D55). Na Azul, seis interrupções de quase 20 h em Saint-Michel (out/2024) estavam registradas como "2 min ou menos": o MTTR dela vai de {br(L_V1["azul"]["mttr_min"], 2)} para {br(L["azul"]["mttr_min"], 2)} min, e os minutos parados por ano de {br(L_V1["azul"]["min_fora_ano"])} para {br(L["azul"]["min_fora_ano"])}. Rede: {br(R["falhas_por_dia"], 1)} falhas por dia; MTBF {br(R["mtbf_op_h"], 2)} h.</p>""",
"dados/derivados/painel/linhas.json (e o mesmo arquivo na etiqueta v1.1.0); definições em docs/relatorio/relatorio.md §2; regra da duração: specs/017-fontes-e-duracoes e fontes/verificacao/fontes_e_duracoes.md",
f"""<p>Ler da esquerda para a direita. Laranja e Verde têm mais de uma falha técnica por dia; a Amarela, com 3 estações, tem bem menos.</p>
<p>Na versão anterior, a Azul parecia a linha que mais ficava parada. A revisão mostrou que isso vinha de seis registros de Saint-Michel, em outubro de 2024, com quase 20 horas pelos horários e "2 min ou menos" pela faixa oficial da STM. Com a faixa, o MTTR da Azul cai para {br(L["azul"]["mttr_min"], 2)} min.</p>
<p>Agora a {NOME[MAIS_PARADA]} é a que fica mais tempo parada. Todas ficam acima de 99,5%: o problema não é cada linha, é a rede, como veremos.</p>
<p><b>Tempo:</b> 1 min 30 s.</p>""")

# 6 ---------------------------------------------------------------
_AB, _NEVE, _CALOR, _FRIO, _GREVE = (FATORES[i] for i in (0, 2, 3, 4, 5))
_TCPE_AB = next(c["multiplicador"] for c in TF["fontes"]["tcpe"]["coeficientes"] if c["termo"] == "faixa=abertura")  # taxa_fontes.json
assert contem_1(_GREVE[1]) and contem_1(_GREVE[2]), "greve fora de 1: revisar a D42 e o texto do slide 6"
assert contem_1(_CALOR[1]) and not contem_1(_CALOR[2]) and contem_1(_FRIO[1]) and contem_1(_FRIO[2]), "revisar o texto de calor e frio do slide 6"
slide("O que muda a taxa de falha · binomial negativa com exposição", f"A abertura do serviço multiplica a taxa de falha por {br(_AB[1][0], 1)} a {br(_AB[2][0], 1)}; neve e calor também pesam", f"""
{floresta()}
<div class="tri">
  <p><b>Greve</b> reduz a oferta, mas não muda a taxa por trem-hora: o intervalo contém 1. <span class="tag">após a revisão</span> Com o km de 2025 medido, a exposição dos dias de greve precisou de correção (D63).</p>
  <p><b>Calor</b> pesa só nos equipamentos fixos (+{br(100 * (_CALOR[2][0] - 1))}%), e vem da via. <b>Frio intenso</b> não tem efeito detectável.</p>
  <p><b>Binomial negativa vence Poisson</b> nas duas causas (α = {br(TAXA["MR"]["alpha_nb"], 2)} e {br(TAXA["EF"]["alpha_nb"], 2)}; p &lt; 10⁻³⁰).</p>
</div>
<p class="nota">Vazio e em cinza: intervalo de 95% contém 1. Referência: Laranja, entrepico, dia útil, outono, 5 a 15 °C, sem precipitação. IC por bootstrap em blocos semanais (B = {TAXA["MR"]["bootstrap_b"]}).</p>""",
"relatório §4.1; fontes/verificacao/modelo_taxa.md e taxa_por_fonte.md; dados/derivados/modelos/taxa_MR.json e taxa_EF.json",
f"""<p>Cada ponto é quanto um fator multiplica a taxa de falha por trem-hora, com o intervalo de 95%. À direita do 1, aumenta; à esquerda, diminui.</p>
<p>O maior efeito é a abertura do serviço, das 5 às 6 h: a taxa fica {br(_AB[1][0], 1)} vezes maior no material rodante e {br(_AB[2][0], 1)} vezes nos equipamentos fixos. Por fonte, a abertura eleva todas; na energia (TCPE), a taxa fica {br(_TCPE_AB, 1)} vezes maior, o que lemos como falha ao energizar a rede.</p>
<p>Neve acumulada acima de 10 cm eleva as duas causas em cerca de {br(100 * (_NEVE[1][0] - 1))}%. Calor de 25 °C ou mais pesa nos equipamentos fixos, e por fonte ele vem da via. O frio intenso, que seria o palpite óbvio em Montreal, não aparece.</p>
<p>A greve só reduz a oferta: por trem que roda, a taxa não muda de forma detectável.</p>
<p>Após a revisão, com a exposição medida em todo o período, os multiplicadores por família mudam só na segunda casa decimal.</p>
<p><b>Tempo:</b> 1 min 30 s.</p>""")

# 7 ---------------------------------------------------------------
_DEF = {c: TAXA[c]["defasagem_1h"] for c in TAXA}
_RS = [v for k, v in DIST["reescala"].items()]
_REJ = sum(not v["compativel_poisson"] for v in _RS)
_P_EXP = tuple(str(round(math.log10(f(v["p_ks"] for v in _RS)))).replace("-", "−") for f in (max, min))
_MED = (min(v["media"] for v in _RS), max(v["media"] for v in _RS))
_FONTE_FORMA = (min(v["weibull_reescalado"]["forma"] for v in DIST["reescala_fonte"].values()), max(v["weibull_reescalado"]["forma"] for v in DIST["reescala_fonte"].values()))
slide("As falhas se agrupam · teste de reescala do tempo", "Depois de uma falha, a próxima vem mais cedo: o processo não é Poisson", f"""
<div class="cols c-60-40">
  <div>
    <h3>Forma da Weibull no tempo reescalado</h3>
    <p class="sub">círculo: material rodante (MR) · quadrado: equipamentos fixos (EF)</p>
    {pontos_weibull()}
  </div>
  <div class="stats">
    <div class="stat"><div class="stat-v">×{br(_DEF["MR"]["multiplicador"], 2)}</div><div class="stat-l">taxa de material rodante na hora seguinte a uma falha na mesma linha <span class="muted">(IC {br(_DEF["MR"]["ic95_modelo"][0], 2)}–{br(_DEF["MR"]["ic95_modelo"][1], 2)})</span></div></div>
    <div class="stat"><div class="stat-v">×{br(_DEF["EF"]["multiplicador"], 2)}</div><div class="stat-l">taxa de equipamentos fixos na mesma situação <span class="muted">(IC&#160;{br(_DEF["EF"]["ic95_modelo"][0], 2)}–{br(_DEF["EF"]["ic95_modelo"][1], 2)})</span></div></div>
    <div class="stat"><div class="stat-v">{_REJ} de {len(_RS)}</div><div class="stat-l">combinações linha × causa em que o teste de reescala rejeita Poisson (p de 10<sup>{_P_EXP[0]}</sup> a 10<sup>{_P_EXP[1]}</sup>)</div></div>
  </div>
</div>
<p class="nota">Com a taxa que muda por hora, clima e oferta, a média reescalada fica entre {br(_MED[0], 2)} e {br(_MED[1], 2)}: a taxa está calibrada. Mesmo assim a forma fica abaixo de 1. Por isso o simulador usa renovação Weibull no tempo reescalado. A Weibull é a melhor família em 23 de 29 estratos. <span class="tag">após a revisão</span> Cada fonte tem a sua forma, de {br(_FONTE_FORMA[0], 2)} (via com sintoma de trem, a mais em rajadas) a {br(_FONTE_FORMA[1], 2)}, sempre abaixo de 1.</p>""",
"docs/relatorio/relatorio.md §4.1 e §4.2; fontes/verificacao/distribuicoes.md (teste de reescala); fontes/verificacao/modelo_taxa.md (defasagem)",
"""<p>Forma da Weibull menor que 1 quer dizer que o risco de nova falha é maior logo depois de uma falha. Todas as oito combinações ficam abaixo de 1; a Amarela nos equipamentos fixos é a mais agrupada.</p>
<p>A pergunta era se isso era só mistura de condições (pico, inverno). O teste de reescala responde que não: mesmo descontando hora, clima e oferta, sobra agrupamento.</p>
<p>Em linguagem simples: uma falha na hora anterior dobra a chance de outra no material rodante e quase triplica nos equipamentos fixos. Tratar as falhas como independentes subestima o risco.</p>
<p><b>Tempo:</b> 1 min 15 s.</p>""")

# 8 ---------------------------------------------------------------
slide("Causa comum", "45 eventos param várias linhas ao mesmo tempo, e a Laranja está em 44 deles", f"""
<div class="cols c-52-48">
  <div>
    <h3>Eventos por grupo de linhas que parou junto</h3>
    <p class="sub"><i class="sw" style="background:var(--accent)"></i>inclui Verde e Laranja: 31 eventos · <i class="sw" style="background:var(--bar)"></i>demais</p>
    {barras_grupos()}
    <ul class="lista lista-sm">
      <li>β da Verde = <b>{br(BETA_VL_V1["beta_a"], 3)}</b> (IC {br(BETA_VL_V1["beta_a_ic95"][0], 3)}–{br(BETA_VL_V1["beta_a_ic95"][1], 3)}) sobre todas as falhas. <span class="tag">após a revisão</span> 40 dos 45 eventos são de equipamento fixo; nas falhas fixas, o β da Verde é <b>{br(BETA_VL_EF["beta_a"], 3)}</b> ({br(BETA_VL_EF["beta_a_ic95"][0], 3)}–{br(BETA_VL_EF["beta_a_ic95"][1], 3)}).</li>
      <li>Duração média dos 45 eventos: <b>{br(CC_DUR_MEDIA, 1)} min</b>.</li>
    </ul>
  </div>
  <div>
    <figure class="fig-mapa">{mapa_corr}</figure>
    <p class="corpo-sm cap-mapa">No centro, Verde e Laranja são o caminho alternativo uma da outra, entre Lionel-Groulx e Berri-UQAM. A redundância supõe falhas independentes; a causa comum quebra essa hipótese.</p>
  </div>
</div>""",
"fontes/verificacao/distribuicoes.md (grupos e β); fontes/verificacao/politicas.md (44 dos 45); docs/relatorio/relatorio.md §4.2 e §7",
"""<p>Causa comum é a falha que para mais de uma linha ao mesmo tempo, como energia ou controle compartilhados.</p>
<p>São 45 eventos em 7 grupos. O mais frequente é Verde e Laranja juntas: 12 eventos só das duas, 31 contando os que pararam três ou quatro linhas. E a Laranja aparece em 44 dos 45.</p>
<p>Por que isso importa: a redundância de rota supõe que os dois caminhos falham de forma independente. O fator β é de cerca de 1% sobre todas as falhas e de cerca de 2% sobre as de equipamento fixo, que é de onde vêm quase todos os eventos. Parece pouco, mas é exatamente o evento que derruba os dois caminhos do centro juntos.</p>
<p><b>Tempo:</b> 1 min 15 s.</p>""")

# 9 ---------------------------------------------------------------
slide("Simulador · eventos discretos no navegador", "Um simulador da rede, trem a trem, que reproduz o que já sabemos antes de prever", f"""
<div class="cols c-50-50">
  <div>
    <div class="label">Como funciona</div>
    <ul class="lista">
      <li>Motor de eventos discretos em TypeScript. Cada trem segue o horário do GTFS.</li>
      <li>Falhas sorteadas pela taxa do modelo (hora, clima, oferta, cenário) e pela renovação Weibull.</li>
      <li>Material rodante para o trem; equipamento fixo bloqueia o trecho nos dois sentidos; causa comum para o grupo de linhas.</li>
      <li>Monte Carlo em Web Workers: 1.000 dias em cerca de 3 s.</li>
      <li>Mapa com os trens animados sobre o traçado real. O cenário inteiro, com a semente, fica no link.</li>
    </ul>
  </div>
  <div>
    <div class="label">Validação</div>
    <div class="val">
      <p><b>Sem falhas,</b> reproduz o horário exatamente: 26, 31, 2 e 9 trens às 08:00.</p>
      <p><b>Reserva k-de-n contra Markov</b> (Laranja, frota completa com 0, 1 e 2 reservas)</p>
      <table class="tab tab-num"><thead><tr><th></th><th>0</th><th>1</th><th>2</th></tr></thead>
        <tbody><tr><td>Simulador</td><td>0,674</td><td>0,939</td><td>0,992</td></tr><tr><td>Markov</td><td>0,671</td><td>0,938</td><td>0,992</td></tr></tbody></table>
      <p><b>Laranja, minutos por ano:</b> {"o intervalo do simulador contém os dois valores do painel." if LAR_DENTRO else '<span class="tag">após a revisão</span> com a taxa de 2025, abaixo da média de 2019 a 2026 do painel. Contra 2025: ' + f"{REV_NO_IC} de {N_COMP} médias dentro do IC."}</p>
      {faixa_laranja()}
      <p class="corpo-sm muted">1 ou 8 processos dão resultado idêntico.</p>
    </div>
  </div>
</div>""",
"docs/relatorio/relatorio.md §4.3; specs/007, 008, 009, 010 e 011 (seções Resultado); fontes/verificacao/politicas.md",
"""<p>O simulador põe cada trem do horário real na rede e sorteia as falhas com os modelos dos slides anteriores. Roda inteiro no navegador, sem servidor.</p>
<p>Antes de usá-lo para prever, conferimos que ele reproduz o que já sabemos: o horário sem falhas, o modelo de Markov da reserva de trens e os minutos parados da Laranja calculados de outros dois jeitos.</p>
<p>Após a revisão, a Laranja simulada fica abaixo do painel. Não é defeito: o simulador usa a taxa de 2025, e 2025 ficou abaixo da média de 2019 a 2026. A comparação certa passou a ser contra o próprio ano de 2025, dia a dia, com as condições de cada dia.</p>
<p>Se der tempo, abrir o simulador ao vivo (link no último slide). Hipótese declarada: separação mínima de 90 s entre trens.</p>
<p><b>Tempo:</b> 1 min 30 s.</p>""")

# 10 --------------------------------------------------------------
MENOS = "\u2212"
_lp = []
for (n, s, (v, a, b), th, od, fr, d) in POLITICAS:
    ic = f'<span class="ic">IC {MENOS}{br(b, 1)} a {MENOS}{br(a, 1)}</span>' if v else ""
    cls = "dest" if d else ""
    _lp.append(f'<tr class="{cls}"><td><b>{n}</b><br><span class="muted">{s}</span></td>'
               f'<td>{barra_politica(v, a, b, d)}{ic}</td><td class="num">{th}</td><td class="num">{od}</td><td class="num">{fr}</td></tr>')
linhas_pol = "".join(_lp)
_OD = POLITICAS[0][2][0]
_OD_V1 = -_json_v1("dados/derivados/simulador/politicas.json")["politicas"]["1"]["operacaoDegradada"]["minutos_rede"]["media"]
assert all(_OD > p[2][0] for p in POLITICAS[1:]), "revisar o título do slide 10: a operação degradada deixou de ser a maior"
slide("Políticas de tolerância a falhas · dia útil, reparo de 1 dia · após a revisão", f"Operação degradada continua a política que mais reduz minutos parados: −{br(_OD, 1)} por dia útil", f"""
<table class="tab tab-pol">
  <thead><tr><th>Política</th><th>Minutos parados a menos por dia útil<br>(soma das 4 linhas, IC 95%)</th><th class="num">Trens-hora<br>perdidos</th><th class="num">Disp. origem-<br>destino (p.p.)</th><th class="num">Frota completa<br>na Laranja (p.p.)</th></tr></thead>
  <tbody>{linhas_pol}</tbody>
</table>
<div class="tri">
  <p><b>Ataca a causa mais frequente:</b> equipamentos fixos são {br(R["falhas_ef"])} das {br(R["falhas"])} falhas técnicas.</p>
  <p><b>Reserva fria protege a oferta,</b> não a continuidade. O efeito cresce com o reparo na oficina (hipótese): {sn(P1["reservaFria"]["frota_completa_laranja_pp"]["media"], 1)} p.p. com 1 dia, {sn(P4["reservaFria"]["frota_completa_laranja_pp"]["media"], 0)} p.p. com 4 dias.</p>
  <p><b>Retorno parcial vale mais que rota alternativa</b> ({sn(P1["retornoParcial"]["disp_od_pp"]["media"], 2)} contra {sn(P1["rotaAlternativa"]["disp_od_pp"]["media"], 3)} p.p.): a rede tem poucos caminhos alternativos.</p>
</div>
<p class="nota"><span class="tag">após a revisão</span> Na v1.1.0, −{br(_OD_V1, 1)}: a queda vem das durações corrigidas pela faixa oficial (D55).</p>""",
"fontes/verificacao/politicas.md e politicas.json (e os da v1.1.0); relatório §4.3; spec 008",
f"""<p>Cada política foi comparada com "nenhuma política" usando as mesmas falhas sorteadas nas duas versões, para isolar o efeito.</p>
<p>A operação degradada, liberar o trecho em marcha lenta depois de uma falha de equipamento fixo, é a que mais reduz minutos parados e trens-hora perdidos. Faz sentido: ataca a causa mais frequente. Após a revisão, o ganho ficou menor (−{br(_OD, 1)} contra −{br(_OD_V1, 1)}), porque parte das interrupções longas de equipamento fixo eram registros com a duração contraditória.</p>
<p>A reserva fria não muda os minutos parados; ela garante a frota completa no início do dia. Quanto vale depende do tempo de reparo na oficina, que a STM não publica: por isso aparece como hipótese.</p>
<p>Retorno parcial e rota alternativa só mudam a disponibilidade origem-destino, e pouco, porque há poucos caminhos alternativos.</p>
<p><b>Tempo:</b> 1 min 30 s.</p>""")

# 11 --------------------------------------------------------------
slide("Que linha construir · disponibilidade origem-destino, dia útil", "A ligação que mais ajuda dá à Azul um caminho que não passa pela Laranja", f"""
<div class="cols c-40-60">
  <div>
    <figure class="fig-mapa">{mapa_exp}</figure>
    <p class="corpo-sm">Hoje a Azul só alcança o resto da rede pela Laranja, em Snowdon e Jean-Talon. Quando a Laranja para, a Azul fica isolada: é o maior ponto único de falha do modelo.</p>
  </div>
  <div>
    <h3>Ganho sobre a rede atual ({br(DISP_OD_ATUAL, 3)}%), sem retorno parcial</h3>
    <p class="sub">pontos percentuais, após a revisão; o traçado das candidatas é aproximado</p>
    {barras_ganho()}
    <p class="corpo-sm muted">Ramais não criam caminho alternativo e somam trechos que podem falhar. Com retorno parcial (hipótese): Rosa + Azul {_rot(_RP["rosa_2017+azul_anjou"])}; anel {_rot(_RP["laranja_anel_artm_2019"])}; Rosa {_rot(_RP["rosa_2017"])}; ramais 0.</p>
  </div>
</div>""",
"fontes/verificacao/expansao.md; dados/derivados/simulador/expansao.json; docs/relatorio/relatorio.md §4.4; specs/014-expansao-rede",
f"""<p>A pergunta foi: que ligação nova deixa a rede mais confiável como sistema? A métrica é a fração do tempo em que cada par de estações atuais tem caminho, ponderada pela oferta.</p>
<p>Entre as candidatas oficiais, só as que fecham ciclos ganham. Após a revisão, a Rosa com o prolongamento da Azul passou à frente da Rosa sozinha: o trecho novo herda as durações da Azul, que perderam as interrupções de quase 20 horas, e o ciclo que ele fecha com a Rosa passa a render. Os ramais sozinhos, inclusive o prolongamento da Azul que já está em obras, ampliam a cobertura, mas não criam redundância; sem retorno parcial, até reduzem a disponibilidade.</p>
<p>A busca entre {N_LIGACOES} ligações possíveis aponta Atwater–Université-de-Montréal, porque dá à Azul um segundo caminho que não depende da Laranja.</p>
<p>Ressalva: cobertura de bairros novos não entra, porque não há dado de passageiros.</p>
<p><b>Tempo:</b> 1 min 30 s.</p>""")

# 12 --------------------------------------------------------------
slide("Validação contra o histórico · 72 casos linha × mês, 2025-01 a 2026-06", "A versão pré-registrada não passou: 66,7% de cobertura contra 80% exigidos", f"""
<h3>Cobertura do intervalo de predição de 90%</h3>
<p class="sub">ponto cheio: pré-registrada · ponto vazio: definida depois de ver a versão A</p>
{cobertura()}
<div class="tri">
  <p><b>Por que falhou:</b> 22 dos 24 casos fora ficaram abaixo do intervalo. O modelo superestimou 2025.</p>
  <p><b>Causa:</b> herdou o efeito de 2024, ano atípico: cerca de 1.000 falhas técnicas no 2º semestre, contra cerca de 500 nos vizinhos.</p>
  <p><b>Correção testada em outro período</b> (D): 90,3%, PIT compatível com a uniforme (p&#160;=&#160;0,16). O resultado oficial continua sendo o de A.</p>
</div>
<p class="nota"><span class="tag">pós-hoc</span> Refeito com os dados revistos: A {br(POS_HOC["A"][0], 1)}%, C {br(POS_HOC["C"][0], 1)}%, D {br(POS_HOC["D"][0], 1)}%. A A falha nos equipamentos fixos ({br(_BT_FAM["A"]["EF"], 1)}%), não no material rodante ({br(_BT_FAM["A"]["MR"], 1)}%).</p>""",
"fontes/verificacao/backtest.md; specs/012-backtest (Resultado); docs/relatorio/relatorio.md §5",
"""<p>Este é o slide de que a equipe mais se orgulha, mesmo sendo um resultado negativo.</p>
<p>Ajustamos o modelo só até 2024 e previmos cada linha e mês de 2025 e 2026. O critério foi escrito antes de ver o teste: o intervalo de 90% deveria conter o observado em 80% a 98% dos casos. Deu 66,7%. Não passou.</p>
<p>O motivo: o segundo semestre de 2024 teve o dobro de falhas dos semestres vizinhos, e a versão A carregou esse efeito para 2025.</p>
<p>Não mexemos no critério. Registramos uma regra nova com data e a testamos num período diferente, como a especificação manda: 90,3%. A versão que falhou continua publicada.</p>
<p><b>Tempo:</b> 1 min 30 s.</p>""")

# 13 --------------------------------------------------------------
slide("Decisões tomadas depois de ver os dados · 2026-10-21", "Três mudanças feitas depois de ver os dados, todas registradas com data", """
<div class="cards c3 cards-alto">
  <div class="card"><h3>Duração das interrupções</h3>
    <p class="vimos"><span class="label">O que vimos</span>A média observada era maior que a da lognormal: 23% a 29% na Laranja e 26% nos equipamentos fixos da Verde; 3,4 vezes na Azul.</p>
    <p class="mudou"><span class="label">O que mudou</span>O simulador passou a sortear a duração da amostra observada. Na Laranja, de 1.433 min/ano (execução anterior à correção, registro histórico na D25), para 1.704, que contém os valores do painel.</p>
    <p class="onde">specs 006 e 009 · 2026-10-21</p></div>
  <div class="card"><h3>Causa comum por grupo</h3>
    <p class="vimos"><span class="label">O que vimos</span>Sorteada por par de linhas, a causa comum contava duas ou três vezes os eventos de 3 ou 4 linhas.</p>
    <p class="mudou"><span class="label">O que mudou</span>Passou a ser sorteada por grupo: 7 grupos, cada evento entra uma vez só.</p>
    <p class="onde">spec 006 · 2026-10-21</p></div>
  <div class="card"><h3>Efeito do ano sorteado</h3>
    <p class="vimos"><span class="label">O que vimos</span>A versão A herdava o efeito de 2024 e superestimava 2025.</p>
    <p class="mudou"><span class="label">O que mudou</span>Versão C sorteia o efeito do ano entre 2019 e 2024; retestada em outro período (D).</p>
    <p class="onde">spec 012 · 2026-10-21</p></div>
</div>
<div class="faixa">
  <div><span class="label">Exceções registradas, sem afrouxar o critério</span>98,83% das durações na faixa oficial (pedido: 99%) · 94,0% das falhas com posição (pedido: 95%) · 4 de 220 meses com erro de exposição acima de 10% (após a revisão, com o km real até 2026-06: 6 de 356)</div>
</div>""",
"specs/006, 009 e 012 (Resultado); fontes/verificacao/duracoes.md (razões das médias); fontes/verificacao/backtest.md (registro de mudança); docs/relatorio/relatorio.md §3.3 e §4.3",
"""<p>Mudar o modelo depois de ver os dados é normal; o problema é esconder. Aqui as três mudanças estão registradas com data, e o motivo de cada uma está no repositório.</p>
<p>As duas primeiras apareceram quando o simulador não batia com o painel: a média das durações estava baixa e a causa comum estava contada em dobro.</p>
<p>A terceira veio do backtest. Embaixo, as exceções aos critérios: o critério ficou como estava e o resultado aparece como exceção.</p>
<p><b>Tempo:</b> 1 min.</p>""")

# 13b -------------------------------------------------------------- revisão de 2026-11
_RZ = TF["mr_empilhado"]["razao_mr73_mpm10_verde"]
RZ_ANO = TAXA["MR"]["ano_base"] if TAXA["MR"].get("ano_base") in _RZ else max(_RZ)
RZ = _RZ[RZ_ANO]
RZ_MIN, RZ_MAX = min(v["valor"] for v in _RZ.values()), max(v["valor"] for v in _RZ.values())
LR_LINHA, GL_LINHA = TF["mr_empilhado"]["lr_linha_dentro_da_frota"], TF["mr_empilhado"]["gl"]
slide("Revisão de 2026-11 · ressegmentação por frota e setor", "Separar a frota e o setor de cada falha mudou três leituras e confirmou o resto do modelo", f"""
<div class="cards c4 cards-alto">
  <div class="card"><h3>Duração pela faixa oficial</h3>
    <p class="vimos"><span class="label">O que vimos</span>100 durações (1,2% das falhas) contradiziam a faixa oficial da STM e somavam 25% dos minutos parados; seis delas, de quase 20 h, eram "2 min ou menos".</p>
    <p class="mudou"><span class="label">O que mudou</span>Nelas vale a faixa: os minutos das falhas técnicas vão de {br(NORM["minutos_total_calculada"])} para {br(NORM["minutos_total_final"])}, e o MTTR da Azul de {br(L_V1["azul"]["mttr_min"], 2)} para {br(L["azul"]["mttr_min"], 2)} min.</p>
    <p class="onde">spec 017 · D55</p></div>
  <div class="card"><h3>A frota pesa mais que a linha</h3>
    <p class="vimos"><span class="label">O que vimos</span>Na Verde, no mesmo trilho, o MR-73 falha {br(RZ["valor"], 1)} vezes mais que o MPM-10 por trem-hora em {RZ_ANO} (IC {br(RZ["ic95"][0], 1)}–{br(RZ["ic95"][1], 1)}; {br(RZ_MIN, 1)} a {br(RZ_MAX, 1)} entre os anos).</p>
    <p class="mudou"><span class="label">O que mudou</span>O material rodante é modelado por frota, com a parcela diária medida pelo km real. A linha ainda pesa dentro da frota (razão de verossimilhança {br(LR_LINHA)}, {GL_LINHA} graus de liberdade).</p>
    <p class="onde">spec 018 · D56 e D57</p></div>
  <div class="card"><h3>O surto de 2024 é de registro</h3>
    <p class="vimos"><span class="label">O que vimos</span>De maio a dezembro de 2024, 516 falhas de via com sintoma de trem, 472 de zero minuto, quase todas nos terminais; em 2025, 52.</p>
    <p class="mudou"><span class="label">O que mudou</span>Viram uma fonte própria, e a pergunta foi para o pedido à STM. A lição da spec 012 (o efeito de um ano não passa para o seguinte) ganha a causa.</p>
    <p class="onde">specs 017 e 018 · D56</p></div>
  <div class="card"><h3>Causa comum por família</h3>
    <p class="vimos"><span class="label">O que vimos</span>40 dos 45 eventos de causa comum são de equipamento fixo, mas o β dividia por todas as falhas.</p>
    <p class="mudou"><span class="label">O que mudou</span>β da Verde com a Laranja nas falhas fixas: {br(BETA_VL_EF["beta_a"], 3)} (IC {br(BETA_VL_EF["beta_a_ic95"][0], 3)}–{br(BETA_VL_EF["beta_a_ic95"][1], 3)}), o dobro do {br(BETA_VL_V1["beta_a"], 3)} de antes.</p>
    <p class="onde">spec 018</p></div>
</div>
<div class="faixa">
  <div><span class="label">Simulador contra 2025</span>{REV_NO_IC} de {N_COMP} médias por linha × família dentro do IC 95% do observado (v1.1.0: {V1_NO_IC} de {N_COMP}).</div>
  <div><span class="label">Continua valendo</span>Binomial negativa contra Poisson, agrupamento (Weibull com forma &lt; 1), k-de-n contra Markov, motor e grafo. A v1.1.0 segue publicada em /versoes/v1.1.0/.</div>
</div>""",
"specs/017 a 020; fontes/verificacao/fontes_e_duracoes.md, taxa_por_fonte.md, revalidacao.md e revisao_2026-11.md; docs/decisoes/registro_de_decisoes.md (D55 a D63)",
f"""<p>Na reunião de 2026-10-27 a turma perguntou por fabricantes, por via ou trem e por sistemas separados. Os dados da STM separam mais do que o modelo usava: a frota no material rodante e o setor nos equipamentos fixos.</p>
<p>Refizemos tudo no lugar e congelamos a versão anterior. Três leituras mudaram: a Azul parava metade do que parecia; a frota explica boa parte do que atribuíamos à linha; e o surto de 2024 vem de um tipo de registro nos terminais, não de mais falhas.</p>
<p>O simulador revisto reproduz {REV_NO_IC} das {N_COMP} médias de 2025 dentro do intervalo do observado; a versão anterior, {V1_NO_IC}.</p>
<p><b>Tempo:</b> 1 min 30 s.</p>""")

# 14 --------------------------------------------------------------
slide("Limitações", "O que o modelo não sabe, e como isso aparece nos resultados", """
<table class="tab tab-lim">
  <thead><tr><th>Limitação</th><th>Como tratamos</th></tr></thead>
  <tbody>
    <tr><td><b>Não há passageiros diários</b></td><td>Todas as métricas são ponderadas pela oferta. A cobertura de bairros novos não entra na escolha da expansão.</td></tr>
    <tr><td><b>Reparo na oficina e aparelhos de mudança de via</b> não são públicos</td><td>Entram como hipóteses ajustáveis, com sensibilidade (reparo de 0,5 a 4 dias). O retorno parcial usa só as pontas de viagem.</td></tr>
    <tr><td><b>Setores sem definição pública</b></td><td>"Service aux trains" e "Service TCPE" ficam com o nome da STM; "controle de trens" e "energia" são dedução, que está no pedido à STM. <span class="tag">após a revisão</span> A exposição depois de 2023-09 deixou de ser estimada: o km real republicado cobre tudo.</td></tr>
    <tr><td><b>Traçado das candidatas</b></td><td>Aproximação em linha reta entre estações, exceto a Azul até Anjou (em obras no OpenStreetMap).</td></tr>
    <tr><td><b>Duração registrada</b></td><td>Mede o tempo até o serviço voltar, não o reparo do equipamento. Horários e faixa oficial às vezes se contradizem: vale a faixa nas 100 exceções (D55).</td></tr>
    <tr><td><b>Dados incompletos</b></td><td>6% das falhas sem posição (sobretudo subestações); condição do tempo só em 45,8% das horas de operação. Aparecem como falta, nunca como zero.</td></tr>
  </tbody>
</table>""",
"docs/relatorio/relatorio.md §6; fontes/FONTES.md §6; specs/002 e 003 (Resultado); fontes/verificacao/politicas.md (hipóteses)",
"""<p>As quatro primeiras são as limitações do relatório. A principal é a falta de passageiros: sem ela, não dá para dizer quantas pessoas cada falha atinge, só quantos trens.</p>
<p>O que não vem dos dados aparece marcado como hipótese, com análise de sensibilidade, e o simulador mostra o rótulo ao lado do número.</p>
<p><b>Tempo:</b> 45 s.</p>""")

# 15 --------------------------------------------------------------
_DISP = [POL["disponibilidade_dia_util"][l]["media"] * 100 for l in ORDEM]
slide("Conclusões · após a revisão", f"Linhas com {br(min(_DISP), 1)}% a {br(max(_DISP), 1)}% de disponibilidade num dia útil (simulador), numa rede que depende de poucos pontos", f"""
<ol class="conclusoes">
  <li><h3>As falhas se agrupam e têm causa comum.</h3><p>No tempo, uma falha dobra ou quase triplica a chance de outra na hora seguinte. No espaço, eventos que param Verde e Laranja juntas tiram a única redundância de rota do centro. Tratar as falhas como independentes subestima o risco.</p></li>
  <li><h3>A política que mais rende ataca os equipamentos fixos.</h3><p>Eles são mais da metade das falhas. A operação degradada reduz mais os minutos parados do que reservar trens; a reserva protege a oferta.</p></li>
  <li><h3>Uma linha nova vale pelos caminhos alternativos que cria.</h3><p>Ramais ampliam a cobertura, mas não criam redundância. O maior ponto único de falha é a dependência da Azul em relação à Laranja.</p></li>
</ol>
<div class="faixa">
  <div><span class="label">Revisão de 2026-11</span>A frota pesa mais que a linha (MR-73 falha cerca de {br(RZ["valor"], 0)} vezes mais que o MPM-10 na Verde), e o surto de 2024 é de registro nos terminais. As três conclusões continuam valendo com os números revistos.</div>
  <div><span class="label">Limite do modelo</span>O efeito de um ano não se transfere para o seguinte: a previsão precisa carregar a incerteza entre anos. Somar fontes independentes agrupa menos que o observado nos equipamentos fixos da Verde.</div>
  <div><span class="label">Próximos passos</span>Pedir à STM passageiros diários, posição das subestações e tempo de reparo; repetir o backtest com o motor TypeScript.</div>
</div>""",
"docs/relatorio/relatorio.md §7; disponibilidade em dia útil: fontes/verificacao/politicas.md",
"""<p>Três conclusões para a decisão, na ordem das perguntas do início.</p>
<p>Cada linha, isolada, tem disponibilidade alta. O risco está no sistema: falhas que vêm juntas, eventos que param duas linhas de uma vez e uma linha inteira, a Azul, que depende de outra.</p>
<p>E o que aprendemos com o backtest: a incerteza entre anos precisa entrar na previsão.</p>
<p><b>Tempo:</b> 1 min.</p>""")

# 16 --------------------------------------------------------------
BASE = "https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/"
REPOURL = "https://github.com/felipe44776-eseg/confiabilidade-metro-montreal"
slide("Confira você mesmo", "Tudo é público: site, simulador, dados e o comando que refaz as contas", f"""
<div class="cols c-55-45">
  <div>
    <ul class="links">
      <li><span class="label">Site</span><a href="{BASE}">{BASE.replace("https://", "")}</a></li>
      <li><span class="label">Simulador</span><a href="{BASE}simulador/">{BASE.replace("https://", "")}simulador/</a></li>
      <li><span class="label">Mapa</span><a href="{BASE}mapa/">{BASE.replace("https://", "")}mapa/</a></li>
      <li><span class="label">Fontes e verificação</span><a href="{BASE}fontes/">{BASE.replace("https://", "")}fontes/</a></li>
      <li><span class="label">Repositório</span><a href="{REPOURL}">{REPOURL.replace("https://", "")}</a></li>
    </ul>
  </div>
  <div>
    <div class="label">Refazer as contas, sem confiar na equipe</div>
    <pre class="cmd">python -I pipeline/verifica_fontes.py \\
  --baixa-release --recalcula</pre>
    <p class="corpo-sm">Baixa os dados da Release, confere cada SHA-256 e recalcula {N_RECALC} números com código independente do pipeline. Python 3.11, sem biblioteca extra.</p>
    <div class="obrigado">Obrigado. Perguntas?</div>
    <p class="corpo-sm muted">Ana Paula Duanetti · Felipe Marins<br>Lorena Feitosa de Freitas · Sophia Braz</p>
  </div>
</div>""",
"fontes/FONTES.md (Como conferir sozinho); docs/relatorio/relatorio.md (cabeçalho e apêndice)",
"""<p>Mostrar que qualquer pessoa da turma pode rodar a verificação. Se houver tempo, abrir o simulador e trocar um cenário ao vivo, por exemplo um dia de neve.</p>
<p>Abrir para perguntas.</p>
<p><b>Tempo:</b> 30 s.</p>""")

# ---------------------------------------------------------------- CSS / JS
CSS = r"""
:root{
  --slide-w:1280px; --slide-h:720px; --s:1;
  --page:#E6E7EA; --surface:#FBFBFA; --zebra:#F3F3F1;
  --ink:#15181C; --ink-2:#3F454D; --muted:#5F666E; --rule:#D3D7DC; --rule-2:#E7E9EC;
  --accent:#4A3A8C; --accent-soft:#ECE9F5; --bar:#7B828B;
}
*{box-sizing:border-box}
html{scroll-snap-type:y mandatory;background:var(--page)}
body{margin:0;font-family:"Segoe UI",system-ui,-apple-system,"Helvetica Neue",Roboto,Arial,sans-serif;color:var(--ink);
  -webkit-print-color-adjust:exact;print-color-adjust:exact;-webkit-font-smoothing:antialiased}
.frame{height:100vh;display:flex;align-items:center;justify-content:center;scroll-snap-align:start;overflow:hidden}
.frame-in{width:calc(var(--slide-w) * var(--s));height:calc(var(--slide-h) * var(--s));flex:none}
.slide{width:var(--slide-w);height:var(--slide-h);overflow:hidden;position:relative;display:flex;flex-direction:column;
  background:var(--surface);transform:scale(var(--s));transform-origin:0 0;box-shadow:0 2px 20px rgba(20,24,28,.16);
  padding:40px 64px 0}
.slide > header{flex:none;margin-bottom:22px}
.slide > header::before{content:"";display:block;width:56px;height:4px;margin-bottom:16px;
  background:linear-gradient(90deg,#008E4F 0 25%,#EF8122 25% 50%,#FFD900 50% 75%,#0076BE 75%)}
.eyebrow{font-size:14px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
h1{font-size:50px;line-height:1.08;font-weight:700;letter-spacing:-.01em;margin:0 0 14px}
h2{font-size:33px;line-height:1.16;font-weight:650;letter-spacing:-.005em;margin:0;max-width:1120px;text-wrap:balance}
h3{font-size:19px;font-weight:650;margin:0 0 2px}
.slide-body{flex:1;min-height:0;padding-bottom:50px;position:relative}
.slide > footer{position:absolute;left:64px;right:64px;bottom:0;height:40px;border-top:1px solid var(--rule);
  display:flex;align-items:center;justify-content:space-between;gap:24px;font-size:11.5px;color:var(--muted)}
.slide > footer .pg{font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap;flex:none}
.label{display:block;font-size:13px;font-weight:650;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.sub{font-size:15px;color:var(--muted);margin:0 0 10px}
.muted{color:var(--muted)}
.lede{font-size:26px;color:var(--ink-2);margin:0 0 40px}
.nota{font-size:14.5px;line-height:1.4;color:var(--ink-2);margin:14px 0 0;max-width:1150px}
.corpo-sm{font-size:16px;line-height:1.45;margin:10px 0 0}
code{font-family:"Cascadia Mono",Consolas,"SFMono-Regular",Menlo,monospace;font-size:.88em;background:var(--rule-2);padding:1px 5px;border-radius:4px}
b{font-weight:650}
.cols{display:grid;gap:44px}
.cap-mapa{max-width:500px;margin:8px auto 0}
.c-60-40{grid-template-columns:3fr 2fr}.c-50-50{grid-template-columns:1fr 1fr}.c-52-48{grid-template-columns:52fr 48fr}
.c-40-60{grid-template-columns:40fr 60fr;gap:32px}.c-55-45{grid-template-columns:55fr 45fr}
.lista{margin:0;padding-left:20px;font-size:19px;line-height:1.42}
.lista li{margin:0 0 10px}
.lista-sm{font-size:16.5px}
.lista-sm li{margin-bottom:6px}
.caixa{background:var(--zebra);border-radius:10px;padding:22px 26px}
.perguntas{margin:0;padding:0;list-style:none;counter-reset:q}
.perguntas li{counter-increment:q;position:relative;padding:0 0 0 58px;margin:0 0 22px;font-size:21px;line-height:1.38}
.perguntas li::before{content:counter(q);position:absolute;left:0;top:-2px;width:38px;height:38px;border-radius:50%;
  border:2px solid var(--accent);color:var(--accent);font-weight:700;font-size:19px;display:flex;align-items:center;justify-content:center}
.faixa{display:flex;gap:40px;border-top:1px solid var(--rule);padding-top:14px;margin-top:20px;font-size:16.5px;line-height:1.4}
.faixa > div{flex:1}
.faixa .label{margin-bottom:4px}
.cards{display:grid;gap:18px}
.c3{grid-template-columns:repeat(3,1fr)}
.c4{grid-template-columns:repeat(4,1fr);gap:14px}
.c4 .card{padding:14px 14px 12px}
.c4 .card p{font-size:14px;line-height:1.36}
.c4 .card h3{font-size:17px}
.card{border:1px solid var(--rule);border-radius:10px;padding:18px 20px 16px;background:#fff;position:relative}
.card h3{margin-bottom:6px}
.card p{font-size:16px;line-height:1.42;margin:0}
.card-k{position:absolute;top:16px;right:18px;font-size:14px;font-weight:700;color:var(--accent)}
.tag{display:inline-block;margin-top:6px;font-size:13px;font-weight:600;color:var(--accent);background:var(--accent-soft);border-radius:4px;padding:2px 8px}
.cards-alto .card p{margin-bottom:12px}
.cards-alto .label{margin-bottom:2px;font-size:12px}
.cards-alto .onde{font-size:13.5px;color:var(--accent);font-weight:600;margin:0}
.tab{border-collapse:collapse;width:100%;font-size:16px;line-height:1.38}
.tab th{text-align:left;font-size:13px;font-weight:650;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);
  border-bottom:1.5px solid var(--ink-2);padding:6px 10px 6px 0}
.tab td{border-bottom:1px solid var(--rule);padding:9px 12px 9px 0;vertical-align:top}
.tab .num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.tab-num{width:auto;margin:4px 0 14px;font-size:16px}
.tab-num th,.tab-num td{padding:4px 22px 4px 0;text-align:right;font-variant-numeric:tabular-nums}
.tab-num th:first-child,.tab-num td:first-child{text-align:left}
.tab-pol{font-size:15.5px;line-height:1.3}
.tab-pol td{vertical-align:middle;padding:5px 14px 5px 0}
.tab-pol td:nth-child(2){white-space:nowrap}
.tab-pol svg{vertical-align:middle}
.tab-pol .ic{font-size:13.5px;color:var(--muted);margin-left:2px;font-variant-numeric:tabular-nums}
.tab-pol tr.dest td:first-child b{color:var(--accent)}
.tab-lim td{padding:11px 16px 11px 0;font-size:17.5px}
.tab-lim td:first-child{width:38%}
.tri{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:14px}
.tri p{margin:0;font-size:16.5px;line-height:1.42;border-left:3px solid var(--accent);padding-left:14px}
.multiplos{display:grid;grid-template-columns:repeat(3,1fr);gap:26px}
.multiplos h3{font-size:21px}
.disp{display:grid;grid-template-columns:1.05fr repeat(4,1fr);gap:18px;align-items:center;margin-top:18px;
  border-top:1px solid var(--rule);padding-top:16px}
.disp .sub{margin:0}
.tile-l{display:flex;gap:10px;align-items:flex-start}
.tile-l .chip{margin-top:9px}
.tile-v{font-size:30px;font-weight:650;line-height:1.1}
.tile-s{font-size:14px;color:var(--muted)}
.chip{display:inline-block;width:14px;height:14px;border-radius:50%;vertical-align:-1px;margin-right:6px;flex:none}
.chip.am,.legenda i.am{box-shadow:inset 0 0 0 1.25px #A38B00}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-1px;margin:0 6px 0 0}
.sub .sw + *{margin-left:0}
.legenda{display:flex;gap:18px;font-size:15px;color:var(--ink-2);margin-top:6px;flex-wrap:wrap}
.legenda .lg{display:inline-flex;align-items:center;gap:7px}
.legenda i{display:inline-block;width:22px;height:7px;border-radius:4px}
.stats{display:flex;flex-direction:column;gap:22px;padding-top:6px}
.stat-v{font-size:46px;font-weight:650;line-height:1;color:var(--accent)}
.stat-l{font-size:17px;line-height:1.38;margin-top:6px}
.val p{font-size:17px;line-height:1.4;margin:0 0 6px}
.capa-slide{padding-top:64px}
.capa{display:grid;grid-template-columns:1fr 470px;gap:36px;height:100%}
.capa-txt{display:flex;flex-direction:column;justify-content:center;padding-bottom:70px}
.capa-txt::before{content:"";display:block;width:84px;height:6px;margin-bottom:26px;
  background:linear-gradient(90deg,#008E4F 0 25%,#EF8122 25% 50%,#FFD900 50% 75%,#0076BE 75%)}
.equipe p{font-size:21px;line-height:1.45;margin:0}
.url{font-size:16px;color:var(--muted);margin:34px 0 0}
.capa-mapa{margin:0;align-self:center}
figure{margin:0}
figcaption{font-size:12.5px;color:var(--muted);margin-top:6px}
.fig-mapa{display:flex;justify-content:center}
.links{list-style:none;margin:0;padding:0}
.links li{padding:12px 0;border-bottom:1px solid var(--rule);font-size:17px}
.links .label{margin-bottom:2px}
.links a{color:var(--ink);text-decoration:none;border-bottom:1.5px solid var(--accent)}
.cmd{font-family:"Cascadia Mono",Consolas,Menlo,monospace;font-size:17px;line-height:1.45;background:#15181C;color:#F2F2F0;
  border-radius:8px;padding:16px 20px;margin:0}
.obrigado{font-size:34px;font-weight:650;margin-top:34px}
.conclusoes{margin:0;padding:0;list-style:none;counter-reset:c;display:grid;grid-template-columns:repeat(3,1fr);gap:30px}
.conclusoes li{counter-increment:c;border-top:4px solid var(--accent);padding-top:14px}
.conclusoes li::before{content:counter(c);display:block;font-size:40px;font-weight:700;color:var(--accent);line-height:1;margin-bottom:10px}
.conclusoes h3{font-size:21px;line-height:1.25;margin-bottom:8px}
.conclusoes p{font-size:17px;line-height:1.42;margin:0}
/* graficos */
svg text{font-family:inherit}
.c-lab{font-size:16px;fill:var(--ink)}
.c-sm{font-size:15px}
.c-val{font-size:16px;font-weight:650;fill:var(--ink);font-variant-numeric:tabular-nums}
.c-num{font-size:15px;fill:var(--ink);font-variant-numeric:tabular-nums}
.c-forte{font-weight:700}
.c-fraco{fill:var(--muted)}
.c-head{font-size:13px;font-weight:650;letter-spacing:.05em;text-transform:uppercase;fill:var(--muted)}
.c-head2{font-size:14px;font-weight:650;fill:var(--ink-2)}
.c-tick{font-size:13px;fill:var(--muted);font-variant-numeric:tabular-nums}
.c-acc{font-size:14px;font-weight:600;fill:var(--accent)}
.c-acc-t{fill:var(--accent);font-weight:650}
.c-sm-t{font-size:14px;fill:var(--ink-2)}
.c-in{font-size:15px;fill:#fff;font-weight:600}
.c-k{font-weight:700;fill:var(--accent)}
.grade{stroke:var(--rule-2);stroke-width:1}
.eixo{stroke:var(--rule);stroke-width:1}
.ref{stroke:var(--ink-2);stroke-width:1.25}
.m-lab{font-size:13.5px;fill:var(--ink);font-weight:600;paint-order:stroke;stroke:var(--surface);stroke-width:4px;stroke-linejoin:round}
.m-fraco{fill:var(--muted);font-weight:500}
.m-acc{fill:var(--accent);font-weight:700}
/* tela */
.notes{display:none}
#pos{position:fixed;right:16px;top:10px;font:600 13px/1 "Segoe UI",system-ui,sans-serif;color:#fff;background:rgba(21,24,28,.72);
  padding:7px 10px;border-radius:6px;z-index:10;font-variant-numeric:tabular-nums}
#ajuda{position:fixed;left:16px;top:10px;font:600 12px/1 "Segoe UI",system-ui,sans-serif;color:#fff;background:rgba(21,24,28,.72);
  padding:7px 10px;border-radius:6px;z-index:10;transition:opacity .8s}
#painel-notas{display:none;position:fixed;left:0;right:0;bottom:0;height:34vh;overflow:auto;background:#15181C;color:#F2F2F0;
  font:18px/1.5 "Segoe UI",system-ui,sans-serif;padding:16px 28px 40px;z-index:9}
#painel-notas p{margin:0 0 8px;max-width:1100px}
body.com-notas #painel-notas{display:block}
body.com-notas .frame{align-items:flex-start;padding-top:10px}
#check-out{white-space:pre;font:12px monospace}
@page{size:1280px 720px;margin:0}
@media print{
  html{scroll-snap-type:none;background:#fff}
  html,body{margin:0;padding:0;background:#fff}
  .frame{height:auto;display:block;overflow:visible;padding:0!important;break-after:page;page-break-after:always}
  .frame:last-of-type{break-after:auto;page-break-after:auto}
  .frame-in{width:auto;height:auto}
  .slide{transform:none!important;box-shadow:none;break-inside:avoid;page-break-inside:avoid}
  .no-print,#check-out{display:none!important}
}
"""

JS = r"""
(function(){
  var raiz=document.documentElement, sc=document.scrollingElement||raiz;
  var frames=[].slice.call(document.querySelectorAll('.frame')), N=frames.length, idx=0;
  var pos=document.getElementById('pos'), painel=document.getElementById('painel-notas');
  var verifica=/[?&]check\b/.test(location.search);
  function ajusta(){
    if(verifica){raiz.style.setProperty('--s','1');return;}
    var notas=document.body.classList.contains('com-notas');
    var h=notas? innerHeight*0.66-14 : innerHeight;
    var s=Math.min(innerWidth/1280, h/720);
    raiz.style.setProperty('--s', (s>0? s:1).toFixed(4));
  }
  function atual(){ return Math.max(0, Math.min(N-1, Math.round(sc.scrollTop/innerHeight))); }
  function mostra(i){
    idx=i; pos.textContent=(i+1)+' / '+N;
    if(document.body.classList.contains('com-notas')){
      var a=frames[i].querySelector('aside.notes');
      painel.innerHTML='<p style="opacity:.6;font-size:14px">Notas · slide '+(i+1)+' de '+N+'</p>'+(a? a.innerHTML:'');
    }
    if(history.replaceState) history.replaceState(null,'','#'+(i+1));
  }
  function vai(i){ i=Math.max(0,Math.min(N-1,i)); sc.scrollTop=i*innerHeight; mostra(i); }
  function telaCheia(){
    if(!document.fullscreenElement){ (raiz.requestFullscreen? raiz.requestFullscreen(): Promise.resolve()).catch(function(){}); }
    else if(document.exitFullscreen){ document.exitFullscreen(); }
  }
  function notas(){ document.body.classList.toggle('com-notas'); ajusta(); vai(idx); }
  addEventListener('keydown',function(e){
    if(e.altKey||e.ctrlKey||e.metaKey) return;
    var k=e.key;
    if(k==='ArrowRight'||k==='ArrowDown'||k==='PageDown'||(k===' '&&!e.shiftKey)){e.preventDefault();vai(idx+1);}
    else if(k==='ArrowLeft'||k==='ArrowUp'||k==='PageUp'||(k===' '&&e.shiftKey)){e.preventDefault();vai(idx-1);}
    else if(k==='Home'){e.preventDefault();vai(0);}
    else if(k==='End'){e.preventDefault();vai(N-1);}
    else if(k==='f'||k==='F'){e.preventDefault();telaCheia();}
    else if(k==='n'||k==='N'){e.preventDefault();notas();}
  });
  var t; addEventListener('scroll',function(){clearTimeout(t);t=setTimeout(function(){var i=atual(); if(i!==idx) mostra(i);},90);},{passive:true});
  addEventListener('resize',function(){ajusta(); vai(idx);});
  var solo=/[?&]solo=(\d+)/.exec(location.search);
  if(solo){ frames.forEach(function(f,i){ if(i!==+solo[1]-1) f.style.display='none'; }); }
  if(/[?&]notas\b/.test(location.search)) document.body.classList.add('com-notas');
  ajusta();
  var h=parseInt((location.hash||'').slice(1),10);
  if(h>=1&&h<=N) vai(h-1); else mostra(0);
  addEventListener('load',function(){ if(h>=1&&h<=N&&!solo) vai(h-1); });
  var dica=document.getElementById('ajuda');
  setTimeout(function(){ dica.style.opacity='0'; }, 6000);
  if(verifica){
    var out=[];
    document.querySelectorAll('.slide').forEach(function(s,i){
      var r=s.getBoundingClientRect(), lim=r.top+720-42, pior=0, quem='';
      s.querySelectorAll('header *, .slide-body *').forEach(function(el){
        if(el.closest('.notes')) return;
        var b=el.getBoundingClientRect(); if(!b.width&&!b.height) return;
        var exc=Math.max(b.bottom-lim, b.right-(r.left+1280-36), (r.left+36)-b.left, r.top+20-b.top, 0);
        if(exc>pior){pior=exc; quem=el.tagName+' "'+(el.textContent||'').trim().slice(0,50)+'"';}
      });
      var body=s.querySelector('.slide-body'), bb=body.getBoundingClientRect();
      out.push('slide '+(i+1)+': '+(pior>0.5? 'EXCEDE '+pior.toFixed(1)+'px '+quem : 'ok')+' | conteudo ate y='+Math.round(maxBottom(s)-r.top));
    });
    function maxBottom(s){var m=0; s.querySelectorAll('.slide-body *').forEach(function(el){var b=el.getBoundingClientRect(); if(b.height&&b.bottom>m) m=b.bottom;}); return m;}
    var ep=document.elementFromPoint(innerWidth/2, innerHeight/2), es=ep&&ep.closest('.slide');
    out.push('nav: idx='+idx+' scrollTop='+sc.scrollTop+' innerHeight='+innerHeight+' frameTop='+Math.round(frames[idx].getBoundingClientRect().top)+' centro=slide '+(es? es.dataset.n:'nenhum'));
    var pre=document.createElement('pre'); pre.id='check-out'; pre.textContent=out.join('\n'); document.body.appendChild(pre);
  }
})();
"""

def monta():
    partes = []
    N = len(SLIDES)
    for i, s in enumerate(SLIDES, 1):
        cab = ""
        if s["titulo"]:
            cab = f'<header><div class="eyebrow">{s["eyebrow"]}</div><h2>{s["titulo"]}</h2></header>'
        partes.append(
            f'<div class="frame" id="s{i}"><div class="frame-in"><section class="slide {s["classe"]}" data-n="{i}" aria-label="Slide {i} de {N}">'
            f'{cab}<div class="slide-body">{s["corpo"]}</div>'
            f'<footer><span>Fonte: {s["fonte"]}</span><span class="pg">dados {VERSAO_DADOS} · {i}</span></footer>'
            f'<aside class="notes no-print">{s["notas"]}</aside>'
            f'</section></div></div>')
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<link rel="icon" href="data:,">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Confiabilidade e tolerância a falhas do metrô de Montreal · apresentação</title>
<style>{CSS}</style>
</head>
<body>
{"".join(partes)}
<div id="pos" class="no-print">1 / {N}</div>
<div id="ajuda" class="no-print">→ ← espaço · F tela cheia · N notas</div>
<div id="painel-notas" class="no-print" aria-live="polite"></div>
<script>{JS}</script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"{N} slides -> {OUT} ({len(html.encode('utf-8')) / 1024:.0f} KB)")

monta()
