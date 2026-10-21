"""Critérios de aceite das specs 005 (modelo da taxa) e 006 (distribuições) e do contrato parametros.json."""
import json
import os

import pytest

M = "dados/derivados/modelos"
PARAM = "dados/derivados/simulador/parametros.json"
pytestmark = pytest.mark.skipif(not os.path.exists(f"{M}/distribuicoes.json"), reason="rode modelo_taxa.py e distribuicoes.py antes")
CANDIDATAS = {"exponencial", "weibull", "gama", "lognormal", "log-logistica"}


@pytest.fixture(scope="module", params=["MR", "EF"])
def taxa(request):
    return json.load(open(f"{M}/taxa_{request.param}.json", encoding="utf-8"))


@pytest.fixture(scope="module")
def dist():
    return json.load(open(f"{M}/distribuicoes.json", encoding="utf-8"))


def test_poisson_contra_binomial_negativa(taxa):
    assert taxa["aic_poisson"] > 0 and taxa["aic_nb"] > 0 and taxa["alpha_nb"] > 0
    assert 0 <= taxa["p_lr_dispersao"] <= 1
    esperado = "binomial negativa" if (taxa["aic_nb"] < taxa["aic_poisson"] and taxa["p_lr_dispersao"] < 0.05) else "Poisson"
    assert taxa["modelo_escolhido"] == esperado


def test_ic_por_bootstrap_em_blocos(taxa):
    assert taxa["bootstrap_b"] >= 200
    for c in taxa["coeficientes"]:
        lo, hi = c["ic95"]
        assert lo <= hi, c["termo"]
        assert c["reamostras_validas"] >= 150, c["termo"]


def test_residuos_e_rootograma(taxa):
    q = taxa["residuos_quantilicos"]
    assert abs(q["media"]) < 0.1 and 0.8 < q["desvio"] < 1.2
    assert [x["contagem"] for x in taxa["rootograma"]] == [0, 1, 2, "3+"]


def test_greve_entra_no_modelo(taxa):
    assert any(c["termo"] == "greve" for c in taxa["coeficientes"])


def test_comparacao_mr_ef():
    comp = json.load(open(f"{M}/comparacao_mr_ef.json", encoding="utf-8"))
    termos = {x["termo"] for x in comp}
    assert {"faixa=pico_manha", "temp=abaixo_-15"} <= termos
    assert all(x["ic95"][0] <= x["ic95"][1] and x["conclusao"] for x in comp)
    texto = open("fontes/verificacao/modelo_taxa.md", encoding="utf-8").read()
    assert "## Material rodante contra equipamentos fixos" in texto and "## Greves" in texto


def test_tbf_por_estrato(dist):
    for chave, v in dist["tbf"].items():
        if "herda_de" in v:
            assert v["n"] < 30 and v["herda_de"] in dist["tbf"]
            continue
        assert set(v["aic"]) == CANDIDATAS
        assert v["melhor"] == min(v["aic"], key=v["aic"].get)
        a = v["aderencia_melhor"]
        assert 0 <= a["p_ks_bootstrap"] <= 1 and 0 <= a["p_ad_bootstrap"] <= 1 and a["b"] >= 200
    assert any(k.endswith("|inverno") for k in dist["tbf"]) and any("|MPM-10" in k for k in dist["tbf"])


def test_reescala_decide_o_processo(dist):
    assert len(dist["reescala"]) == 8
    for k, v in dist["reescala"].items():
        assert 0.9 < v["media"] < 1.1, k  # Λ(t) bem calibrado
        poisson = v["p_ks"] > 0.05
        assert v["compativel_poisson"] == poisson
        assert v["processo_no_simulador"].startswith("Poisson" if poisson else "renovação Weibull")


def test_ttr_massa_em_zero_e_tempo_acelerado(dist):
    for k, v in dist["ttr"].items():
        assert 0 <= v["p_zero"] <= 1 and v["lognormal_positivos"]["sigma_log"] > 0
    termos = set(dist["ttr_aft"]["multiplicadores"])
    assert "evacuacao" in termos and any(t.startswith("faixa_") for t in termos) and any(t.startswith("sec_") for t in termos)


def test_beta_com_clopper_pearson(dist):
    vl = dist["causa_comum"]["verde-laranja"]
    assert vl["eventos"] == 31
    assert vl["beta_a_ic95"][0] <= vl["beta_a"] <= vl["beta_a_ic95"][1]


def test_grupos_de_causa_comum_sem_dupla_contagem(dist):
    grupos = dist["causa_comum_grupos"]
    assert sum(g["eventos"] for g in grupos.values()) == 45  # cada evento num grupo só
    assert all(len(g["linhas"]) >= 2 and "-".join(sorted(g["linhas"])) == k for k, g in grupos.items())
    assert sum(g["eventos"] for g in grupos.values() if {"verde", "laranja"} <= set(g["linhas"])) == dist["causa_comum"]["verde-laranja"]["eventos"]


def _parametros(obj, caminho=""):
    if isinstance(obj, dict):
        if "valor" in obj and "status" in obj:
            yield caminho, obj
        else:
            for k, v in obj.items():
                yield from _parametros(v, f"{caminho}/{k}")


@pytest.mark.skipif(not os.path.exists(PARAM), reason="rode parametros.py antes")
def test_contrato_parametros():
    p = json.load(open(PARAM, encoding="utf-8"))
    schema = json.load(open("contratos/parametros.schema.json", encoding="utf-8"))
    assert set(schema["required"]) <= set(p)
    n = 0
    for caminho, par in _parametros({k: v for k, v in p.items() if k not in ("locais_ef",)}):
        n += 1
        assert par["status"] in ("ajustado", "deduzido", "hipótese", "não verificado"), caminho
        assert par["metodo"] and par["script"] and isinstance(par["fontes"], list), caminho
        if par["status"] == "ajustado":
            assert par["fontes"], caminho
        if par["status"] == "hipótese":
            assert par.get("faixa") or caminho.endswith("janela_operacao_h"), caminho
    assert n > 100
    assert all(len(v["linhas"]) >= 2 for v in p["causa_comum"].values())
    for k, v in p["ttr"].items():  # o simulador sorteia a duração positiva da amostra observada
        a = v["amostra_positivos"]
        assert a["n"] == len(a["minutos"]) > 0 and a["minutos"] == sorted(a["minutos"]) and min(a["minutos"]) > 0, k
    assert p["causa_comum_beta"]["verde-laranja"]["eventos"] == 31
    assert not any(nivel == "sem_dado" for c in ("MR", "EF") for f in p["taxas"][c]["multiplicadores"].values() for nivel in f)
    for l in ("verde", "laranja", "amarela", "azul"):
        assert p["taxas"]["MR"]["base_por_trem_hora"][l]["ic95"]
        assert sum(x["peso"] for x in p["locais_ef"][l]) > 0
