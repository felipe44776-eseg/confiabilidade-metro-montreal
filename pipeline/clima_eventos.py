"""Spec 003: painel horário de clima e eventos externos, na hora do dia de operação.

Uso (da raiz do repositório): .venv/Scripts/python -I pipeline/clima_eventos.py
Entradas: dados/brutos/eccc_horario/<estação>/<AAAA-MM>.csv (hora LST = UTC-5 fixo), clima diário (neve no solo),
          dados/brutos/eventos/nhl_MTL_*.json, dados/brutos/eventos/f1_villeneuve.json, feriados, dados/manuais/greves_stm.csv
Saída: dados/derivados/clima/painel_horario.csv  (uma linha por hora UTC de 2019-01-01 a 2026-07-01)
       dados/derivados/clima/eventos_externos.csv  (cada evento com data, faixa, URL da fonte e status)
       dados/derivados/clima/resumo_clima.json
Regras declaradas:
- Precipitação: estação 10761 (McTavish, centro); se faltar, 30165 (aeroporto). A coluna estacao_precip diz qual.
- Temperatura, vento, sensação térmica e condição ("Weather"): estação 51157; temperatura cai para 30165 e 10761 se faltar.
- Condição ausente fica vazia: não vira "sem chuva" (constituição, princípio 6).
- Dia de operação: a hora local de 00:00 a 03:59 pertence ao dia anterior, como hora 24 a 27.
- Jogo do Canadiens em casa: de 1 h antes a 3 h 30 depois do início (hipótese declarada).
"""
import csv
import glob
import io
import json
import os
import zipfile
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Montreal")
LST = timezone(timedelta(hours=-5))
SAIDA = "dados/derivados/clima"
INICIO_UTC = datetime(2019, 1, 1, 5, tzinfo=timezone.utc)
FIM_UTC = datetime(2026, 7, 1, 10, tzinfo=timezone.utc)
CHUVA = ("Rain", "Drizzle", "Showers")
NEVE = ("Snow", "Ice Pellets", "Snow Grains")
CONGELANTE = ("Freezing Rain", "Freezing Drizzle")
NHL_URL = "https://api-web.nhle.com/v1/club-schedule-season/MTL/{temporada}"
F1_URL = "https://api.jolpi.ca/ergast/f1/circuits/villeneuve/races.json?limit=100"


def num(s):
    try:
        return float(str(s).replace(",", "."))
    except (TypeError, ValueError):
        return None


def carrega_estacao(est):
    """{instante UTC: linha} de todos os meses da estação. Lê o zip da Release; sem ele, os CSV mensais baixados."""
    zipado = f"dados/brutos/eccc_horario/eccc_horario_{est}.zip"
    if os.path.exists(zipado):
        z = zipfile.ZipFile(zipado)
        textos = [z.read(n).decode("utf-8-sig") for n in sorted(z.namelist())]
    else:
        textos = [open(a, encoding="utf-8-sig", newline="").read() for a in sorted(glob.glob(f"dados/brutos/eccc_horario/{est}/*.csv"))]
    out = {}
    for texto in textos:
        for r in csv.DictReader(io.StringIO(texto, newline="")):
            t = datetime.strptime(r["Date/Time (LST)"], "%Y-%m-%d %H:%M").replace(tzinfo=LST).astimezone(timezone.utc)
            out[t] = r
    return out


def coluna(r, *prefixos):
    for k in r:
        if any(k.startswith(p) for p in prefixos):
            return r[k]
    return None


def dia_operacao(local):
    """Hora local -> (dia de operação, hora 0..27). 00:00-03:59 contam no dia anterior."""
    if local.hour < 4:
        return (local.date() - timedelta(days=1)), local.hour + 24
    return local.date(), local.hour


def janelas_de(texto):
    out = []
    for j in filter(None, texto.split(";")):
        a, b = j.split("-")
        out.append((int(a[:2]) * 60 + int(a[3:]), int(b[:2]) * 60 + int(b[3:])))
    return out


def main():
    os.makedirs(SAIDA, exist_ok=True)
    prec_c, prec_a, cond = carrega_estacao("10761"), carrega_estacao("30165"), carrega_estacao("51157")
    neve_solo = {}
    for arq in glob.glob("dados/brutos/eccc/eccc_diario_*.csv"):
        for r in csv.DictReader(open(arq, encoding="utf-8-sig")):
            neve_solo[r["Date/Time"]] = num(r["Snow on Grnd (cm)"])
    jogos, eventos = [], []
    for arq in sorted(glob.glob("dados/brutos/eventos/nhl_MTL_*.json")):
        for g in json.load(open(arq, encoding="utf-8"))["games"]:
            if g.get("homeTeam", {}).get("abbrev") == "MTL" and g.get("gameType") in (2, 3):
                ini = datetime.strptime(g["startTimeUTC"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                jogos.append((ini - timedelta(hours=1), ini + timedelta(hours=3, minutes=30)))
                eventos.append(["jogo_canadiens", ini.astimezone(FUSO).date().isoformat(), (ini - timedelta(hours=1)).astimezone(FUSO).strftime("%Y-%m-%dT%H:%M%z"),
                                (ini + timedelta(hours=3, minutes=30)).astimezone(FUSO).strftime("%Y-%m-%dT%H:%M%z"),
                                NHL_URL.format(temporada=os.path.basename(arq)[8:16]), "verificado", "API da NHL (não documentada); janela de 1 h antes a 3 h 30 depois é hipótese"])
    gp = set()
    for corrida in json.load(open("dados/brutos/eventos/f1_villeneuve.json", encoding="utf-8"))["MRData"]["RaceTable"]["Races"]:
        gp.add(corrida["date"])
        if corrida["date"] >= "2019-01-01":
            eventos.append(["gp_f1", corrida["date"], (date.fromisoformat(corrida["date"]) - timedelta(days=2)).isoformat() + "T00:00", corrida["date"] + "T23:59", F1_URL, "não verificado",
                            "Jolpica, base comunitária sucessora da Ergast; fim de semana do GP inteiro marcado"])
    gp_fds = {(date.fromisoformat(d) - timedelta(days=k)).isoformat() for d in gp for k in (0, 1, 2)}
    feriados = set()
    for arq in glob.glob("dados/brutos/nager/nager_CA_*.json"):
        for h in json.load(open(arq, encoding="utf-8")):
            if h.get("global") or "CA-QC" in (h.get("counties") or []):
                feriados.add(h["date"])
    greves = {}
    with open("dados/manuais/greves_stm.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            greves[r["data_servico"]] = janelas_de(r["janelas_com_servico"])
            eventos.append(["greve_stm", r["data_servico"], r["janelas_com_servico"] or "sem serviço", "", r["fonte"],
                            "não verificado" if r["status"] == "imprensa" else r["status"], "faixas com serviço, segundo a imprensa; " + r["observacao"]])

    colunas = ["inicio_utc", "local", "data_servico", "hora_servico", "temp_c", "sensacao_c", "vento_kmh", "precip_mm", "estacao_precip",
               "condicao", "chuva", "neve", "chuva_congelante", "neve_solo_cm", "jogo_canadiens", "gp_f1_fim_de_semana", "feriado", "fracao_servico"]
    linhas, t = [], INICIO_UTC
    while t < FIM_UTC:
        local = t.astimezone(FUSO)
        d, h = dia_operacao(local)
        p, est = None, ""
        for fonte, nome in ((prec_c, "10761"), (prec_a, "30165")):
            v = num(coluna(fonte.get(t, {}), "Precip. Amount"))
            if v is not None:
                p, est = v, nome
                break
        c = cond.get(t, {})
        temp = next((v for v in (num(coluna(x.get(t, {}), "Temp (")) for x in (cond, prec_a, prec_c)) if v is not None), None)
        sens = next((v for v in (num(coluna(c, "Wind Chill")), num(coluna(c, "Hmdx")), temp) if v is not None), None)
        vento = num(coluna(c, "Wind Spd"))
        w = (coluna(c, "Weather") or "").strip()
        tem_cond = bool(w) and w != "NA"
        flag = lambda termos: ("1" if any(x in w for x in termos) else "0") if tem_cond else ""
        chuva = flag(CHUVA) if not any(x in w for x in CONGELANTE) else ("0" if tem_cond else "")
        jan = greves.get(d.isoformat())
        frac = 1.0 if jan is None else sum(max(0, min(h * 60 + 60, b) - max(h * 60, a)) for a, b in jan) / 60
        linhas.append([t.strftime("%Y-%m-%dT%H:%MZ"), local.strftime("%Y-%m-%dT%H:%M%z"), d.isoformat(), h,
                       "" if temp is None else temp, "" if sens is None else sens, "" if vento is None else vento,
                       "" if p is None else p, est, w if tem_cond else "", chuva, flag(NEVE), flag(CONGELANTE),
                       "" if neve_solo.get(d.isoformat()) is None else neve_solo[d.isoformat()],
                       int(any(a <= t < b for a, b in jogos)), int(d.isoformat() in gp_fds), int(d.isoformat() in feriados), round(frac, 4)])
        t += timedelta(hours=1)
    with open(f"{SAIDA}/painel_horario.csv", "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter=";", lineterminator="\n")
        wr.writerow(colunas)
        wr.writerows(linhas)

    with open(f"{SAIDA}/eventos_externos.csv", "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter=";", lineterminator="\n")
        wr.writerow(["tipo", "data_servico", "inicio_local", "fim_local", "fonte_url", "status", "observacao"])
        wr.writerows(sorted(e for e in eventos if "2019-01-01" <= e[1] <= "2026-06-30"))

    servico = [r for r in linhas if 5 <= r[3] <= 24]
    resumo = {
        "horas": len(linhas),
        "horas_de_operacao": len(servico),
        "pct_horas_operacao_com_precip": round(sum(1 for r in servico if r[7] != "") / len(servico), 4),
        "pct_precip_estacao_10761": round(sum(1 for r in servico if r[8] == "10761") / len(servico), 4),
        "pct_horas_operacao_com_condicao": round(sum(1 for r in servico if r[9] != "") / len(servico), 4),
        "pct_horas_operacao_com_temperatura": round(sum(1 for r in servico if r[4] != "") / len(servico), 4),
        "horas_chuva_congelante": sum(1 for r in linhas if r[12] == "1"),
        "chuva_congelante_2023_04_05": [r[1][11:16] for r in linhas if r[1].startswith("2023-04-05") and r[12] == "1"],
        "jogos_canadiens_em_casa": len(jogos),
        "gp_f1": sorted(gp),
        "dias_de_greve": len(greves),
        "meses_baixados": {e: len(glob.glob(f"dados/brutos/eccc_horario/{e}/*.csv")) for e in ("10761", "30165", "51157")},
    }
    with open(f"{SAIDA}/resumo_clima.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=1)
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
