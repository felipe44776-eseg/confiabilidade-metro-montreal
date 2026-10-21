"""Analise de confiabilidade e tolerancia a falhas do metro de Montreal (STM).

Gera os conjuntos de dados do painel em dados/derivados/painel/*.json (um arquivo por tabela).
Uso (da raiz do projeto): python -I pipeline/analise_confiabilidade.py

Definicoes:
- Falha tecnica: causa primaria "Matériel roulant" (material rodante) ou "Équipements fixes"
  (equipamentos fixos), em incidentes de uma unica linha. Incidentes em mais de uma linha
  entram como causa comum.
- Tempo de operacao: janela de 20 h por dia de servico (05:00 a 01:00), inferida do horario
  dos incidentes (p1 = 04:18, p99,5 = 25:18). Hora 24:xx e 25:xx = depois da meia-noite.
- Duracao: hora de retomada menos hora do incidente (tempo ate o servico voltar).
"""
import csv
import json
import math
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BRUTOS = "dados/brutos"
DERIV = "dados/derivados"
SAIDA = f"{DERIV}/painel"
LINHAS = {"Ligne verte": "verde", "Ligne orange": "laranja", "Ligne jaune": "amarela", "Ligne bleue": "azul"}
NUM_LINHA = {"1": "verde", "2": "laranja", "4": "amarela", "5": "azul"}
ORDEM = ["verde", "laranja", "amarela", "azul"]
NOME = {"verde": "Verde (1)", "laranja": "Laranja (2)", "amarela": "Amarela (4)", "azul": "Azul (5)", "rede": "Rede"}
INICIO, FIM = date(2019, 1, 1), date(2026, 6, 30)
FIM_KM = date(2023, 9, 30)
JAN_INI, JAN_MIN = 300, 1200  # janela de operacao: comeca 05:00, dura 1200 min
DIAS = (FIM - INICIO).days + 1
DIAS_KM = (FIM_KM - INICIO).days + 1
TEC = {"Matériel roulant": "MR", "Équipements fixes": "EF"}
random.seed(20261020)


def minutos(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def op_min(dia, m):
    """Minutos de operacao acumulados desde INICIO ate o instante (dia de servico, minuto)."""
    return (dia - INICIO).days * JAN_MIN + min(max(m - JAN_INI, 0), JAN_MIN)


def num(s):
    try:
        return float((s or "").strip().replace(",", "."))
    except ValueError:
        return None


def r(x, n=3):
    return None if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))) else round(x, n)


def salva(nome, linhas):
    with open(f"{SAIDA}/{nome}.json", "w", encoding="utf-8") as f:
        json.dump(linhas, f, ensure_ascii=False, separators=(",", ":"))
    print(f"  {nome}.json: {len(linhas)} linhas")


# ---------------------------------------------------------------- leitura dos incidentes
with open(f"{BRUTOS}/stm/incidents_metro.csv", encoding="utf-8-sig", newline="") as f:
    bruto = list(csv.reader(f, delimiter=";"))
cab = bruto[1]
eventos, multi, sem_linha = [], [], []
for row in bruto[2:]:
    if len(row) < len(cab) or not row[0].strip():
        continue
    e = dict(zip(cab, (c.strip() for c in row)))
    dia = date.fromisoformat(e["Jour calendaire"])
    m0, m1 = minutos(e["Heure de l'incident"]), minutos(e["Heure de reprise"])
    ev = {
        "dia": dia, "min": m0, "op": op_min(dia, m0), "dur": (m1 - m0) % 1440,
        "causa": TEC.get(e["Cause primaire"]), "causa_txt": e["Cause primaire"],
        "frota": e["Cause secondaire"] if e["Cause secondaire"] in ("MR-73", "MPM-10") else None,
        "local": e["Code de lieu"], "veiculo": e["Véhicule"] if e["Véhicule"] not in ("#", "") else None,
        "evac": e["Évacuation"] not in ("#", ""), "linha_txt": e["Ligne"], "faixa": e["Incident en minutes"],
    }
    if e["Ligne"] in LINHAS:
        ev["linha"] = LINHAS[e["Ligne"]]
        eventos.append(ev)
    else:
        ev["linhas"] = sorted({NUM_LINHA[x] for x in re.findall(r"\d", e["Ligne"]) if x in NUM_LINHA})
        if len(ev["linhas"]) >= 2:
            multi.append(ev)
        else:
            sem_linha.append(ev)

tec = [e for e in eventos if e["causa"]]
por_linha = {l: sorted((e for e in tec if e["linha"] == l), key=lambda e: e["op"]) for l in ORDEM}
print(f"eventos de uma linha: {len(eventos)} | tecnicos: {len(tec)} | multilinha: {len(multi)}")

# ---------------------------------------------------------------- exposicao (km real por composicao)
km_dia_linha = defaultdict(float)
km_ano_frota = defaultdict(float)
km_mes = defaultdict(float)
km_linha = defaultdict(float)
comp_dia = defaultdict(set)
with open(f"{BRUTOS}/stm/km_reel.csv", encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        l = LINHAS.get(row["Ligne"])
        km = num(row["Km voiture"])
        if not l or km is None:
            continue
        dia = row["Jour calendaire"]
        km_dia_linha[(dia, l)] += km
        km_linha[l] += km
        frota = {"73": "MR-73", "10": "MPM-10"}.get(row["Type matériel"])
        if frota:
            km_ano_frota[(dia[:4], frota)] += km
        km_mes[(dia[:7], l)] += km
        comp_dia[(dia, l)].add(row["Composition du train"])

# ---------------------------------------------------------------- clima e mobilidade
clima = {}
for ano in range(2019, 2027):
    for row in csv.DictReader(open(f"{BRUTOS}/eccc/eccc_diario_{ano}.csv", encoding="utf-8-sig")):
        clima[row["Date/Time"]] = {"tmax": num(row["Max Temp (°C)"]), "tmed": num(row["Mean Temp (°C)"]),
                                   "neve": num(row["Total Snow (cm)"]), "neve_solo": num(row["Snow on Grnd (cm)"]),
                                   "precip": num(row["Total Precip (mm)"])}
mob = {row["date"]: num(row["transit_stations_percent_change_from_baseline"])
       for row in csv.DictReader(open(f"{DERIV}/mobilidade/google_mobilidade_montreal_2020_2022.csv", encoding="utf-8"))}


# ---------------------------------------------------------------- ajuste de distribuicoes
def ajusta(x):
    x = [max(v, 1 / 60) for v in x]
    n = len(x)
    lx = [math.log(v) for v in x]
    mlx = statistics.fmean(lx)
    # Exponencial
    lam = 1 / statistics.fmean(x)
    ll_exp = n * math.log(lam) - lam * sum(x)
    # Weibull por maxima verossimilhanca (bissecao na equacao de perfil de beta)
    def g(b):
        xb = [v ** b for v in x]
        return sum(a * l for a, l in zip(xb, lx)) / sum(xb) - 1 / b - mlx
    lo, hi = 0.05, 10.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if g(mid) < 0 else (lo, mid)
    beta = (lo + hi) / 2
    eta = (sum(v ** beta for v in x) / n) ** (1 / beta)
    ll_wei = n * math.log(beta) - n * beta * math.log(eta) + (beta - 1) * sum(lx) - sum((v / eta) ** beta for v in x)
    # Lognormal
    mu, sig = mlx, statistics.pstdev(lx)
    ll_log = -sum(lx) - n * math.log(sig * math.sqrt(2 * math.pi)) - sum((l - mu) ** 2 for l in lx) / (2 * sig * sig)
    F = {
        "exponencial": lambda t: 1 - math.exp(-lam * t),
        "weibull": lambda t: 1 - math.exp(-((t / eta) ** beta)),
        "lognormal": lambda t: 0.5 * (1 + math.erf((math.log(t) - mu) / (sig * math.sqrt(2)))),
    }
    xs = sorted(x)
    ks = {}
    for nome, cdf in F.items():
        dmax = 0.0
        for i, v in enumerate(xs):
            fv = cdf(v)
            dmax = max(dmax, abs(fv - i / n), abs(fv - (i + 1) / n))
        ks[nome] = dmax
    res = {
        "exponencial": {"p1": lam, "p2": None, "ll": ll_exp, "k": 1},
        "weibull": {"p1": beta, "p2": eta, "ll": ll_wei, "k": 2},
        "lognormal": {"p1": mu, "p2": sig, "ll": ll_log, "k": 2},
    }
    for nome, v in res.items():
        v["aic"] = 2 * v["k"] - 2 * v["ll"]
        v["ks"] = ks[nome]
        v["F"] = F[nome]
    return res, xs


def quantil(v, p):
    v = sorted(v)
    return v[int(p * (len(v) - 1))] if v else None


# ---------------------------------------------------------------- por linha
linhas_out, ajustes_out, curvas_out, hist_out = [], [], [], []
tbf_op = {}
GRADE = [10 ** (math.log10(0.05) + i * (math.log10(400) - math.log10(0.05)) / 44) for i in range(45)]
BORDAS = [0] + [10 ** (math.log10(0.1) + i * (math.log10(500) - math.log10(0.1)) / 18) for i in range(19)]
falhas_dia = defaultdict(lambda: Counter())
for e in tec:
    falhas_dia[e["linha"]][e["dia"]] += 1
trens_dia_util = {}
lam_trem = {}
for l in ORDEM:
    ev = por_linha[l]
    ops = [e["op"] for e in ev]
    tbf = [(b - a) / 60 for a, b in zip(ops, ops[1:])]
    tbf_op[l] = tbf
    durs = [e["dur"] for e in ev]
    n_mr = sum(1 for e in ev if e["causa"] == "MR")
    n_ef = len(ev) - n_mr
    horas_op = DIAS * JAN_MIN / 60
    downtime = sum(durs)
    res, xs = ajusta(tbf)
    melhor = min(res, key=lambda k: res[k]["aic"])
    emp = lambda t: sum(1 for v in xs if v > t) / len(xs)
    wR = lambda t: 1 - res["weibull"]["F"](t)
    # Exposicao e frota (2019-01 a 2023-09)
    mr_km = sum(1 for e in ev if e["causa"] == "MR" and e["dia"] <= FIM_KM)
    dias_uteis = [d for (d, ll), s in comp_dia.items() if ll == l and date.fromisoformat(d).weekday() < 5]
    trens = sorted(len(comp_dia[(d, l)]) for d in dias_uteis)
    trens_dia_util[l] = statistics.median(trens)
    trem_dias = sum(len(s) for (d, ll), s in comp_dia.items() if ll == l)
    lam_trem[l] = mr_km / trem_dias
    dias_sem = sum(1 for i in range(DIAS) if falhas_dia[l][INICIO + timedelta(days=i)] == 0)
    mttr_h = statistics.fmean(durs) / 60
    lam_h = len(ev) / horas_op
    linhas_out.append({
        "linha": l, "nome": NOME[l], "falhas": len(ev), "falhas_mr": n_mr, "falhas_ef": n_ef,
        "falhas_por_dia": r(len(ev) / DIAS), "mtbf_op_h": r(horas_op / len(ev), 2),
        "mtbf_mr_op_h": r(horas_op / n_mr, 2), "mtbf_ef_op_h": r(horas_op / n_ef, 2),
        "mtbf_cal_h": r(DIAS * 24 / len(ev), 2), "mediana_tbf_op_h": r(statistics.median(tbf), 2),
        "cv_tbf": r(statistics.pstdev(tbf) / statistics.fmean(tbf), 2),
        "mttr_min": r(statistics.fmean(durs), 2), "mediana_ttr_min": statistics.median(durs),
        "p90_ttr_min": quantil(durs, 0.9), "pct_sem_interrupcao": r(sum(1 for d in durs if d == 0) / len(durs), 4),
        "min_fora_ano": r(downtime / (DIAS / 365.25), 1),
        "disponibilidade": r(1 - downtime / (DIAS * JAN_MIN), 6),
        "lambda_h": r(lam_h, 5), "mu_h": r(1 / mttr_h, 3), "a_markov": r((1 / mttr_h) / (lam_h + 1 / mttr_h), 6),
        "p_dia_sem_falha": r(dias_sem / DIAS, 4),
        "km_carro_milhoes": r(km_linha[l] / 1e6, 2), "km_por_falha_mr": r(km_linha[l] / mr_km, 0),
        "falhas_mr_por_mkm": r(mr_km / (km_linha[l] / 1e6), 3),
        "weibull_beta": r(res["weibull"]["p1"], 3), "weibull_eta_h": r(res["weibull"]["p2"], 2),
        "melhor_modelo": melhor,
        "r_1h": r(wR(1), 4), "r_4h": r(wR(4), 4), "r_8h": r(wR(8), 4), "r_20h": r(wR(20), 4),
        "r_emp_1h": r(emp(1), 4), "r_emp_8h": r(emp(8), 4), "r_emp_20h": r(emp(20), 4),
        "evacuacoes": sum(1 for e in ev if e["evac"]),
        "trens_dia_util": trens_dia_util[l], "lambda_trem_dia": r(lam_trem[l], 5),
    })
    for nome in ("exponencial", "weibull", "lognormal"):
        v = res[nome]
        ajustes_out.append({"linha": l, "modelo": nome, "p1": r(v["p1"], 4), "p2": r(v["p2"], 4),
                            "loglik": r(v["ll"], 1), "aic": r(v["aic"], 1), "ks": r(v["ks"], 4),
                            "delta_aic": None, "melhor": nome == melhor})
    aic_min = res[melhor]["aic"]
    for a in ajustes_out:
        if a["linha"] == l:
            a["delta_aic"] = r(res[a["modelo"]]["aic"] - aic_min, 1)
    for t in GRADE:
        curvas_out.append({"linha": l, "t_h": r(t, 4), "empirica": r(emp(t), 4),
                           **{nome: r(1 - res[nome]["F"](t), 4) for nome in ("exponencial", "weibull", "lognormal")}})
    for a, b in zip(BORDAS, BORDAS[1:]):
        n = sum(1 for v in tbf if a <= v < b)
        hist_out.append({"linha": l, "de_h": r(a, 3), "ate_h": r(b, 3), "n": n, "pct": r(n / len(tbf), 4)})

FAIXA_OFICIAL = {"02 min et moins": (0, 2), "03 à 04 min": (3, 4), "05 à 09 min": (5, 9), "10 à 14 min": (10, 14),
                 "15 à 19 min": (15, 19), "20 à 24 min": (20, 24), "25 à 29 min": (25, 29), "30 min et plus": (30, 10 ** 6)}


def faixa_ok(e):
    a, b = FAIXA_OFICIAL.get(e["faixa"], (None, None))
    return a is not None and a <= e["dur"] <= b


# Rede: qualquer falha tecnica em qualquer linha (sistema em serie de 4 linhas)
todos = sorted(tec, key=lambda e: e["op"])
tbf_rede = [(b["op"] - a["op"]) / 60 for a, b in zip(todos, todos[1:])]
dur_rede = [e["dur"] for e in todos]
horas_op = DIAS * JAN_MIN / 60
dias_sem_rede = sum(1 for i in range(DIAS) if all(falhas_dia[l][INICIO + timedelta(days=i)] == 0 for l in ORDEM))
km_total = sum(km_linha.values())
mr_km_rede = sum(1 for e in todos if e["causa"] == "MR" and e["dia"] <= FIM_KM)
linhas_out.append({
    "linha": "rede", "nome": NOME["rede"], "falhas": len(todos),
    "falhas_mr": sum(1 for e in todos if e["causa"] == "MR"), "falhas_ef": sum(1 for e in todos if e["causa"] == "EF"),
    "falhas_por_dia": r(len(todos) / DIAS), "mtbf_op_h": r(horas_op / len(todos), 2),
    "mtbf_mr_op_h": r(horas_op / sum(1 for e in todos if e["causa"] == "MR"), 2),
    "mtbf_ef_op_h": r(horas_op / sum(1 for e in todos if e["causa"] == "EF"), 2),
    "mtbf_cal_h": r(DIAS * 24 / len(todos), 2), "mediana_tbf_op_h": r(statistics.median(tbf_rede), 2),
    "cv_tbf": r(statistics.pstdev(tbf_rede) / statistics.fmean(tbf_rede), 2),
    "mttr_min": r(statistics.fmean(dur_rede), 2), "mediana_ttr_min": statistics.median(dur_rede),
    "p90_ttr_min": quantil(dur_rede, 0.9), "pct_sem_interrupcao": r(sum(1 for d in dur_rede if d == 0) / len(dur_rede), 4),
    "min_fora_ano": r(sum(dur_rede) / (DIAS / 365.25), 1),
    "disponibilidade": r(1 - sum(dur_rede) / (DIAS * JAN_MIN * 4), 6),
    "lambda_h": r(len(todos) / horas_op, 5), "mu_h": r(60 / statistics.fmean(dur_rede), 3), "a_markov": None,
    "p_dia_sem_falha": r(dias_sem_rede / DIAS, 4),
    "km_carro_milhoes": r(km_total / 1e6, 2), "km_por_falha_mr": r(km_total / mr_km_rede, 0),
    "falhas_mr_por_mkm": r(mr_km_rede / (km_total / 1e6), 3),
    "weibull_beta": None, "weibull_eta_h": None, "melhor_modelo": None,
    "r_1h": None, "r_4h": None, "r_8h": None, "r_20h": None,
    "r_emp_1h": None, "r_emp_8h": None, "r_emp_20h": None,
    "evacuacoes": sum(1 for e in todos if e["evac"]),
    "trens_dia_util": sum(trens_dia_util.values()), "lambda_trem_dia": None,
    "tecnicos_sem_linha": sum(1 for e in sem_linha if e["causa"]),
    "tecnicos_multilinha": sum(1 for e in multi if e["causa"]),
    "concordancia_faixa": r(sum(1 for e in todos if faixa_ok(e)) / len(todos), 4),
})

# ---------------------------------------------------------------- serie anual por linha
anual_out = []
for ano in range(2019, 2027):
    ini = date(ano, 1, 1)
    fim = min(date(ano, 12, 31), FIM)
    nd = (fim - ini).days + 1
    for l in ORDEM + ["rede"]:
        ev = [e for e in tec if e["dia"].year == ano and (l == "rede" or e["linha"] == l)]
        km = sum(v for (d, ll), v in km_dia_linha.items() if d[:4] == str(ano) and (l == "rede" or ll == l))
        mr = sum(1 for e in ev if e["causa"] == "MR")
        mr_k = sum(1 for e in ev if e["causa"] == "MR" and e["dia"] <= FIM_KM)
        lin = [l] if l != "rede" else ORDEM
        sem = sum(1 for i in range(nd) if all(falhas_dia[x][ini + timedelta(days=i)] == 0 for x in lin))
        anual_out.append({
            "ano": ano, "linha": l, "parcial": ano == 2026, "dias": nd, "falhas_mr": mr, "falhas_ef": len(ev) - mr,
            "falhas": len(ev), "min_fora": sum(e["dur"] for e in ev),
            "mtbf_op_h": r(nd * JAN_MIN / 60 * (4 if l == "rede" else 1) / len(ev), 2) if ev else None,
            "p_dia_sem_falha": r(sem / nd, 4),
            "km_carro_milhoes": r(km / 1e6, 3) if km else None,
            "falhas_mr_por_mkm": r(mr_k / (km / 1e6), 3) if km else None,
        })

# ---------------------------------------------------------------- frota por ano
frota_out = []
for ano in range(2019, 2024):
    for frota in ("MR-73", "MPM-10"):
        n = sum(1 for e in tec if e["frota"] == frota and e["dia"].year == ano and e["dia"] <= FIM_KM)
        km = km_ano_frota[(str(ano), frota)]
        frota_out.append({"ano": ano, "frota": frota, "parcial": ano == 2023, "falhas": n,
                          "km_carro_milhoes": r(km / 1e6, 3), "km_por_falha": r(km / n, 0) if n else None,
                          "falhas_por_mkm": r(n / (km / 1e6), 3) if km else None})
for frota in ("MR-73", "MPM-10"):
    n = sum(1 for e in tec if e["frota"] == frota and e["dia"] <= FIM_KM)
    km = sum(v for (a, f), v in km_ano_frota.items() if f == frota)
    frota_out.append({"ano": "2019–2023", "frota": frota, "parcial": True, "falhas": n,
                      "km_carro_milhoes": r(km / 1e6, 3), "km_por_falha": r(km / n, 0), "falhas_por_mkm": r(n / (km / 1e6), 3)})

# ---------------------------------------------------------------- tempo de restabelecimento por faixa
FAIXAS = [("0 min", 0, 0), ("1 min", 1, 1), ("2 min", 2, 2), ("3–4 min", 3, 4), ("5–9 min", 5, 9),
          ("10–14 min", 10, 14), ("15–29 min", 15, 29), ("30 min ou mais", 30, 10 ** 6)]
ttr_out = []
for l in ORDEM + ["rede"]:
    for c in ("MR", "EF"):
        ds = [e["dur"] for e in tec if e["causa"] == c and (l == "rede" or e["linha"] == l)]
        for i, (rot, a, b) in enumerate(FAIXAS):
            n = sum(1 for d in ds if a <= d <= b)
            ttr_out.append({"linha": l, "causa": c, "ordem": i, "faixa": rot, "n": n, "pct": r(n / len(ds), 4)})

# ---------------------------------------------------------------- perfis (hora, mes, dia da semana, temperatura, neve)
perfil_out = []
for h in range(2, 26):
    ev = [e for e in tec if e["min"] // 60 == h]
    perfil_out.append({"dimensao": "hora", "ordem": h, "categoria": f"{h % 24:02d}h",
                       "falhas_mr": sum(1 for e in ev if e["causa"] == "MR"), "falhas_ef": sum(1 for e in ev if e["causa"] == "EF"),
                       "km_carro_milhoes": None, "falhas_mr_por_mkm": None})
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
DSEM = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def taxa_por(filtro_dia, rotulo, dimensao, ordem):
    dias = [d for d in (INICIO + timedelta(days=i) for i in range(DIAS_KM)) if filtro_dia(d)]
    ds = {d.isoformat() for d in dias}
    km = sum(v for (d, l), v in km_dia_linha.items() if d in ds)
    ev = [e for e in tec if e["dia"].isoformat() in ds]
    mr = sum(1 for e in ev if e["causa"] == "MR")
    perfil_out.append({"dimensao": dimensao, "ordem": ordem, "categoria": rotulo, "falhas_mr": mr,
                       "falhas_ef": len(ev) - mr, "km_carro_milhoes": r(km / 1e6, 2),
                       "falhas_mr_por_mkm": r(mr / (km / 1e6), 3) if km else None, "dias": len(dias)})


for i, m in enumerate(MESES):
    taxa_por(lambda d, i=i: d.month == i + 1, m, "mes", i)
for i, s in enumerate(DSEM):
    taxa_por(lambda d, i=i: d.weekday() == i, s, "dia_semana", i)
TEMPS = [("abaixo de −10 °C", -99, -10), ("−10 a 0 °C", -10, 0), ("0 a 10 °C", 0, 10), ("10 a 20 °C", 10, 20),
         ("20 a 25 °C", 20, 25), ("25 °C ou mais", 25, 99)]
for i, (rot, a, b) in enumerate(TEMPS):
    taxa_por(lambda d, a=a, b=b: (clima.get(d.isoformat(), {}).get("tmax") is not None and a <= clima[d.isoformat()]["tmax"] < b),
             rot, "temperatura", i)
NEVE = [("inverno, sem neve no solo", -1, 0.5), ("1 a 10 cm", 0.5, 10.5), ("mais de 10 cm", 10.5, 999)]
for i, (rot, a, b) in enumerate(NEVE):
    taxa_por(lambda d, a=a, b=b: (clima.get(d.isoformat(), {}).get("neve_solo") is not None and a < clima[d.isoformat()]["neve_solo"] <= b),
             rot, "neve_solo", i)

# ---------------------------------------------------------------- correlacoes diarias (rede)
dias_ok = [INICIO + timedelta(days=i) for i in range(DIAS)]
clientela = Counter(e["dia"] for e in eventos if e["causa_txt"] == "Clientèle")
serie = []
for d in dias_ok:
    ds = d.isoformat()
    c = clima.get(ds, {})
    serie.append({
        "d": d, "km": sum(km_dia_linha.get((ds, l), 0) for l in ORDEM) if d <= FIM_KM else None,
        "tmed": c.get("tmed"), "neve": c.get("neve"), "neve_solo": c.get("neve_solo"), "precip": c.get("precip"),
        "mob": mob.get(ds), "clientela": clientela[d],
    })
mr_dia = Counter(e["dia"] for e in tec if e["causa"] == "MR")
ef_dia = Counter(e["dia"] for e in tec if e["causa"] == "EF")
for s in serie:
    s["falhas_mr"], s["falhas_ef"] = mr_dia[s["d"]], ef_dia[s["d"]]


def pearson(a, b):
    pares = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    n = len(pares)
    mx, my = statistics.fmean(p[0] for p in pares), statistics.fmean(p[1] for p in pares)
    sxy = sum((x - mx) * (y - my) for x, y in pares)
    sx = math.sqrt(sum((x - mx) ** 2 for x, _ in pares))
    sy = math.sqrt(sum((y - my) ** 2 for _, y in pares))
    return (sxy / (sx * sy) if sx and sy else None), n


VARS = [("km", "Km-carro real no dia"), ("tmed", "Temperatura média"), ("neve", "Neve no dia (cm)"),
        ("neve_solo", "Neve no solo (cm)"), ("precip", "Precipitação total (mm)"),
        ("mob", "Mobilidade em estações (Google, %)"), ("clientela", "Incidentes causados por passageiros")]
corr_out = []
for alvo, rot_alvo in (("falhas_mr", "Falhas de material rodante"), ("falhas_ef", "Falhas de equipamentos fixos")):
    for v, rot in VARS:
        rr, n = pearson([s[alvo] for s in serie], [s[v] for s in serie])
        corr_out.append({"alvo": alvo, "alvo_nome": rot_alvo, "variavel": v, "variavel_nome": rot, "r": r(rr, 3), "n": n})

# ---------------------------------------------------------------- locais (equipamentos fixos) e veiculos (Pareto)
locais = defaultdict(list)
for e in tec:
    locais[e["local"]].append(e)
locais_out = []
for loc, ev in sorted(locais.items(), key=lambda kv: -len(kv[1]))[:20]:
    linha_mais = Counter(e["linha"] for e in ev).most_common(1)[0][0]
    locais_out.append({"local": loc, "linha": linha_mais, "falhas": len(ev),
                       "falhas_mr": sum(1 for e in ev if e["causa"] == "MR"), "falhas_ef": sum(1 for e in ev if e["causa"] == "EF"),
                       "min_fora": sum(e["dur"] for e in ev), "mttr_min": r(statistics.fmean(e["dur"] for e in ev), 2)})

pareto_out = []
for frota in ("MR-73", "MPM-10"):
    cont = Counter(e["veiculo"] for e in tec if e["frota"] == frota and e["veiculo"])
    v = sorted(cont.values(), reverse=True)
    tot, acum = sum(v), 0
    pontos = {0: 0.0}
    for i, x in enumerate(v, 1):
        acum += x
        pontos[i] = acum / tot
    for p in range(0, 101, 2):
        k = round(p / 100 * len(v))
        pareto_out.append({"frota": frota, "pct_veiculos": p / 100, "pct_falhas": r(pontos[k], 4),
                           "veiculos": len(v), "falhas": tot})

# ---------------------------------------------------------------- causa comum (incidentes em mais de uma linha)
tec_multi = [e for e in multi if e["causa"]]
cc_out = []
for a, b in (("verde", "laranja"), ("laranja", "azul"), ("verde", "amarela"), ("laranja", "amarela")):
    cc_t = [e for e in tec_multi if a in e["linhas"] and b in e["linhas"]]
    cc_all = [e for e in multi if a in e["linhas"] and b in e["linhas"]]
    na, nb = len(por_linha[a]), len(por_linha[b])
    cc_out.append({"par": f"{a}-{b}", "par_nome": f"{NOME[a]} e {NOME[b]}", "eventos_tecnicos": len(cc_t),
                   "eventos_todas_causas": len(cc_all), "beta_a": r(len(cc_t) / (len(cc_t) + na), 4),
                   "beta_b": r(len(cc_t) / (len(cc_t) + nb), 4),
                   "duracao_media_min": r(statistics.fmean(e["dur"] for e in cc_t), 1) if cc_t else None,
                   "min_fora_ano": r(sum(e["dur"] for e in cc_t) / (DIAS / 365.25), 1)})

# ---------------------------------------------------------------- corredor redundante: analitico + Monte Carlo
T = DIAS * JAN_MIN
Q = {l: sum(e["dur"] for e in por_linha[l]) / T for l in ORDEM}
cc12 = sorted((e for e in tec_multi if "verde" in e["linhas"] and "laranja" in e["linhas"]), key=lambda e: e["op"])
cc25 = [e for e in tec_multi if "laranja" in e["linhas"] and "azul" in e["linhas"]]
Qcc12 = sum(e["dur"] for e in cc12) / T
Qcc25 = sum(e["dur"] for e in cc25) / T
MIN_ANO = 365.25 * JAN_MIN

# Monte Carlo: semanas de 140 h de operacao, tempo entre falhas e duracao reamostrados da propria base
SEMANA = 7 * JAN_MIN  # minutos
amostra_tbf = {l: [t * 60 for t in tbf_op[l]] for l in ("verde", "laranja")}
amostra_dur = {l: [e["dur"] for e in por_linha[l]] for l in ("verde", "laranja")}
cc_ops = [e["op"] for e in cc12]
amostra_tbf_cc = [b - a for a, b in zip(cc_ops, cc_ops[1:])] or [T]
amostra_dur_cc = [e["dur"] for e in cc12]


def processo(tbfs, durs):
    # Inicio estacionario: sorteia um intervalo com peso pelo comprimento e cai num ponto uniforme dele,
    # para a semana simulada nao comecar logo depois de uma falha.
    t = random.choices(tbfs, weights=tbfs)[0] * random.random()
    paradas = []
    while t < SEMANA:
        d = random.choice(durs)
        paradas.append((t, min(t + d, SEMANA)))
        t += max(random.choice(tbfs), d)
    return paradas


def uniao(*listas):
    ints = sorted(i for ls in listas for i in ls if i[1] > i[0])
    out = []
    for a, b in ints:
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def intersec(x, y):
    out, i, j = [], 0, 0
    while i < len(x) and j < len(y):
        a, b = max(x[i][0], y[j][0]), min(x[i][1], y[j][1])
        if a < b:
            out.append((a, b))
        if x[i][1] < y[j][1]:
            i += 1
        else:
            j += 1
    return out


def total(ints):
    return sum(b - a for a, b in ints)


RODADAS = 4000
cen = {"so_laranja": [], "so_verde": [], "paralelo_indep": [], "paralelo_cc": []}
amostra = None
for k in range(RODADAS):
    v = processo(amostra_tbf["verde"], amostra_dur["verde"])
    o = processo(amostra_tbf["laranja"], amostra_dur["laranja"])
    cc = processo(amostra_tbf_cc, amostra_dur_cc)
    cen["so_laranja"].append(total(uniao(o, cc)))
    cen["so_verde"].append(total(uniao(v, cc)))
    ambos = intersec(uniao(v), uniao(o))
    cen["paralelo_indep"].append(total(ambos))
    cen["paralelo_cc"].append(total(uniao(ambos, cc)))
    if amostra is None and cc:
        amostra = (v, o, cc, uniao(ambos, cc))
if amostra is None:
    amostra = (v, o, cc, uniao(ambos, cc))

CEN_NOME = {"so_laranja": "Só a Laranja (sem redundância)", "so_verde": "Só a Verde (sem redundância)",
            "paralelo_indep": "Verde e Laranja em paralelo, falhas independentes",
            "paralelo_cc": "Verde e Laranja em paralelo, com causa comum"}
ANALITICO = {"so_laranja": Q["laranja"] + Qcc12, "so_verde": Q["verde"] + Qcc12,
             "paralelo_indep": Q["verde"] * Q["laranja"], "paralelo_cc": Q["verde"] * Q["laranja"] + Qcc12}
corredor_out = []
for i, (c, vals) in enumerate(cen.items()):
    corredor_out.append({
        "cenario": c, "ordem": i, "nome": CEN_NOME[c],
        "indisp_analitica": r(ANALITICO[c], 8), "min_ano_analitico": r(ANALITICO[c] * MIN_ANO, 2),
        "disp_analitica": r(1 - ANALITICO[c], 8),
        "sim_min_semana_media": r(statistics.fmean(vals), 3), "sim_min_ano": r(statistics.fmean(vals) * 365.25 / 7, 2),
        "sim_p95_min_semana": r(quantil(vals, 0.95), 2), "sim_p_semana_sem_parada": r(sum(1 for x in vals if x == 0) / len(vals), 4),
        "rodadas": RODADAS,
    })
corredor_out.append({"cenario": "serie_laranja_azul", "ordem": 4, "nome": "Laranja e Azul em série (viagem que usa as duas)",
                     "indisp_analitica": r(Q["laranja"] + Q["azul"] + Qcc25, 8),
                     "min_ano_analitico": r((Q["laranja"] + Q["azul"] + Qcc25) * MIN_ANO, 2),
                     "disp_analitica": r(1 - (Q["laranja"] + Q["azul"] + Qcc25), 8),
                     "sim_min_semana_media": None, "sim_min_ano": None, "sim_p95_min_semana": None,
                     "sim_p_semana_sem_parada": None, "rodadas": None})

BIN = [0, 1, 5, 10, 20, 30, 45, 60, 90, 120, 180, 10 ** 6]
ROT_BIN = ["0", "1–4", "5–9", "10–19", "20–29", "30–44", "45–59", "60–89", "90–119", "120–179", "180+"]
simhist_out = []
for c, vals in cen.items():
    for i, (a, b) in enumerate(zip(BIN, BIN[1:])):
        n = sum(1 for x in vals if (x == 0 if a == 0 else a <= x < b)) if a == 0 else sum(1 for x in vals if a <= x < b and x > 0)
        simhist_out.append({"cenario": c, "nome": CEN_NOME[c], "ordem": i, "faixa_min": ROT_BIN[i], "n": n, "pct": r(n / RODADAS, 4)})
amostra_out = []
for faixa, ints in zip(("verde", "laranja", "causa_comum", "corredor"), amostra):
    for a, b in ints:
        amostra_out.append({"faixa": faixa, "inicio_h": r(a / 60, 3), "fim_h": r(b / 60, 3), "dur_min": r(b - a, 1)})

# ---------------------------------------------------------------- redundancia de frota k-de-n (Markov nascimento e morte)
kdn_out = []
for l in ORDEM:
    n = int(trens_dia_util[l])
    lam = lam_trem[l]
    for reparo in (0.5, 1, 2, 4):
        mu = 1 / reparo
        for s in range(0, 9):
            N = n + s
            p = [1.0]
            for j in range(1, N + 1):
                taxa_falha = lam * min(n, N - (j - 1))
                p.append(p[-1] * taxa_falha / (j * mu))
            z = sum(p)
            p = [x / z for x in p]
            kdn_out.append({"linha": l, "trens_necessarios": n, "reservas": s, "reparo_dias": reparo,
                            "lambda_trem_dia": r(lam, 5), "disponibilidade": r(sum(p[: s + 1]), 6),
                            "trens_parados_medio": r(sum(j * x for j, x in enumerate(p)), 3)})

# ---------------------------------------------------------------- estacoes (topologia GTFS) com falhas por estacao
def norma(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    s = re.sub(r"^(STATION|STAT\.)\s*", "", s.strip())
    s = s.replace("SAINT-", "ST-").replace("U. DE SHERBROOKE", "UNIVERSITE-DE-SHERBROOKE").replace(" ", "")
    return s.replace("-", "")


falhas_loc = Counter()
falhas_loc_mr = Counter()
for e in tec:
    if e["local"].startswith(("STATION", "STAT.")):
        k = norma(e["local"])
        falhas_loc[k] += 1
        if e["causa"] == "MR":
            falhas_loc_mr[k] += 1
estacoes_out = []
vistas = defaultdict(set)
ROTA = {"1": "verde", "2": "laranja", "4": "amarela", "5": "azul"}
with open(f"{DERIV}/gtfs/metro_sequencias.csv", encoding="utf-8") as f:
    seqs = [x for x in csv.DictReader(f, delimiter=";") if x["direction_id"] == "0"]
for x in seqs:
    vistas[norma(x["estacao"])].add(ROTA[x["route_id"]])
casadas = 0
for x in seqs:
    k = norma(x["estacao"])
    casadas += falhas_loc[k] > 0
    estacoes_out.append({"linha": ROTA[x["route_id"]], "ordem": int(x["ordem"]), "estacao": x["estacao"].replace("STATION ", "").title(),
                         "lat": float(x["lat"]), "lon": float(x["lon"]), "falhas": falhas_loc[k], "falhas_mr": falhas_loc_mr[k],
                         "transferencia": len(vistas[k]) > 1})

# ---------------------------------------------------------------- grava
import os
os.makedirs(SAIDA, exist_ok=True)
print("gravando:")
salva("linhas", linhas_out)
salva("ajustes", ajustes_out)
salva("tbf_curvas", curvas_out)
salva("tbf_hist", hist_out)
salva("anual", anual_out)
salva("frota_anual", frota_out)
salva("ttr_faixas", ttr_out)
salva("perfil", perfil_out)
salva("correlacoes", corr_out)
salva("locais", locais_out)
salva("pareto", pareto_out)
salva("causa_comum", cc_out)
salva("corredor", corredor_out)
salva("sim_hist", simhist_out)
salva("sim_amostra", amostra_out)
salva("kdn", kdn_out)
salva("estacoes", estacoes_out)
print(f"estacoes com falhas casadas: {casadas} de {len(seqs)} | eventos de causa comum Verde-Laranja: {len(cc12)}")
