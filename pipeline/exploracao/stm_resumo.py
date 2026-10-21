import csv
import statistics
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def minutos(hhmm):
    try:
        h, m = hhmm.strip().split(":")
        return int(h) * 60 + int(m)
    except ValueError:
        return None


with open(sys.argv[1], encoding="utf-8-sig", newline="") as f:
    linhas = list(csv.reader(f, delimiter=";"))

cab = linhas[1]
idx = {c: i for i, c in enumerate(cab)}
dados = [r for r in linhas[2:] if len(r) >= len(cab) and r[0].strip()]
print("eventos:", len(dados))
datas = sorted(r[idx["Jour calendaire"]] for r in dados)
print("periodo:", datas[0], "->", datas[-1])

col = lambda r, c: r[idx[c]].strip()
print("\nType:", Counter(col(r, "Type d'incident") for r in dados).most_common())
print("\nCause primaire:", Counter(col(r, "Cause primaire") for r in dados).most_common())
print("\nLigne:", Counter(col(r, "Ligne") for r in dados).most_common())
print("\nFaixa 'Incident en minutes':", Counter(col(r, "Incident en minutes") for r in dados).most_common())

dur = defaultdict(list)
sem_hora = 0
for r in dados:
    a, b = minutos(col(r, "Heure de l'incident")), minutos(col(r, "Heure de reprise"))
    if a is None or b is None:
        sem_hora += 1
        continue
    d = (b - a) % 1440
    dur[col(r, "Cause primaire")].append(d)
print("\nsem hora de inicio ou retomada:", sem_hora)
print("Duracao (retomada - incidente, min) por causa primaria:")
for c, v in sorted(dur.items(), key=lambda kv: -len(kv[1])):
    v.sort()
    p90 = v[int(0.9 * (len(v) - 1))]
    print(f"  {c:32s} n={len(v):6d} mediana={statistics.median(v):6.1f} p90={p90:5d} max={v[-1]}")

tec = [r for r in dados if col(r, "Cause primaire") in ("Matériel roulant", "Équipement fixe", "Équipements fixes")]
print("\nCausas tecnicas (material rodante + equipamento fixo):", len(tec))
print("  por ano:", sorted(Counter(col(r, "Année civile") for r in tec).items()))
print("  causa secundaria (top 12):", Counter(col(r, "Cause secondaire") for r in tec).most_common(12))
