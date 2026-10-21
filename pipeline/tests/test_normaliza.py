"""Critérios de aceite da spec 001 (normalização dos incidentes)."""
import csv
import hashlib
import json
import subprocess
import sys
from datetime import date

import pytest

import normaliza as nz


def test_hora_depois_da_meia_noite_vira_dia_seguinte_com_virada_de_mes_e_ano():
    assert nz.instante_local(date(2019, 12, 31), "24:30").isoformat() == "2020-01-01T00:30:00"
    assert nz.instante_local(date(2024, 2, 29), "25:10").isoformat() == "2024-03-01T01:10:00"
    assert nz.instante_local(date(2023, 4, 30), "23:59").isoformat() == "2023-04-30T23:59:00"


def test_retomada_menor_que_incidente_passa_para_o_dia_seguinte():
    assert nz.duracao("23:50", "00:05") == 15
    assert nz.duracao("24:50", "25:05") == 15
    assert nz.duracao("10:00", "10:00") == 0
    for a, b in [("05:00", "04:59"), ("12:00", "11:00")]:
        assert 0 <= nz.duracao(a, b) < 1440


def test_conversao_para_utc_respeita_horario_de_verao():
    # Inverno: UTC-5; verão: UTC-4 (America/Montreal)
    assert nz.para_utc(nz.instante_local(date(2024, 1, 15), "08:00")).hour == 13
    assert nz.para_utc(nz.instante_local(date(2024, 7, 15), "08:00")).hour == 12


def test_faixa_vizinha():
    assert nz.faixa_de(0) == 0 and nz.faixa_de(2) == 0 and nz.faixa_de(3) == 1 and nz.faixa_de(30) == 7


@pytest.fixture(scope="module")
def resumo():
    return json.load(open("dados/derivados/eventos/resumo_normalizacao.json", encoding="utf-8"))


def test_contagens_batem_com_o_painel(resumo):
    assert resumo["tecnicos_uma_linha"] == 8530
    assert resumo["por_causa"] == {"MR": 3982, "EF": 4548}
    assert resumo["causa_comum"] == 45 and resumo["causa_comum_verde_laranja"] == 31
    assert resumo["sem_linha"] == 44


def test_todo_evento_tem_inicio_e_fim_ou_e_excecao(resumo):
    with open("dados/derivados/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
        ev = list(csv.DictReader(f, delimiter=";"))
    assert len(ev) == 8530
    assert all(e["inicio_utc"] and e["fim_utc"] and 0 <= int(e["duracao_min"]) < 1440 for e in ev)
    with open("dados/derivados/eventos/excecoes.csv", encoding="utf-8") as f:
        exc = list(csv.DictReader(f, delimiter=";"))
    assert len(exc) == resumo["excecoes"] == 8530 - resumo["na_faixa_ou_vizinha"]


def test_normalizacao_e_reprodutivel():
    caminho = "dados/derivados/eventos/eventos_tecnicos.csv"
    antes = hashlib.sha256(open(caminho, "rb").read()).hexdigest()
    subprocess.run([sys.executable, "-I", "pipeline/normaliza.py"], check=True, capture_output=True)
    assert hashlib.sha256(open(caminho, "rb").read()).hexdigest() == antes
