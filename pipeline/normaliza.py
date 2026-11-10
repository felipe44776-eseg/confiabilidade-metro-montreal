"""Spec 001 e spec 017: normaliza os incidentes técnicos em eventos com início e fim absolutos, fonte e duração.

Uso (da raiz do repositório): .venv/Scripts/python -I pipeline/normaliza.py
Entrada: dados/brutos/stm/incidents_metro.csv (e o km real, para a parcela de cada frota na linha)
Saídas em dados/derivados/eventos/:
  eventos_tecnicos.csv       falhas técnicas de uma linha (material rodante ou equipamentos fixos)
  eventos_causa_comum.csv    falhas técnicas registradas em mais de uma linha, com a lista de linhas
  eventos_sem_linha.csv      falhas técnicas sem linha ("Non affecté"): registradas, fora das métricas por linha
  excecoes.csv               eventos cuja duração calculada não cabe na faixa oficial nem na vizinha
  resumo_normalizacao.json   contagens usadas nos critérios de aceite
Hora: a STM conta o dia de operação; 24:xx e 25:xx caem no dia civil seguinte. A hora é local de Montreal
(America/Montreal, com horário de verão) e é convertida para UTC com a base tzdata.
Duração (spec 017, D55): a calculada pelos horários; fora da faixa oficial e da vizinha, vale a faixa (duracao.py).
Fonte (spec 017, D56): no material rodante, a frota (mr73, mpm10; mr_outros para veículos de trabalho, causa genérica
e frota com menos de 2% do km da linha); nos equipamentos fixos, o setor da STM, dividido pelo sintoma (atribuído na
hora a material rodante ou não) quando as duas partes têm 400 falhas ou mais na rede.
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import duracao as du  # noqa: E402
import km_real  # noqa: E402

BRUTO = "dados/brutos/stm/incidents_metro.csv"
SAIDA = "dados/derivados/eventos"
FUSO = ZoneInfo("America/Montreal")
LINHAS = {"Ligne verte": "verde", "Ligne orange": "laranja", "Ligne jaune": "amarela", "Ligne bleue": "azul"}
NUM_LINHA = {"1": "verde", "2": "laranja", "4": "amarela", "5": "azul"}
CAUSA = {"Matériel roulant": "MR", "Équipements fixes": "EF"}
FAIXAS, INDICE_FAIXA = du.FAIXAS, du.INDICE_FAIXA
FROTA_FONTE = {"MR-73": "mr73", "MPM-10": "mpm10"}
TIPO_KM = {"73": "MR-73", "10": "MPM-10"}
SETOR = {"Service de la voie": "voie", "Service aux trains": "aux_trains", "Service aux stations": "aux_stations", "Service TCPE": "tcpe"}
SINTOMA_TREM = "Matériel roulant"
LIMITE_DIVISAO = 400   # falhas em cada parte do setor (sintoma de trem e sintoma fixo) para dividir
PARCELA_MINIMA = 0.02  # frota com menos que isto do km da linha vai para mr_outros
COLUNAS = ["id", "linha", "linhas", "causa", "causa_secundaria", "frota", "fonte", "sintoma", "tipo", "data_servico",
           "inicio_local", "fim_local", "inicio_utc", "fim_utc", "duracao_min", "duracao_calculada_min", "duracao_ponto_medio_min",
           "regra_duracao", "faixa_oficial", "na_faixa", "na_faixa_vizinha", "virada_de_dia", "classe_gravidade", "classe_faixa_oficial",
           "veiculo", "local_codigo", "evacuacao", "cat", "porta", "kfs", "urgencia", "dano", "tipo_materiel"]


def minutos(hhmm):
    return du.minutos(hhmm)


def instante_local(data_servico, hhmm):
    """Dia de operação + hora (que pode passar de 24:00) -> datetime civil local, sem fuso."""
    return datetime.combine(data_servico, datetime.min.time()) + timedelta(minutes=minutos(hhmm))


def para_utc(local):
    return local.replace(tzinfo=FUSO).astimezone(timezone.utc)


def duracao(h_ini, h_fim):
    """Retomada sem data: se a hora é menor que a do incidente, passou para o dia seguinte."""
    return du.calculada(h_ini, h_fim)


def faixa_de(minutos_):
    return du.faixa_de(minutos_)


def linhas_do_campo(campo):
    return sorted({NUM_LINHA[d] for d in re.findall(r"\d", campo) if d in NUM_LINHA})


def parcelas_frota(ate=km_real.FIM_V1):
    """Parcela do km de cada frota em cada linha, no período do km real usado (spec 004)."""
    km = defaultdict(float)
    for r in km_real.registros(ate=ate):
        l = LINHAS.get(r["ligne"])
        if l and r["km"] is not None:
            km[(l, TIPO_KM.get(r["tipo_materiel"], "outra"))] += r["km"]
    total = defaultdict(float)
    for (l, _), v in km.items():
        total[l] += v
    return {(l, f): v / total[l] for (l, f), v in km.items() if total[l] > 0}


def setores_divididos(tecnicos_brutos):
    """Setores do equipamento fixo em que as duas partes (sintoma de trem e sintoma fixo) têm LIMITE_DIVISAO falhas."""
    n = Counter()
    for e in tecnicos_brutos:
        s = SETOR.get(e["Cause secondaire"])
        if CAUSA[e["Cause primaire"]] == "EF" and s:
            n[(s, e["Symptome"] == SINTOMA_TREM)] += 1
    return sorted(s for s in SETOR.values() if n[(s, True)] >= LIMITE_DIVISAO and n[(s, False)] >= LIMITE_DIVISAO)


def fonte_de(e, linha, parcelas, divididos):
    if CAUSA[e["Cause primaire"]] == "MR":
        f = e["Cause secondaire"] if e["Cause secondaire"] in FROTA_FONTE else None
        if f and (linha is None or parcelas.get((linha, f), 0.0) >= PARCELA_MINIMA):
            return FROTA_FONTE[f]
        return "mr_outros"
    s = SETOR.get(e["Cause secondaire"], "ef_outros")
    if s in divididos:
        return s + ("_sintoma_trem" if e["Symptome"] == SINTOMA_TREM else "_sintoma_fixo")
    return s


def bandeira(v):
    return "1" if v == "1" else "0"


def normaliza_registro(e, fin, fonte=""):
    d = date.fromisoformat(e["Jour calendaire"])
    ini = instante_local(d, e["Heure de l'incident"])
    fim = ini + timedelta(minutes=fin["duracao_min"])
    frota = e["Cause secondaire"] if e["Cause secondaire"] in ("MR-73", "MPM-10") else ""
    return {
        "id": e["Numero d'incident"], "causa": CAUSA[e["Cause primaire"]], "causa_secundaria": e["Cause secondaire"],
        "frota": frota, "fonte": fonte, "sintoma": e["Symptome"], "tipo": e["Type d'incident"], "data_servico": d.isoformat(),
        "inicio_local": ini.strftime("%Y-%m-%dT%H:%M"), "fim_local": fim.strftime("%Y-%m-%dT%H:%M"),
        "inicio_utc": para_utc(ini).strftime("%Y-%m-%dT%H:%MZ"), "fim_utc": para_utc(fim).strftime("%Y-%m-%dT%H:%MZ"),
        **fin, "faixa_oficial": e["Incident en minutes"],
        "veiculo": "" if e["Véhicule"] in ("#", "") else e["Véhicule"], "local_codigo": e["Code de lieu"],
        "evacuacao": "" if e["Évacuation"] in ("#", "") else e["Évacuation"],
        "cat": bandeira(e["CAT"]), "porta": bandeira(e["Porte"]), "kfs": bandeira(e["KFS"]), "urgencia": bandeira(e["Urgence métro"]),
        "dano": bandeira(e["Dommage matériel"]), "tipo_materiel": e["Type de matériel"],
    }


def carrega(caminho=BRUTO):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    cab = linhas[1]
    return [dict(zip(cab, (c.strip() for c in r))) for r in linhas[2:] if len(r) >= len(cab) and r[0].strip()]


def grava(nome, registros, colunas=COLUNAS):
    with open(os.path.join(SAIDA, nome), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas, delimiter=";", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(registros)


RELATORIO = "fontes/verificacao/fontes_e_duracoes.md"
ORDEM_LINHAS = ("verde", "laranja", "amarela", "azul")
ORDEM_CLASSES = ("menos_de_5", "5_a_10", "10_a_30", "30_ou_mais")


def relatorio(tecnicos, comum, divididos, brutos_uma_linha):
    n = lambda xs: f"{xs:,}".replace(",", ".")
    fontes = sorted({r["fonte"] for r in tecnicos})
    L = ["# Fontes de falha e durações pela faixa oficial (spec 017)", "",
         "Gerado por `pipeline/normaliza.py`, com a regra de duração de `pipeline/duracao.py` (D55) e as fontes da D56. "
         "Falhas técnicas de uma linha, de 2019-01-01 a 2026-06-30.", "",
         "## Falhas por fonte e linha", "", "| Fonte | " + " | ".join(ORDEM_LINHAS) + " | Rede |", "|---|" + "---|" * 5]
    for f in fontes:
        c = [sum(1 for r in tecnicos if r["fonte"] == f and r["linha"] == l) for l in ORDEM_LINHAS]
        L.append(f"| `{f}` | " + " | ".join(n(x) for x in c) + f" | {n(sum(c))} |")
    L += ["", f"Causa comum (45 eventos): " + ", ".join(f"`{k}` {v}" for k, v in sorted(Counter(r['fonte'] for r in comum).items())) + ".", "",
          "## Divisão dos setores pelo sintoma", "",
          f"Um setor se divide em sintoma de trem (atribuído na hora a material rodante) e sintoma fixo quando cada parte tem {LIMITE_DIVISAO} falhas ou mais na rede.", "",
          "| Setor | Sintoma de trem | Sintoma fixo | Dividido |", "|---|---|---|---|"]
    cont = Counter()
    for e in brutos_uma_linha:
        s = SETOR.get(e["Cause secondaire"])
        if CAUSA[e["Cause primaire"]] == "EF" and s:
            cont[(s, e["Symptome"] == SINTOMA_TREM)] += 1
    for s in SETOR.values():
        L.append(f"| `{s}` | {n(cont[(s, True)])} | {n(cont[(s, False)])} | {'sim' if s in divididos else 'não'} |")
    L += ["", "## Frota: causa secundária contra \"Type de matériel\"", "", "| Causa secundária | " + " | ".join(["73", "10", "Non affecté"]) + " |", "|---|---|---|---|"]
    for cs in ("MR-73", "MPM-10", "Véhicules de travaux", "Matériel roulant"):
        L.append(f"| {cs} | " + " | ".join(str(sum(1 for r in tecnicos if r["causa_secundaria"] == cs and r["tipo_materiel"] == t)) for t in ("73", "10", "Non affecté")) + " |")
    L += ["", "## Durações", "",
          "Exceção: duração calculada fora da faixa oficial e da vizinha. Nela, vale a faixa (sorteio entre as durações coerentes da mesma faixa e família, "
          "semente pelo número do incidente). \"Ponto médio\" é a sensibilidade com o centro da faixa.", "",
          "| Linha | Família | Falhas | Exceções | Minutos calculados | Minutos pela regra | Minutos com o ponto médio | Minutos das exceções (calculados → regra) |",
          "|---|---|---|---|---|---|---|---|"]
    for l in ORDEM_LINHAS:
        for c in ("MR", "EF"):
            g = [r for r in tecnicos if r["linha"] == l and r["causa"] == c]
            x = [r for r in g if not r["na_faixa_vizinha"]]
            s = lambda xs, k: sum(r[k] for r in xs)
            L.append(f"| {l} | {c} | {n(len(g))} | {len(x)} | {n(s(g, 'duracao_calculada_min'))} | {n(s(g, 'duracao_min'))} | "
                     f"{n(round(s(g, 'duracao_ponto_medio_min')))} | {n(s(x, 'duracao_calculada_min'))} → {n(s(x, 'duracao_min'))} |")
    tot = lambda k: sum(r[k] for r in tecnicos)
    exc = [r for r in tecnicos if not r["na_faixa_vizinha"]]
    pct = lambda x: f"{x:.1%}".replace(".", ",")
    L += ["", f"Total: {n(tot('duracao_calculada_min'))} minutos calculados, {n(tot('duracao_min'))} pela regra, "
          f"{n(round(tot('duracao_ponto_medio_min')))} com o ponto médio. As {len(exc)} exceções ({pct(len(exc) / len(tecnicos))} das falhas) "
          f"tinham {n(sum(r['duracao_calculada_min'] for r in exc))} minutos calculados "
          f"({pct(sum(r['duracao_calculada_min'] for r in exc) / tot('duracao_calculada_min'))} do total) e ficam com "
          f"{n(sum(r['duracao_min'] for r in exc))} pela regra.", "",
          f"Retomada no dia civil seguinte: {sum(r['virada_de_dia'] for r in tecnicos)} falhas, "
          f"{sum(1 for r in tecnicos if r['virada_de_dia'] and r['na_faixa_vizinha'])} coerentes com a faixa (cruzam a meia-noite) e "
          f"{sum(1 for r in tecnicos if r['virada_de_dia'] and not r['na_faixa_vizinha'])} exceções.", "",
          "### Falhas de 300 minutos ou mais depois da regra", "", "| Incidente | Linha | Fonte | Início | Minutos | Faixa oficial | Local |", "|---|---|---|---|---|---|---|"]
    for r in sorted((r for r in tecnicos if r["duracao_min"] >= 300), key=lambda r: -r["duracao_min"]):
        L.append(f"| {r['id']} | {r['linha']} | `{r['fonte']}` | {r['inicio_local']} | {n(r['duracao_min'])} | {r['faixa_oficial']} | {r['local_codigo']} |")
    L += ["", "## Gravidade (D58)", "", "Classes pelos limites da STM: o indicador conta 5 min ou mais; aviso aos usuários acima de 10 min; ônibus substituto acima de 30 min.", "",
          "| Fonte | " + " | ".join(ORDEM_CLASSES) + " | 5 min ou mais (pela regra) | 5 min ou mais (faixa oficial) |", "|---|" + "---|" * 6]
    for f in fontes:
        g = [r for r in tecnicos if r["fonte"] == f]
        c = [sum(1 for r in g if r["classe_gravidade"] == k) for k in ORDEM_CLASSES]
        of5 = sum(1 for r in g if r["classe_faixa_oficial"] not in ("menos_de_5", ""))
        L.append(f"| `{f}` | " + " | ".join(n(x) for x in c) + f" | {n(sum(c[1:]))} | {n(of5)} |")
    open(RELATORIO, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")


def main():
    os.makedirs(SAIDA, exist_ok=True)
    brutos = carrega()
    finais = du.calcula(brutos)
    tecnicos_brutos = [e for e in brutos if e["Cause primaire"] in CAUSA]
    parcelas = parcelas_frota()
    divididos = setores_divididos([e for e in tecnicos_brutos if e["Ligne"] in LINHAS])
    tecnicos, comum, sem_linha, excecoes = [], [], [], []
    for e in tecnicos_brutos:
        fin = finais[e["Numero d'incident"]]
        if e["Ligne"] in LINHAS:
            linha = LINHAS[e["Ligne"]]
            r = normaliza_registro(e, fin, fonte_de(e, linha, parcelas, divididos))
            r["linha"], r["linhas"] = linha, linha
            tecnicos.append(r)
            if not r["na_faixa_vizinha"]:
                excecoes.append(r | {"motivo": "duração calculada fora da faixa oficial e da vizinha"})
        else:
            ls = linhas_do_campo(e["Ligne"])
            r = normaliza_registro(e, fin, fonte_de(e, None, parcelas, divididos))
            r["linha"], r["linhas"] = "", ",".join(ls)
            (comum if len(ls) >= 2 else sem_linha).append(r)
    chave = lambda r: (r["inicio_utc"], r["id"])
    for lista in (tecnicos, comum, sem_linha, excecoes):
        lista.sort(key=chave)
    grava("eventos_tecnicos.csv", tecnicos)
    grava("eventos_causa_comum.csv", comum)
    grava("eventos_sem_linha.csv", sem_linha)
    grava("excecoes.csv", excecoes, COLUNAS + ["motivo"])
    n = len(tecnicos)
    soma = lambda lista, campo: int(sum(r[campo] for r in lista))
    resumo = {
        "tecnicos_uma_linha": n,
        "por_linha": {l: sum(1 for r in tecnicos if r["linha"] == l) for l in ("verde", "laranja", "amarela", "azul")},
        "por_causa": {c: sum(1 for r in tecnicos if r["causa"] == c) for c in ("MR", "EF")},
        "por_fonte": dict(sorted(Counter(r["fonte"] for r in tecnicos).items())),
        "setores_divididos_pelo_sintoma": divididos,
        "na_faixa": sum(r["na_faixa"] for r in tecnicos),
        "na_faixa_ou_vizinha": sum(r["na_faixa_vizinha"] for r in tecnicos),
        "pct_na_faixa_ou_vizinha": round(sum(r["na_faixa_vizinha"] for r in tecnicos) / n, 4),
        "excecoes": len(excecoes),
        "minutos_total_calculada": soma(tecnicos, "duracao_calculada_min"),
        "minutos_total_final": soma(tecnicos, "duracao_min"),
        "minutos_excecoes_calculada": soma(excecoes, "duracao_calculada_min"),
        "minutos_excecoes_final": soma(excecoes, "duracao_min"),
        "virada_de_dia": sum(r["virada_de_dia"] for r in tecnicos),
        "por_classe_gravidade": dict(sorted(Counter(r["classe_gravidade"] for r in tecnicos).items())),
        "por_classe_faixa_oficial": dict(sorted(Counter(r["classe_faixa_oficial"] for r in tecnicos).items())),
        "causa_comum": len(comum),
        "causa_comum_verde_laranja": sum(1 for r in comum if {"verde", "laranja"} <= set(r["linhas"].split(","))),
        "causa_comum_por_fonte": dict(sorted(Counter(r["fonte"] for r in comum).items())),
        "sem_linha": len(sem_linha),
        "inicio_depois_da_meia_noite": sum(1 for r in tecnicos if r["inicio_local"][:10] != r["data_servico"]),
        "duracao_max_min": max(r["duracao_min"] for r in tecnicos),
    }
    with open(os.path.join(SAIDA, "resumo_normalizacao.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=1)
    relatorio(tecnicos, comum, divididos, [e for e in tecnicos_brutos if e["Ligne"] in LINHAS])
    print(json.dumps(resumo, ensure_ascii=False))


if __name__ == "__main__":
    main()
