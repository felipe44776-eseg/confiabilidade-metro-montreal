"""Critérios de aceite da spec 012 (validação contra o histórico), sobre o resultado gravado."""
import json
import os

import pytest

BT = "dados/derivados/modelos/backtest.json"
pytestmark = pytest.mark.skipif(not os.path.exists(BT), reason="rode pipeline/backtest.py antes")


@pytest.fixture(scope="module")
def bt():
    return json.load(open(BT, encoding="utf-8"))


def test_versoes_e_pre_registro(bt):
    assert set(bt) == {"A", "B", "C", "D"}
    assert bt["A"]["pre_registrada"] and bt["B"]["pre_registrada"]
    assert not bt["C"]["pre_registrada"] and not bt["D"]["pre_registrada"]
    assert bt["A"]["corte"] == "2024-12-31" and bt["B"]["corte"] == "2023-09-30"
    assert bt["D"]["teste"][0] > bt["D"]["corte"]  # reteste em outro período, depois do corte


def test_72_casos_linha_mes_com_ip_e_pit(bt):
    for v, x in bt.items():
        assert len(x["casos"]) == 72, v
        for c in x["casos"]:
            assert c["ip90"][0] <= c["mediana"] <= c["ip90"][1]
            assert 0 <= c["pit"] <= 1
        assert sum(x["pit_histograma_10"]) == 72
        t = x["cobertura_total"]
        assert t["casos"] == 72 and t["ic95"][0] <= t["cobertura"] <= t["ic95"][1]
        assert x["vetores_bootstrap"] >= 100


def test_greve_separada_e_minutos(bt):
    a = bt["A"]
    assert a["cobertura_meses_greve"]["casos"] == 16 and a["cobertura_sem_greve"]["casos"] == 56
    for l in ("verde", "laranja", "amarela", "azul"):
        m = a["minutos_ano"][l]
        assert m["ic95"][0] <= m["mediana"] <= m["ic95"][1] and m["observado"] > 0


def test_relatorio_lista_falhas_e_registro():
    texto = open("fontes/verificacao/backtest.md", encoding="utf-8").read()
    for secao in ("## Cobertura do intervalo de predição de 90%", "## Registro de mudança", "## Onde o modelo falhou", "## PIT", "## Minutos parados"):
        assert secao in texto
    assert os.path.exists("fontes/verificacao/backtest_pit.svg")
