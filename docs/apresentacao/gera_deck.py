# Gera os dois decks autocontidos, na identidade visual da ESEG (docs/apresentacao/marca/LEIAME.md):
#   docs/apresentacao/index.html    executiva, para a turma
#   docs/apresentacao/interna.html  interna e detalhada, para a equipe: tudo o que foi feito desde 2026-10-20
# Uso, da raiz: python -I docs/apresentacao/gera_deck.py
# Os números vêm dos JSON gerados pelo pipeline (e da etiqueta v1.1.0, para o antes e depois); cada slide cita a fonte no rodapé.
# PDF: Chrome sem janela, --print-to-pdf (página 1280 x 720, sem margens).
import base64, csv, json, math, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # raiz do repositorio
DIR = os.path.join(REPO, "docs", "apresentacao")
OUT_EXEC = os.path.join(DIR, "index.html")
OUT_INT = os.path.join(DIR, "interna.html")
_MARCA = os.path.join(DIR, "marca")
LOGO_BRANCO = open(os.path.join(_MARCA, "eseg-logo-branco.svg"), encoding="utf-8").read()
LOGO_MARINHO = open(os.path.join(_MARCA, "eseg-logo-marinho.svg"), encoding="utf-8").read()
FONTE_B64 = base64.b64encode(open(os.path.join(_MARCA, "public-sans-latin-wght.woff2"), "rb").read()).decode("ascii")

def logo(svg, altura, classe=""):
    """Logo da ESEG (89 x 64) na altura pedida, com texto alternativo."""
    w = round(89 * altura / 64, 1)
    return svg.replace('width="89" height="64"', f'width="{w}" height="{altura}" class="logo {classe}" role="img" aria-label="Faculdade ESEG, Grupo Etapa"', 1)
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
            sn(p["disp_od_pp"]["media"], 2 if abs(p["disp_od_pp"]["media"]) >= 0.01 or p["disp_od_pp"]["media"] == 0 else 3),
            sn(p["frota_completa_laranja_pp"]["media"], 1), chave == "operacaoDegradada")

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

SLIDES = []  # registro de todos os slides; cada deck escolhe os seus no fim

def slide(eyebrow, titulo, corpo, fonte, notas, classe=""):
    s = dict(eyebrow=eyebrow, titulo=titulo, corpo=corpo, fonte=fonte, notas=notas, classe=classe)
    SLIDES.append(s)
    return s

def capa(lede, rotulo, notas):
    """Capa em marinho, com o logo da ESEG e o mapa das quatro linhas."""
    return slide("", "", f"""
<div class="capa">
  <div class="capa-txt">
    {logo(LOGO_BRANCO, 76)}
    <div class="eyebrow">Sistemas Tolerantes a Falhas · Engenharia de Produção · 2026</div>
    <h1>Confiabilidade e tolerância a falhas do metrô de Montreal</h1>
    <p class="lede">{lede}</p>
    <div class="equipe">
      <div class="label">{rotulo}</div>
      <p>Ana Paula Duanetti · Felipe Marins<br>Lorena Feitosa de Freitas · Sophia Braz</p>
    </div>
    <p class="url">felipe44776-eseg.github.io/confiabilidade-metro-montreal</p>
  </div>
  <figure class="capa-mapa">{mapa_titulo}{legenda_linhas()}
    <figcaption>Posição das estações no GTFS da STM; linhas ligadas em linha reta entre estações.</figcaption>
  </figure>
</div>""", "docs/equipe.json; dados/derivados/gtfs/metro_sequencias.csv (mapa)", notas, "capa-slide escuro")

def divisor(n, titulo, sub, notas=""):
    """Divisória de parte, em marinho (só no deck interno)."""
    return slide("", "", f"""
<div class="div-in">
  <div class="div-n">{n:02d}</div>
  <h1>{titulo}</h1>
  <p class="lede">{sub}</p>
</div>""", "", notas or f"<p>Abertura da parte {n}: {esc(titulo)}.</p>", "divisor escuro")

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
  <div class="card"><div class="card-k">5</div><h3>Reprodução do zero</h3><p><code>reproduz.yml</code> refaz o pipeline numa máquina limpa e compara com o publicado. <span class="tag">passou em 2026-10-21 (commit a7f0594): 48 idênticos, 5 na tolerância, 0 fora; não refeita após a revisão de 2026-11</span></p></div>
  <div class="card"><div class="card-k">6</div><h3>Decisões com data (SDD)</h3><p>Critério de aceite escrito antes do código. Se o resultado não atende, vira exceção registrada: o critério não é afrouxado.</p></div>
</div>
<p class="nota">Verificação na origem: em 2026-10-20, 26 das 27 fontes baixadas de novo vieram idênticas byte a byte; a 27ª (mobilidade do Google, 98 MB) foi conferida pelo tamanho.</p>""",
"docs/relatorio/relatorio.md §3.2; fontes/FONTES.md (resultado local, §5); specs/constitution.md; specs/013-publicacao/spec.md (Resultado) e tasks.md",
f"""<p>Este slide vem antes dos resultados de propósito: a equipe quis que ninguém precisasse confiar em quem fez as contas.</p>
<p>Destacar o item 2: um segundo programa, escrito à parte, refaz {N_RECALC} números direto dos dados brutos e chega ao mesmo valor. E o item 3: o site não publica se essa conferência falhar.</p>
<p>Item 5: a reprodução do zero rodou no GitHub Actions em 2026-10-21. A primeira execução reproduziu todos os resultados e só acusou metadados (commit e tempo de execução gravados nos relatórios); depois da correção, a segunda deu 45 arquivos idênticos byte a byte, 8 dentro da tolerância e nenhum fora. No commit ba19e74, com o hash do código também comparado, a execução 39556506384 deu 48 idênticos, 5 dentro da tolerância e 0 fora; a última, no a7f0594 (39609801611), deu o mesmo. Depois da revisão de 2026-11 a reprodução não foi refeita: a execução agendada de 2026-11-01 falhou na integridade dos JSON da NHL baixados da origem, e a equipe desligou a agenda (D65). Os números revistos ficam conferidos pelo deploy, que recalcula 38 números com código próprio e roda os testes.</p>
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
  <p><b>Calor</b> pesa só nos equipamentos fixos (+{br(100 * (_CALOR[2][0] - 1))}%), e vem sobretudo da via. <b>Frio intenso</b> não tem efeito detectável.</p>
  <p><b>Binomial negativa vence Poisson</b> nas duas causas (α = {br(TAXA["MR"]["alpha_nb"], 2)} e {br(TAXA["EF"]["alpha_nb"], 2)}; p &lt; 10⁻³⁰).</p>
</div>
<p class="nota">Vazio e em cinza: intervalo de 95% contém 1. Referência: Laranja, entrepico, dia útil, outono, 5 a 15 °C, sem precipitação. IC por bootstrap em blocos semanais (B = {TAXA["MR"]["bootstrap_b"]}).</p>""",
"relatório §4.1; fontes/verificacao/modelo_taxa.md e taxa_por_fonte.md; dados/derivados/modelos/taxa_MR.json e taxa_EF.json",
f"""<p>Cada ponto é quanto um fator multiplica a taxa de falha por trem-hora, com o intervalo de 95%. À direita do 1, aumenta; à esquerda, diminui.</p>
<p>O maior efeito é a abertura do serviço, das 5 às 6 h: a taxa fica {br(_AB[1][0], 1)} vezes maior no material rodante e {br(_AB[2][0], 1)} vezes nos equipamentos fixos. Por fonte, a abertura eleva todas; na energia (TCPE), a taxa fica {br(_TCPE_AB, 1)} vezes maior, o que lemos como falha ao energizar a rede.</p>
<p>Neve acumulada acima de 10 cm eleva as duas causas em cerca de {br(100 * (_NEVE[1][0] - 1))}%. Calor de 25 °C ou mais pesa nos equipamentos fixos, e por fonte ele vem sobretudo da via. O frio intenso, que seria o palpite óbvio em Montreal, não aparece.</p>
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
<p><b>Tempo:</b> 1 min 30 s.</p>""", "compacto")

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
<p class="nota"><span class="tag">pós-hoc</span> Refeito com os dados revistos: A {br(POS_HOC["A"][0], 1)}%, C {br(POS_HOC["C"][0], 1)}%, D {br(POS_HOC["D"][0], 1)}%. A versão A falha nos equipamentos fixos ({br(_BT_FAM["A"]["EF"], 1)}%), não no material rodante ({br(_BT_FAM["A"]["MR"], 1)}%).</p>""",
"fontes/verificacao/backtest.md; specs/012-backtest (Resultado); docs/relatorio/relatorio.md §5",
"""<p>Este é o slide de que a equipe mais se orgulha, mesmo sendo um resultado negativo.</p>
<p>Ajustamos o modelo só até 2024 e previmos cada linha e mês de 2025 e 2026. O critério foi escrito antes de ver o teste: o intervalo de 90% deveria conter o observado em 80% a 98% dos casos. Deu 66,7%. Não passou.</p>
<p>O motivo: o segundo semestre de 2024 teve o dobro de falhas dos semestres vizinhos, e a versão A carregou esse efeito para 2025.</p>
<p>Não mexemos no critério. Registramos uma regra nova com data e a testamos num período diferente, como a especificação manda: 90,3%. A versão que falhou continua publicada.</p>
<p><b>Tempo:</b> 1 min 30 s.</p>""", "compacto")

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
    <p class="mudou"><span class="label">O que mudou</span>Viram uma fonte própria; por que a STM os registra assim fica em aberto. A lição da spec 012 (o efeito de um ano não passa para o seguinte) ganha a causa.</p>
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
    <tr><td><b>Setores sem definição pública</b></td><td>"Service aux trains" e "Service TCPE" ficam com o nome da STM; "controle de trens" e "energia" são dedução, sem confirmação da STM.</td></tr>
    <tr><td><b>Exposição depois de 2023-09</b></td><td><span class="tag">após a revisão</span> Deixou de ser estimada: o km real republicado pela STM cobre o período todo no modelo e no simulador.</td></tr>
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
/* Identidade da ESEG: cores e fonte do site eseg.edu.br (docs/apresentacao/marca/LEIAME.md).
   Public Sans: SIL Open Font License 1.1, The Public Sans Project Authors (github.com/uswds/public-sans). */
@font-face{font-family:"Public Sans";font-style:normal;font-weight:100 900;font-display:block;
  src:url(data:font/woff2;base64,__FONTE__) format("woff2")}
:root{
  --slide-w:1280px; --slide-h:720px; --s:1;
  --navy:#08223D; --turq:#00A1B8; --ouro:#F1B634;
  --page:#E5E6E7; --surface:#FFFFFF; --zebra:#FAFAFA;
  --ink:#0F1322; --ink-2:#333643; --muted:#474A56; --rule:#C2C3C7; --rule-2:#E5E6E7;
  --accent:#00A1B8; --accent-soft:rgba(0,161,184,.13); --accent-text:#08223D; --bar:#999BA1;
  --ouro-soft:rgba(241,182,52,.30);
}
*{box-sizing:border-box}
html{scroll-snap-type:y mandatory;background:var(--page)}
body{margin:0;font-family:"Public Sans","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Roboto,Arial,sans-serif;color:var(--ink);
  -webkit-print-color-adjust:exact;print-color-adjust:exact;-webkit-font-smoothing:antialiased}
.frame{height:100vh;display:flex;align-items:center;justify-content:center;scroll-snap-align:start;overflow:hidden}
.frame-in{width:calc(var(--slide-w) * var(--s));height:calc(var(--slide-h) * var(--s));flex:none}
.slide{width:var(--slide-w);height:var(--slide-h);overflow:hidden;position:relative;display:flex;flex-direction:column;
  background:var(--surface);transform:scale(var(--s));transform-origin:0 0;box-shadow:0 2px 20px rgba(20,24,28,.16);
  padding:40px 64px 0}
.slide > header{flex:none;margin-bottom:22px}
.slide > header::before{content:"";display:block;width:64px;height:4px;margin-bottom:16px;
  background:linear-gradient(90deg,var(--turq) 0 72%,var(--ouro) 72%)}
.eyebrow{font-size:14px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
h1{font-size:50px;line-height:1.08;font-weight:700;letter-spacing:-.015em;margin:0 0 14px;color:var(--navy)}
h2{font-size:32px;line-height:1.16;font-weight:600;letter-spacing:-.01em;margin:0;max-width:1120px;text-wrap:balance;color:var(--navy)}
h3{font-size:19px;font-weight:600;margin:0 0 2px;color:var(--navy)}
.slide-body{flex:1;min-height:0;padding-bottom:50px;position:relative}
.slide > footer{position:absolute;left:64px;right:64px;bottom:0;height:40px;border-top:1px solid var(--rule);
  display:flex;align-items:center;justify-content:space-between;gap:24px;font-size:11.5px;color:var(--muted)}
.slide > footer .pg{font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap;flex:none;display:flex;align-items:center;gap:12px}
.slide > footer .logo{display:block}
/* slides escuros: capa e divisórias */
.escuro{background:var(--navy);color:#fff}
.escuro h1{color:#fff}
.escuro .eyebrow{color:var(--turq)}
.escuro .lede{color:rgba(255,255,255,.82)}
.escuro .label{color:var(--turq)}
.escuro > footer{border-top-color:rgba(255,255,255,.22);color:rgba(255,255,255,.62)}
.escuro .legenda{color:rgba(255,255,255,.85)}
.escuro figcaption{color:rgba(255,255,255,.62)}
.escuro .m-lab{fill:#fff;stroke:var(--navy)}
.divisor{justify-content:center}
.div-in{display:flex;flex-direction:column;justify-content:center;height:100%;padding:0 0 40px 0}
.div-in::before{content:"";display:block;width:84px;height:6px;margin-bottom:26px;background:linear-gradient(90deg,var(--turq) 0 72%,var(--ouro) 72%)}
.div-n{font-size:88px;font-weight:700;line-height:1;color:var(--turq);margin-bottom:18px;font-variant-numeric:tabular-nums}
.div-in h1{font-size:54px;max-width:1000px}
.div-in .lede{max-width:980px;font-size:24px;line-height:1.4}
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
  border:2px solid var(--accent);color:var(--accent-text);font-weight:700;font-size:19px;display:flex;align-items:center;justify-content:center}
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
.card-k{position:absolute;top:16px;right:18px;font-size:14px;font-weight:700;color:var(--accent-text)}
.tag{display:inline-block;margin-top:6px;font-size:13px;font-weight:600;color:var(--navy);background:var(--ouro-soft);border-radius:4px;padding:2px 8px}
.cards-alto .card p{margin-bottom:12px}
.cards-alto .label{margin-bottom:2px;font-size:12px}
.cards-alto .onde{font-size:13.5px;color:var(--accent-text);font-weight:600;margin:0}
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
.tab-pol tr.dest td:first-child b{color:var(--accent-text)}
.tab-pol tr.dest td{background:var(--accent-soft)}
.tab-lim td{padding:10px 16px 10px 0;font-size:16.5px}
.tab-lim td:first-child{width:38%}
.tri{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:14px}
.tri p{margin:0;font-size:16.5px;line-height:1.42;border-left:3px solid var(--accent);padding-left:14px}
.compacto > header{margin-bottom:12px}.compacto .tri{margin-top:8px}.compacto .nota{margin-top:6px}
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
.stat-v{font-size:46px;font-weight:650;line-height:1;color:var(--accent-text)}
.stat-l{font-size:17px;line-height:1.38;margin-top:6px}
.val p{font-size:17px;line-height:1.4;margin:0 0 6px}
.capa-slide{padding-top:48px}
.capa{display:grid;grid-template-columns:1fr 470px;gap:36px;height:100%}
.capa-txt{display:flex;flex-direction:column;justify-content:center;padding-bottom:60px}
.capa-txt .logo{margin-bottom:34px}
.capa-txt h1{font-size:48px}
.capa-txt .lede{margin-bottom:34px}
.equipe p{font-size:21px;line-height:1.45;margin:0}
.url{font-size:16px;color:rgba(255,255,255,.7);margin:30px 0 0}
.capa-slide .m-lab{font-size:13.5px}
.capa-mapa{margin:0;align-self:center}
figure{margin:0}
figcaption{font-size:12.5px;color:var(--muted);margin-top:6px}
.fig-mapa{display:flex;justify-content:center}
.links{list-style:none;margin:0;padding:0}
.links li{padding:12px 0;border-bottom:1px solid var(--rule);font-size:17px}
.links .label{margin-bottom:2px}
.links a{color:var(--ink);text-decoration:none;border-bottom:1.5px solid var(--accent)}
.cmd{font-family:"Cascadia Mono",Consolas,Menlo,monospace;font-size:17px;line-height:1.45;background:var(--navy);color:#F2F2F0;
  border-radius:8px;padding:16px 20px;margin:0}
.obrigado{font-size:34px;font-weight:650;margin-top:34px}
.conclusoes{margin:0;padding:0;list-style:none;counter-reset:c;display:grid;grid-template-columns:repeat(3,1fr);gap:30px}
.conclusoes li{counter-increment:c;border-top:4px solid var(--accent);padding-top:14px}
.conclusoes li::before{content:counter(c);display:block;font-size:40px;font-weight:700;color:var(--accent-text);line-height:1;margin-bottom:10px}
.conclusoes h3{font-size:21px;line-height:1.25;margin-bottom:8px}
.conclusoes p{font-size:17px;line-height:1.42;margin:0}
/* deck interno */
.nw{white-space:nowrap}
.corpo{font-size:18px;line-height:1.45;margin:0}
.agenda{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:6px 48px}
.agenda li{display:grid;grid-template-columns:62px 1fr auto;column-gap:14px;padding:16px 0;border-bottom:1px solid var(--rule-2)}
.ag-n{grid-column:1;grid-row:1/3;font-size:36px;font-weight:700;color:var(--turq);line-height:1;font-variant-numeric:tabular-nums}
.ag-t{grid-column:2;grid-row:1;font-size:21px;font-weight:600;color:var(--navy)}
.ag-s{grid-column:2/4;grid-row:2;font-size:15px;color:var(--muted);line-height:1.35;margin-top:4px}
.ag-p{grid-column:3;grid-row:1;font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums;align-self:center}
.tl{display:grid;grid-template-columns:repeat(7,1fr);gap:16px;position:relative}
.tl::before{content:"";position:absolute;left:0;right:0;top:35px;height:3px;background:var(--rule)}
.tl-d{font-size:15px;font-weight:700;color:var(--navy);height:24px;white-space:nowrap}
.tl-p{display:block;width:18px;height:18px;border-radius:50%;background:var(--turq);border:3px solid #fff;box-shadow:0 0 0 1px var(--turq);position:relative;margin:4px 0 16px}
.tl-ouro .tl-p{background:var(--ouro);box-shadow:0 0 0 1px #C8901A}
.tl-n h3{font-size:19px;margin-bottom:8px}
.tl-n p{font-size:15px;line-height:1.42;margin:0 0 10px}
.tl-n .onde{font-size:13px;font-weight:600;color:var(--accent-text)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:44px 28px}
.kpi{border-top:4px solid var(--turq);padding-top:12px}
.kpi:nth-child(4n+1){border-top-color:var(--navy)}
.kpi-v{font-size:46px;font-weight:700;color:var(--navy);line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.kpi-l{font-size:15.5px;line-height:1.38;margin-top:8px;color:var(--ink-2)}
.passos{margin:0;padding:0;list-style:none;counter-reset:p}
.passos li{counter-increment:p;position:relative;padding:0 0 0 44px;margin:0 0 14px;font-size:18px;line-height:1.4}
.passos li::before{content:counter(p);position:absolute;left:0;top:0;width:28px;height:28px;border-radius:6px;background:var(--navy);color:#fff;
  font-weight:700;font-size:14px;display:flex;align-items:center;justify-content:center}
.passos-sm li{font-size:16px;margin-bottom:8px;padding-left:40px}
.specs{display:grid;grid-template-columns:repeat(7,1fr);gap:10px}
.spec{border:1px solid var(--rule);border-radius:8px;padding:9px 10px 10px;background:#fff;min-height:112px;display:flex;flex-direction:column}
.spec-rev{border:2px solid var(--ouro)}
.spec-n{font-weight:700;color:var(--navy);font-size:16px;font-variant-numeric:tabular-nums}
.spec-t{font-size:13.5px;line-height:1.3;margin:3px 0 8px;flex:1}
.st{align-self:flex-start;font-size:11.5px;font-weight:600;border-radius:4px;padding:2px 7px}
.st-ok{background:var(--navy);color:#fff}
.st-exc{background:var(--ouro-soft);color:var(--navy)}
.fluxo{display:flex;align-items:stretch;margin-bottom:34px}
.fx{flex:1;border:1px solid var(--rule);border-radius:10px;padding:16px 16px 18px;background:#fff}
.fx p{margin:0;font-size:16.5px;line-height:1.42}
.fx .label{margin-bottom:5px;color:var(--navy)}
.fx-dest{border:2px solid var(--turq)}
.fx-ver{background:var(--navy);border-color:var(--navy);color:#fff}
.fx-ver .label{color:var(--turq)}
.fx-ver code{background:rgba(255,255,255,.14);color:#fff}
.seta{flex:none;width:34px;display:flex;align-items:center;justify-content:center;color:var(--turq);font-size:26px;font-weight:700}
.tab-num2{font-size:17.5px}
.tab-num2 td{padding:11px 12px 11px 0}
.tab-num2 .num{white-space:nowrap}
.tab-dif{font-size:15px;line-height:1.3}
.tab-dif td{padding:6px 12px 6px 0}
.tab-dif td:first-child,.tab-dif td:last-child{white-space:nowrap;color:var(--muted)}
.tab-ad{font-size:15.5px}
.tab-ad td{padding:7px 14px 7px 0}
.tab-rot{font-size:14.5px;line-height:1.3}
.tab-rot td{padding:5px 12px 5px 0}
.qa{display:grid;grid-template-columns:1fr 1fr;gap:40px 44px}
.qa-i{border-left:4px solid var(--turq);padding-left:18px}
.qa-i h3{font-size:21px;line-height:1.3;margin-bottom:10px}
.qa-i p{font-size:18.5px;line-height:1.48;margin:0}
/* resumo executivo */
.resposta{border-left:6px solid var(--ouro);padding:4px 0 0 26px}
.r-item{display:grid;grid-template-columns:262px 1fr;gap:16px;align-items:baseline;padding:14px 0;border-bottom:1px solid var(--rule-2)}
.r-v{font-size:52px;font-weight:700;color:var(--navy);line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-.02em;white-space:nowrap}
.kpis-ex .kpi-v{font-size:42px}
.r-v span{font-size:22px;font-weight:600;letter-spacing:0}
.r-v2{font-size:40px}
.r-t{font-size:17.5px;line-height:1.4}
.achados{margin:0;padding:0;list-style:none;counter-reset:a}
.achados li{counter-increment:a;position:relative;padding:0 0 0 46px;margin:0 0 16px;font-size:17.5px;line-height:1.4}
.achados li::before{content:counter(a);position:absolute;left:0;top:-1px;width:30px;height:30px;border-radius:50%;background:var(--navy);
  color:#fff;font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center}
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
.c-acc{font-size:14px;font-weight:600;fill:var(--accent-text)}
.c-acc-t{fill:var(--accent-text);font-weight:650}
.c-sm-t{font-size:14px;fill:var(--ink-2)}
.c-in{font-size:15px;fill:#fff;font-weight:600}
.c-k{font-weight:700;fill:var(--accent-text)}
.grade{stroke:var(--rule-2);stroke-width:1}
.eixo{stroke:var(--rule);stroke-width:1}
.ref{stroke:var(--ink-2);stroke-width:1.25}
.m-lab{font-size:13.5px;fill:var(--ink);font-weight:600;paint-order:stroke;stroke:var(--surface);stroke-width:4px;stroke-linejoin:round}
.m-fraco{fill:var(--muted);font-weight:500}
.m-acc{fill:var(--accent-text);font-weight:700}
/* tela */
.notes{display:none}
#pos{position:fixed;right:16px;top:10px;font:600 13px/1 "Public Sans","Segoe UI",system-ui,sans-serif;color:#fff;background:rgba(8,34,61,.82);
  padding:7px 10px;border-radius:6px;z-index:10;font-variant-numeric:tabular-nums}
#ajuda{position:fixed;left:16px;top:10px;font:600 12px/1 "Public Sans","Segoe UI",system-ui,sans-serif;color:#fff;background:rgba(8,34,61,.82);
  padding:7px 10px;border-radius:6px;z-index:10;transition:opacity .8s}
#painel-notas{display:none;position:fixed;left:0;right:0;bottom:0;height:34vh;overflow:auto;background:var(--navy);color:#F2F2F0;
  font:18px/1.5 "Public Sans","Segoe UI",system-ui,sans-serif;padding:16px 28px 40px;z-index:9}
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

def monta(slides, out, titulo):
    partes = []
    N = len(slides)
    for i, s in enumerate(slides, 1):
        cab = ""
        if s["titulo"]:
            cab = f'<header><div class="eyebrow">{s["eyebrow"]}</div><h2>{s["titulo"]}</h2></header>'
        escuro = "escuro" in s["classe"]
        marca = "" if "capa-slide" in s["classe"] else logo(LOGO_BRANCO if escuro else LOGO_MARINHO, 24)
        fonte = f'Fonte: {s["fonte"]}' if s["fonte"] else ""
        partes.append(
            f'<div class="frame" id="s{i}"><div class="frame-in"><section class="slide {s["classe"]}" data-n="{i}" aria-label="Slide {i} de {N}">'
            f'{cab}<div class="slide-body">{s["corpo"]}</div>'
            f'<footer><span>{fonte}</span><span class="pg">dados {VERSAO_DADOS} · {i}{marca}</span></footer>'
            f'<aside class="notes no-print">{s["notas"]}</aside>'
            f'</section></div></div>')
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<link rel="icon" href="data:,">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>{CSS.replace("__FONTE__", FONTE_B64)}</style>
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
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"{N} slides -> {os.path.relpath(out, REPO)} ({len(html.encode('utf-8')) / 1024:.0f} KB)")

def pega(prefixo):
    """Slide do registro pelo começo do sobretítulo (falha se não houver exatamente um)."""
    achados = [s for s in SLIDES if s["eyebrow"].startswith(prefixo)]
    assert len(achados) == 1, (prefixo, len(achados))
    return achados[0]

# ================================================================ deck executivo (turma)
_ATW = _MELHOR["ganho"]
_RAZ = _CAND["rosa_2017+azul_anjou"]["ganho"]
def _pp(g, d=3):
    return br(100 * g, d)
CAPA_EXEC = capa("Qual ligação nova deixa a rede mais tolerante a falhas: dados públicos, modelos e simulação", "Equipe",
"""<p>Apresentar a equipe e o tema em uma frase: medimos a confiabilidade do metrô de Montreal só com dados públicos e simulamos a rede para descobrir que ligação nova mais ajuda.</p>
<p>Avisar que todo número tem a fonte no rodapé e pode ser refeito por qualquer pessoa.</p>
<p><b>Tempo:</b> 20 s.</p>""")

RESUMO = slide("Resumo · a resposta antes dos detalhes",
    "A ligação Atwater–Université-de-Montréal é a que mais melhora a rede; entre as propostas oficiais, a Rosa com a Azul até Anjou", f"""
<div class="cols c-55-45">
  <div class="resposta">
    <div class="label">A resposta</div>
    <div class="r-item"><div class="r-v">+{_pp(_ATW["media"])}<span> p.p.</span></div>
      <div class="r-t"><b>Atwater (Verde) – Université-de-Montréal (Azul)</b>, ligação direta de {br(_MELHOR["km"], 1)} km. IC 95% de +{_pp(_ATW["ic95"][0])} a +{_pp(_ATW["ic95"][1])}.</div></div>
    <div class="r-item"><div class="r-v r-v2">+{_pp(_RAZ["media"])}<span> p.p.</span></div>
      <div class="r-t"><b>Linha Rosa com a Azul até Anjou</b>, a melhor das propostas oficiais. IC 95% de +{_pp(_RAZ["ic95"][0])} a +{_pp(_RAZ["ic95"][1])}.</div></div>
    <p class="corpo-sm muted">Ganho na disponibilidade dos deslocamentos entre estações num dia útil, ponderada pela oferta de trens. A rede atual tem {br(DISP_OD_ATUAL, 3)}%. Não há dado público de passageiros: o ganho é medido em pares de estações com caminho, não em pessoas.</p>
  </div>
  <div>
    <div class="label">Por quê</div>
    <ol class="achados">
      <li><b>A Azul depende da Laranja.</b> Ela só alcança o resto da rede em Snowdon e Jean-Talon: quando a Laranja para, a Azul fica isolada. É o maior ponto único de falha do modelo.</li>
      <li><b>As falhas não são independentes.</b> Elas vêm em rajadas, e 45 eventos param várias linhas juntas; a Laranja está em 44.</li>
      <li><b>A política que mais rende é a operação degradada</b>, em marcha lenta depois de uma falha de equipamento fixo: −{br(_OD, 1)} minutos parados por dia útil.</li>
    </ol>
  </div>
</div>
<div class="faixa">
  <div><span class="label">Por que confiar</span>{N_RECALC} números refeitos por um segundo programa, com zero diferença. A validação pré-registrada não passou e continua publicada.</div>
  <div><span class="label">Versão</span>Números após a revisão de 2026-11 (v1.2.0). A versão anterior continua no ar em /versoes/v1.1.0/.</div>
</div>""",
"dados/derivados/simulador/expansao.json e politicas.json; docs/relatorio/relatorio.md (Resumo e §7); fontes/verificacao/expansao.md",
f"""<p>Começar pela resposta: o objetivo do trabalho era dizer que linha melhor resolve a movimentação das pessoas na rede, do ponto de vista de falhas.</p>
<p>A melhor ligação nova é Atwater–Université-de-Montréal: +{_pp(_ATW["media"])} ponto percentual na disponibilidade dos deslocamentos. Parece pouco, mas é quase o dobro da melhor proposta oficial, a Rosa com a Azul até Anjou (+{_pp(_RAZ["media"])}).</p>
<p>O motivo é estrutural: hoje a Azul só chega ao resto da rede passando pela Laranja.</p>
<p>Ressalva que precisa ser dita: sem dado de passageiros, medimos pares de estações com caminho, ponderados pela oferta de trens, e não pessoas.</p>
<p><b>Tempo:</b> 1 min 15 s.</p>""")

CONFIANCA = slide("Confiança e limites", "Por que confiar nos números, e o que o modelo não sabe", f"""
<div class="kpis kpis-ex">
  <div class="kpi"><div class="kpi-v">{N_RECALC}</div><div class="kpi-l">números refeitos por um segundo programa a cada publicação: zero diferença</div></div>
  <div class="kpi"><div class="kpi-v">{br(VERSOES[0][3], 1)}%</div><div class="kpi-l">cobertura da validação pré-registrada contra 2025 e 2026, com 80% exigidos: não passou e continua publicada</div></div>
  <div class="kpi"><div class="kpi-v">{br(VERSOES[3][3], 1)}%</div><div class="kpi-l">cobertura da regra corrigida, testada em outro período</div></div>
  <div class="kpi"><div class="kpi-v">{REV_NO_IC} de {N_COMP}</div><div class="kpi-l">médias do simulador, por linha e família, dentro do intervalo do observado em 2025</div></div>
</div>
<div class="cols c-50-50" style="margin-top:26px">
  <div>
    <div class="label">Por que confiar</div>
    <ul class="lista lista-sm">
      <li><b>Cópia exata dos dados</b> em três Releases do GitHub, com o SHA-256 de cada arquivo.</li>
      <li><b>O site não é publicado</b> se a conferência ou os testes falham.</li>
      <li><b>Critério escrito antes</b> de ver o resultado: o que não passa vira exceção, e o critério não muda.</li>
    </ul>
  </div>
  <div>
    <div class="label">O que o modelo não sabe</div>
    <ul class="lista lista-sm">
      <li><b>Passageiros por dia:</b> não são públicos. Tudo é ponderado pela oferta de trens.</li>
      <li><b>Tempo de reparo na oficina:</b> hipótese, com sensibilidade de 0,5 a 4 dias.</li>
      <li><b>Setores "Service aux trains" e "TCPE":</b> sem definição pública; "energia" é dedução nossa.</li>
      <li><b>Traçado das candidatas:</b> aproximado em linha reta entre estações.</li>
    </ul>
  </div>
</div>""",
"fontes/FONTES.md; fontes/verificacao/backtest.md e revalidacao.md; specs/012 e 020; docs/relatorio/relatorio.md §5 e §6",
f"""<p>Dois lados da mesma moeda. À esquerda, o que faz o número ser confiável: dados com hash, um segundo programa que refaz as contas e uma validação com critério escrito antes.</p>
<p>A validação pré-registrada não passou ({br(VERSOES[0][3], 1)}% contra 80%): 2024 teve um tipo de registro nos terminais que inflou as falhas, e o modelo levou isso para 2025. Não mexemos no critério; testamos a regra nova em outro período.</p>
<p>À direita, o que fica fora. A principal limitação é não ter passageiros.</p>
<p><b>Tempo:</b> 1 min.</p>""")

EXECUTIVA = [CAPA_EXEC, RESUMO, pega("A pergunta"), pega("Indicadores por linha"), pega("O que muda a taxa"),
             pega("As falhas se agrupam"), pega("Causa comum"), pega("Simulador · eventos"), pega("Políticas"),
             pega("Que linha construir"), CONFIANCA, pega("Conclusões"), pega("Confira")]
monta(EXECUTIVA, OUT_EXEC, "Confiabilidade do metrô de Montreal · apresentação executiva")

# ================================================================ deck interno (equipe): tudo o que foi feito
import subprocess
def _git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, check=True, timeout=60).stdout.decode("utf-8").strip()

def _ler(*partes):
    return open(os.path.join(REPO, *partes), encoding="utf-8").read()

CURTO = {"000": "Proveniência", "001": "Normalização dos incidentes", "002": "Base geoespacial", "003": "Clima e eventos",
         "004": "Exposição (trens-hora)", "005": "Taxa de falha", "006": "Tempo entre falhas, duração e causa comum",
         "007": "Motor de eventos discretos", "008": "Políticas", "009": "Monte Carlo e métricas", "010": "Mapa com trens",
         "011": "Cenários", "012": "Backtest", "013": "Publicação", "014": "Expansão da rede", "015": "Viagem de A a B",
         "016": "Linhas novas na viagem", "017": "Fontes e durações", "018": "Taxa por fonte", "019": "Motor com N fontes",
         "020": "Revalidação"}
SPECS = []  # (número, nome curto, status) lidos de specs/*/spec.md
for d in sorted(os.listdir(os.path.join(REPO, "specs"))):
    if re.match(r"\d{3}-", d) and os.path.exists(os.path.join(REPO, "specs", d, "spec.md")):
        st = re.search(r"\*\*Status:\*\* *(.+)", _ler("specs", d, "spec.md")).group(1).strip()
        SPECS.append((d[:3], CURTO[d[:3]], st))
assert [s[0] for s in SPECS] == sorted(CURTO), "specs mudaram: revisar CURTO"
N_IMPL = sum(s[2] == "implementada" for s in SPECS)
N_EXC = sum(s[2] == "implementada com exceções" for s in SPECS)
assert N_IMPL + N_EXC == len(SPECS)
REG = _ler("docs", "decisoes", "registro_de_decisoes.md")
N_DEC = len(re.findall(r"^### D\d\d ", REG, re.M))
CRITICAS = []  # (data, achados, médios, corrigidos) de fontes/verificacao/critica_*.md
for f in sorted(os.listdir(os.path.join(REPO, "fontes", "verificacao"))):
    if f.startswith("critica_"):
        m = re.search(r"(\d+) achados(?: novos)?: (\d+) altos?, (\d+) médios?, (\d+) baixos?\. (\d+) corrigidos", _ler("fontes", "verificacao", f))
        CRITICAS.append((f[8:18], int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(5))))
assert len(CRITICAS) == 4 and sum(c[2] for c in CRITICAS) == 0
VERS = [(t, _git("rev-list", "-n", "1", t)[:7]) for t in ("v1.0.0", "v1.1.0", "v1.2.0")]
N_FONTES = len(_MAN["fontes"])
N_PYTEST = int(re.search(r"# (\d+) testes em", _ler("docs", "arquitetura.md")).group(1))
POL_V1 = _json_v1("dados/derivados/simulador/politicas.json")
EXP_V1 = _json_v1("dados/derivados/simulador/expansao.json")
_RAZ_V1 = next(c for c in EXP_V1["candidatas"]["sem_retorno_parcial"] if c["id"] == "rosa_2017+azul_anjou")["ganho"]["media"]
_VG = _ler("fontes", "verificacao", "viagem.md").split("## Angrignon → Saint-Michel", 1)[1]
VG_PROD = re.search(r"\| Produto dos trechos \(série\) \| ([\d,]+%)", _VG).group(1)
VG_SIM = re.search(r"\| Viagem inteira, simulada \| ([\d,]+%) \(([\d,]+%) a ([\d,]+%)\)", _VG).groups()
VG_DIAS = re.search(r"\| Dias com ao menos uma interrupção no caminho \| ([\d,]+%)", _VG).group(1)
_LN = _ler("fontes", "verificacao", "linhas_novas.md").split("## Atwater", 1)[1]
LN_PROG = re.search(r"\| Tempo programado do caminho \(min\) \| ([\d,]+) \| ([\d,]+) \|", _LN).groups()
LN_SEM = re.search(r"\| Tempo sem caminho \(min por dia\) \| ([\d,]+) \([^)]*\) \| ([\d,]+) \(", _LN).groups()
LN_NOVES = re.search(r"\| Noves[^|]*\| ([\d,]+) \([^)]*\) \| ([\d,]+) \(", _LN).groups()
SPEC19 = _ler("specs", "019-motor-n-fontes", "spec.md")
assert "0,1576" in SPEC19 and "0,1563" in SPEC19 and "20.000 dias úteis" in SPEC19 and "198 casos" in SPEC19

CAPA_INT = capa('Apresentação interna: tudo o que fizemos, de <span class="nw">2026-10-20</span> a <span class="nw">2026-11-11</span>', "Equipe",
"""<p>Este deck é para nós quatro: conta o projeto inteiro, na ordem em que foi feito, com o porquê de cada escolha.</p>
<p>No fim há o roteiro da apresentação executiva para a turma e as perguntas que podem aparecer, com resposta.</p>""")

AGENDA = slide("Roteiro", "Oito partes, na ordem em que o trabalho aconteceu", "", "este deck",
"""<p>Usar como índice. Cada parte abre com uma divisória azul-marinho; o número do slide está no rodapé.</p>""")

LINHA_TEMPO = slide("Linha do tempo · 2026-10-20 a 2026-11-11", "Do tema à entrega em 23 dias, com uma revisão grande no meio", f"""
<div class="tl">
  <div class="tl-n"><div class="tl-d">até 10-20</div><i class="tl-p"></i><h3>Tema</h3>
    <p>Comparamos São Paulo e redes europeias. Montreal publica cada incidente com início, fim, causa, linha e local.</p><p class="onde">D01</p></div>
  <div class="tl-n"><div class="tl-d">10-20</div><i class="tl-p"></i><h3>Fundação</h3>
    <p>Painel no ar, monorepo SDD, specs 000 a 013 escritas, dados numa Release com hash. O 1º deploy foi bloqueado: o Windows mudou o fim de linha e os hashes.</p><p class="onde">F0 · D02 a D12</p></div>
  <div class="tl-n tl-ouro"><div class="tl-d">10-21</div><i class="tl-p"></i><h3>Tudo num dia</h3>
    <p>Dados, modelos, simulador, backtest e publicação (F1 a F6); <b>v1.0.0</b>; relatório e deck; três rodadas de crítica; reprodução do zero sem diferença. À noite, specs 015 e 016.</p><p class="onde">D13 a D54</p></div>
  <div class="tl-n"><div class="tl-d">10-23 e 10-27</div><i class="tl-p"></i><h3>Perguntas novas</h3>
    <p>A STM republica o km real até 2026-09. Na reunião, perguntas sobre frota, via ou trem e sistemas separados.</p><p class="onde">specs 004 e 017</p></div>
  <div class="tl-n"><div class="tl-d">11-01</div><i class="tl-p"></i><h3>Reprodução quebra</h3>
    <p>A execução agendada do <code>reproduz.yml</code> falha: a API da NHL mudou a resposta.</p><p class="onde">D65</p></div>
  <div class="tl-n"><div class="tl-d">11-10</div><i class="tl-p"></i><h3>Revisão</h3>
    <p>v1.1.0 congelada antes de mexer; specs 017 a 020; duração pela faixa oficial; falhas por frota e setor. Erro da greve achado no meio da rodada.</p><p class="onde">D55 a D63</p></div>
  <div class="tl-n tl-ouro"><div class="tl-d">11-11</div><i class="tl-p"></i><h3>Entrega</h3>
    <p>4ª crítica ({CRITICAS[-1][1]} achados); resposta ao objetivo no relatório; licença MIT; <b>v1.2.0</b> congelada.</p><p class="onde">D64 a D66</p></div>
</div>
<p class="nota">Entre 10-26 e 11-09, a verificação semanal conferiu as fontes na origem toda segunda-feira e gravou um relatório datado no repositório.</p>""",
"git log e etiquetas (git tag); docs/decisoes/registro_de_decisoes.md; fontes/verificacao/online_*.txt",
"""<p>A linha do tempo mostra o ritmo: a primeira versão completa saiu em dois dias, e a maior parte do tempo depois disso foi para conferir, revisar e corrigir.</p>
<p>Dois marcos em dourado: a v1.0.0 (10-21), primeira versão inteira, e a v1.2.0 (11-11), a versão de entrega.</p>
<p>O ponto de virada foi a reunião de 10-27: as perguntas sobre frota e sistemas levaram à revisão de 11-10.</p>""")

EM_NUMEROS = slide("O projeto em números", "Uma pergunta só, e cada número conferido mais de uma vez", f"""
<div class="kpis">
  <div class="kpi"><div class="kpi-v">{len(SPECS)}</div><div class="kpi-l">specs, cada uma com pergunta e critério escritos antes: {N_IMPL} implementadas e {N_EXC} com exceção registrada</div></div>
  <div class="kpi"><div class="kpi-v">{N_DEC}</div><div class="kpi-l">decisões com data, motivo e alternativas, no registro de decisões</div></div>
  <div class="kpi"><div class="kpi-v">{N_FONTES}</div><div class="kpi-l">fontes no manifesto, cada arquivo com SHA-256</div></div>
  <div class="kpi"><div class="kpi-v">{N_RECALC}</div><div class="kpi-l">números refeitos por um segundo programa, a cada publicação: zero diferença</div></div>
  <div class="kpi"><div class="kpi-v">{len(CRITICAS)}</div><div class="kpi-l">rodadas do agente crítico, com {sum(c[1] for c in CRITICAS)} achados; nenhum de gravidade alta</div></div>
  <div class="kpi"><div class="kpi-v">{len(VERS)}</div><div class="kpi-l">versões congeladas e no ar: {", ".join(t for t, _ in VERS)}</div></div>
  <div class="kpi"><div class="kpi-v">{N_PYTEST}</div><div class="kpi-l">testes do pipeline em Python, além dos testes do simulador em TypeScript</div></div>
  <div class="kpi"><div class="kpi-v">{br(45785)}</div><div class="kpi-l">incidentes da STM lidos, de 2019-01 a 2026-06, que viraram {br(R["falhas"])} falhas técnicas</div></div>
</div>""",
"specs/*/spec.md (status); docs/decisoes/registro_de_decisoes.md; fontes/fontes_manifesto.json; fontes/verificacao/critica_*.md; git tag; docs/arquitetura.md; linhas.json",
"""<p>O tema cabe numa frase, mas quase todo número passou por mais de uma conferência.</p>
<p>As exceções são critérios que não foram atingidos e ficaram registrados como estão: não mudamos o critério para passar.</p>""")

METODO = slide("Como trabalhamos · SDD (desenvolvimento guiado por especificação)", "Critério escrito antes do código; o que não passa vira exceção, não critério novo", f"""
<div class="cols c-50-50">
  <div>
    <div class="label">O ciclo de cada parte</div>
    <ol class="passos">
      <li><b>Pergunta de engenharia</b> e o número que a responde.</li>
      <li><b>Critérios de aceite</b> escritos antes de ver o resultado.</li>
      <li><b>Código e testes</b>: o critério vira teste sempre que dá.</li>
      <li><b>Resultado na própria spec</b>: atende, ou exceção com o motivo.</li>
      <li><b>Decisão registrada</b> (Dxx) quando há escolha: por quê, alternativas e consequência.</li>
    </ol>
  </div>
  <div>
    <div class="label">Princípios que mais pesaram</div>
    <ul class="lista lista-sm">
      <li><b>Todo número é rastreável</b> à fonte, ao hash, ao script e ao commit.</li>
      <li><b>Fato, dedução e hipótese separados</b>: cada parâmetro leva um status.</li>
      <li><b>Duas implementações</b> para os números-chave.</li>
      <li><b>Dado ausente nunca vira zero.</b></li>
      <li><b>Critério não se ajusta ao resultado.</b></li>
      <li><b>A simulação reproduz o que sabemos antes de prever.</b></li>
      <li><b>Publicar exige verificação verde.</b></li>
    </ul>
  </div>
</div>
<p class="nota">Por que assim: a equipe temia números "alucinados" por IA. A resposta foi a D03 (proveniência verificável antes de qualquer modelo) e a D04 (SDD).</p>""",
"specs/constitution.md (16 princípios); specs/README.md; docs/decisoes/registro_de_decisoes.md (D03 e D04)",
"""<p>SDD quer dizer que cada parte do projeto começa por um documento com a pergunta e o critério de aceite, antes de qualquer código.</p>
<p>O efeito prático aparece no backtest: o critério era 80% de cobertura, deu 66,7%, e ficou registrado como exceção. Sem o critério escrito antes, seria tentador ajustar.</p>""")

SPECS_SL = slide(f"As {len(SPECS)} specs", f"{N_IMPL} atendem a todos os critérios; {N_EXC} têm exceção registrada", f"""
<div class="specs">{"".join(f'<div class="spec{" spec-rev" if int(n) >= 17 else ""}"><div class="spec-n">{n}</div><div class="spec-t">{esc(nome)}</div><span class="st {"st-ok" if st == "implementada" else "st-exc"}">{"atende" if st == "implementada" else "com exceção"}</span></div>' for n, nome, st in SPECS)}</div>
<div class="faixa">
  <div><span class="label">Fases</span>F0 a F6 em 10-20 e 10-21 (000 a 014); 015 e 016 na noite de 10-21; 017 a 020 na revisão de 2026-11 (borda dourada).</div>
  <div><span class="label">Exceções principais</span>001: 98,83% das durações na faixa (pedido 99%) · 002: 94,0% com posição (pedido 95%) · 012: backtest 66,7% (pedido 80%) · 013: reprodução não refeita após a revisão.</div>
</div>""",
"specs/*/spec.md (linha Status e seção Resultado)",
"""<p>Cada quadrado é uma spec, com o status que está escrito nela. "Com exceção" quer dizer que um critério não foi atingido e o motivo está na própria spec.</p>
<p>Vale lembrar: exceção não é defeito escondido. É o critério original preservado, com o resultado ao lado.</p>""")

NORMALIZA = slide("Dados · decisões de tratamento", "Como 45.785 incidentes viraram uma tabela de falhas com hora, duração, local e exposição", f"""
<div class="cards c3 cards-alto">
  <div class="card"><h3>O que é falha técnica</h3><p>Causa primária "Matériel roulant" (trem) ou "Équipements fixes" (via, sinalização, energia, portas). Mais de uma linha vira causa comum; sem linha fica registrado, fora das métricas.</p><p class="onde">D13</p></div>
  <div class="card"><h3>Horas e duração</h3><p>Janela de 20 h (05:00 a 01:00). 24:xx e 25:xx são do dia seguinte. Na revisão, quando a duração calculada contradiz a faixa oficial da STM, vale a faixa.</p><p class="onde">D12 · D14 · D55</p></div>
  <div class="card"><h3>Exposição</h3><p>Trens em viagem por hora no horário do GTFS, calibrados pelo km real de cada dia. Na revisão, o km republicado cobre até 2026-09 e nada mais é estimado.</p><p class="onde">D17 · spec 004</p></div>
  <div class="card"><h3>Clima</h3><p>Três estações do ECCC: precipitação de McTavish, com o aeroporto de reserva; temperatura e condição da 51157. Condição ausente fica vazia, nunca "seco".</p><p class="onde">D15</p></div>
  <div class="card"><h3>Eventos externos</h3><p>Jogos do Canadiens (API da NHL, verificado), GP do Canadá e greves de 2025 (não verificados), cada um com URL e status.</p><p class="onde">D16</p></div>
  <div class="card"><h3>Mapa e local</h3><p>Traçado do OpenStreetMap (não do GTFS); estações casadas com o Wikidata. Códigos de local <code>xSyy</code> deduzidos como a plataforma da 2ª linha.</p><p class="onde">D10 · D11 · spec 002</p></div>
</div>""",
"docs/decisoes/registro_de_decisoes.md (D10 a D17 e D55); specs/001 a 004",
"""<p>Cada cartão é uma decisão de tratamento dos dados, com o número dela no registro.</p>
<p>A regra geral: nada some em silêncio. O que não entra numa métrica fica registrado com o motivo, e o dado que falta aparece como falta.</p>""")

ARQ = slide("Simulador · arquitetura", "Python prepara os números; o navegador simula; um segundo programa confere tudo antes de publicar", f"""
<div class="fluxo">
  <div class="fx"><div class="label">1 · Fontes públicas</div><p>STM (incidentes, km real, GTFS), ECCC, NHL, OpenStreetMap, Wikidata</p></div><div class="seta">→</div>
  <div class="fx"><div class="label">2 · Releases</div><p>Cópia exata no GitHub, SHA-256 de cada arquivo no manifesto</p></div><div class="seta">→</div>
  <div class="fx"><div class="label">3 · Pipeline Python</div><p>Normalização, exposição, clima, modelo da taxa, distribuições, backtest</p></div><div class="seta">→</div>
  <div class="fx fx-dest"><div class="label">4 · Contrato</div><p><code>parametros.json</code> v2, validado por esquema, com o hash do código que o gerou</p></div>
</div>
<div class="fluxo">
  <div class="fx"><div class="label">5 · Motor TypeScript</div><p>Eventos discretos: cada trem do horário, {len(TF["fontes"])} fontes de falha por linha, bloqueio por trecho</p></div><div class="seta">→</div>
  <div class="fx"><div class="label">6 · Monte Carlo</div><p>Web Workers; mesmo resultado com 1 ou 8 processos (sorteio por fluxo)</p></div><div class="seta">→</div>
  <div class="fx"><div class="label">7 · Site estático</div><p>Painel (d3), mapa com trens (MapLibre, WebGL), simulador, relatórios</p></div><div class="seta">←</div>
  <div class="fx fx-ver"><div class="label">Conferência</div><p><code>verifica_fontes.py</code> refaz {N_RECALC} números sem usar o pipeline; o deploy para se divergir</p></div>
</div>
<p class="nota">Tudo roda no navegador, sem servidor nem conta. O link guarda o cenário inteiro, com a semente: quem abre o mesmo link vê os mesmos números.</p>""",
"docs/arquitetura.md; contratos/parametros.schema.json; specs 007, 009, 011 e 013; dados/derivados/modelos/taxa_fontes.json",
"""<p>A divisão de trabalho entre linguagens: Python para estatística, TypeScript para simular no navegador. O contrato entre os dois é um único arquivo JSON validado por esquema.</p>
<p>Ao lado do caminho principal, um segundo programa, escrito à parte, refaz os números-chave direto dos dados brutos. Se der diferença, o site não é publicado.</p>""")

VIAGEM = slide("Simulador · viagem de uma estação a outra · specs 015 e 016", "Na viagem, a ligação nova troca três linhas por uma e corta o tempo sem caminho", f"""
<div class="cols c-50-50">
  <div>
    <h3>Angrignon → Saint-Michel (Verde, Laranja, Azul)</h3>
    <p class="sub">dia útil, 1.000 dias simulados</p>
    <table class="tab tab-num2"><tbody>
      <tr><td>Produto das três linhas, como se falhassem de forma independente</td><td class="num">{VG_PROD}</td></tr>
      <tr><td>Viagem inteira, simulada (IC 95%)</td><td class="num"><b>{VG_SIM[0]}</b> ({VG_SIM[1]} a {VG_SIM[2]})</td></tr>
      <tr><td>Dias com ao menos uma interrupção no caminho</td><td class="num">{VG_DIAS}</td></tr>
    </tbody></table>
    <p class="corpo-sm">Em série, a viagem é quase o produto dos trechos: a confiabilidade de um caminho cai a cada linha a mais.</p>
  </div>
  <div>
    <h3>Atwater → Université-de-Montréal</h3>
    <p class="sub">rede atual contra a rede com a ligação nova</p>
    <table class="tab tab-num2"><thead><tr><th></th><th class="num">hoje</th><th class="num">com a ligação</th></tr></thead><tbody>
      <tr><td>Tempo programado do caminho (min)</td><td class="num">{LN_PROG[0]}</td><td class="num"><b>{LN_PROG[1]}</b></td></tr>
      <tr><td>Tempo sem caminho (min por dia)</td><td class="num">{LN_SEM[0]}</td><td class="num"><b>{LN_SEM[1]}</b></td></tr>
      <tr><td>Noves (−log₁₀ da indisponibilidade)</td><td class="num">{LN_NOVES[0]}</td><td class="num"><b>{LN_NOVES[1]}</b></td></tr>
    </tbody></table>
    <p class="corpo-sm">Perto de 100%, a disponibilidade esconde as diferenças; por isso a escala em noves (99% são 2 noves, 99,9% são 3).</p>
  </div>
</div>""",
"fontes/verificacao/viagem.md e linhas_novas.md; specs/015 e 016; D52 a D54",
"""<p>Duas perguntas que vieram depois da v1.0.0: como se comporta uma viagem que usa várias linhas, e quanto uma linha nova muda essa viagem.</p>
<p>O caso de Atwater a Université-de-Montréal mostra o efeito da ligação recomendada do ponto de vista de quem viaja: menos linhas no caminho e muito menos tempo sem caminho.</p>""")

PUBLICACAO = slide("Publicação · GitHub Pages e Actions", "O site só vai ao ar se a conferência passar, e cada versão fica guardada", f"""
<div class="cols c-55-45">
  <div>
    <div class="label">A cada push na main (deploy.yml)</div>
    <ol class="passos passos-sm">
      <li>Baixa as Releases de dados e confere o SHA-256 de cada arquivo.</li>
      <li>Recalcula {N_RECALC} números com <code>verifica_fontes.py</code>, sem usar o pipeline.</li>
      <li>Roda os testes do pipeline (pytest) e do simulador (vitest).</li>
      <li>Monta o site e inclui cada versão congelada em <code>/versoes/</code>.</li>
      <li>Qualquer erro impede a publicação.</li>
    </ol>
    <p class="corpo-sm"><b>Toda segunda-feira</b> (<code>verifica-fontes.yml</code>): confere as fontes na origem; mudança vira aviso e relatório datado. <b>Reprodução do zero</b> (<code>reproduz.yml</code>): última com sucesso no commit a7f0594, 48 arquivos idênticos e 5 na tolerância; não refeita depois da revisão (D65).</p>
  </div>
  <div>
    <div class="label">Versões congeladas</div>
    <table class="tab"><thead><tr><th>Versão</th><th>Commit</th><th>O que guarda</th></tr></thead><tbody>
      <tr><td><b>{VERS[0][0]}</b></td><td><code>{VERS[0][1]}</code></td><td>primeira versão inteira (10-21)</td></tr>
      <tr><td><b>{VERS[1][0]}</b></td><td><code>{VERS[1][1]}</code></td><td>números antes da revisão de 2026-11</td></tr>
      <tr><td><b>{VERS[2][0]}</b></td><td><code>{VERS[2][1]}</code></td><td>versão de entrega (11-11)</td></tr>
    </tbody></table>
    <p class="corpo-sm muted">Cada uma tem uma Release com o zip do site e fica em /versoes/&lt;versão&gt;/.</p>
  </div>
</div>""",
".github/workflows/; specs/013-publicacao (Resultado e revisão); git tag; docs/decisoes/registro_de_decisoes.md (D36, D37, D65, D66)",
"""<p>O site é montado pelo GitHub Actions. O passo que importa é o 2: um programa independente refaz os números a partir dos dados brutos, e qualquer diferença bloqueia a publicação.</p>
<p>As versões congeladas permitem comparar: a v1.1.0 guarda os números de antes da revisão, e a v1.2.0 é a entregue.</p>""")

_EX_CRIT = {"2026-10-21": "O simulador aplicava à greve um multiplicador que a spec 005 mandava não usar (D42)",
            "2026-10-21_": "4 das 13 correções da 1ª rodada estavam incompletas (D44, D45)",
            "2026-10-21__": "O teste de fps media uma aba oculta: \"60 fps\" falso (D46 a D48)",
            "2026-11-11": "O rodapé do PDF riscava notas; /versoes/v1.1.0/ dava 404 antes do deploy (D64)"}
_lc = []
for i, (data, n, alt, med, cor) in enumerate(CRITICAS):
    chave = data + "_" * (i if data == "2026-10-21" else 0)
    _lc.append(f'<tr><td><b>R{i + 1}</b> · {data}</td><td class="num">{n}</td><td class="num">{med}</td><td class="num">{cor}</td><td>{esc(_EX_CRIT[chave])}</td></tr>')
CRITICAS_SL = slide("Revisão crítica · agente critico-stf", f"Quatro rodadas de crítica, {sum(c[1] for c in CRITICAS)} achados, e só o que foi reproduzido virou correção", f"""
<table class="tab"><thead><tr><th>Rodada</th><th class="num">Achados</th><th class="num">Médios</th><th class="num">Corrigidos pelo agente</th><th>Exemplo do que pegou</th></tr></thead>
<tbody>{"".join(_lc)}</tbody></table>
<div class="faixa">
  <div><span class="label">Como o agente trabalha</span>Roda todos os testes, confere cada número dos documentos contra o arquivo que o gerou, procura defeitos no pipeline, no motor e no site, e grava um relatório datado.</div>
  <div><span class="label">O que ele não faz</span>Não corrige sem reproduzir o defeito. O que não foi reproduzido fica como proposta, e a equipe decide.</div>
</div>
<p class="nota">Nenhum achado de gravidade alta em nenhuma rodada. As propostas aceitas viraram decisões no registro.</p>""",
"fontes/verificacao/critica_2026-10-21.md, _rodada2, _rodada3 e critica_2026-11-11.md; .claude/agents/critico-stf.md; D41 a D48 e D64",
"""<p>O agente crítico é um revisor automático que tenta derrubar os números. Ele roda antes de cada entrega.</p>
<p>A coluna "corrigidos" conta só o que o próprio agente corrigiu depois de reproduzir o defeito. As propostas foram decididas pela equipe e aplicadas na sessão principal.</p>""")

DIFICULDADES = slide("O que deu errado, e como resolvemos", "Os problemas que mais custaram, cada um com a decisão que o resolveu", """
<table class="tab tab-dif"><thead><tr><th>Quando</th><th>Problema</th><th>Como resolvemos</th><th>Onde</th></tr></thead><tbody>
  <tr><td>10-20</td><td>O 1º deploy foi bloqueado: o Windows trocou o fim de linha dos CSV e os hashes divergiram</td><td>Bytes exatos por <code>.gitattributes</code></td><td>D08</td></tr>
  <tr><td>10-20</td><td>O servidor da STM recusou o download do GTFS</td><td>Espelho do Mobility Database, com hash</td><td>D09</td></tr>
  <tr><td>10-21</td><td>A causa comum era contada duas ou três vezes nos eventos de 3 ou 4 linhas</td><td>Sorteio por grupo de linhas</td><td>D24</td></tr>
  <tr><td>10-21</td><td>A lognormal subestimava a duração média (3,4 vezes na Azul)</td><td>Duração sorteada da amostra observada</td><td>D25</td></tr>
  <tr><td>10-21</td><td>Dois ajustes com bootstrap caíram por falta de memória</td><td>Um ajuste de cada vez, coleta de lixo após cada ajuste, a mesma reamostra repetida</td><td>D40</td></tr>
  <tr><td>10-21</td><td>O teste de fluidez media uma aba oculta</td><td>Aba em primeiro plano no teste de navegador</td><td>D46 · D48</td></tr>
  <tr><td>11-10</td><td>Seis interrupções de quase 20 h em Saint-Michel registradas como "2 min ou menos"</td><td>Vale a faixa oficial quando a calculada a contradiz</td><td>D55</td></tr>
  <tr><td>11-10</td><td>A greve contada duas vezes na exposição: multiplicador de 1,17 para 1,73</td><td>Rodada parada, exposição corrigida e refeita</td><td>D63</td></tr>
  <tr><td>11-01</td><td>A API da NHL mudou e a reprodução do zero quebrou</td><td>Exceção registrada; agenda mensal desligada</td><td>D65</td></tr>
</tbody></table>""",
"docs/decisoes/registro_de_decisoes.md (D08, D09, D24, D25, D40, D46, D48, D55, D63, D65)",
"""<p>Os erros mais úteis de contar são o de Saint-Michel e o da greve: os dois foram achados porque um número não batia com outro, e os dois estão registrados com data.</p>
<p>Se alguém da turma perguntar o que deu errado, esta é a lista.</p>""", "compacto")

_F9 = [("mr73", "MR-73", "trem"), ("mpm10", "MPM-10", "trem"), ("mr_outros", "outros trens", "trem"),
       ("voie_sintoma_trem", "via, sintoma de trem", "fixo"), ("voie_sintoma_fixo", "via, sintoma fixo", "fixo"),
       ("aux_trains_sintoma_trem", "Service aux trains, sintoma de trem", "fixo"), ("aux_trains_sintoma_fixo", "Service aux trains, sintoma fixo", "fixo"),
       ("aux_stations", "Service aux stations", "fixo"), ("tcpe", "TCPE (energia, por dedução)", "fixo")]
assert sorted(k for k, _, _ in _F9) == sorted(NORM["por_fonte"]) and sum(NORM["por_fonte"].values()) == R["falhas"]
def barras_fontes():
    w = 620; lx = 270; bw_max = 280; rh = 34; bh = 20; top = 4
    vmax = max(NORM["por_fonte"].values()); h = top + rh * len(_F9) + 8
    o = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Falhas técnicas por fonte">']
    o.append(f'<line x1="{lx}" y1="0" x2="{lx}" y2="{h}" class="eixo"/>')
    for i, (k, nome, fam) in enumerate(_F9):
        v = NORM["por_fonte"][k]; yc = top + i * rh + rh / 2 + (6 if fam == "fixo" else 0)
        cor = "var(--navy)" if fam == "trem" else "var(--accent)"
        o.append(f'<text x="{lx - 10}" y="{yc + 5:.1f}" text-anchor="end" class="c-lab c-sm">{esc(nome)}</text>')
        o.append(barra_h(lx + 1, yc - bh / 2, bw_max * v / vmax, bh, cor).replace("/>", f"><title>{esc(nome)}: {v}</title></path>"))
        o.append(f'<text x="{lx + 1 + bw_max * v / vmax + 8:.1f}" y="{yc + 6:.1f}" class="c-val">{br(v)}</text>')
    o.append("</svg>")
    return "".join(o)
FONTES9 = slide("Revisão de 2026-11 · da reunião às fontes de falha", f"Os dados da STM já separavam a frota e o setor: {len(_F9)} fontes no lugar de duas causas", f"""
<div class="cols c-52-48">
  <div>
    <h3>Falhas técnicas de uma linha, por fonte</h3>
    <p class="sub"><i class="sw" style="background:var(--navy)"></i>trem: para o trem no sentido · <i class="sw" style="background:var(--accent)"></i>equipamento fixo: bloqueia o trecho</p>
    {barras_fontes()}
  </div>
  <div>
    <div class="label">Regras escritas antes de ajustar (D56)</div>
    <ul class="lista lista-sm">
      <li><b>Frota pelo campo da STM</b> ("Cause secondaire"), conferida com o tipo de material.</li>
      <li><b>Setor dividido pelo sintoma</b> quando cada parte tem 400 falhas ou mais; senão fica inteiro.</li>
      <li><b>Modelo próprio</b> só com 400 falhas ou mais; abaixo disso, modelo reduzido.</li>
      <li><b>Nomes da STM mantidos</b>: "Service aux trains" e "TCPE" não têm definição pública; "energia" é dedução nossa.</li>
    </ul>
    <p class="corpo-sm">Origem: na reunião de 2026-10-27 vieram perguntas sobre fabricantes, via ou trem e sistemas separados.</p>
  </div>
</div>""",
"dados/derivados/eventos/resumo_normalizacao.json (por_fonte); specs/017 e 018; docs/decisoes/registro_de_decisoes.md (D56)",
f"""<p>Antes da revisão, o modelo tinha duas causas por linha: trem e equipamento fixo. Os dados da STM permitiam separar mais.</p>
<p>A soma das {len(_F9)} fontes é exatamente o total de {br(R["falhas"])} falhas técnicas de uma linha; nenhuma falha mudou de lugar, só ganhou rótulo.</p>
<p>As regras de divisão foram escritas antes de ajustar os modelos, para não escolher a divisão pelo resultado.</p>""")

PROTOCOLO = slide("Revisão de 2026-11 · protocolo", "Antes de mexer, congelamos a versão anterior e escrevemos as previsões", """
<div class="cols c-55-45">
  <div>
    <ol class="passos">
      <li><b>Congelar a v1.1.0</b>, com etiqueta e o site guardado em /versoes/v1.1.0/.</li>
      <li><b>Gravar a referência do motor</b>: depois de trocar a estrutura, os 198 casos de referência saíram idênticos.</li>
      <li><b>Pré-registrar as previsões</b> (v1 e v2) para os meses que a STM ainda vai publicar, com commit antes de qualquer download.</li>
      <li><b>Escrever as specs 017 a 020</b> e as regras de divisão antes de ajustar.</li>
      <li><b>Refazer tudo no lugar</b>, marcando como "após a revisão" o que mudou depois de ver os dados.</li>
      <li><b>Comparar antes e depois</b> por script, número a número.</li>
    </ol>
  </div>
  <div>
    <div class="caixa">
      <div class="label">O erro achado no meio (D63)</div>
      <p class="corpo-sm">Na rodada da noite de 11-10, o multiplicador da greve no material rodante subiu de 1,17 para 1,73 (nos equipamentos fixos, de 1,11 para 1,66).</p>
      <p class="corpo-sm">Causa: com o km de 2025 medido, a exposição já descontava a greve, e o código descontava de novo.</p>
      <p class="corpo-sm">A rodada foi parada, a exposição corrigida e tudo refeito. A greve voltou a não ter efeito detectável por trem-hora.</p>
    </div>
  </div>
</div>""",
"docs/decisoes/registro_de_decisoes.md (D60, D61, D63); specs/019 (referência do motor) e 020; fontes/verificacao/preregistro/",
"""<p>O protocolo existe para que a revisão não vire ajuste ao gosto do resultado: a versão anterior fica guardada, as previsões ficam congeladas antes dos dados existirem e as regras são escritas antes.</p>
<p>O caso da greve mostra por que conferir no meio: um número estranho parou a rodada.</p>""")

_DV1 = {l: POL_V1["disponibilidade_dia_util"][l]["media"] * 100 for l in ORDEM}
_DV2 = {l: POL["disponibilidade_dia_util"][l]["media"] * 100 for l in ORDEM}
_AD = [
    ("Minutos parados das falhas técnicas, total", br(NORM["minutos_total_calculada"]), br(NORM["minutos_total_final"]), "duração pela faixa oficial (D55)"),
    ("Minutos parados por ano, rede (painel)", br(L_V1["rede"]["min_fora_ano"]), br(L["rede"]["min_fora_ano"]), "idem"),
    ("MTTR da Azul (min)", br(L_V1["azul"]["mttr_min"], 2), br(L["azul"]["mttr_min"], 2), "seis registros de Saint-Michel"),
    ("Disponibilidade da Azul, dia útil (simulador)", br(_DV1["azul"], 2) + "%", br(_DV2["azul"], 2) + "%", "idem"),
    ("β Verde–Laranja", br(BETA_VL_V1["beta_a"], 3) + " (todas)", br(BETA_VL_EF["beta_a"], 3) + " (fixas)", "denominador da família (spec 018)"),
    ("Operação degradada, min por dia útil", "−" + br(_OD_V1, 1), "−" + br(_OD, 1), "menos interrupções longas de EF"),
    ("Disponibilidade origem-destino da rede atual", br(EXP_V1["rede_atual"]["dispOD"]["media"] * 100, 3) + "%", br(DISP_OD_ATUAL, 3) + "%", "idem"),
    ("Ganho de Atwater–Université-de-Montréal", "+" + _pp(EXP_V1["busca_exaustiva"]["por_ganho"][0]["ganho"]["media"]), "+" + _pp(_ATW["media"]), "continua a melhor ligação"),
    ("Ganho da Rosa com a Azul até Anjou", sn(100 * _RAZ_V1, 3), "+" + _pp(_RAZ["media"]), "passa à frente da Rosa sozinha"),
    ("Simulador contra 2025: médias dentro do IC", f"{V1_NO_IC} de {N_COMP}", f"{REV_NO_IC} de {N_COMP}", "spec 020"),
]
ANTES_DEPOIS = slide("Revisão de 2026-11 · antes e depois", "Os números mudaram; a resposta e as três conclusões ficaram", f"""
<table class="tab tab-ad"><thead><tr><th>Número</th><th class="num">v1.1.0 (antes)</th><th class="num">v1.2.0 (depois)</th><th>Por quê</th></tr></thead>
<tbody>{"".join(f'<tr><td>{a}</td><td class="num">{b}</td><td class="num"><b>{c}</b></td><td class="muted">{d}</td></tr>' for a, b, c, d in _AD)}</tbody></table>""",
"fontes/verificacao/revisao_2026-11.md; os JSON citados nos slides anteriores, no disco e na etiqueta v1.1.0",
"""<p>A tabela completa, com todos os números que mudaram, é gerada por script em revisao_2026-11.md.</p>
<p>O ponto a destacar: a ligação recomendada e as três conclusões não mudaram. Mudou o tamanho dos efeitos.</p>""", "compacto")

SOMA = slide("Revisão de 2026-11 · a soma das fontes", "A Azul parecia 9% abaixo nos equipamentos fixos; com dias suficientes, era acaso", """
<div class="cols c-50-50">
  <div>
    <div class="label">A pergunta</div>
    <p class="corpo">Com as falhas divididas em fontes, o simulador ainda gera, por linha e família, o total que os parâmetros mandam? Numa crítica, a Azul nos equipamentos fixos apareceu 9% abaixo.</p>
    <div class="label" style="margin-top:22px">O teste</div>
    <ul class="lista lista-sm">
      <li>20.000 dias úteis com os parâmetros reais (<code>soma_fontes.test.ts</code>).</li>
      <li>Intervalo pela variância observada entre os dias: as falhas vêm agrupadas, e o intervalo de Poisson fica estreito demais.</li>
      <li>Cada uma das fontes conferida sozinha, com 200 mil sorteios.</li>
    </ul>
  </div>
  <div>
    <div class="stats">
      <div class="stat"><div class="stat-v">8 de 8</div><div class="stat-l">combinações linha × família dentro do IC 95% do esperado</div></div>
      <div class="stat"><div class="stat-v">0,1576</div><div class="stat-l">falhas por dia simuladas na Azul, equipamentos fixos, contra 0,1563 esperadas</div></div>
      <div class="stat"><div class="stat-v">1 − 0,95⁸</div><div class="stat-l">= 34% de chance de pelo menos uma das 8 cair fora por acaso: um caso fora num lote pequeno não é defeito</div></div>
    </div>
  </div>
</div>
<p class="nota">O número de dias foi escolhido depois de ver dois lotes de 10.000 dias, e isso está escrito no teste e na spec 019. O teste roda em toda publicação.</p>""",
"specs/019-motor-n-fontes (Resultado, soma das fontes); app/tests/motor/soma_fontes.test.ts; D66",
"""<p>Este foi o item 7 da lista de conferência final. A suspeita era de defeito no motor; o teste mostrou que não.</p>
<p>Lição: com 8 comparações a 95%, a chance de ao menos uma cair fora por acaso é de um terço. Um caso fora não basta para dizer que há defeito.</p>""")

FECHAMENTO = slide("Fechamento · D65 e D66 · 2026-11-11", "Como fechamos a entrega", f"""
<div class="cards c3 cards-alto">
  <div class="card"><h3>A resposta ao objetivo</h3><p>"A linha que melhor resolve a movimentação das pessoas": o relatório agora diz o nome. Atwater–Université-de-Montréal (+{_pp(_ATW["media"])} p.p.); entre as oficiais, a Rosa com a Azul até Anjou (+{_pp(_RAZ["media"])}).</p><p class="onde">D66 · relatório §7</p></div>
  <div class="card"><h3>Sem pedido à STM</h3><p>O e-mail com as dúvidas sobre os dados não foi enviado. As perguntas viraram limitações declaradas no relatório.</p><p class="onde">D65</p></div>
  <div class="card"><h3>Reprodução do zero</h3><p>Vale até o commit a7f0594 (48 idênticos, 5 na tolerância). Depois da revisão não foi refeita: exceção registrada na spec 013.</p><p class="onde">D65 · spec 013</p></div>
  <div class="card"><h3>Licença MIT</h3><p>Código e textos da equipe sob MIT. Os dados seguem a licença de cada fonte; os artigos da IEEE ficam fora do repositório.</p><p class="onde">D66 · LICENSE</p></div>
  <div class="card"><h3>v1.2.0 congelada</h3><p>Etiqueta no commit de entrega ({VERS[2][1]}) e Release com o zip do site, servida em /versoes/v1.2.0/.</p><p class="onde">D66 · spec 013</p></div>
  <div class="card"><h3>Navegador</h3><p>Basta funcionar no Chrome do notebook da equipe. Firefox, Safari e celular físico ficam fora desta entrega.</p><p class="onde">D66 · spec 010</p></div>
</div>""",
"docs/decisoes/registro_de_decisoes.md (D65 e D66); README.md; LICENSE; specs 010 e 013",
"""<p>As decisões do último dia. A mais importante é a primeira: o objetivo do trabalho pede o nome de uma linha, e o relatório agora o diz.</p>
<p>O resto é escopo: o que fica de fora desta entrega está registrado como exceção, com o motivo.</p>""")

PENDENCIAS = slide("O que fica aberto", "Pendências registradas, nenhuma bloqueia a entrega", """
<table class="tab"><thead><tr><th>Spec</th><th>Pendência</th><th>Por que ficou</th></tr></thead><tbody>
  <tr><td>010</td><td>Abrir o site no Chrome do notebook e olhar o contador de quadros (pico, 300×)</td><td>Única conferência que só a equipe faz</td></tr>
  <tr><td>020</td><td>Avaliar as previsões pré-registradas contra os meses novos</td><td>Espera a STM publicar 3 meses depois de 2026-06</td></tr>
  <tr><td>019</td><td>Fator diário comum por família; dispersão por mês</td><td>Somar fontes independentes agrupa menos que o observado</td></tr>
  <tr><td>018</td><td>Horas de serviço como medida de exposição (sensibilidade)</td><td>Fora do escopo da revisão</td></tr>
  <tr><td>012</td><td>Backtest com o motor TypeScript</td><td>Hoje o backtest roda no Python</td></tr>
  <tr><td>003</td><td>Datas do GP do Canadá numa segunda fonte</td><td>Status "não verificado"</td></tr>
  <tr><td>021 e 022</td><td>Importância de cada componente (Birnbaum) e cenário 2031 (frota nova e Azul até Anjou)</td><td>Próxima rodada, por decisão da equipe</td></tr>
</tbody></table>""",
"specs/*/tasks.md (tarefas abertas); docs/decisoes/registro_de_decisoes.md (D60, D66)",
"""<p>Nada aqui impede a entrega: são extensões ou conferências que dependem de dado que ainda não existe.</p>
<p>A única que depende de nós é a primeira: abrir o simulador no Chrome e olhar o contador de quadros por segundo.</p>""")

def _seg(notas):
    m = re.search(r"Tempo:</b> *(?:(\d+) min)? *(?:(\d+) s)?", notas)
    return (int(m.group(1) or 0) * 60 + int(m.group(2) or 0)) if m else 0
def _mmss(s):
    return f"{s} s" if s < 60 else (f"{s // 60} min {s % 60:02d} s" if s % 60 else f"{s // 60} min")
def _assunto(s):
    """Assunto do slide: o começo do sobretítulo, ou o título."""
    return (s["eyebrow"].split(" · ")[0] or "Capa") if s["eyebrow"] else "Capa"
_TEMPOS = [_seg(s["notas"]) for s in EXECUTIVA]
assert all(_TEMPOS), "slide da executiva sem tempo nas notas"
ROTEIRO_EXEC = slide("Para a apresentação à turma", f"A executiva tem {len(EXECUTIVA)} slides e cerca de {round(sum(_TEMPOS) / 60)} minutos", f"""
<div class="cols c-60-40">
  <table class="tab tab-rot"><thead><tr><th class="num">#</th><th>Assunto</th><th class="num">Tempo</th><th class="num">Acumulado</th></tr></thead><tbody>
  {"".join(f'<tr><td class="num">{i}</td><td>{_assunto(s)}</td><td class="num">{_mmss(t)}</td><td class="num muted">{_mmss(sum(_TEMPOS[:i]))}</td></tr>' for i, (s, t) in enumerate(zip(EXECUTIVA, _TEMPOS), 1))}
  </tbody></table>
  <div>
    <div class="label">Como usar</div>
    <ul class="lista lista-sm">
      <li><b>Endereço:</b> /apresentacao/ no site (este deck interno fica em /apresentacao/interna.html).</li>
      <li><b>Teclas:</b> setas ou espaço para andar, F para tela cheia, N para as notas de cada slide.</li>
      <li><b>PDF</b> ao lado do HTML, para levar num pendrive.</li>
      <li><b>Se sobrar tempo:</b> abrir o simulador e trocar o cenário ao vivo, por exemplo um dia de neve.</li>
      <li><b>Tempos</b> vêm das notas de cada slide; a divisão de quem fala é da equipe.</li>
    </ul>
  </div>
</div>""",
"docs/apresentacao/index.html (notas de cada slide)",
"""<p>Os tempos somam as notas de cada slide da executiva. Dá para dividir em blocos: abertura e resposta (1 e 2), medição e modelos (3 a 7), simulador e escolhas (8 a 10), confiança e conclusões (11 a 13).</p>""", "compacto")

_TX = TAXA
QA = [
    ("Por que Montreal, e não São Paulo?", "Metrô, CPTM e ViaQuatro só publicam PDF, e a API Direto dos Trens exige token. A STM publica cada incidente de 2019 a 2026, com início, retomada, causa, linha e local, sob CC BY 4.0 (D01)."),
    ("Por que binomial negativa, e não Poisson?", f"A variância das contagens por hora passa da média: α = {br(_TX['MR']['alpha_nb'], 2)} no material rodante e {br(_TX['EF']['alpha_nb'], 2)} nos equipamentos fixos. O teste rejeita Poisson com p &lt; 10⁻³⁰ (D19)."),
    ("O que é o β da causa comum?", f"A fração das falhas de uma linha que derruba outra junto. Verde com Laranja, nas falhas de equipamento fixo: {br(BETA_VL_EF['beta_a'], 3)}. É pouco, mas é o evento que tira os dois caminhos do centro ao mesmo tempo."),
    ("Se a validação não passou, por que confiar?", f"O critério foi escrito antes e não mudou. A falha tem causa conhecida (o registro de 2024 nos terminais), a regra nova passou em outro período ({br(VERSOES[3][3], 1)}%) e o simulador revisto reproduz {REV_NO_IC} de {N_COMP} médias de 2025."),
    ("Por que Atwater–Université-de-Montréal, se ninguém propôs essa ligação?", f"Ela saiu de uma busca entre {N_LIGACOES} ligações diretas de até 3 km. É hipótese de traçado, não projeto: o valor dela é mostrar o ponto fraco, a Azul presa à Laranja."),
    ("+0,063 ponto percentual não é pouco?", f"A rede já tem {br(DISP_OD_ATUAL, 1)}% de disponibilidade, e o ganho é quase o dobro da melhor proposta oficial. Na viagem de Atwater a Université-de-Montréal, o tempo sem caminho cai de {LN_SEM[0]} para {LN_SEM[1]} min por dia."),
    ("Vocês usaram IA? Como sabem que os números não foram inventados?", f"Sim: o Claude Code ajudou no código e nos textos, e um agente crítico revisou o trabalho em {len(CRITICAS)} rodadas. Por isso nenhum número vale sem fonte com hash, script e um segundo programa que o refaz."),
    ("Por que a Azul mudou tanto na revisão?", f"Seis registros de Saint-Michel, em outubro de 2024, tinham quase 20 h pelos horários e \"2 min ou menos\" pela faixa oficial. Com a faixa (D55), o MTTR da Azul cai de {br(L_V1['azul']['mttr_min'], 2)} para {br(L['azul']['mttr_min'], 2)} min."),
]
def _qa(itens):
    return '<div class="qa">' + "".join(f'<div class="qa-i"><h3>{q}</h3><p>{r}</p></div>' for q, r in itens) + "</div>"
QA1 = slide("Para a apresentação · perguntas prováveis (1 de 2)", "Dados e modelos", _qa(QA[:4]),
            "docs/decisoes/registro_de_decisoes.md; taxa_MR.json e taxa_EF.json; distribuicoes.json; backtest.json; revalidacao.json",
            "<p>Respostas curtas para as perguntas mais prováveis. Cada uma cita a decisão ou o arquivo de onde vem.</p>")
QA2 = slide("Para a apresentação · perguntas prováveis (2 de 2)", "Resposta, confiança e revisão", _qa(QA[4:]),
            "expansao.json; fontes/verificacao/linhas_novas.md; critica_*.md; linhas.json (e na v1.1.0)",
            "<p>A pergunta sobre IA é provável. A resposta honesta é sim, e o projeto foi desenhado para não depender de confiar em quem fez as contas, humano ou IA.</p>")

INTERNA = [CAPA_INT, AGENDA, LINHA_TEMPO, EM_NUMEROS,
           divisor(1, "Como começamos", "O tema, a pergunta e o método"), pega("A pergunta"), METODO, SPECS_SL,
           divisor(2, "Dados", "Das fontes públicas a uma tabela de falhas que qualquer pessoa pode refazer"),
           pega("Antes dos resultados"), pega("Dados · 2019"), NORMALIZA, pega("Indicadores por linha"),
           divisor(3, "Modelos", "Taxa de falha, agrupamento no tempo e causa comum"),
           pega("O que muda a taxa"), pega("As falhas se agrupam"), pega("Causa comum"),
           divisor(4, "Simulador", "A rede trem a trem, no navegador, para comparar políticas e linhas novas"),
           ARQ, pega("Simulador · eventos"), pega("Políticas"), VIAGEM, pega("Que linha construir"),
           divisor(5, "Validação", "Prever o que o modelo não viu, com o critério escrito antes"),
           pega("Validação contra o histórico"), pega("Decisões tomadas depois"),
           divisor(6, "Publicação e crítica", "Site público, conferência automática e quatro rodadas de revisão"),
           PUBLICACAO, CRITICAS_SL, DIFICULDADES,
           divisor(7, "Revisão de 2026-11", "Falhas por frota e por setor, durações pela faixa oficial e tudo refeito"),
           FONTES9, PROTOCOLO, pega("Revisão de 2026-11 · ressegmentação"), ANTES_DEPOIS, SOMA,
           divisor(8, "Fechamento", "A resposta, as conclusões, o que fica aberto e a apresentação para a turma"),
           RESUMO, pega("Conclusões"), pega("Limitações"), FECHAMENTO, PENDENCIAS, ROTEIRO_EXEC, QA1, QA2, pega("Confira")]
_AG = []
for i, s in enumerate(INTERNA, 1):
    if "divisor" in s["classe"]:
        n = re.search(r'div-n">(\d+)', s["corpo"]).group(1)
        t = re.search(r"<h1>(.*?)</h1>", s["corpo"]).group(1)
        sub = re.search(r'lede">(.*?)</p>', s["corpo"]).group(1)
        _AG.append(f'<li><span class="ag-n">{n}</span><span class="ag-t">{t}</span><span class="ag-s">{sub}</span><span class="ag-p">slide {i}</span></li>')
assert len(_AG) == 8
AGENDA["corpo"] = '<ol class="agenda">' + "".join(_AG) + "</ol>"
monta(INTERNA, OUT_INT, "Confiabilidade do metrô de Montreal · apresentação interna da equipe")
