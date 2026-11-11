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


def test_alvos_da_revisao_por_familia_e_5_min(bt):
    """Spec 020: o backtest refeito traz os alvos por família e de 5 min ou mais, em todas as versões."""
    linhas = ("verde", "laranja", "amarela", "azul")
    for v, x in bt.items():
        assert len(x["casos_familia"]) == 144, v
        for c in ("MR", "EF"):
            assert x["cobertura_por_familia"][c]["casos"] == 72
        for l in linhas:
            g = x["ge5_ano"][l]
            assert g["ic95"][0] <= g["mediana"] <= g["ic95"][1]
            assert g["observado"] >= sum(x["ge5_familia"][f"{l}|{c}"]["observado"] for c in ("MR", "EF"))  # o total soma a causa comum
            assert x["minutos_ano"][l]["observado"] >= sum(x["minutos_familia"][f"{l}|{c}"]["observado"] for c in ("MR", "EF"))
        # a contagem mensal da família soma a do total
        tot = {(c["linha"], c["mes"]): c["observado"] for c in x["casos"]}
        fam = {}
        for c in x["casos_familia"]:
            fam[(c["linha"], c["mes"])] = fam.get((c["linha"], c["mes"]), 0) + c["observado"]
        assert fam == tot, v


def test_relatorio_lista_falhas_e_registro():
    texto = open("fontes/verificacao/backtest.md", encoding="utf-8").read()
    for secao in ("## Cobertura do intervalo de predição de 90%", "## Registro de mudança", "## Onde o modelo falhou", "## PIT", "## Minutos parados",
                  "após a revisão (pós-hoc, spec 020)", "## Por família", "## Falhas de 5 min ou mais"):
        assert secao in texto
    assert os.path.exists("fontes/verificacao/backtest_pit.svg")
