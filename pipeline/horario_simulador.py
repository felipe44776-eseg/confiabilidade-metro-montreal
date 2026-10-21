"""Exporta o horário do GTFS no formato compacto que o simulador (app/) lê.

Uso (da raiz do repositório): python -I pipeline/horario_simulador.py
Saída: dados/derivados/simulador/rede.json
  linhas: estações na ordem do sentido 0, com km ao longo do traçado (spec 002) e coordenadas
  horarios: por tipo de dia (útil, sábado, domingo), por linha e sentido, cada viagem como a lista de
            [chegada, partida] em segundos desde a meia-noite do dia de operação, alinhada às estações do sentido
  correspondencias: estações servidas por mais de uma linha
Viagens curtas (que não começam ou não terminam num terminal) ficam, com o índice da primeira estação.
"""
import csv
import io
import json
import os
import zipfile
from collections import defaultdict

GTFS = "dados/brutos/gtfs/gtfs_stm_mdb-2126_latest.zip"
ROTA = {"1": "verde", "2": "laranja", "4": "amarela", "5": "azul"}
MOLDE = {"26N-GLOBAUX-01-S": "util", "26N-GLOBAUX-00-A": "sabado", "26N-GLOBAUX-01-I": "domingo"}
COR = {"verde": "#008E4F", "laranja": "#EF8122", "amarela": "#FFD900", "azul": "#0076BE"}


def seg(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def main():
    z = zipfile.ZipFile(GTFS)
    tab = lambda n: csv.DictReader(io.TextIOWrapper(z.open(n), encoding="utf-8-sig"))
    est = json.load(open("dados/derivados/geo/estacoes.geojson", encoding="utf-8"))["features"]
    seq = defaultdict(list)
    with open("dados/derivados/gtfs/metro_sequencias.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["direction_id"] == "0":
                seq[ROTA[r["route_id"]]].append(r)
    linhas = {}
    indice_mae = {}
    for l, rs in seq.items():
        rs.sort(key=lambda r: int(r["ordem"]))
        props = {f["properties"]["ordem"]: f for f in est if f["properties"]["linha"] == l}
        estacoes = []
        for i, r in enumerate(rs):
            f = props[int(r["ordem"])]
            estacoes.append({"id": r["parent_station"], "nome": f["properties"]["estacao"], "km": f["properties"]["km_linha"],
                             "lat": round(f["geometry"]["coordinates"][1], 6), "lon": round(f["geometry"]["coordinates"][0], 6)})
            indice_mae[(l, r["parent_station"])] = i
        linhas[l] = {"cor": COR[l], "estacoes": estacoes}
    mae = {s["stop_id"]: s.get("parent_station") or s["stop_id"] for s in tab("stops.txt")}
    viagens = {t["trip_id"]: (ROTA[t["route_id"]], int(t["direction_id"]), MOLDE[t["service_id"]]) for t in tab("trips.txt")
               if t["route_id"] in ROTA and t["service_id"] in MOLDE}
    paradas = defaultdict(list)
    for st in tab("stop_times.txt"):
        if st["trip_id"] in viagens:
            paradas[st["trip_id"]].append((int(st["stop_sequence"]), seg(st["arrival_time"]), seg(st["departure_time"]), st["stop_id"]))
    horarios = {t: {l: {"0": [], "1": []} for l in linhas} for t in ("util", "sabado", "domingo")}
    for tid, ps in paradas.items():
        l, d, tipo = viagens[tid]
        ps.sort()
        n = len(linhas[l]["estacoes"])
        idx = [indice_mae[(l, mae[p[3]])] for p in ps]
        # no sentido 1 as estações vêm na ordem inversa; guardamos o índice no sentido 0
        passos = idx if d == 0 else [n - 1 - i for i in idx]
        if passos != list(range(passos[0], passos[0] + len(passos))):
            raise ValueError(f"viagem {tid} pula estações: {passos}")
        horarios[tipo][l][str(d)].append({"inicio": passos[0], "tempos": [[p[1], p[2]] for p in ps]})
    for t in horarios:
        for l in horarios[t]:
            for d in ("0", "1"):
                horarios[t][l][d].sort(key=lambda v: v["tempos"][0][1])
    nomes = defaultdict(set)
    for l, info in linhas.items():
        for e in info["estacoes"]:
            nomes[e["id"]].add(l)
    correspondencias = [{"estacao": next(e["nome"] for info in linhas.values() for e in info["estacoes"] if e["id"] == k), "id": k, "linhas": sorted(v)}
                        for k, v in sorted(nomes.items()) if len(v) > 1]
    rede = {"fonte": "GTFS STM 20261007130000_26N (moldes 26N-GLOBAUX-01-S, 00-A, 01-I); km da spec 002",
            "linhas": linhas, "correspondencias": correspondencias, "horarios": horarios}
    os.makedirs("dados/derivados/simulador", exist_ok=True)
    with open("dados/derivados/simulador/rede.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(rede, f, ensure_ascii=False, separators=(",", ":"))
    print({t: {l: len(v["0"]) + len(v["1"]) for l, v in horarios[t].items()} for t in horarios}, "| correspondências:",
          [(c["estacao"], c["linhas"]) for c in correspondencias])


if __name__ == "__main__":
    main()
