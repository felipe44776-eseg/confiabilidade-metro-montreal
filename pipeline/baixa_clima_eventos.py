"""Spec 003: baixa clima horário (ECCC) e eventos externos (jogos do Canadiens, GP de F1).

Uso (da raiz do repositório): python -I pipeline/baixa_clima_eventos.py
Saídas em dados/brutos/:
  eccc_horario/<estação>/<AAAA-MM>.csv   clima horário do ECCC, hora em LST (UTC-5 fixo)
  eventos/nhl_MTL_<temporada>.json       calendário do Canadiens (API pública não documentada da NHL)
  eventos/f1_villeneuve.json             GPs no circuito Gilles-Villeneuve (Jolpica, sucessora da Ergast)
Arquivos já baixados e válidos não são baixados de novo. Python puro, com teto de tempo e novas tentativas.
"""
import json
import os
import sys
import time
import urllib.request
import zipfile

ESTACOES = {"10761": "MCTAVISH", "30165": "MONTREAL/PIERRE ELLIOTT TRUDEAU INTL", "51157": "MONTREAL INTL A"}
ECCC = ("https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={est}&Year={ano}&Month={mes}"
        "&Day=1&timeframe=1&submit=Download+Data")
NHL = "https://api-web.nhle.com/v1/club-schedule-season/MTL/{temporada}"
F1 = "https://api.jolpi.ca/ergast/f1/circuits/villeneuve/races.json?limit=100"
# Identificação pelo repositório público, sem e-mail de integrante (dado pessoal fora dos arquivos versionados).
UA = {"User-Agent": "ESEG-SistemasTolerantesFalha/1.0 (projeto academico; https://github.com/felipe44776-eseg/confiabilidade-metro-montreal)"}
MESES = [(a, m) for a in range(2019, 2027) for m in range(1, 13) if (a, m) <= (2026, 6)]


def baixa(url, destino, valido, tentativas=4):
    for n in range(tentativas):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                corpo = r.read()
            if valido(corpo):
                tmp = destino + ".parcial"
                with open(tmp, "wb") as f:
                    f.write(corpo)
                os.replace(tmp, destino)
                return True
        except Exception as ex:  # URLError, IncompleteRead, timeout: tenta de novo
            print(f"   tentativa {n + 1}: {ex}", flush=True)
        time.sleep(5 * (n + 1))
    return False


def csv_eccc_valido(corpo):
    return corpo.lstrip(b"\xef\xbb\xbf").startswith(b'"Longitude')


def ja_valido(destino, valido):
    return os.path.exists(destino) and valido(open(destino, "rb").read())


def main():
    falhas = []
    for est in ESTACOES:
        pasta = f"dados/brutos/eccc_horario/{est}"
        if os.path.exists(f"dados/brutos/eccc_horario/eccc_horario_{est}.zip") and not os.path.isdir(pasta):
            print(f"zip da Release presente para {est}: não baixa o ECCC de novo", flush=True)
            continue
        os.makedirs(pasta, exist_ok=True)
        for ano, mes in MESES:
            destino = f"{pasta}/{ano}-{mes:02d}.csv"
            if ja_valido(destino, csv_eccc_valido):
                continue
            ok = baixa(ECCC.format(est=est, ano=ano, mes=mes), destino, csv_eccc_valido)
            print(f"{'ok   ' if ok else 'FALHA'} {est} {ano}-{mes:02d}", flush=True)
            if not ok:
                falhas.append(destino)
            time.sleep(0.5)
    os.makedirs("dados/brutos/eventos", exist_ok=True)
    for ano in range(2018, 2026):
        temporada = f"{ano}{ano + 1}"
        destino = f"dados/brutos/eventos/nhl_MTL_{temporada}.json"
        if not ja_valido(destino, lambda c: b'"games"' in c):
            ok = baixa(NHL.format(temporada=temporada), destino, lambda c: b'"games"' in c)
            print(f"{'ok   ' if ok else 'FALHA'} NHL {temporada}", flush=True)
            if not ok:
                falhas.append(destino)
    destino = "dados/brutos/eventos/f1_villeneuve.json"
    if not ja_valido(destino, lambda c: b'"Races"' in c):
        ok = baixa(F1, destino, lambda c: b'"Races"' in c)
        print(f"{'ok   ' if ok else 'FALHA'} F1", flush=True)
        if not ok:
            falhas.append(destino)
    if not falhas:
        for est in ESTACOES:
            if os.path.isdir(f"dados/brutos/eccc_horario/{est}") and len(os.listdir(f"dados/brutos/eccc_horario/{est}")) == len(MESES):
                empacota(est)
    print(f"concluido; falhas: {len(falhas)} {falhas[:5]}")
    sys.exit(1 if falhas else 0)


def empacota(est):
    """Junta os CSV mensais da estação num zip determinístico (data fixa, ordem fixa): é o arquivo da Release."""
    pasta = f"dados/brutos/eccc_horario/{est}"
    destino = f"dados/brutos/eccc_horario/eccc_horario_{est}.zip"
    with zipfile.ZipFile(destino + ".parcial", "w") as z:
        for nome in sorted(os.listdir(pasta)):
            info = zipfile.ZipInfo(f"{est}/{nome}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, open(f"{pasta}/{nome}", "rb").read(), compresslevel=9)
    os.replace(destino + ".parcial", destino)
    print(f"zip   {destino}", flush=True)


if __name__ == "__main__":
    main()
