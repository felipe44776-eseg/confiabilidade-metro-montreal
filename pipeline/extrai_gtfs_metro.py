"""Extrai do GTFS da STM as tabelas leves e a sequencia de estacoes das 4 linhas de metro.

Uso (da raiz do projeto): python -I pipeline/extrai_gtfs_metro.py dados/brutos/gtfs/gtfs_stm_mdb-2126_latest.zip
Saida: dados/derivados/gtfs/{agency,routes,stops,calendar,calendar_dates,feed_info}.txt e dados/derivados/gtfs/metro_sequencias.csv

Para cada linha (route_id 1, 2, 4, 5) e sentido, escolhe a viagem com mais paradas e grava as estacoes
na ordem, com nome e coordenadas da estacao-mae (parent_station).
"""
import csv
import io
import os
import sys
import zipfile
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
z = zipfile.ZipFile(sys.argv[1])
SAIDA = "dados/derivados/gtfs"
os.makedirs(SAIDA, exist_ok=True)


def tabela(nome):
    return csv.DictReader(io.TextIOWrapper(z.open(nome), encoding="utf-8-sig"))


for nome in ("agency.txt", "routes.txt", "stops.txt", "calendar.txt", "calendar_dates.txt", "feed_info.txt"):
    if nome in z.namelist():
        open(os.path.join(SAIDA, nome), "wb").write(z.read(nome))

viagens = {t["trip_id"]: (t["route_id"], t.get("direction_id", "")) for t in tabela("trips.txt") if t["route_id"] in ("1", "2", "4", "5")}
print("viagens de metro:", len(viagens), dict(Counter(v[0] for v in viagens.values())))
seq = defaultdict(list)
for st in tabela("stop_times.txt"):
    if st["trip_id"] in viagens:
        seq[st["trip_id"]].append((int(st["stop_sequence"]), st["stop_id"]))
melhor = {}
for tid, s in seq.items():
    k = viagens[tid]
    if k not in melhor or len(s) > len(seq[melhor[k]]):
        melhor[k] = tid
paradas = {s["stop_id"]: s for s in tabela("stops.txt")}
with open(os.path.join(SAIDA, "metro_sequencias.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["route_id", "direction_id", "ordem", "stop_id", "parent_station", "estacao", "lat", "lon"])
    for (rid, did), tid in sorted(melhor.items()):
        pontos = sorted(seq[tid])
        for ordem, sid in pontos:
            s = paradas[sid]
            mae = paradas.get(s.get("parent_station") or "", s)
            w.writerow([rid, did, ordem, sid, s.get("parent_station", ""), mae["stop_name"], mae["stop_lat"], mae["stop_lon"]])
        print(f"linha {rid} sentido {did}: {len(pontos)} estacoes")
