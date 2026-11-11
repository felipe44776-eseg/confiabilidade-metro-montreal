"""Spec 020 (D62): falhas de zero minuto por fonte e ano, com a leitura fixada antes de calcular."""
import json
import os

import pytest

import distribuicoes as ds

DIST = "dados/derivados/modelos/distribuicoes.json"


def eventos(p_zero_por_fonte, n=400, anos=("2023", "2024", "2025")):
    """Eventos sintéticos: em cada fonte e ano, a fração p de duração zero e o resto com 7 min."""
    ev = []
    for f, p in p_zero_por_fonte.items():
        for a in anos:
            k = round(p(a) * n) if callable(p) else round(p * n)
            ev += [{"fonte": f, "data_servico": f"{a}-05-01", "duracao_min": "0"}] * k
            ev += [{"fonte": f, "data_servico": f"{a}-05-01", "duracao_min": "7"}] * (n - k)
    return ev


TODAS = ds.REARME + ds.OUTRAS_FIXAS


def test_rearme_quando_controle_e_frotas_tem_mais_zeros_e_estaveis():
    m = ds.massa_em_zero(eventos({f: (0.6 if f in ds.REARME else 0.2) for f in TODAS}))
    assert m["leitura"] == "parada segura com rearme rápido"


def test_registro_quando_as_fontes_sao_iguais():
    m = ds.massa_em_zero(eventos({f: 0.4 for f in TODAS}))
    assert m["leitura"] == "artefato de registro"


def test_registro_quando_um_ano_salta_na_maioria_das_fontes():
    salto = lambda a: 0.7 if a == "2024" else 0.3
    m = ds.massa_em_zero(eventos({f: (salto if f in TODAS[:5] else 0.3) for f in TODAS}))
    assert "2024" in m["saltos_comuns"] and m["leitura"] in ("artefato de registro", "os dois padrões")


def test_inconclusiva_quando_heterogeneas_sem_o_padrao_do_rearme():
    p = {f: 0.2 for f in TODAS}
    p["mr73"] = 0.1  # uma frota abaixo de uma fonte fixa: não é o padrão do rearme
    p["aux_stations"] = 0.9
    m = ds.massa_em_zero(eventos(p))
    assert m["leitura"] == "inconclusiva"


def test_mr_outros_fica_fora_das_comparacoes():
    p = {f: 0.4 for f in TODAS}
    p["mr_outros"] = 0.95
    m = ds.massa_em_zero(eventos(p))
    assert "mr_outros" in m["fontes"] and "mr_outros" not in m["fontes_comparadas"]
    assert m["leitura"] == "artefato de registro"


@pytest.mark.skipif(not os.path.exists(DIST), reason="rode distribuicoes.py antes")
def test_resultado_gravado_cobre_todas_as_falhas():
    m = json.load(open(DIST, encoding="utf-8"))["massa_em_zero"]
    assert sum(v["n"] for v in m["fontes"].values()) == 8530
    assert m["leitura"] in ("parada segura com rearme rápido", "artefato de registro", "os dois padrões", "inconclusiva")
    for f, v in m["fontes"].items():
        assert v["p_zero_ic95"][0] <= v["p_zero"] <= v["p_zero_ic95"][1], f
        assert v["p_zero"] <= v["p_ate_1min"], f
        assert sum(x["n"] for x in v["por_ano"].values()) == v["n"], f
