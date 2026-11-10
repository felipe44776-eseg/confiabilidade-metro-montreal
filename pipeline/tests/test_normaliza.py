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


@pytest.fixture(scope="module")
def eventos():
    with open("dados/derivados/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


# ---------------------------------------------------------------- spec 017 (fontes e durações)

def test_fontes_somam_o_total_e_seguem_a_regra_de_divisao(resumo, eventos):
    assert sum(resumo["por_fonte"].values()) == 8530
    assert set(resumo["por_fonte"]) == {"mr73", "mpm10", "mr_outros", "voie_sintoma_trem", "voie_sintoma_fixo",
                                        "aux_trains_sintoma_trem", "aux_trains_sintoma_fixo", "aux_stations", "tcpe"}
    assert resumo["setores_divididos_pelo_sintoma"] == ["aux_trains", "voie"]
    for e in eventos:
        if e["causa"] == "MR":
            assert e["fonte"] in ("mr73", "mpm10", "mr_outros")
        else:
            assert e["fonte"].split("_sintoma_")[0] in ("voie", "aux_trains", "aux_stations", "tcpe")
            if "_sintoma_" in e["fonte"]:
                assert (e["sintoma"] == "Matériel roulant") == e["fonte"].endswith("_sintoma_trem")
    # frota fora da sua linha (menos de 2% do km) vai para mr_outros
    assert not any(e["fonte"] == "mr73" and e["linha"] == "laranja" for e in eventos)
    assert not any(e["fonte"] == "mpm10" and e["linha"] == "azul" for e in eventos)


def test_duracao_pela_faixa_oficial(eventos):
    import duracao as du
    for e in eventos:
        dur, calc = int(e["duracao_min"]), int(e["duracao_calculada_min"])
        if e["na_faixa_vizinha"] == "1":
            assert e["regra_duracao"] == "calculada" and dur == calc
        else:
            # exceção: a duração final cai na própria faixa oficial
            assert e["regra_duracao"] == "faixa" and du.faixa_de(dur) == du.INDICE_FAIXA[e["faixa_oficial"]]
        assert e["classe_gravidade"] == du.classe(dur)
    st_michel = [e for e in eventos if e["id"] == "T17102402"]  # 1.170 min calculados, faixa "02 min et moins"
    assert st_michel and int(st_michel[0]["duracao_min"]) <= 2


def test_regra_de_duracao_nao_depende_da_ordem_dos_registros():
    import random
    import duracao as du
    brutos = nz.carrega()
    a = du.calcula(brutos)
    embaralhados = brutos[:]
    random.Random(1).shuffle(embaralhados)
    assert du.calcula(embaralhados) == a


def test_minutos_e_viradas_de_dia(resumo):
    assert resumo["minutos_total_calculada"] == 43971
    assert resumo["minutos_excecoes_calculada"] == 11129
    assert resumo["minutos_excecoes_final"] < 1000
    assert resumo["virada_de_dia"] == 27


def test_normalizacao_e_reprodutivel():
    caminho = "dados/derivados/eventos/eventos_tecnicos.csv"
    antes = hashlib.sha256(open(caminho, "rb").read()).hexdigest()
    subprocess.run([sys.executable, "-I", "pipeline/normaliza.py"], check=True, capture_output=True)
    assert hashlib.sha256(open(caminho, "rb").read()).hexdigest() == antes
