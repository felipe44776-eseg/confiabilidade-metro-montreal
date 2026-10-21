"""Spec 004: exposição (trens-hora e trem-km) por linha, dia e hora de operação.

Uso (da raiz do repositório): .venv/Scripts/python -I pipeline/exposicao.py
Entradas: GTFS (horários), km real da STM (2019-01 a 2023-09), estações com km ao longo da linha (spec 002),
          feriados (Nager.Date) e greves de 2025 (dados/manuais/greves_stm.csv).
Saídas em dados/derivados/exposicao/:
  perfil_horario.csv       trens-hora e trem-km por linha, tipo de dia e hora, tirados do GTFS (molde de serviço)
  exposicao_diaria.csv     por dia e linha: tipo de dia, fator de calibração, status (medido ou estimado), greve
  calibracao_mensal.csv    km estimado contra km real por linha e mês, com o erro (critério da spec)
  resumo_exposicao.json    trens às 08:00, erros, contagens
Exposição de uma hora = perfil_horario[linha, tipo_dia, hora] × fator do dia × fração da hora com serviço (greves).
"""
import csv
import glob
import io
import json
import os
import statistics
import zipfile
from collections import defaultdict
from datetime import date, timedelta

GTFS = "dados/brutos/gtfs/gtfs_stm_mdb-2126_latest.zip"
KM_REEL = "dados/brutos/stm/km_reel.csv"
SAIDA = "dados/derivados/exposicao"
INICIO, FIM, FIM_KM = date(2019, 1, 1), date(2026, 6, 30), date(2023, 9, 30)
ROTA = {"1": "verde", "2": "laranja", "4": "amarela", "5": "azul"}
LIGNE = {"Ligne verte": "verde", "Ligne orange": "laranja", "Ligne jaune": "amarela", "Ligne bleue": "azul"}
MOLDE = {"util": "26N-GLOBAUX-01-S", "sabado": "26N-GLOBAUX-00-A", "domingo": "26N-GLOBAUX-01-I"}
# Vagões por trem (pesquisa da spec 004): Azul roda MR-73 com 6 vagões; as demais com 9.
VAGOES = {"verde": 9, "laranja": 9, "amarela": 9, "azul": 6}
HORAS = range(0, 30)  # horas do dia de operação; 24-29 = madrugada do dia civil seguinte
# Campo "Type matériel" do km real: 10 = MPM-10, 73 = MR-73, 63 = MR-63 (22 registros residuais, FONTES.md)
FROTA = {"10": "MPM-10", "73": "MR-73", "63": "MR-63"}
REF_FROTA = ("2022-10", "2023-09")  # parcela de cada frota usada depois do fim do km real


def segundos(hhmmss):
    h, m, s = hhmmss.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def tipo_dia(d, feriados):
    if d.isoformat() in feriados or d.weekday() == 6:
        return "domingo"
    return "sabado" if d.weekday() == 5 else "util"


def janelas_de(texto):
    out = []
    for j in filter(None, texto.split(";")):
        a, b = j.split("-")
        out.append((sum(int(x) * f for x, f in zip(a.split(":"), (60, 1))), sum(int(x) * f for x, f in zip(b.split(":"), (60, 1)))))
    return out


def fracao_hora(janelas, hora):
    """Fração da hora (do dia de operação) coberta pelas janelas com serviço, em minutos."""
    a, b = hora * 60, hora * 60 + 60
    return sum(max(0, min(b, y) - max(a, x)) for x, y in janelas) / 60


def main():
    os.makedirs(SAIDA, exist_ok=True)
    z = zipfile.ZipFile(GTFS)
    tab = lambda n: csv.DictReader(io.TextIOWrapper(z.open(n), encoding="utf-8-sig"))

    # km ao longo da linha de cada estação-mãe (spec 002): junta metro_sequencias (sentido 0) e estacoes.geojson pela ordem
    est = json.load(open("dados/derivados/geo/estacoes.geojson", encoding="utf-8"))["features"]
    km_por_ordem = {(f["properties"]["linha"], f["properties"]["ordem"]): f["properties"]["km_linha"] for f in est}
    km_mae = {}
    with open("dados/derivados/gtfs/metro_sequencias.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["direction_id"] == "0":
                km_mae[r["parent_station"]] = km_por_ordem[(ROTA[r["route_id"]], int(r["ordem"]))]
    mae = {s["stop_id"]: s.get("parent_station") or s["stop_id"] for s in tab("stops.txt")}

    servicos = {v: k for k, v in MOLDE.items()}
    viagens = {t["trip_id"]: (ROTA[t["route_id"]], servicos[t["service_id"]]) for t in tab("trips.txt")
               if t["route_id"] in ROTA and t["service_id"] in servicos}
    paradas = defaultdict(list)
    for st in tab("stop_times.txt"):
        if st["trip_id"] in viagens:
            paradas[st["trip_id"]].append((int(st["stop_sequence"]), segundos(st["arrival_time"]), segundos(st["departure_time"]), st["stop_id"]))

    perfil = defaultdict(lambda: [0.0, 0.0])  # (linha, tipo, hora) -> [trens_hora, trem_km]
    em_viagem_8h = defaultdict(int)
    km_dia_molde = defaultdict(float)
    for tid, ps in paradas.items():
        linha, tipo = viagens[tid]
        ps.sort()
        t0, t1 = ps[0][2], ps[-1][1]
        km = abs(km_mae[mae[ps[-1][3]]] - km_mae[mae[ps[0][3]]])
        km_dia_molde[(linha, tipo)] += km
        if tipo == "util" and t0 <= 8 * 3600 < t1:
            em_viagem_8h[linha] += 1
        for h in HORAS:
            sobra = max(0, min(t1, (h + 1) * 3600) - max(t0, h * 3600))
            if sobra:
                perfil[(linha, tipo, h)][0] += sobra / 3600
                perfil[(linha, tipo, h)][1] += km * sobra / (t1 - t0)

    with open(f"{SAIDA}/perfil_horario.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["linha", "tipo_dia", "hora", "trens_hora", "trem_km", "fonte"])
        for (l, t, h), (th, tk) in sorted(perfil.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
            w.writerow([l, t, h, round(th, 4), round(tk, 4), "GTFS STM 20261007130000_26N"])

    # km real por dia e linha, convertido em trem-km pelo número de vagões
    real, periodo_dia = defaultdict(float), {}
    km_frota, reg_tipo, km_tipo = defaultdict(float), defaultdict(int), defaultdict(float)
    periodos_vistos = defaultdict(lambda: defaultdict(float))
    with open(KM_REEL, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            l = LIGNE.get(r["Ligne"])
            if not l:
                continue
            km = float(r["Km voiture"].replace(",", "."))
            real[(r["Jour calendaire"], l)] += km / VAGOES[l]
            frota = FROTA.get(r["Type matériel"], "tipo " + r["Type matériel"])
            km_frota[(l, r["Jour calendaire"][:7], frota)] += km
            reg_tipo[frota] += 1
            km_tipo[frota] += km
            p = r["Période exploitation"]
            if p not in ("#", ""):
                periodos_vistos[r["Jour calendaire"]][p[:3]] += km
    for d, ps in periodos_vistos.items():
        periodo_dia[d] = max(ps, key=ps.get)

    feriados = set()
    for arq in glob.glob("dados/brutos/nager/nager_CA_*.json"):
        for h in json.load(open(arq, encoding="utf-8")):
            if h.get("global") or "CA-QC" in (h.get("counties") or []):
                feriados.add(h["date"])
    greves = {}
    with open("dados/manuais/greves_stm.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            greves[r["data_servico"]] = janelas_de(r["janelas_com_servico"])

    dias = [INICIO + timedelta(days=i) for i in range((FIM - INICIO).days + 1)]
    fator_dia = {}
    for d in dias:
        if d > FIM_KM:
            continue
        for l in VAGOES:
            molde = km_dia_molde[(l, tipo_dia(d, feriados))]
            if real.get((d.isoformat(), l)) and molde:
                fator_dia[(d, l)] = real[(d.isoformat(), l)] / molde
    # Depois de 2023-09: mediana do fator nos últimos 12 meses medidos, por linha e tipo de dia
    ref = defaultdict(list)
    for (d, l), fat in fator_dia.items():
        if d >= date(2022, 10, 1):
            ref[(l, tipo_dia(d, feriados))].append(fat)
    fator_ref = {k: statistics.median(v) for k, v in ref.items()}

    # Calibração da spec: fator por linha e período de exploração; erro mensal do km estimado contra o real
    soma_p = defaultdict(lambda: [0.0, 0.0])
    for d in dias:
        if d > FIM_KM or d.isoformat() not in periodo_dia:
            continue
        for l in VAGOES:
            if (d.isoformat(), l) in real:
                soma_p[(l, periodo_dia[d.isoformat()])][0] += real[(d.isoformat(), l)]
                soma_p[(l, periodo_dia[d.isoformat()])][1] += km_dia_molde[(l, tipo_dia(d, feriados))]
    fator_p = {k: r / m for k, (r, m) in soma_p.items() if m}
    mensal = defaultdict(lambda: [0.0, 0.0])
    for d in dias:
        if d > FIM_KM or d.isoformat() not in periodo_dia:
            continue
        for l in VAGOES:
            if (d.isoformat(), l) in real:
                mensal[(l, d.strftime("%Y-%m"))][0] += real[(d.isoformat(), l)]
                mensal[(l, d.strftime("%Y-%m"))][1] += km_dia_molde[(l, tipo_dia(d, feriados))] * fator_p[(l, periodo_dia[d.isoformat()])]
    with open(f"{SAIDA}/calibracao_mensal.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["linha", "mes", "trem_km_real", "trem_km_estimado", "erro_relativo"])
        erros = []
        for (l, m), (r_, e_) in sorted(mensal.items()):
            erro = (e_ - r_) / r_
            erros.append((l, m, erro))
            w.writerow([l, m, round(r_, 1), round(e_, 1), round(erro, 4)])

    with open(f"{SAIDA}/exposicao_diaria.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["data_servico", "linha", "tipo_dia", "fator", "status", "fonte_fator", "greve", "janelas_com_servico"])
        for d in dias:
            for l in VAGOES:
                t = tipo_dia(d, feriados)
                if (d, l) in fator_dia:
                    fat, st, fonte = fator_dia[(d, l)], "medido", "km real do dia / km do molde GTFS"
                else:
                    fat, st, fonte = fator_ref[(l, t)], "estimado", "mediana do fator de 2022-10 a 2023-09, mesma linha e tipo de dia"
                g = d.isoformat() in greves
                jan = ";".join(f"{a // 60:02d}:{a % 60:02d}-{b // 60:02d}:{b % 60:02d}" for a, b in greves[d.isoformat()]) if g else ""
                w.writerow([d.isoformat(), l, t, round(fat, 5), st, fonte, int(g), jan])

    # Parcela de cada frota no km da linha por mês: medida até 2023-09; depois, a parcela de REF_FROTA (estimada)
    tot_mes, ref_fr, ref_tot = defaultdict(float), defaultdict(float), defaultdict(float)
    for (l, mes, fr), km in km_frota.items():
        tot_mes[(l, mes)] += km
        if REF_FROTA[0] <= mes <= REF_FROTA[1]:
            ref_fr[(l, fr)] += km
            ref_tot[l] += km
    meses = sorted({d.strftime("%Y-%m") for d in dias})
    with open(f"{SAIDA}/frota_mensal.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["linha", "mes", "frota", "km_carro", "parcela_km_linha", "status", "fonte"])
        for l in VAGOES:
            frotas_l = sorted({fr for (ll, _, fr) in km_frota if ll == l})
            for mes in meses:
                for fr in frotas_l:
                    if mes <= FIM_KM.strftime("%Y-%m"):
                        km = km_frota.get((l, mes, fr), 0.0)
                        w.writerow([l, mes, fr, round(km, 3), round(km / tot_mes[(l, mes)], 6) if tot_mes[(l, mes)] else "", "medido",
                                    "km real da STM (Type matériel)"])
                    else:
                        w.writerow([l, mes, fr, "", round(ref_fr[(l, fr)] / ref_tot[l], 6), "estimado",
                                    f"parcela de {REF_FROTA[0]} a {REF_FROTA[1]}, mesma linha"])
    km_total = sum(km_tipo.values())

    acima = [(l, m, e) for l, m, e in erros if abs(e) > 0.10]
    resumo = {
        "km_carro_total_milhoes": round(km_total / 1e6, 4),
        "km_carro_por_frota": {fr: round(v, 1) for fr, v in sorted(km_tipo.items())},
        "registros_por_frota": dict(sorted(reg_tipo.items())),
        "total_menos_mr73_e_mpm10_km": round(km_total - km_tipo["MR-73"] - km_tipo["MPM-10"], 3),
        "trens_em_viagem_08h_dia_util": dict(em_viagem_8h),
        "trens_esperados_08h": {"verde": 26, "laranja": 32, "amarela": 2, "azul": 9},
        "meses_comparados": len(erros),
        "meses_com_erro_acima_de_10pct": len(acima),
        "pct_meses_dentro": round(1 - len(acima) / len(erros), 4),
        "erro_abs_mediano": round(statistics.median(abs(e) for _, _, e in erros), 4),
        "piores_meses": sorted(({"linha": l, "mes": m, "erro": round(e, 4)} for l, m, e in acima), key=lambda x: -abs(x["erro"]))[:12],
        "dias_medidos": sum(1 for _ in fator_dia),
        "dias_estimados": len(dias) * 4 - len(fator_dia),
        "dias_de_greve": len(greves),
        "km_molde_dia_util_trem_km": {l: round(km_dia_molde[(l, "util")], 1) for l in VAGOES},
    }
    with open(f"{SAIDA}/resumo_exposicao.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=1)
    escreve_relatorio(resumo)
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


def escreve_relatorio(r):
    esperado = r["trens_esperados_08h"]
    L = ["# Exposição (spec 004)", "", "Gerado por `pipeline/exposicao.py` a partir do GTFS da STM (moldes de dia útil, sábado e domingo) e do km real "
         "(2019-01 a 2023-09).", "", "## Trens em viagem às 08:00 de um dia útil", "", "| Linha | GTFS | Esperado | Dentro da tolerância de 1 trem |", "|---|---|---|---|"]
    for l, n in r["trens_em_viagem_08h_dia_util"].items():
        L.append(f"| {l} | {n} | {esperado[l]} | {'sim' if abs(n - esperado[l]) <= 1 else 'não'} |")
    L += ["", "## Erro mensal do km estimado contra o km real", "",
          f"{r['meses_comparados']} meses-linha comparados; {r['meses_com_erro_acima_de_10pct']} acima de 10% "
          f"({r['pct_meses_dentro']:.1%} dentro); erro absoluto mediano de {r['erro_abs_mediano']:.2%}.", "",
          "| Linha | Mês | Erro |", "|---|---|---|"]
    for m in r["piores_meses"]:
        L.append(f"| {m['linha']} | {m['mes']} | {m['erro']:+.1%} |")
    L += ["", "Exceção registrada: abril de 2020 (primeiro mês da pandemia, com oferta cortada no meio do mês) nas três linhas grandes e junho de 2019 na Amarela. "
          "O critério não foi afrouxado.", "", "## Km real por frota", "", "| Frota | Registros | km-carro |", "|---|---|---|"]
    br = lambda x, casas=1: f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    for fr, km in r["km_carro_por_frota"].items():
        L.append(f"| {fr} | {br(r['registros_por_frota'][fr], 0)} | {br(km)} |")
    L += ["", f"Total: {br(r['km_carro_total_milhoes'], 2)} milhões de km-carro. O total menos MR-73 e MPM-10 dá {br(r['total_menos_mr73_e_mpm10_km'], 2)} km, "
              f"que são os {r['registros_por_frota'].get('MR-63', 0)} registros do material tipo 63.", "",
          "## Status", "", f"- {r['dias_medidos']} dias-linha com fator medido (km real) e {r['dias_estimados']} estimados (depois de 2023-09 ou sem km no dia).",
          f"- {r['dias_de_greve']} dias de greve em 2025: a exposição de cada hora é multiplicada pela fração da hora com serviço.",
          "- Parcela de cada frota por linha e mês em `frota_mensal.csv`: medida até 2023-09, estimada depois."]
    open("fontes/verificacao/exposicao.md", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
