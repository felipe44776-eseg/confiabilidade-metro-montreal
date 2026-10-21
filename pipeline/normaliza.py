"""Spec 001: normaliza os incidentes técnicos em eventos com início e fim absolutos.

Uso (da raiz do repositório): .venv/Scripts/python -I pipeline/normaliza.py
Entrada: dados/brutos/stm/incidents_metro.csv
Saídas em dados/derivados/eventos/:
  eventos_tecnicos.csv       falhas técnicas de uma linha (material rodante ou equipamentos fixos)
  eventos_causa_comum.csv    falhas técnicas registradas em mais de uma linha, com a lista de linhas
  eventos_sem_linha.csv      falhas técnicas sem linha ("Non affecté"): registradas, fora das métricas por linha
  excecoes.csv               eventos cuja duração calculada não cabe na faixa oficial nem na vizinha
  resumo_normalizacao.json   contagens usadas nos critérios de aceite
Hora: a STM conta o dia de operação; 24:xx e 25:xx caem no dia civil seguinte. A hora é local de Montreal
(America/Montreal, com horário de verão) e é convertida para UTC com a base tzdata.
"""
import csv
import json
import os
import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

BRUTO = "dados/brutos/stm/incidents_metro.csv"
SAIDA = "dados/derivados/eventos"
FUSO = ZoneInfo("America/Montreal")
LINHAS = {"Ligne verte": "verde", "Ligne orange": "laranja", "Ligne jaune": "amarela", "Ligne bleue": "azul"}
NUM_LINHA = {"1": "verde", "2": "laranja", "4": "amarela", "5": "azul"}
CAUSA = {"Matériel roulant": "MR", "Équipements fixes": "EF"}
# Faixas oficiais de "Incident en minutes", na ordem; a vizinha é a de índice ±1.
FAIXAS = [("02 min et moins", 0, 2), ("03 à 04 min", 3, 4), ("05 à 09 min", 5, 9), ("10 à 14 min", 10, 14),
          ("15 à 19 min", 15, 19), ("20 à 24 min", 20, 24), ("25 à 29 min", 25, 29), ("30 min et plus", 30, 10 ** 6)]
INDICE_FAIXA = {nome: i for i, (nome, _, _) in enumerate(FAIXAS)}
COLUNAS = ["id", "linha", "linhas", "causa", "causa_secundaria", "frota", "sintoma", "tipo", "data_servico",
           "inicio_local", "fim_local", "inicio_utc", "fim_utc", "duracao_min", "faixa_oficial", "na_faixa", "na_faixa_vizinha",
           "veiculo", "local_codigo", "evacuacao"]


def minutos(hhmm):
    h, m = hhmm.strip().split(":")
    return int(h) * 60 + int(m)


def instante_local(data_servico, hhmm):
    """Dia de operação + hora (que pode passar de 24:00) -> datetime civil local, sem fuso."""
    return datetime.combine(data_servico, datetime.min.time()) + timedelta(minutes=minutos(hhmm))


def para_utc(local):
    return local.replace(tzinfo=FUSO).astimezone(timezone.utc)


def duracao(h_ini, h_fim):
    """Retomada sem data: se a hora é menor que a do incidente, passou para o dia seguinte."""
    return (minutos(h_fim) - minutos(h_ini)) % 1440


def faixa_de(minutos_):
    for i, (_, a, b) in enumerate(FAIXAS):
        if a <= minutos_ <= b:
            return i
    return None


def linhas_do_campo(campo):
    return sorted({NUM_LINHA[d] for d in re.findall(r"\d", campo) if d in NUM_LINHA})


def normaliza_registro(e):
    d = date.fromisoformat(e["Jour calendaire"])
    ini = instante_local(d, e["Heure de l'incident"])
    dur = duracao(e["Heure de l'incident"], e["Heure de reprise"])
    fim = ini + timedelta(minutes=dur)
    oficial = INDICE_FAIXA.get(e["Incident en minutes"])
    calculada = faixa_de(dur)
    na_faixa = oficial is not None and calculada == oficial
    vizinha = oficial is not None and calculada is not None and abs(calculada - oficial) <= 1
    frota = e["Cause secondaire"] if e["Cause secondaire"] in ("MR-73", "MPM-10") else ""
    return {
        "id": e["Numero d'incident"], "causa": CAUSA[e["Cause primaire"]], "causa_secundaria": e["Cause secondaire"],
        "frota": frota, "sintoma": e["Symptome"], "tipo": e["Type d'incident"], "data_servico": d.isoformat(),
        "inicio_local": ini.strftime("%Y-%m-%dT%H:%M"), "fim_local": fim.strftime("%Y-%m-%dT%H:%M"),
        "inicio_utc": para_utc(ini).strftime("%Y-%m-%dT%H:%MZ"), "fim_utc": para_utc(fim).strftime("%Y-%m-%dT%H:%MZ"),
        "duracao_min": dur, "faixa_oficial": e["Incident en minutes"], "na_faixa": int(na_faixa), "na_faixa_vizinha": int(vizinha),
        "veiculo": "" if e["Véhicule"] in ("#", "") else e["Véhicule"], "local_codigo": e["Code de lieu"],
        "evacuacao": "" if e["Évacuation"] in ("#", "") else e["Évacuation"],
    }


def carrega(caminho=BRUTO):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    cab = linhas[1]
    return [dict(zip(cab, (c.strip() for c in r))) for r in linhas[2:] if len(r) >= len(cab) and r[0].strip()]


def grava(nome, registros, colunas=COLUNAS):
    with open(os.path.join(SAIDA, nome), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas, delimiter=";", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(registros)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    tecnicos, comum, sem_linha, excecoes = [], [], [], []
    for e in carrega():
        if e["Cause primaire"] not in CAUSA:
            continue
        r = normaliza_registro(e)
        if e["Ligne"] in LINHAS:
            r["linha"], r["linhas"] = LINHAS[e["Ligne"]], LINHAS[e["Ligne"]]
            tecnicos.append(r)
            if not r["na_faixa_vizinha"]:
                excecoes.append(r | {"motivo": "duração calculada fora da faixa oficial e da vizinha"})
        else:
            ls = linhas_do_campo(e["Ligne"])
            r["linha"], r["linhas"] = "", ",".join(ls)
            (comum if len(ls) >= 2 else sem_linha).append(r)
    chave = lambda r: (r["inicio_utc"], r["id"])
    for lista in (tecnicos, comum, sem_linha, excecoes):
        lista.sort(key=chave)
    grava("eventos_tecnicos.csv", tecnicos)
    grava("eventos_causa_comum.csv", comum)
    grava("eventos_sem_linha.csv", sem_linha)
    grava("excecoes.csv", excecoes, COLUNAS + ["motivo"])
    n = len(tecnicos)
    resumo = {
        "tecnicos_uma_linha": n,
        "por_linha": {l: sum(1 for r in tecnicos if r["linha"] == l) for l in ("verde", "laranja", "amarela", "azul")},
        "por_causa": {c: sum(1 for r in tecnicos if r["causa"] == c) for c in ("MR", "EF")},
        "na_faixa": sum(r["na_faixa"] for r in tecnicos),
        "na_faixa_ou_vizinha": sum(r["na_faixa_vizinha"] for r in tecnicos),
        "pct_na_faixa_ou_vizinha": round(sum(r["na_faixa_vizinha"] for r in tecnicos) / n, 4),
        "excecoes": len(excecoes),
        "causa_comum": len(comum),
        "causa_comum_verde_laranja": sum(1 for r in comum if {"verde", "laranja"} <= set(r["linhas"].split(","))),
        "sem_linha": len(sem_linha),
        "inicio_depois_da_meia_noite": sum(1 for r in tecnicos if r["inicio_local"][:10] != r["data_servico"]),
        "duracao_max_min": max(r["duracao_min"] for r in tecnicos),
    }
    with open(os.path.join(SAIDA, "resumo_normalizacao.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=1)
    print(json.dumps(resumo, ensure_ascii=False))


if __name__ == "__main__":
    main()
