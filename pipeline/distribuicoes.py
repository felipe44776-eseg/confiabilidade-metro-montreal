"""Spec 006: distribuições do tempo entre falhas (TBF), do tempo até o serviço voltar (TTR) e da causa comum.

Uso (da raiz do repositório): .venv/Scripts/python -I pipeline/distribuicoes.py [--bootstrap N]
Entradas: eventos (spec 001), painel do modelo de taxa com a falha esperada por hora (spec 005), km real.
Saídas: dados/derivados/modelos/distribuicoes.json e fontes/verificacao/distribuicoes.md
Tempo de operação: janela de 20 h por dia de serviço (05:00 a 01:00), a mesma do painel.
"""
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import date

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

SEMENTE = 20261021
B = int(sys.argv[sys.argv.index("--bootstrap") + 1]) if "--bootstrap" in sys.argv else 200
INICIO = date(2019, 1, 1)
JAN_INI, JAN_MIN = 300, 1200
LINHAS = ("verde", "laranja", "amarela", "azul")
CANDIDATAS = {"exponencial": (stats.expon, 1), "weibull": (stats.weibull_min, 2), "gama": (stats.gamma, 2),
              "lognormal": (stats.lognorm, 2), "log-logistica": (stats.fisk, 2)}
MIN_ESTRATO = 30


def minuto_servico(r):
    h = int(r["inicio_local"][11:13]) + (24 if r["inicio_local"][:10] != r["data_servico"] else 0)
    return h * 60 + int(r["inicio_local"][14:16])


def op_horas(r):
    d = (date.fromisoformat(r["data_servico"]) - INICIO).days
    return (d * JAN_MIN + min(max(minuto_servico(r) - JAN_INI, 0), JAN_MIN)) / 60


def ajusta_todas(x):
    out = {}
    for nome, (dist, k) in CANDIDATAS.items():
        params = dist.fit(x, floc=0)
        ll = float(np.sum(dist.logpdf(x, *params)))
        out[nome] = {"params": [float(p) for p in params], "loglik": ll, "aic": 2 * k - 2 * ll, "k": k}
    return out


def ad_stat(x, cdf):
    x = np.sort(x)
    n = len(x)
    F = np.clip(cdf(x), 1e-12, 1 - 1e-12)
    i = np.arange(1, n + 1)
    return float(-n - np.mean((2 * i - 1) * (np.log(F) + np.log(1 - F[::-1]))))


def aderencia(x, nome, params, rng, B):
    dist = CANDIDATAS[nome][0]
    cdf = lambda v, p=params: dist.cdf(v, *p)
    ks0, ad0 = stats.kstest(x, cdf).statistic, ad_stat(x, cdf)
    ks_b, ad_b = [], []
    for _ in range(B):
        xb = np.maximum(dist.rvs(*params, size=len(x), random_state=rng), 1 / 60)
        pb = dist.fit(xb, floc=0)
        cb = lambda v, p=pb: dist.cdf(v, *p)
        ks_b.append(stats.kstest(xb, cb).statistic)
        ad_b.append(ad_stat(xb, cb))
    return {"ks": round(float(ks0), 4), "p_ks_bootstrap": round(float(np.mean(np.array(ks_b) >= ks0)), 4),
            "ad": round(ad0, 3), "p_ad_bootstrap": round(float(np.mean(np.array(ad_b) >= ad0)), 4), "b": B}


def descreve(nome, ajuste):
    p = ajuste["params"]
    if nome == "exponencial":
        return {"taxa_por_hora": 1 / p[1]}  # expon.fit devolve (loc, escala)
    if nome == "weibull":
        return {"forma": p[0], "escala_h": p[2]}
    if nome == "gama":
        return {"forma": p[0], "escala_h": p[2]}
    if nome == "lognormal":
        return {"mu_log": float(np.log(p[2])), "sigma_log": p[0]}
    return {"forma": p[0], "escala_h": p[2]}


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    m = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(c - m, 4), round(c + m, 4)]


def clopper(k, n):
    lo = 0.0 if k == 0 else stats.beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k)
    return [round(float(lo), 5), round(float(hi), 5)]


def garwood(k, t):
    lo = 0.0 if k == 0 else stats.chi2.ppf(0.025, 2 * k) / 2
    hi = stats.chi2.ppf(0.975, 2 * k + 2) / 2
    return [round(lo / t, 8), round(hi / t, 8)]


def main():
    rng = np.random.default_rng(SEMENTE)
    with open("dados/derivados/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
        ev = list(csv.DictReader(f, delimiter=";"))
    with open("dados/derivados/eventos/eventos_causa_comum.csv", encoding="utf-8") as f:
        cc = list(csv.DictReader(f, delimiter=";"))
    resultado = {"semente": SEMENTE, "bootstrap_b": B, "tbf": {}, "reescala": {}, "ttr": {}, "causa_comum": {}}

    # ---------------- TBF por estrato: linha × causa, × frota (material rodante) e × condição (inverno ou resto do ano)
    # Frota: intervalos entre falhas da mesma frota. Condição: intervalos da série da linha e causa, classificados
    # pelo mês da falha que fecha o intervalo (dezembro a fevereiro = inverno).
    series = defaultdict(list)
    for r in ev:
        series[(r["linha"], r["causa"], "")].append((op_horas(r), int(r["data_servico"][5:7])))
        if r["causa"] == "MR" and r["frota"]:
            series[(r["linha"], "MR", r["frota"])].append((op_horas(r), int(r["data_servico"][5:7])))
    estratos = {}
    for (l, c, frota), pts in series.items():
        pts.sort()
        x = np.maximum(np.diff(np.array([p[0] for p in pts])), 1 / 60)
        estratos[(l, c, frota, "")] = x
        if not frota:
            inverno = np.isin(np.array([p[1] for p in pts])[1:], [12, 1, 2])
            estratos[(l, c, "", "inverno")] = x[inverno]
            estratos[(l, c, "", "resto_do_ano")] = x[~inverno]
    for (l, c, frota, cond), x in sorted(estratos.items()):
        chave = f"{l}|{c}|{frota or 'todas'}" + (f"|{cond}" if cond else "")
        if len(x) < MIN_ESTRATO:
            resultado["tbf"][chave] = {"n": int(len(x)), "herda_de": f"{l}|{c}|todas", "motivo": f"menos de {MIN_ESTRATO} intervalos"}
            continue
        aj = ajusta_todas(x)
        melhor = min(aj, key=lambda k: aj[k]["aic"])
        resultado["tbf"][chave] = {
            "n": int(len(x)), "media_h": round(float(x.mean()), 3), "cv": round(float(x.std() / x.mean()), 3),
            "aic": {k: round(v["aic"], 2) for k, v in aj.items()}, "delta_aic": {k: round(v["aic"] - aj[melhor]["aic"], 2) for k, v in aj.items()},
            "melhor": melhor, "parametros": {k: {kk: round(vv, 6) for kk, vv in descreve(k, v).items()} for k, v in aj.items()},
            "aderencia_melhor": aderencia(x, melhor, aj[melhor]["params"], rng, B),
        }
        print(f"TBF {chave}: n={len(x)} melhor={melhor}", flush=True)

    # ---------------- Teste de reescala do tempo com a taxa da spec 005
    painel = pd.read_csv("dados/derivados/modelos/painel_modelo.csv.gz", sep=";", usecols=["data_servico", "linha", "hora", "mu_MR", "mu_EF"])
    for c in ("MR", "EF"):
        for l in LINHAS:
            p = painel[painel.linha == l].sort_values(["data_servico", "hora"])
            chaves = list(zip(p.data_servico, p.hora))
            mu = p[f"mu_{c}"].to_numpy()
            acum = np.concatenate([[0.0], np.cumsum(mu)])
            pos = {k: i for i, k in enumerate(chaves)}
            Lam = []
            for r in ev:
                if r["linha"] != l or r["causa"] != c:
                    continue
                m = minuto_servico(r)
                i = pos.get((r["data_servico"], m // 60))
                if i is not None:
                    Lam.append(acum[i] + mu[i] * (m % 60) / 60)
            Lam = np.sort(np.array(Lam))
            tau = np.maximum(np.diff(Lam), 1e-6)
            ks = stats.kstest(tau, "expon")
            wb = stats.weibull_min.fit(tau, floc=0)
            bw = [stats.weibull_min.fit(rng.choice(tau, len(tau)), floc=0) for _ in range(min(B, 100))]
            ic_forma = [round(float(np.percentile([x[0] for x in bw], q)), 4) for q in (2.5, 97.5)]
            ic_escala = [round(float(np.percentile([x[2] for x in bw], q)), 4) for q in (2.5, 97.5)]
            resultado["reescala"][f"{l}|{c}"] = {
                "n": int(len(tau)), "media": round(float(tau.mean()), 4), "ks_exp1": round(float(ks.statistic), 4), "p_ks": float(ks.pvalue),
                "compativel_poisson": bool(ks.pvalue > 0.05), "weibull_reescalado": {"forma": round(float(wb[0]), 4), "escala": round(float(wb[2]), 4), "forma_ic95": ic_forma, "escala_ic95": ic_escala},
                "processo_no_simulador": "Poisson com taxa variável" if ks.pvalue > 0.05 else "renovação Weibull no tempo reescalado (taxa variável + agrupamento)",
            }
            print(f"reescala {l}|{c}: KS={ks.statistic:.3f} p={ks.pvalue:.2g} forma={wb[0]:.3f}", flush=True)

    # ---------------- TTR: massa em zero + lognormal; regressão de tempo acelerado (lognormal) com fatores
    for l in LINHAS:
        for c in ("MR", "EF"):
            d = np.array([int(r["duracao_min"]) for r in ev if r["linha"] == l and r["causa"] == c])
            pos_ = d[d > 0]
            lg = np.log(pos_)
            reamostras = [np.log(rng.choice(pos_, len(pos_))) for _ in range(B)]
            bmu = [x.mean() for x in reamostras]
            bsig = [x.std(ddof=1) for x in reamostras]
            resultado["ttr"][f"{l}|{c}"] = {
                "n": int(len(d)), "p_zero": round(float((d == 0).mean()), 4), "p_zero_ic95": wilson(int((d == 0).sum()), len(d)),
                "lognormal_positivos": {"mu_log": round(float(lg.mean()), 4), "sigma_log": round(float(lg.std(ddof=1)), 4),
                                        "sigma_log_ic95": [round(float(np.percentile(bsig, 2.5)), 4), round(float(np.percentile(bsig, 97.5)), 4)],
                                        "mu_log_ic95": [round(float(np.percentile(bmu, 2.5)), 4), round(float(np.percentile(bmu, 97.5)), 4)]},
                "media_min": round(float(d.mean()), 3), "mediana_min": float(np.median(d)), "p90_min": float(np.percentile(d, 90)),
                "max_min": int(d.max()),
            }
    dfp = pd.DataFrame([r for r in ev if int(r["duracao_min"]) > 0])
    dfp["logdur"] = np.log(dfp["duracao_min"].astype(float))
    top = dfp["causa_secundaria"].value_counts()
    dfp["sec"] = dfp["causa_secundaria"].where(dfp["causa_secundaria"].isin(top[top >= 50].index), "outra")
    dfp["evac"] = (dfp["evacuacao"].fillna("") != "").astype(float)
    hh = dfp.apply(minuto_servico, axis=1) // 60
    dfp["faixa"] = pd.cut(hh, [0, 6, 9, 15, 18, 22, 30], labels=["abertura", "pico_manha", "entrepico", "pico_tarde", "noite", "fim"])
    X = pd.get_dummies(dfp[["linha", "sec", "faixa"]].astype(str), drop_first=True, dtype=float)
    X["evacuacao"] = dfp["evac"]
    ols = sm.OLS(dfp["logdur"].to_numpy(), sm.add_constant(X)).fit()
    resultado["ttr_aft"] = {"n": int(len(dfp)), "r2": round(float(ols.rsquared), 4), "sigma": round(float(np.sqrt(ols.scale)), 4),
                            "multiplicadores": {k: {"mult": round(float(np.exp(v)), 4),
                                                    "ic95": [round(float(np.exp(ols.conf_int().loc[k, 0])), 4), round(float(np.exp(ols.conf_int().loc[k, 1])), 4)]}
                                                for k, v in ols.params.items()}}

    # ---------------- Causa comum: fator β (Clopper-Pearson), taxa por hora de operação (Garwood) e duração
    horas_op = ((date(2026, 6, 30) - INICIO).days + 1) * JAN_MIN / 60
    por_linha = defaultdict(int)
    for r in ev:
        por_linha[r["linha"]] += 1
    # β por par: todo evento que atinge as duas linhas (um evento de 3 ou 4 linhas conta em vários pares).
    # Serve para o relatório; o simulador usa os grupos abaixo, para não contar o mesmo evento mais de uma vez.
    pares = [(a, b) for i, a in enumerate(LINHAS) for b in LINHAS[i + 1:] if any({a, b} <= set(r["linhas"].split(",")) for r in cc)]
    for a, b in pares:
        sel = [r for r in cc if {a, b} <= set(r["linhas"].split(","))]
        k = len(sel)
        dur = np.array([int(r["duracao_min"]) for r in sel]) if sel else np.array([0])
        pos_ = dur[dur > 0]
        resultado["causa_comum"][f"{a}-{b}"] = {
            "eventos": k, "beta_a": round(k / (k + por_linha[a]), 5), "beta_a_ic95": clopper(k, k + por_linha[a]),
            "beta_b": round(k / (k + por_linha[b]), 5), "beta_b_ic95": clopper(k, k + por_linha[b]),
            "taxa_por_hora_op": round(k / horas_op, 8), "taxa_ic95": garwood(k, horas_op),
            "p_zero": round(float((dur == 0).mean()), 4),
            "lognormal_positivos": {"mu_log": round(float(np.log(pos_).mean()), 4) if len(pos_) else None,
                                    "sigma_log": round(float(np.log(pos_).std(ddof=1)), 4) if len(pos_) > 1 else None},
            "media_min": round(float(dur.mean()), 2),
        }
    # Grupos: o conjunto exato de linhas que cada evento parou. Taxa por grupo (Garwood); duração do conjunto
    # dos 45 eventos (a maioria dos grupos tem menos de 10 eventos).
    todas = np.array([int(r["duracao_min"]) for r in cc])
    pos_t = np.log(todas[todas > 0])
    resultado["causa_comum_duracao_conjunta"] = {
        "n": int(len(todas)), "p_zero": round(float((todas == 0).mean()), 4), "p_zero_ic95": wilson(int((todas == 0).sum()), len(todas)),
        "mu_log": round(float(pos_t.mean()), 4), "sigma_log": round(float(pos_t.std(ddof=1)), 4), "media_min": round(float(todas.mean()), 2)}
    grupos = defaultdict(list)
    for r in cc:
        grupos["-".join(sorted(r["linhas"].split(",")))].append(r)
    resultado["causa_comum_grupos"] = {
        g: {"linhas": g.split("-"), "eventos": len(rs), "taxa_por_hora_op": round(len(rs) / horas_op, 8), "taxa_ic95": garwood(len(rs), horas_op),
            "media_min_grupo": round(float(np.mean([int(r["duracao_min"]) for r in rs])), 2)}
        for g, rs in sorted(grupos.items())}
    os.makedirs("dados/derivados/modelos", exist_ok=True)
    with open("dados/derivados/modelos/distribuicoes.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=1)
    escreve_relatorio(resultado)


def escreve_relatorio(r):
    L = ["# Distribuições do tempo entre falhas, do tempo até restabelecer e da causa comum (spec 006)", "",
         f"Gerado por `pipeline/distribuicoes.py`, semente {r['semente']}, bootstrap paramétrico com {r['bootstrap_b']} reamostras. "
         "Tempo em horas de operação (20 h por dia).", "", "## Tempo entre falhas por estrato", "",
         "| Estrato (linha, causa, frota, condição) | n | Média (h) | CV | Melhor por AIC | ΔAIC Weibull | ΔAIC exponencial | KS | p KS | AD | p AD |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in r["tbf"].items():
        if "herda_de" in v:
            L.append(f"| {k} | {v['n']} | | | herda de {v['herda_de']} | | | | | | |")
            continue
        a = v["aderencia_melhor"]
        L.append(f"| {k} | {v['n']} | {v['media_h']} | {v['cv']} | {v['melhor']} | {v['delta_aic']['weibull']} | {v['delta_aic']['exponencial']} | "
                 f"{a['ks']} | {a['p_ks_bootstrap']} | {a['ad']} | {a['p_ad_bootstrap']} |")
    L += ["", "## Teste de reescala do tempo (o agrupamento é só heterogeneidade?)", "",
          "Com a taxa horária da spec 005, os intervalos reescalados deveriam seguir uma exponencial de média 1 se as falhas fossem um processo de Poisson com taxa variável.", "",
          "| Linha e causa | n | Média reescalada | KS contra Exp(1) | p | Forma da Weibull reescalada | Processo usado no simulador |", "|---|---|---|---|---|---|---|"]
    for k, v in r["reescala"].items():
        L.append(f"| {k} | {v['n']} | {v['media']} | {v['ks_exp1']} | {v['p_ks']:.2g} | {v['weibull_reescalado']['forma']} | {v['processo_no_simulador']} |")
    L += ["", "## Tempo até o serviço voltar", "", "| Linha e causa | n | Sem interrupção (IC 95%) | μ log (IC 95%) | σ log | Média (min) | p90 (min) |", "|---|---|---|---|---|---|---|"]
    for k, v in r["ttr"].items():
        ln = v["lognormal_positivos"]
        L.append(f"| {k} | {v['n']} | {v['p_zero']} ({v['p_zero_ic95'][0]}–{v['p_zero_ic95'][1]}) | {ln['mu_log']} ({ln['mu_log_ic95'][0]}–{ln['mu_log_ic95'][1]}) | "
                 f"{ln['sigma_log']} | {v['media_min']} | {v['p90_min']} |")
    a = r["ttr_aft"]
    L += ["", f"Regressão de tempo acelerado (lognormal) nas {a['n']} interrupções com duração positiva: R² {a['r2']}, σ {a['sigma']}. Multiplicadores da duração:", "",
          "| Termo | Multiplicador | IC 95% |", "|---|---|---|"]
    for k, v in a["multiplicadores"].items():
        L.append(f"| {k} | {v['mult']} | {v['ic95'][0]}–{v['ic95'][1]} |")
    L += ["", "## Causa comum: fator β por par", "",
          "Um evento que para três ou quatro linhas conta em todos os pares que ele contém. Por isso a soma dos pares passa do total de 45 eventos.", "",
          "| Par | Eventos | β da 1ª (IC 95%) | β da 2ª (IC 95%) | Taxa por hora de operação (IC 95%) | Duração média (min) |", "|---|---|---|---|---|---|"]
    for k, v in r["causa_comum"].items():
        L.append(f"| {k} | {v['eventos']} | {v['beta_a']} ({v['beta_a_ic95'][0]}–{v['beta_a_ic95'][1]}) | {v['beta_b']} ({v['beta_b_ic95'][0]}–{v['beta_b_ic95'][1]}) | "
                 f"{v['taxa_por_hora_op']:.2e} ({v['taxa_ic95'][0]:.2e}–{v['taxa_ic95'][1]:.2e}) | {v['media_min']} |")
    d = r["causa_comum_duracao_conjunta"]
    L += ["", "## Causa comum: grupos usados pelo simulador", "",
          "Cada evento entra uma vez só, no grupo exato de linhas que parou. A duração vem dos 45 eventos juntos: "
          f"sem interrupção {d['p_zero']} (IC {d['p_zero_ic95'][0]}–{d['p_zero_ic95'][1]}), lognormal com μ log {d['mu_log']} e σ log {d['sigma_log']}, média {d['media_min']} min.", "",
          "| Grupo de linhas | Eventos | Taxa por hora de operação (IC 95%) | Duração média no grupo (min) |", "|---|---|---|---|"]
    for k, v in r["causa_comum_grupos"].items():
        L.append(f"| {k} | {v['eventos']} | {v['taxa_por_hora_op']:.2e} ({v['taxa_ic95'][0]:.2e}–{v['taxa_ic95'][1]:.2e}) | {v['media_min_grupo']} |")
    open("fontes/verificacao/distribuicoes.md", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
