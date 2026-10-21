"""Critérios de aceite da spec 004 (exposição), sobre os derivados gerados."""
import csv
import json
import os

import pytest

RESUMO = "dados/derivados/exposicao/resumo_exposicao.json"
pytestmark = pytest.mark.skipif(not os.path.exists(RESUMO), reason="rode pipeline/exposicao.py antes")
# Exceções aceitas e documentadas na spec 004 (abril de 2020, início da pandemia, e junho de 2019 na Amarela)
EXCECOES = {("verde", "2020-04"), ("azul", "2020-04"), ("laranja", "2020-04"), ("amarela", "2019-06")}


@pytest.fixture(scope="module")
def resumo():
    return json.load(open(RESUMO, encoding="utf-8"))


def test_trens_em_viagem_as_8h(resumo):
    esperado = {"verde": 26, "laranja": 32, "amarela": 2, "azul": 9}
    for linha, n in esperado.items():
        assert abs(resumo["trens_em_viagem_08h_dia_util"][linha] - n) <= 1, linha


def test_erro_mensal_ate_10pct_salvo_excecoes_documentadas(resumo):
    with open("dados/derivados/exposicao/calibracao_mensal.csv", encoding="utf-8") as f:
        meses = list(csv.DictReader(f, delimiter=";"))
    fora = {(m["linha"], m["mes"]) for m in meses if abs(float(m["erro_relativo"])) > 0.10}
    assert fora == EXCECOES
    assert resumo["meses_com_erro_acima_de_10pct"] == len(EXCECOES)


def test_sem_trens_de_madrugada():
    with open("dados/derivados/exposicao/perfil_horario.csv", encoding="utf-8") as f:
        perfil = list(csv.DictReader(f, delimiter=";"))
    assert all(float(r["trens_hora"]) == 0 for r in perfil if int(r["hora"]) in (3, 4))
    assert all(float(r["trens_hora"]) > 0 for r in perfil if int(r["hora"]) == 8)


def test_frotas_somam_o_total_menos_o_tipo_63(resumo):
    km = resumo["km_carro_por_frota"]
    assert resumo["registros_por_frota"]["MR-63"] == 22
    # o total está em milhões com 4 casas (passo de 100 km): a soma tem de bater até meio passo
    assert abs(resumo["km_carro_total_milhoes"] * 1e6 - km["MR-73"] - km["MPM-10"] - km["MR-63"]) <= 50
    assert resumo["total_menos_mr73_e_mpm10_km"] == pytest.approx(km["MR-63"], abs=0.1)
    with open("dados/derivados/exposicao/frota_mensal.csv", encoding="utf-8") as f:
        fr = list(csv.DictReader(f, delimiter=";"))
    assert all(r["status"] == ("medido" if r["mes"] <= "2023-09" else "estimado") and r["fonte"] for r in fr)


def test_status_medido_e_estimado():
    with open("dados/derivados/exposicao/exposicao_diaria.csv", encoding="utf-8") as f:
        dias = list(csv.DictReader(f, delimiter=";"))
    assert all(d["status"] == "medido" for d in dias if d["data_servico"] <= "2023-09-30" and d["fonte_fator"].startswith("km real"))
    assert all(d["status"] == "estimado" for d in dias if d["data_servico"] > "2023-09-30")
    greve = [d for d in dias if d["greve"] == "1"]
    assert len({d["data_servico"] for d in greve}) == 25
