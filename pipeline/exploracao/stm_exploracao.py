"""Exploração da base de incidentes do metrô de Montreal (STM) para planejar o trabalho.

Uso: python -I pipeline/exploracao/stm_exploracao.py dados/brutos/stm/incidents_metro.csv
A exposicao (km) entra no painel: ver pipeline/monta_painel.py.
"""
import csv
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TECNICAS = ("Matériel roulant", "Équipements fixes")
FAIXAS = {
    "02 min et moins": (0, 2), "03 à 04 min": (3, 4), "05 à 09 min": (5, 9), "10 à 14 min": (10, 14),
    "15 à 19 min": (15, 19), "20 à 24 min": (20, 24), "25 à 29 min": (25, 29), "30 min et plus": (30, 10**6),
}


def carrega(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    cab = linhas[1]
    return [dict(zip(cab, (c.strip() for c in r))) for r in linhas[2:] if len(r) >= len(cab) and r[0].strip()]


def minutos(hhmm):
    # A STM usa o dia de servico: depois da meia-noite a hora segue como 24:xx, 25:xx.
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def instante(r):
    return datetime.strptime(r["Jour calendaire"], "%Y-%m-%d") + timedelta(minutes=minutos(r["Heure de l'incident"]))


def duracao(r):
    return (minutos(r["Heure de reprise"]) - minutos(r["Heure de l'incident"])) % 1440


def resumo(v):
    v = sorted(v)
    media = statistics.fmean(v)
    cv = statistics.pstdev(v) / media if media else float("nan")
    return f"n={len(v):5d} media={media:7.1f} mediana={statistics.median(v):7.1f} p90={v[int(0.9 * (len(v) - 1))]:7.1f} CV={cv:4.2f}"


dados = carrega(sys.argv[1])
tec = [r for r in dados if r["Cause primaire"] in TECNICAS]
print(f"eventos: {len(dados)} | tecnicos: {len(tec)}")

print("\n[1] Tipo (T=trem, S=estacao) nos tecnicos:", Counter((r["Cause primaire"], r["Type d'incident"]) for r in tec).most_common())
print("\n[2] Sintoma nos tecnicos (top 15):", Counter(r["Symptome"] for r in tec).most_common(15))
print("\n[3] Sintoma em 'Autres' (top 8):", Counter(r["Symptome"] for r in dados if r["Cause primaire"] == "Autres").most_common(8))

dentro = sum(1 for r in tec if r["Incident en minutes"] in FAIXAS and FAIXAS[r["Incident en minutes"]][0] <= duracao(r) <= FAIXAS[r["Incident en minutes"]][1])
print(f"\n[4] Duracao calculada cai na faixa oficial em {dentro}/{len(tec)} eventos tecnicos ({100 * dentro / len(tec):.0f}%)")
print("    Faixa oficial nos tecnicos:", Counter(r["Incident en minutes"] for r in tec).most_common())

mr = [r for r in tec if r["Cause primaire"] == "Matériel roulant"]
veic = Counter(r["Véhicule"] for r in mr if r["Véhicule"] not in ("#", ""))
print(f"\n[5] Material rodante: {len(mr)} eventos, {sum(veic.values())} com veiculo, {len(veic)} veiculos distintos")
print("    Exemplos de codigo de veiculo:", [v for v, _ in veic.most_common(6)])
por_veic = Counter(veic.values())
print("    Eventos por veiculo (n eventos: n veiculos):", sorted(por_veic.items())[:12])
print("    Frota x tipo de material:", Counter((r["Cause secondaire"], r["Type de matériel"]) for r in mr).most_common(8))

print("\n[6] Eventos tecnicos por linha e ano:")
tab = defaultdict(Counter)
for r in tec:
    tab[r["Ligne"]][r["Année civile"]] += 1
anos = sorted({r["Année civile"] for r in tec})
print("    " + "linha".ljust(14) + " ".join(a.rjust(5) for a in anos))
for linha in ("Ligne verte", "Ligne orange", "Ligne bleue", "Ligne jaune"):
    print("    " + linha.ljust(14) + " ".join(str(tab[linha][a]).rjust(5) for a in anos))

print("\n[7] Tempo entre falhas tecnicas por linha (horas de calendario):")
for linha in ("Ligne verte", "Ligne orange", "Ligne bleue", "Ligne jaune"):
    ts = sorted(instante(r) for r in tec if r["Ligne"] == linha)
    tbf = [(b - a).total_seconds() / 3600 for a, b in zip(ts, ts[1:])]
    zeros = sum(1 for x in tbf if x == 0)
    print(f"    {linha:13s} {resumo(tbf)} | intervalos=0: {zeros}")
print("    (CV perto de 1 sugere exponencial; acima de 1, falhas agrupadas)")

print("\n[8] Duracao (tempo ate retomar, min) por causa e linha:")
for causa in TECNICAS:
    for linha in ("Ligne verte", "Ligne orange", "Ligne bleue", "Ligne jaune"):
        v = [duracao(r) for r in tec if r["Cause primaire"] == causa and r["Ligne"] == linha]
        if v:
            print(f"    {causa:18s} {linha:13s} {resumo(v)}")
