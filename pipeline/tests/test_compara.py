"""Spec 013: o comparador de derivados aceita diferença no último dígito e recusa diferença real."""
import json

import compara_derivados as cd


def _grava(p, conteudo):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(conteudo, encoding="utf-8")


def test_iguais_tolerancia_e_diferenca(tmp_path):
    a, b = tmp_path / "pub", tmp_path / "novo"
    _grava(a / "x.csv", "linha;valor\nverde;1.0000000000\n")
    _grava(b / "x.csv", "linha;valor\nverde;1.0000000000\n")
    assert cd.compara(str(a / "x.csv"), str(b / "x.csv"), "x.csv")[0] == "IGUAL"
    _grava(b / "x.csv", "linha;valor\nverde;1.0000000000001\n")
    assert cd.compara(str(a / "x.csv"), str(b / "x.csv"), "x.csv")[0] == "DENTRO DA TOLERÂNCIA"
    _grava(b / "x.csv", "linha;valor\nverde;1.01\n")
    assert cd.compara(str(a / "x.csv"), str(b / "x.csv"), "x.csv")[0] == "DIFERE"


def test_modelos_tem_tolerancia_maior_e_ignora_commit(tmp_path):
    a, b = tmp_path / "pub", tmp_path / "novo"
    _grava(a / "modelos/m.json", json.dumps({"alpha": 1.8330, "codigo_commit": "abc"}))
    _grava(b / "modelos/m.json", json.dumps({"alpha": 1.8331, "codigo_commit": "def"}))
    assert cd.compara(str(a / "modelos/m.json"), str(b / "modelos/m.json"), "modelos/m.json")[0] == "DENTRO DA TOLERÂNCIA"
    _grava(b / "modelos/m.json", json.dumps({"alpha": 1.9, "codigo_commit": "def"}))
    assert cd.compara(str(a / "modelos/m.json"), str(b / "modelos/m.json"), "modelos/m.json")[0] == "DIFERE"


def test_texto_diferente_nunca_passa(tmp_path):
    a, b = tmp_path / "pub", tmp_path / "novo"
    _grava(a / "e.json", json.dumps({"status": "medido"}))
    _grava(b / "e.json", json.dumps({"status": "estimado"}))
    assert cd.compara(str(a / "e.json"), str(b / "e.json"), "e.json")[0] == "DIFERE"
