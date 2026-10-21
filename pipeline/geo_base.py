"""Spec 002: base geoespacial do metro de Montreal, com validacao.

Uso (da raiz do projeto): python -I pipeline/geo_base.py
Entradas:
  dados/brutos/osm/overpass_metro_mtl.json        relacoes route=subway (com geometria) e estacoes, OpenStreetMap (ODbL)
  dados/brutos/wikidata/estacoes_metro_mtl.json   estacoes da rede Q392377 com coordenadas (CC0)
  dados/derivados/gtfs/metro_sequencias.csv       estacoes do GTFS da STM, na ordem
  dados/brutos/stm/incidents_metro.csv            incidentes, para georreferenciar o campo "Code de lieu"
Saidas:
  dados/derivados/geo/linhas.geojson     tracado real de cada linha (OSM), orientado como o sentido 0 do GTFS
  dados/derivados/geo/estacoes.geojson   estacoes com km ao longo da linha e distancias a OSM e Wikidata
  dados/derivados/geo/locais.json        cada codigo de local -> tipo, coordenada, status (verificado, deduzido, aproximado, desconhecido)
  fontes/verificacao/validacao_geo.md    relatorio com os criterios da spec 002
"""
import csv
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BRUTOS, DERIV = "dados/brutos", "dados/derivados"
LINHAS = {"1": "verde", "2": "laranja", "4": "amarela", "5": "azul"}
NOME_STM = {"Ligne verte": "verde", "Ligne orange": "laranja", "Ligne jaune": "amarela", "Ligne bleue": "azul"}
# Comprimento oficial: fr.wikipedia "Métro de Montréal", tabela "Lignes du métro de Montréal" (acesso 2026-10-20)
OFICIAL_KM = {"verde": 22.1, "laranja": 30.0, "amarela": 4.25, "azul": 9.7}
# Deducao (nao documentada pela STM): codigo xSyy = plataforma da linha x na estacao de correspondencia
PLATAFORMAS = {"2S46": ("laranja", "LIONEL-GROULX"), "2S60": ("laranja", "BERRI-UQAM"), "4S50": ("amarela", "BERRI-UQAM"),
               "5S32": ("azul", "SNOWDON"), "5S48": ("azul", "JEAN-TALON")}


# Grafias diferentes da mesma estação entre GTFS, OSM, Wikidata e incidentes (conferidas uma a uma em 2026-10-20)
APELIDOS = {"DUPARC": "PARC", "CHAMPSDEMARS": "CHAMPDEMARS", "DELASSOMPTION": "ASSOMPTION", "LASSOMPTION": "ASSOMPTION", "DIBERVILLE": "IBERVILLE",
            "JDRAPEAU": "JEANDRAPEAU", "LONGUEUILUDESHERBROOKE": "LONGUEUILUNIVERSITEDESHERBROOKE"}


def norma(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    s = re.sub(r"^(STATION|STAT\.)\s*", "", s.strip())
    s = s.replace("SAINTE-", "STE-").replace("SAINT-", "ST-").replace("U. DE SHERBROOKE", "UNIVERSITE-DE-SHERBROOKE").replace("–", "-")
    s = re.sub(r"[^A-Z0-9]", "", s)
    return APELIDOS.get(s, s)


def hav(a, b):
    """Distancia em metros entre (lat, lon)."""
    r = 6371008.8
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def comprimento(pts):
    return sum(hav(a, b) for a, b in zip(pts, pts[1:]))


def junta_vias(vias):
    """Encadeia as vias da relacao num unico tracado, invertendo as que vierem ao contrario."""
    linha = list(vias[0])
    restantes = [list(v) for v in vias[1:]]
    while restantes:
        melhor = None
        for i, v in enumerate(restantes):
            for inv in (False, True):
                w = v[::-1] if inv else v
                for fim in ("fim", "inicio"):
                    d = hav(linha[-1], w[0]) if fim == "fim" else hav(w[-1], linha[0])
                    if melhor is None or d < melhor[0]:
                        melhor = (d, i, inv, fim)
        d, i, inv, fim = melhor
        w = restantes.pop(i)
        w = w[::-1] if inv else w
        linha = linha + w[1:] if fim == "fim" else w[:-1] + linha
    return linha


def projeta(pts, p):
    """Projeta p no tracado: (km ao longo, distancia em metros ao tracado). Aproximacao plana local."""
    k = math.cos(math.radians(p[0]))
    melhor, acum = None, 0.0
    for a, b in zip(pts, pts[1:]):
        ax, ay, bx, by, px, py = a[1] * k, a[0], b[1] * k, b[0], p[1] * k, p[0]
        dx, dy = bx - ax, by - ay
        t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        q = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        d = hav(q, p)
        seg = hav(a, b)
        if melhor is None or d < melhor[1]:
            melhor = (acum + t * seg, d)
        acum += seg
    return melhor[0] / 1000, melhor[1]


# ------------------------------------------------------------------ OSM: tracado por linha
osm = json.load(open(f"{BRUTOS}/osm/overpass_metro_mtl.json", encoding="utf-8"))
relacoes = [e for e in osm["elements"] if e["type"] == "relation"]
nos_estacao = [e for e in osm["elements"] if e["type"] == "node"]
seq = defaultdict(list)
with open(f"{DERIV}/gtfs/metro_sequencias.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter=";"):
        if r["direction_id"] == "0":
            seq[LINHAS[r["route_id"]]].append({"ordem": int(r["ordem"]), "estacao": r["estacao"], "lat": float(r["lat"]), "lon": float(r["lon"])})
for l in seq:
    seq[l].sort(key=lambda x: x["ordem"])

tracados, rel_usada = {}, {}
for ref, l in LINHAS.items():
    cand = [r for r in relacoes if r.get("tags", {}).get("ref") == ref]
    rel = sorted(cand, key=lambda r: r["id"])[0]
    vias = [[(g["lat"], g["lon"]) for g in m["geometry"]] for m in rel["members"] if m["type"] == "way" and m.get("geometry")]
    pts = junta_vias(vias)
    inicio = (seq[l][0]["lat"], seq[l][0]["lon"])
    if hav(pts[-1], inicio) < hav(pts[0], inicio):
        pts = pts[::-1]
    tracados[l] = pts
    rel_usada[l] = rel

# ------------------------------------------------------------------ estacoes: km, distancias a OSM e Wikidata
osm_por_nome = defaultdict(list)
for n in nos_estacao:
    osm_por_nome[norma(n.get("tags", {}).get("name", ""))].append((n["lat"], n["lon"]))
wd = json.load(open(f"{BRUTOS}/wikidata/estacoes_metro_mtl.json", encoding="utf-8"))["results"]["bindings"]
wd_por_nome = defaultdict(list)
for b in wd:
    m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", b["coord"]["value"])
    if m:
        wd_por_nome[norma(b["sLabel"]["value"])].append((float(m.group(2)), float(m.group(1))))
linhas_da_estacao = defaultdict(set)
for l, ss in seq.items():
    for s in ss:
        linhas_da_estacao[norma(s["estacao"])].add(l)

feat_est, est_idx = [], {}
for l, ss in seq.items():
    for s in ss:
        p = (s["lat"], s["lon"])
        km, dlin = projeta(tracados[l], p)
        k = norma(s["estacao"])
        d_osm = min((hav(p, q) for q in osm_por_nome.get(k, [])), default=None)
        d_wd = min((hav(p, q) for q in wd_por_nome.get(k, [])), default=None)
        nome = s["estacao"].replace("STATION ", "").title()
        props = {"linha": l, "ordem": s["ordem"], "estacao": nome, "chave": k, "km_linha": round(km, 3),
                 "dist_tracado_m": round(dlin, 1), "dist_osm_m": None if d_osm is None else round(d_osm, 1),
                 "dist_wikidata_m": None if d_wd is None else round(d_wd, 1),
                 "transferencia": len(linhas_da_estacao[k]) > 1, "fonte": "GTFS STM (parent_station)"}
        feat_est.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [s["lon"], s["lat"]]}, "properties": props})
        est_idx[(l, k)] = props | {"lat": s["lat"], "lon": s["lon"]}

# ------------------------------------------------------------------ locais dos incidentes
with open(f"{BRUTOS}/stm/incidents_metro.csv", encoding="utf-8-sig", newline="") as f:
    bruto = list(csv.reader(f, delimiter=";"))
cab = bruto[1]
tec = []
for row in bruto[2:]:
    if len(row) < len(cab) or not row[0].strip():
        continue
    e = dict(zip(cab, (c.strip() for c in row)))
    if e["Cause primaire"] in ("Matériel roulant", "Équipements fixes") and e["Ligne"] in NOME_STM:
        tec.append({"linha": NOME_STM[e["Ligne"]], "local": e["Code de lieu"]})
por_local = defaultdict(list)
for e in tec:
    por_local[e["local"]].append(e["linha"])


def estacao_na_linha(nome, linha):
    k = norma(nome)
    if (linha, k) in est_idx:
        return est_idx[(linha, k)]
    cand = [v for (ll, kk), v in est_idx.items() if ll == linha and (kk.startswith(k) or k.startswith(kk))]
    return cand[0] if len(cand) == 1 else None


def ponto_no_tracado(linha, km):
    pts, acum = tracados[linha], 0.0
    alvo = km * 1000
    for a, b in zip(pts, pts[1:]):
        seg = hav(a, b)
        if acum + seg >= alvo:
            t = 0 if seg == 0 else (alvo - acum) / seg
            return a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
        acum += seg
    return pts[-1]


locais, coerencia = [], {}
for codigo, linhas_ev in sorted(por_local.items(), key=lambda kv: -len(kv[1])):
    linha = Counter(linhas_ev).most_common(1)[0][0]
    item = {"codigo": codigo, "linha": linha, "n_tecnicos": len(linhas_ev), "tipo": "desconhecido", "status": "desconhecido",
            "lat": None, "lon": None, "km_linha": None, "estacoes": [], "metodo": ""}
    if codigo.startswith(("STATION ", "STAT. ")):
        s = estacao_na_linha(codigo, linha)
        if s:
            item.update(tipo="estacao", status="verificado", lat=s["lat"], lon=s["lon"], km_linha=s["km_linha"], estacoes=[s["estacao"]],
                        metodo="nome igual ao do GTFS na mesma linha")
    elif codigo in PLATAFORMAS:
        l_ded, est = PLATAFORMAS[codigo]
        s = estacao_na_linha(est, l_ded)
        coerencia[codigo] = sum(1 for x in linhas_ev if x == l_ded) / len(linhas_ev)
        item.update(tipo="plataforma_correspondencia", status="deduzido", linha=l_ded, lat=s["lat"], lon=s["lon"], km_linha=s["km_linha"],
                    estacoes=[s["estacao"]], metodo="dedução: lacuna na numeração Mxyy do GTFS; não documentado pela STM")
    elif codigo.startswith("INTER."):
        partes = codigo[len("INTER."):].split("/")
        ss = [estacao_na_linha(p, linha) for p in partes]
        if len(ss) == 2 and all(ss):
            km = (ss[0]["km_linha"] + ss[1]["km_linha"]) / 2
            lat, lon = ponto_no_tracado(linha, km)
            item.update(tipo="interestacao", status="verificado", lat=lat, lon=lon, km_linha=round(km, 3),
                        estacoes=[ss[0]["estacao"], ss[1]["estacao"]], metodo="ponto médio no traçado entre as duas estações")
    elif codigo.startswith(("GARAGE ", "ARRIERE-GARE ")):
        nome = codigo.split(" ", 1)[1]
        s = estacao_na_linha(nome, linha)
        if s:
            item.update(tipo="garagem" if codigo.startswith("GARAGE") else "arriere_gare", status="aproximado", lat=s["lat"], lon=s["lon"],
                        km_linha=s["km_linha"], estacoes=[s["estacao"]], metodo="coordenada da estação de mesmo nome; posição real do pátio não verificada")
    if item["status"] == "desconhecido" and codigo.startswith(("POSTE DE REDR", "POSTE DE DISTRICT")):
        item.update(tipo="subestacao", metodo="subestação de energia; a posição não é publicada pela STM")
    elif item["status"] == "desconhecido" and re.fullmatch(r"\d999", codigo):
        item.update(tipo="linha_sem_posicao", metodo="código genérico da linha (x999), sem posição; significado não documentado")
    if item["status"] == "desconhecido" and item["tipo"] == "desconhecido":
        for (ll, kk), s in est_idx.items():
            if ll == linha and len(kk) >= 4 and kk in norma(codigo):
                item.update(tipo="outro", status="aproximado", lat=s["lat"], lon=s["lon"], km_linha=s["km_linha"], estacoes=[s["estacao"]],
                            metodo="nome de estação contido no código")
                break
    locais.append(item)

# ------------------------------------------------------------------ grava
feat_lin = []
comp = {}
for l, pts in tracados.items():
    comp[l] = comprimento(pts) / 1000
    rel = rel_usada[l]
    feat_lin.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[round(lo, 6), round(la, 6)] for la, lo in pts]},
                     "properties": {"linha": l, "ref": rel["tags"].get("ref"), "nome_osm": rel["tags"].get("name"), "cor_osm": rel["tags"].get("colour"),
                                    "comprimento_km": round(comp[l], 3), "comprimento_oficial_km": OFICIAL_KM[l],
                                    "fonte_oficial": "https://fr.wikipedia.org/wiki/M%C3%A9tro_de_Montr%C3%A9al",
                                    "osm_relation": rel["id"], "pontos": len(pts),
                                    "fonte": "OpenStreetMap, © colaboradores do OpenStreetMap, ODbL"}})
# Sem data de geracao nos arquivos: rodar de novo com as mesmas entradas precisa dar arquivos identicos (constituicao, principio III).
meta = {"osm_timestamp": osm["osm3s"]["timestamp_osm_base"], "licenca": "Traçado: ODbL (OpenStreetMap). Estações: GTFS STM, CC BY 4.0."}
gerado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")
json.dump({"type": "FeatureCollection", "metadata": meta, "features": feat_lin}, open(f"{DERIV}/geo/linhas.geojson", "w", encoding="utf-8"), ensure_ascii=False)
json.dump({"type": "FeatureCollection", "metadata": meta, "features": feat_est}, open(f"{DERIV}/geo/estacoes.geojson", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(locais, open(f"{DERIV}/geo/locais.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# ------------------------------------------------------------------ relatorio de validacao
tot = len(tec)
por_status = Counter()
for it in locais:
    por_status[it["status"]] += it["n_tecnicos"]
d_osm = [f["properties"]["dist_osm_m"] for f in feat_est if f["properties"]["dist_osm_m"] is not None]
d_wd = [f["properties"]["dist_wikidata_m"] for f in feat_est if f["properties"]["dist_wikidata_m"] is not None]
sem_osm = sorted({f["properties"]["estacao"] for f in feat_est if f["properties"]["dist_osm_m"] is None})
sem_wd = sorted({f["properties"]["estacao"] for f in feat_est if f["properties"]["dist_wikidata_m"] is None})
d_tr = [f["properties"]["dist_tracado_m"] for f in feat_est]
acima = [(f["properties"]["estacao"], f["properties"]["linha"], f["properties"]["dist_osm_m"], f["properties"]["dist_wikidata_m"])
         for f in feat_est if (f["properties"]["dist_osm_m"] or 0) >= 100]
L = []
L.append("# Validação da base geoespacial (spec 002)\n")
L.append(f"Gerado por `pipeline/geo_base.py` em {gerado_em}. OpenStreetMap consultado em {meta['osm_timestamp']} (Overpass API).\n")
L.append("## Comprimento das linhas\n")
L.append("| Linha | Traçado OSM (km) | Oficial (km) | Diferença | Critério ±3% | Pontos | Relação OSM |")
L.append("|---|---|---|---|---|---|---|")
for l in ("verde", "laranja", "amarela", "azul"):
    dif = comp[l] / OFICIAL_KM[l] - 1
    L.append(f"| {l} | {comp[l]:.2f} | {OFICIAL_KM[l]} | {dif:+.1%} | {'atende' if abs(dif) <= 0.03 else 'NÃO atende'} | {len(tracados[l])} | {rel_usada[l]['id']} |")
L.append("\nComprimento oficial: tabela \"Lignes du métro de Montréal\" em https://fr.wikipedia.org/wiki/M%C3%A9tro_de_Montr%C3%A9al (acesso 2026-10-20). "
         "O `shapes.txt` do GTFS liga as estações em linha reta e fica 2% a 10% abaixo do oficial (pesquisa de 2026-10-20).\n")
L.append("## Estações\n")
L.append(f"- Estações por linha no GTFS (sentido 0): " + ", ".join(f"{l} {len(seq[l])}" for l in ("verde", "laranja", "amarela", "azul")) + ".")
L.append(f"- Distância GTFS → nó de estação do OSM: {len(d_osm)} de {len(feat_est)} casadas pelo nome; máxima {max(d_osm):.0f} m; mediana {sorted(d_osm)[len(d_osm)//2]:.0f} m. Sem par no OSM: {', '.join(sem_osm) or 'nenhuma'}.")
L.append(f"- Distância GTFS → Wikidata (rede Q392377): {len(d_wd)} de {len(feat_est)} casadas; máxima {max(d_wd):.0f} m; mediana {sorted(d_wd)[len(d_wd)//2]:.0f} m. Sem par: {', '.join(sem_wd) or 'nenhuma'}.")
L.append(f"- Distância da estação ao traçado OSM: máxima {max(d_tr):.0f} m; mediana {sorted(d_tr)[len(d_tr)//2]:.0f} m.")
L.append(f"- Critério da spec (todas a menos de 100 m do OSM): {'atende' if not acima else 'NÃO atende: ' + '; '.join(f'{a} ({b}) {c:.0f} m do OSM e {d:.0f} m do Wikidata' for a, b, c, d in acima)}.")
L.append("  As exceções ficam perto do Wikidata; a diferença vem de onde o nó da estação foi posto no OSM (entrada ou edifício). "
         "Ficam registradas como exceção, sem mudar o critério.\n")
L.append("## Códigos de local dos incidentes técnicos\n")
L.append(f"Base: {tot} falhas técnicas de uma única linha. Códigos distintos: {len(locais)}.\n")
L.append("| Status | Falhas | Parcela |")
L.append("|---|---|---|")
for st in ("verificado", "deduzido", "aproximado", "desconhecido"):
    L.append(f"| {st} | {por_status[st]} | {por_status[st] / tot:.1%} |")
L.append(f"\nGeorreferenciadas (qualquer status, exceto desconhecido): {(tot - por_status['desconhecido']) / tot:.1%}. Critério da spec (≥95%): "
         f"{'atende' if (tot - por_status['desconhecido']) / tot >= 0.95 else 'NÃO atende'}.\n")
L.append("### Coerência da dedução dos códigos xSyy\n")
L.append("Parcela dos incidentes de cada código cuja linha registrada é a linha deduzida. Critério: ≥95%.\n")
L.append("| Código | Estação deduzida | Linha deduzida | Incidentes | Coerência | Critério |")
L.append("|---|---|---|---|---|---|")
for c, (l, est) in PLATAFORMAS.items():
    n = len(por_local.get(c, []))
    v = coerencia.get(c)
    L.append(f"| {c} | {est.title()} | {l} | {n} | {'' if v is None else f'{v:.1%}'} | {'' if v is None else ('atende' if v >= 0.95 else 'NÃO atende')} |")
L.append("\n### Códigos sem localização\n")
L.append("| Código | Linha mais frequente | Falhas |")
L.append("|---|---|---|")
for it in sorted((i for i in locais if i["status"] == "desconhecido"), key=lambda i: -i["n_tecnicos"])[:25]:
    L.append(f"| {it['codigo']} | {it['linha']} | {it['n_tecnicos']} |")
open("fontes/verificacao/validacao_geo.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L[:30]))
