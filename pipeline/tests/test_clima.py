"""Critérios de aceite da spec 003 (clima horário e eventos externos), sobre os derivados gerados."""
import csv
import os
from datetime import datetime, timedelta, timezone

import pytest

PAINEL = "dados/derivados/clima/painel_horario.csv"
EVENTOS = "dados/derivados/clima/eventos_externos.csv"
pytestmark = pytest.mark.skipif(not os.path.exists(PAINEL), reason="rode pipeline/clima_eventos.py antes")


@pytest.fixture(scope="module")
def painel():
    with open(PAINEL, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


@pytest.fixture(scope="module")
def por_utc(painel):
    return {r["inicio_utc"]: r for r in painel}


def test_precipitacao_em_95pct_das_horas_de_operacao(painel):
    servico = [r for r in painel if 5 <= int(r["hora_servico"]) <= 24 and "2019-01-01" <= r["data_servico"] <= "2026-06-30"]
    com = [r for r in servico if r["precip_mm"] != ""]
    assert len(com) / len(servico) >= 0.95
    assert all(r["estacao_precip"] in ("10761", "30165") for r in com)
    assert all(r["estacao_precip"] == "" for r in servico if r["precip_mm"] == "")


def test_horas_utc_continuas_sem_duplicata(painel):
    t = [datetime.strptime(r["inicio_utc"], "%Y-%m-%dT%H:%MZ") for r in painel]
    assert all(b - a == timedelta(hours=1) for a, b in zip(t, t[1:]))


@pytest.mark.parametrize("dia,horas", [("2023-03-12", 23), ("2023-11-05", 25), ("2024-03-10", 23), ("2024-11-03", 25)])
def test_trocas_de_horario_de_verao(painel, dia, horas):
    locais = [r["local"] for r in painel if r["local"].startswith(dia)]
    assert len(locais) == horas
    assert len(set(locais)) == horas


@pytest.mark.parametrize("utc,local", [
    ("2023-11-05T05:00Z", "2023-11-05T01:00-0400"),  # 1ª 01:00 (ainda horário de verão)
    ("2023-11-05T06:00Z", "2023-11-05T01:00-0500"),  # 2ª 01:00 (hora padrão)
    ("2023-03-12T06:00Z", "2023-03-12T01:00-0500"),
    ("2023-03-12T07:00Z", "2023-03-12T03:00-0400"),  # 02:00 não existe
])
def test_conversao_local(por_utc, utc, local):
    assert por_utc[utc]["local"] == local


def test_lst_e_utc_menos_5():
    """A linha do ECCC em LST 2023-07-01 12:00 é a hora UTC 17:00 do painel."""
    from clima_eventos import carrega_estacao
    est = carrega_estacao("51157")
    alvo = datetime(2023, 7, 1, 17, tzinfo=timezone.utc)
    assert est[alvo]["Date/Time (LST)"] == "2023-07-01 12:00"


def test_chuva_congelante_2023_04_05(por_utc):
    # Episódio da pesquisa: 09h às 20h em LST (UTC-5), ou seja, 14:00Z de 05/04 a 01:00Z de 06/04
    inicio = datetime(2023, 4, 5, 14)
    for k in range(12):
        t = (inicio + timedelta(hours=k)).strftime("%Y-%m-%dT%H:%MZ")
        assert por_utc[t]["chuva_congelante"] == "1", t


def test_condicao_ausente_nao_vira_zero(painel):
    sem = [r for r in painel if r["condicao"] == ""]
    assert sem and all(r["chuva"] == r["neve"] == r["chuva_congelante"] == "" for r in sem)


def test_eventos_com_data_faixa_url_e_status():
    with open(EVENTOS, encoding="utf-8") as f:
        ev = list(csv.DictReader(f, delimiter=";"))
    assert {e["tipo"] for e in ev} == {"jogo_canadiens", "gp_f1", "greve_stm"}
    for e in ev:
        assert e["data_servico"] and e["inicio_local"] and e["fonte_url"].startswith("https://")
        assert e["status"] in ("verificado", "não verificado")


def test_greve_vira_exposicao_zero(painel):
    sem_servico = [r for r in painel if r["data_servico"] == "2025-11-01"]
    assert sem_servico and all(float(r["fracao_servico"]) == 0 for r in sem_servico)
    dia = {int(r["hora_servico"]): float(r["fracao_servico"]) for r in painel if r["data_servico"] == "2025-06-09"}
    assert dia[8] == 1.0 and dia[11] == 0.0 and dia[9] == pytest.approx(38 / 60, abs=1e-4)
    normal = [float(r["fracao_servico"]) for r in painel if r["data_servico"] == "2025-06-02"]
    assert all(x == 1.0 for x in normal)


def test_fatores_ausentes_no_dicionario():
    texto = open("docs/dicionario_dados.md", encoding="utf-8").read().lower()
    for fator in ("passageiros diários", "fechamentos planejados", "quedas de energia"):
        assert fator in texto
    assert "ausente" in texto
