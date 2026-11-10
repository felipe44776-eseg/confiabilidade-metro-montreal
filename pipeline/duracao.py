"""Spec 017 (D55, D58): duração de cada incidente pela faixa oficial da STM e classe de gravidade.

A duração calculada vem dos horários de início e de retomada do "délai service clientèle" (retomada sem data: se
a hora é menor, passou para o dia seguinte). A STM publica também a faixa oficial ("Incident en minutes"). Quando a
calculada cai fora da faixa oficial e da faixa vizinha, vale a faixa: a duração é sorteada entre as durações
coerentes (calculada na própria faixa oficial) da mesma faixa e da mesma família, com semente tirada do número do
incidente. Na faixa "30 min et plus" vale a calculada (não há exceção possível: a vizinha cobre 25 a 29 min e o
resto é coerente). Usado por normaliza.py, monta_painel.py e analise_confiabilidade.py, para que o painel, o
FONTES.md e o simulador tenham as mesmas durações.
"""
import hashlib
import random

FAIXAS = [("02 min et moins", 0, 2), ("03 à 04 min", 3, 4), ("05 à 09 min", 5, 9), ("10 à 14 min", 10, 14),
          ("15 à 19 min", 15, 19), ("20 à 24 min", 20, 24), ("25 à 29 min", 25, 29), ("30 min et plus", 30, 10 ** 6)]
INDICE_FAIXA = {nome: i for i, (nome, _, _) in enumerate(FAIXAS)}
PONTO_MEDIO = {0: 1.0, 1: 3.5, 2: 7.0, 3: 12.0, 4: 17.0, 5: 22.0, 6: 27.0}  # faixa "30 min et plus": a calculada
FAMILIA = {"Matériel roulant": "MR", "Équipements fixes": "EF"}
# Limites da STM: o indicador conta 5 min ou mais; aviso aos usuários acima de 10 min; ônibus substituto acima de 30 min.
CLASSES = [("menos_de_5", 0, 4), ("5_a_10", 5, 9), ("10_a_30", 10, 29), ("30_ou_mais", 30, 10 ** 6)]
CLASSE_DA_FAIXA = {0: "menos_de_5", 1: "menos_de_5", 2: "5_a_10", 3: "10_a_30", 4: "10_a_30", 5: "10_a_30", 6: "10_a_30", 7: "30_ou_mais"}


def minutos(hhmm):
    h, m = hhmm.strip().split(":")
    return int(h) * 60 + int(m)


def calculada(h_ini, h_fim):
    """Retomada sem data: se a hora é menor que a do incidente, passou para o dia seguinte."""
    return (minutos(h_fim) - minutos(h_ini)) % 1440


def virada_de_dia(h_ini, h_fim):
    """A retomada cai no dia civil seguinte ao do início (a STM escreve 24:xx depois da meia-noite)."""
    return minutos(h_ini) % 1440 + calculada(h_ini, h_fim) >= 1440


def faixa_de(minutos_):
    for i, (_, a, b) in enumerate(FAIXAS):
        if a <= minutos_ <= b:
            return i
    return None


def classe(minutos_):
    for nome, a, b in CLASSES:
        if a <= minutos_ <= b:
            return nome
    return None


def familia(causa_primaria):
    return FAMILIA.get(causa_primaria, "outra")


def semente(numero_incidente):
    return int.from_bytes(hashlib.sha256(numero_incidente.encode("utf-8")).digest()[:8], "big")


def calcula(registros):
    """registros: linhas do CSV bruto (dict com os nomes das colunas da STM). Devolve {número do incidente: campos}.

    Campos: duracao_calculada_min, duracao_min (final), regra_duracao ("calculada" | "faixa"), duracao_ponto_medio_min,
    na_faixa, na_faixa_vizinha, virada_de_dia, classe_gravidade (pela final), classe_faixa_oficial.
    """
    base = []
    coerentes = {}
    for r in registros:
        calc = calculada(r["Heure de l'incident"], r["Heure de reprise"])
        oficial = INDICE_FAIXA.get(r["Incident en minutes"])
        propria = faixa_de(calc)
        na = oficial is not None and propria == oficial
        viz = oficial is not None and propria is not None and abs(propria - oficial) <= 1
        fam = familia(r["Cause primaire"])
        base.append((r, calc, oficial, na, viz, fam))
        if na:
            coerentes.setdefault((fam, oficial), []).append(calc)
    for k in coerentes:
        coerentes[k].sort()  # ordem fixa: o sorteio não depende da ordem do arquivo
    saida = {}
    for r, calc, oficial, na, viz, fam in base:
        final, regra = calc, "calculada"
        if oficial is not None and not viz:
            pool = coerentes.get((fam, oficial)) or coerentes.get(("MR", oficial), []) + coerentes.get(("EF", oficial), [])
            if pool:
                final = pool[random.Random(semente(r["Numero d'incident"])).randrange(len(pool))]
            else:
                final = PONTO_MEDIO.get(oficial, calc)
            regra = "faixa"
        medio = PONTO_MEDIO.get(oficial, calc) if (oficial is not None and not viz) else calc
        saida[r["Numero d'incident"]] = {
            "duracao_calculada_min": calc, "duracao_min": final, "regra_duracao": regra, "duracao_ponto_medio_min": medio,
            "na_faixa": int(na), "na_faixa_vizinha": int(viz), "virada_de_dia": int(virada_de_dia(r["Heure de l'incident"], r["Heure de reprise"])),
            "classe_gravidade": classe(final), "classe_faixa_oficial": CLASSE_DA_FAIXA.get(oficial, ""),
        }
    return saida
