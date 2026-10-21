import csv
import sys
from collections import Counter
from datetime import datetime


def parse_dt(s):
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%m/%d/%y %H:%M", "%m/%d/%Y %H:%M", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def resumo(path):
    print("=" * 70)
    print(path)
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header = [h.strip() for h in rows[0][:10]]
    print("colunas:", header)
    dados = [r[:10] for r in rows[1:] if any(c.strip() for c in r[:10])]
    print("linhas com conteudo:", len(dados))

    grupo, tipo, local = Counter(), Counter(), Counter()
    falha_local, falha_stop = Counter(), Counter()
    inicios, sem_fim, dur_falha = [], 0, {}
    exemplos_dt = []
    for r in dados:
        r = [c.strip() for c in r] + [""] * (10 - len(r))
        g, stop, tp, loc, ini, fim, dur = r[2], r[3], r[4], r[5], r[7], r[8], r[9]
        grupo[g] += 1
        tipo[tp] += 1
        local[loc] += 1
        d = parse_dt(ini)
        if d:
            inicios.append(d)
        elif len(exemplos_dt) < 3:
            exemplos_dt.append(ini)
        if not fim:
            sem_fim += 1
        if g.upper() == "FAILURE":
            falha_local[loc] += 1
            falha_stop[stop] += 1
            try:
                dur_falha.setdefault(loc, []).append(float(dur))
            except ValueError:
                pass

    if inicios:
        print("periodo:", min(inicios), "->", max(inicios), "| dias distintos:", len({d.date() for d in inicios}))
    if exemplos_dt:
        print("datas nao parseadas (amostra):", exemplos_dt, "| total parseadas:", len(inicios))
    print("sem StopEndTime:", sem_fim)
    print("\nStopGroup:", grupo.most_common())
    print("\nStopType:", tipo.most_common())
    print("\nStopLocation (top 12):", local.most_common(12))
    print("\nFAILURE total:", sum(falha_local.values()))
    print("FAILURE por local:")
    for loc, n in falha_local.most_common():
        ds = sorted(dur_falha.get(loc, []))
        med = ds[len(ds) // 2] if ds else None
        tot = round(sum(ds), 1) if ds else None
        print(f"  {loc:28s} n={n:4d}  TTR mediano={med} min  soma={tot} min")
    print("FAILURE por tipo de parada:", falha_stop.most_common())


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for p in sys.argv[1:]:
    resumo(p)
