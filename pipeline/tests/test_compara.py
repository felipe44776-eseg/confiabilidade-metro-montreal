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


def test_modelos_tem_tolerancia_maior_e_ignora_so_o_tempo(tmp_path):
    a, b = tmp_path / "pub", tmp_path / "novo"
    _grava(a / "modelos/m.json", json.dumps({"alpha": 1.8330, "bootstrap_segundos": 600.1, "codigo_commit": "sha256-scripts:abc"}))
    _grava(b / "modelos/m.json", json.dumps({"alpha": 1.8331, "bootstrap_segundos": 645.4, "codigo_commit": "sha256-scripts:abc"}))
    assert cd.compara(str(a / "modelos/m.json"), str(b / "modelos/m.json"), "modelos/m.json")[0] == "DENTRO DA TOLERÂNCIA"
    _grava(b / "modelos/m.json", json.dumps({"alpha": 1.9, "bootstrap_segundos": 645.4, "codigo_commit": "sha256-scripts:abc"}))
    assert cd.compara(str(a / "modelos/m.json"), str(b / "modelos/m.json"), "modelos/m.json")[0] == "DIFERE"
    # código diferente (hash dos scripts) é diferença, não metadado (decisão D43)
    _grava(b / "modelos/m.json", json.dumps({"alpha": 1.8330, "bootstrap_segundos": 600.1, "codigo_commit": "sha256-scripts:xyz"}))
    assert cd.compara(str(a / "modelos/m.json"), str(b / "modelos/m.json"), "modelos/m.json")[0] == "DIFERE"


def test_texto_diferente_nunca_passa(tmp_path):
    a, b = tmp_path / "pub", tmp_path / "novo"
    _grava(a / "e.json", json.dumps({"status": "medido"}))
    _grava(b / "e.json", json.dumps({"status": "estimado"}))
    assert cd.compara(str(a / "e.json"), str(b / "e.json"), "e.json")[0] == "DIFERE"


def test_arquivo_que_falta_ou_sobra_na_refeita_e_problema(tmp_path, capsys):
    # achado 14 da rodada 3: antes, um arquivo a mais na pasta refeita passava calado
    a, b = tmp_path / "pub", tmp_path / "novo"
    _grava(a / "x.json", json.dumps({"v": 1}))
    _grava(b / "x.json", json.dumps({"v": 1}))
    assert cd.percorre(str(a), str(b)) == 0
    _grava(b / "sub/novo.json", json.dumps({"v": 2}))
    assert cd.percorre(str(a), str(b)) == 1
    assert "SOBRA   sub/novo.json" in capsys.readouterr().out
    _grava(a / "so_publicado.csv", "a;b\n1;2\n")
    assert cd.percorre(str(a), str(b)) == 2
    assert "FALTA   so_publicado.csv" in capsys.readouterr().out
