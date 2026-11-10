"""Leitor do km real da STM ("Kilométrage réalisé par les voitures de métro") nos dois formatos publicados.

- Até a Release dados-2026-10-20: separador vírgula, data em "Jour calendaire", 2019-01 a 2023-09.
- Desde a publicação de 2026-10-23 (Release dados-2026-11): separador ponto e vírgula, data em "Date", milhar com
  espaço ("6 102,000"), 2019-01 a 2026-09. Nos 57 meses em comum, os km por mês, linha e frota são idênticos.
Cada registro sai com nomes fixos: data, ligne, tipo_materiel, km, composicao, periodo, codigo_degradacao, tipo_dia.
"""
import csv
import re

CAMINHO = "dados/brutos/stm/km_reel.csv"
# fim do km real usado até a revisão de 2026-11 (spec 004); a spec 018 estende até o fim do arquivo novo
FIM_V1 = "2023-09-30"
_ESPACO = re.compile(r"\s")


def numero(texto):
    t = _ESPACO.sub("", texto or "")
    if t in ("", "#"):
        return None
    try:
        return float(t.replace(",", "."))
    except ValueError:
        return None


def registros(caminho=CAMINHO, ate=None):
    """Gera os registros, opcionalmente só até a data `ate` (AAAA-MM-DD, inclusive)."""
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        cab = f.readline()
        sep = ";" if cab.count(";") > cab.count(",") else ","
        f.seek(0)  # utf-8-sig tira o BOM de novo depois do seek
        for r in csv.DictReader(f, delimiter=sep):
            data = r.get("Date") or r.get("Jour calendaire")
            if not data or (ate and data > ate):
                continue
            yield {
                "data": data, "ligne": r["Ligne"], "tipo_materiel": r["Type matériel"], "km": numero(r["Km voiture"]),
                "composicao": r.get("Composition du train", ""), "periodo": r.get("Période exploitation", ""),
                "codigo_degradacao": r.get("Code Degradation", r.get("Code dégradation", "")),
                "tipo_dia": r.get("Type de jour", ""),
            }
