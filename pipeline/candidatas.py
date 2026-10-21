"""Spec 014: converte a tabela manual de candidatas de expansão no JSON que o simulador lê.

Uso (da raiz do repositório): python -I pipeline/candidatas.py
Entradas: dados/manuais/candidatas_expansao.csv (pesquisa de 2026-10-21, fontes no LEIAME), estacoes.geojson (spec 002),
          dados/derivados/simulador/rede.json (ids das estações atuais)
Saída: dados/derivados/simulador/candidatas.json
Cada candidata vira uma lista de estações novas, na ordem do traçado, e uma lista de trechos novos
(estação nova ↔ estação nova ou ↔ estação atual). Estação com o mesmo nome da estação atual ligada é fundida com ela.
"""
import csv
import json
import math
from collections import defaultdict

CSV = "dados/manuais/candidatas_expansao.csv"


def norm(s):
    t = s.upper()
    for a, b in (("É", "E"), ("È", "E"), ("Ê", "E"), ("Ô", "O"), ("Î", "I"), ("Â", "A"), ("–", "-"), ("—", "-")):
        t = t.replace(a, b)
    return "".join(ch for ch in t.replace("SAINT-", "ST").replace("SAINTE-", "STE") if ch.isalnum())


def km(a, b):
    """Distância em linha reta (haversine): aproximação, o túnel real é mais longo."""
    la1, lo1, la2, lo2 = map(math.radians, (a["lat"], a["lon"], b["lat"], b["lon"]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))


def main():
    rede = json.load(open("dados/derivados/simulador/rede.json", encoding="utf-8"))
    chave_para = {}
    for f in json.load(open("dados/derivados/geo/estacoes.geojson", encoding="utf-8"))["features"]:
        p = f["properties"]
        est = next(e for e in rede["linhas"][p["linha"]]["estacoes"] if e["nome"] == p["estacao"])
        chave_para.setdefault(p["chave"], []).append({"linha": p["linha"], "id": est["id"], "nome": est["nome"], "lat": est["lat"], "lon": est["lon"]})
    linhas = defaultdict(list)
    with open(CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            linhas[r["candidata"]].append(r)
    saida = []
    for cid, rs in linhas.items():
        rs.sort(key=lambda r: int(r["ordem"]))
        estacoes, trechos, fontes = [], [], []
        for r in rs:
            for u in r["fonte_url"].split("|"):
                if u.strip() and u.strip() not in fontes:
                    fontes.append(u.strip())
            e = {"id": f"{cid}:{r['ordem']}", "nome": r["estacao"], "lat": float(r["lat"]), "lon": float(r["lon"]),
                 "fonte_coord": r["fonte_coord"], "status": r["status"], "funde_com": None}
            if r["liga_a_existente"]:
                alvo = chave_para.get(norm(r["liga_a_existente"]))
                if alvo is None:  # liga a estação de outra candidata (Vertières da Rosa → Vertières da Azul)
                    e["depende_de_candidata"] = r["liga_a_existente"]
                elif norm(r["estacao"]) == norm(r["liga_a_existente"]):
                    e["funde_com"] = alvo[0]
                else:
                    trechos.append({"de": e["id"], "para": alvo[0]["id"], "linha_existente": alvo[0]["linha"],
                                    "km_reta": round(km(e, alvo[0]), 3)})
            estacoes.append(e)
        for a, b in zip(estacoes, estacoes[1:]):
            pa = a["funde_com"]["id"] if a["funde_com"] else a["id"]
            pb = b["funde_com"]["id"] if b["funde_com"] else b["id"]
            trechos.append({"de": pa, "para": pb, "km_reta": round(km(a, b), 3)})
        r0 = rs[0]
        saida.append({"id": cid, "tipo": r0["tipo"], "proponente": r0["proponente"], "ano": int(r0["ano"]), "estacoes": estacoes,
                      "trechos": trechos, "km_reta_total": round(sum(t["km_reta"] for t in trechos), 2), "fontes": fontes,
                      "status": sorted({r["status"] for r in rs})})
    out = {"fonte": "dados/manuais/candidatas_expansao.csv (pesquisa de 2026-10-21; LEIAME e dados/brutos/expansao/manifesto.json)",
           "aviso": "Traçados aproximados: distâncias em linha reta entre estações. Só a Azul está em obras; as demais são hipótese de traçado.",
           "candidatas": saida}
    with open("dados/derivados/simulador/candidatas.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for c in saida:
        print(c["id"], len(c["estacoes"]), "estações", c["km_reta_total"], "km", "| ligações:",
              [t["para"] for t in c["trechos"] if t["para"].startswith("STATION")], "| fundidas:", [e["nome"] for e in c["estacoes"] if e["funde_com"]])


if __name__ == "__main__":
    main()
