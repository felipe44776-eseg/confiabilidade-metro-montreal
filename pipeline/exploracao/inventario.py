import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FORTES = {
    "mkbf": r"mkbf",
    "mtbf": r"mtbf",
    "entre falhas": r"entre\s+falhas",
    "falha(s)": r"\bfalhas?\b",
    "notaveis": r"not[aá]ve(l|is)",
    "incidente": r"incidentes?",
    "confiab.": r"confiabilidade",
    "regularid.": r"regularidade",
}
CTX = re.compile(r"mkbf|mtbf|entre\s+falhas|\bfalhas?\b|incidentes? not|ocorr[eê]ncias? not", re.IGNORECASE)


def inventario(path, mostrar):
    bruto = open(path, encoding="utf-8", errors="replace").read()
    txt = unicodedata.normalize("NFKC", bruto)
    paginas = txt.split("\f")
    ligaduras = sum(bruto.count(c) for c in "ﬁﬂﬀﬃﬄ")
    cont = {k: len(re.findall(v, txt, re.IGNORECASE)) for k, v in FORTES.items()}
    nome = path.replace("\\", "/").split("/")[-1]
    print(f"{nome:16s} pags={len(paginas)-1:>3} ligaduras={ligaduras:>4} | " + " ".join(f"{k}={n}" for k, n in cont.items()))
    if mostrar:
        n = 0
        for i, pag in enumerate(paginas, 1):
            for linha in pag.splitlines():
                if CTX.search(linha) and n < mostrar:
                    print(f"      p{i}: {' '.join(linha.split())[:210]}")
                    n += 1


mostrar = int(sys.argv[1])
for p in sys.argv[2:]:
    inventario(p, mostrar)
