"""Extrai do Google COVID-19 Community Mobility Reports as linhas da regiao de Montreal.

Uso (da raiz do projeto): python -I pipeline/extrai_mobilidade.py dados/brutos/google/google_Region_Mobility_Report_CSVs.zip
Saida: dados/derivados/mobilidade/google_mobilidade_montreal_2020_2022.csv
Filtro: sub_region_1 == "Quebec" e sub_region_2 contendo "Montr" (resulta so em "Montreal").
"""
import csv
import io
import os
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
z = zipfile.ZipFile(sys.argv[1])
os.makedirs("dados/derivados/mobilidade", exist_ok=True)
saida, n, regioes, fo = None, 0, set(), None
for nome in sorted(x for x in z.namelist() if "_CA_" in x):
    rd = csv.DictReader(io.TextIOWrapper(z.open(nome), encoding="utf-8"))
    for r in rd:
        if r["sub_region_1"] == "Quebec" and "Montr" in r["sub_region_2"]:
            regioes.add(r["sub_region_2"])
            if saida is None:
                fo = open("dados/derivados/mobilidade/google_mobilidade_montreal_2020_2022.csv", "w", encoding="utf-8", newline="")
                saida = csv.DictWriter(fo, fieldnames=rd.fieldnames)
                saida.writeheader()
            saida.writerow(r)
            n += 1
fo.close()
print("regioes:", regioes, "| linhas:", n)
