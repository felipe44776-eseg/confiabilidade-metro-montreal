"""Spec 005: falhas observadas contra esperadas pelo modelo da taxa, por faixa do dia e por linha.

Uso (da raiz do repositório, depois de pipeline/modelo_taxa.py): python -I pipeline/diagnostico_taxa.py
Entrada: dados/derivados/modelos/painel_modelo.csv.gz (falhas e falha esperada por hora-linha)
Saídas: fontes/verificacao/modelo_taxa_por_faixa.md e fontes/verificacao/modelo_taxa_por_faixa.svg
"""
import csv
import gzip
import io
from collections import defaultdict

FAIXAS = ["abertura", "pico_manha", "entrepico", "pico_tarde", "noite", "fim"]
ROTULO = {"abertura": "Abertura 5–6 h", "pico_manha": "Pico manhã 7–9 h", "entrepico": "Entrepico 10–15 h",
          "pico_tarde": "Pico tarde 16–18 h", "noite": "Noite 19–22 h", "fim": "Fim 23 h ou mais"}
LINHAS = ("verde", "laranja", "amarela", "azul")


def main():
    soma = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])  # (faixa, linha) -> [y_MR, mu_MR, y_EF, mu_EF]
    texto = gzip.decompress(open("dados/derivados/modelos/painel_modelo.csv.gz", "rb").read()).decode("utf-8")
    for r in csv.DictReader(io.StringIO(texto), delimiter=";"):
        s = soma[(r["faixa"], r["linha"])]
        s[0] += float(r["y_MR"]); s[1] += float(r["mu_MR"]); s[2] += float(r["y_EF"]); s[3] += float(r["mu_EF"])
    L = ["# Observado contra esperado por faixa do dia (spec 005)", "",
         "Gerado por `pipeline/diagnostico_taxa.py` a partir de `dados/derivados/modelos/painel_modelo.csv.gz`. "
         "Esperado = soma da falha esperada pelo modelo escolhido em cada hora-linha. Razão perto de 1 = o modelo acerta o nível da faixa.", "",
         "| Faixa | Causa | Observado | Esperado | Razão |", "|---|---|---|---|---|"]
    barras = []
    for f in FAIXAS:
        for k, causa in ((0, "MR"), (2, "EF")):
            y = sum(soma[(f, l)][k] for l in LINHAS)
            m = sum(soma[(f, l)][k + 1] for l in LINHAS)
            L.append(f"| {ROTULO[f]} | {causa} | {y:.0f} | {m:.1f} | {y / m:.3f} |".replace(".", ","))
            barras.append((f, causa, y, m))
    L += ["", "## Por linha e faixa (MR + EF)", "", "| Linha | " + " | ".join(ROTULO[f] for f in FAIXAS) + " |", "|---|" + "---|" * len(FAIXAS)]
    for l in LINHAS:
        cel = []
        for f in FAIXAS:
            s = soma[(f, l)]
            cel.append(f"{s[0] + s[2]:.0f} / {s[1] + s[3]:.0f}")
        L.append(f"| {l} | " + " | ".join(cel) + " |")
    L += ["", "Cada célula: observado / esperado.", "", "![Observado contra esperado por faixa](modelo_taxa_por_faixa.svg)", ""]
    open("fontes/verificacao/modelo_taxa_por_faixa.md", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    # Gráfico de barras pareadas (observado e esperado) por faixa, uma escala, rótulos em cor de texto
    w, h, mx, my = 720, 300, 56, 40
    topo = max(max(y, m) for _, _, y, m in barras) * 1.12
    gw = (w - 2 * mx) / len(FAIXAS)
    partes = []
    cores = {"observado": "#2f6db3", "esperado": "#9aa7b4"}
    for i, f in enumerate(FAIXAS):
        for j, causa in enumerate(("MR", "EF")):
            _, _, y, m = next(b for b in barras if b[0] == f and b[1] == causa)
            x0 = mx + i * gw + 6 + j * (gw - 12) / 2
            bw = (gw - 12) / 4 - 2
            for k, (nome, v) in enumerate((("observado", y), ("esperado", m))):
                alt = v / topo * (h - 2 * my)
                x = x0 + k * (bw + 2)
                partes.append(f'<rect x="{x:.1f}" y="{h - my - alt:.1f}" width="{bw:.1f}" height="{alt:.1f}" rx="2" fill="{cores[nome]}">'
                              f'<title>{ROTULO[f]}, {causa}, {nome}: {v:.0f}</title></rect>')
            partes.append(f'<text x="{x0 + bw + 1:.1f}" y="{h - my + 13}" font-size="10" text-anchor="middle" fill="#444">{causa}</text>')
        partes.append(f'<text x="{mx + i * gw + gw / 2:.1f}" y="{h - my + 27}" font-size="10.5" text-anchor="middle" fill="#222">{ROTULO[f]}</text>')
    leg = (f'<rect x="{mx}" y="12" width="10" height="10" rx="2" fill="{cores["observado"]}"/><text x="{mx + 14}" y="21" font-size="11" fill="#222">observado</text>'
           f'<rect x="{mx + 90}" y="12" width="10" height="10" rx="2" fill="{cores["esperado"]}"/><text x="{mx + 104}" y="21" font-size="11" fill="#222">esperado pelo modelo</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="sans-serif">'
           f'<rect width="{w}" height="{h}" fill="#fff"/>{leg}<line x1="{mx}" y1="{h - my}" x2="{w - mx}" y2="{h - my}" stroke="#999"/>{"".join(partes)}</svg>')
    open("fontes/verificacao/modelo_taxa_por_faixa.svg", "w", encoding="utf-8", newline="\n").write(svg + "\n")
    print("\n".join(L[:20]))


if __name__ == "__main__":
    main()
