"""Monta o painel diario por linha do metro de Montreal, cruzando falhas com exposicao, calendario, clima e mobilidade.

Uso (da raiz do projeto): python -I pipeline/monta_painel.py
Saida: dados/derivados/painel_diario_linha.csv
"""
import csv
import glob
import json
import sys
from collections import defaultdict
from datetime import date, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

D = "dados/brutos"
DERIV = "dados/derivados"
LINHAS = {"Ligne verte": "verde", "Ligne orange": "laranja", "Ligne jaune": "amarela", "Ligne bleue": "azul"}
INICIO, FIM = date(2019, 1, 1), date(2026, 6, 30)
DIAS_SEMANA = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]


def num(s):
    s = (s or "").strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def minutos(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


painel = defaultdict(lambda: defaultdict(float))

# Falhas: so causas tecnicas; incidentes em mais de uma linha ficam fora do painel por linha.
with open(f"{D}/stm/incidents_metro.csv", encoding="utf-8-sig", newline="") as f:
    linhas = list(csv.reader(f, delimiter=";"))
cab = linhas[1]
for r in linhas[2:]:
    if len(r) < len(cab) or not r[0].strip():
        continue
    r = dict(zip(cab, (c.strip() for c in r)))
    linha = LINHAS.get(r["Ligne"])
    if not linha:
        continue
    chave = (r["Jour calendaire"], linha)
    p = painel[chave]
    p["incidentes_total"] += 1
    dur = (minutos(r["Heure de reprise"]) - minutos(r["Heure de l'incident"])) % 1440
    causa = r["Cause primaire"]
    if causa == "Matériel roulant":
        p["falhas_material_rodante"] += 1
        p["min_fora_material_rodante"] += dur
        if r["Cause secondaire"] == "MR-73":
            p["falhas_mr73"] += 1
        elif r["Cause secondaire"] == "MPM-10":
            p["falhas_mpm10"] += 1
    elif causa == "Équipements fixes":
        p["falhas_equip_fixos"] += 1
        p["min_fora_equip_fixos"] += dur
    elif causa == "Clientèle":
        p["incidentes_clientela"] += 1

# Exposicao real: km-carro por dia e linha (2019-01 a 2023-09), separado por frota.
with open(f"{D}/stm/km_reel.csv", encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        linha = LINHAS.get(r["Ligne"])
        km = num(r["Km voiture"])
        if not linha or km is None:
            continue
        p = painel[(r["Jour calendaire"], linha)]
        p["km_carro_real"] += km
        if r["Type matériel"] == "73":
            p["km_carro_mr73"] += km
        elif r["Type matériel"] == "10":
            p["km_carro_mpm10"] += km

# Exposicao planejada e calendario operacional da propria STM.
tipo_dia = {}
with open(f"{D}/stm/km_planifie.csv", encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        linha = LINHAS.get(r["Ligne"])
        km = num(r["KM planifié"])
        if not linha or km is None:
            continue
        painel[(r["Jour calendaire"], linha)]["km_planejado"] += km
        if r["Type de Jour"] not in ("Non affecté", "#"):
            tipo_dia.setdefault(r["Jour calendaire"], r["Type de Jour"])

feriados = {}
for arq in glob.glob(f"{D}/nager/nager_CA_*.json"):
    for h in json.load(open(arq, encoding="utf-8")):
        if h.get("global") or "CA-QC" in (h.get("counties") or []):
            feriados[h["date"]] = h["localName"]

clima = {}
CLIMA = {"Max Temp (°C)": "temp_max", "Min Temp (°C)": "temp_min", "Mean Temp (°C)": "temp_media",
         "Total Rain (mm)": "chuva_mm", "Total Snow (cm)": "neve_cm", "Total Precip (mm)": "precip_mm",
         "Snow on Grnd (cm)": "neve_solo_cm", "Spd of Max Gust (km/h)": "rajada_kmh"}
for arq in glob.glob(f"{D}/eccc/eccc_diario_*.csv"):
    for r in csv.DictReader(open(arq, encoding="utf-8-sig")):
        clima[r["Date/Time"]] = {v: num(r[k]) for k, v in CLIMA.items()}

mobilidade = {}
for r in csv.DictReader(open(f"{DERIV}/mobilidade/google_mobilidade_montreal_2020_2022.csv", encoding="utf-8")):
    mobilidade[r["date"]] = num(r["transit_stations_percent_change_from_baseline"])

CONTAGENS = ["incidentes_total", "incidentes_clientela", "falhas_material_rodante", "falhas_mr73", "falhas_mpm10",
             "falhas_equip_fixos", "min_fora_material_rodante", "min_fora_equip_fixos"]
EXPOSICAO = ["km_carro_real", "km_carro_mr73", "km_carro_mpm10", "km_planejado"]
colunas = ["data", "linha", "dia_semana", "tipo_dia_stm", "feriado"] + CONTAGENS + EXPOSICAO + list(CLIMA.values()) + ["google_transito_pct"]

fim_km_real = date(2023, 9, 30)
n = 0
with open(f"{DERIV}/painel_diario_linha.csv", "w", encoding="utf-8", newline="") as fo:
    w = csv.writer(fo, delimiter=";")
    w.writerow(colunas)
    d = INICIO
    while d <= FIM:
        ds = d.isoformat()
        for linha in LINHAS.values():
            p = painel.get((ds, linha), {})
            lin = [ds, linha, DIAS_SEMANA[d.weekday()], tipo_dia.get(ds, ""), feriados.get(ds, "")]
            lin += [int(p.get(c, 0)) for c in CONTAGENS]
            for c in EXPOSICAO:
                v = p.get(c)
                if v is None and c.startswith("km_carro") and d <= fim_km_real:
                    v = 0.0
                lin.append("" if v is None else round(v, 1))
            lin += ["" if clima.get(ds, {}).get(c) is None else clima[ds][c] for c in CLIMA.values()]
            lin.append("" if mobilidade.get(ds) is None else mobilidade[ds])
            w.writerow(lin)
            n += 1
        d += timedelta(days=1)
print(f"painel: {n} linhas (dia x linha), {len(colunas)} colunas -> {DERIV}/painel_diario_linha.csv")
