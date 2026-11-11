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


REARME = ("aux_trains_sintoma_fixo", "aux_trains_sintoma_trem", "mr73", "mpm10")  # controle de trens (dedução) e frotas
OUTRAS_FIXAS = ("voie_sintoma_fixo", "voie_sintoma_trem", "aux_stations", "tcpe")


def massa_em_zero(ev):
    """Spec 020 (D62): as falhas de zero minuto vêm de parada segura com rearme rápido ou de artefato de registro?
    Proporção de duração zero e de até 1 min por fonte e por ano, com IC de Clopper–Pearson, e a leitura fixada
    na spec antes de calcular. `mr_outros` (51 falhas) fica fora das comparações."""
    n, zero, ate1 = defaultdict(int), defaultdict(int), defaultdict(int)
    for r in ev:
        d, f, a = int(r["duracao_min"]), r["fonte"], r["data_servico"][:4]
        for k in (f, (f, a)):
            n[k] += 1
            zero[k] += d == 0
            ate1[k] += d <= 1
    fontes = sorted(k for k in n if isinstance(k, str))
    anos = sorted({k[1] for k in n if isinstance(k, tuple)})
    comparadas = [f for f in fontes if f in REARME + OUTRAS_FIXAS]

    def homogeneidade(tabela):
        tabela = np.array(tabela, float)
        tabela = tabela[tabela.sum(axis=1) > 0]
        if len(tabela) < 2 or (tabela.sum(axis=0) == 0).any():
            return None
        return float(stats.chi2_contingency(tabela)[1])

    saida = {"fontes": {}, "anos": anos, "fontes_comparadas": comparadas}
    for f in fontes:
        por_ano = {a: {"n": n[(f, a)], "p_zero": round(zero[(f, a)] / n[(f, a)], 4), "ic95": clopper(zero[(f, a)], n[(f, a)])} for a in anos if n[(f, a)]}
        saida["fontes"][f] = {
            "n": n[f], "p_zero": round(zero[f] / n[f], 4), "p_zero_ic95": clopper(zero[f], n[f]),
            "p_ate_1min": round(ate1[f] / n[f], 4), "p_ate_1min_ic95": clopper(ate1[f], n[f]), "por_ano": por_ano,
            "p_homogeneo_entre_anos": homogeneidade([[zero[(f, a)], n[(f, a)] - zero[(f, a)]] for a in anos])}
    p_fontes = homogeneidade([[zero[f], n[f] - zero[f]] for f in comparadas])
    saida["p_homogeneo_entre_fontes"] = p_fontes
    # leitura fixada na spec 020 antes de calcular
    pz = {f: zero[f] / n[f] for f in comparadas}
    rearme_f = [f for f in REARME if f in pz]
    outras_f = [f for f in OUTRAS_FIXAS if f in pz]
    estaveis = all((saida["fontes"][f]["p_homogeneo_entre_anos"] or 1.0) >= 0.01 for f in rearme_f)
    rearme = p_fontes is not None and p_fontes < 0.01 and min(pz[f] for f in rearme_f) > max(pz[f] for f in outras_f) and estaveis
    saltos = {}
    for a in anos:
        acima = [f for f in comparadas if a in saida["fontes"][f]["por_ano"] and saida["fontes"][f]["por_ano"][a]["ic95"][0] > pz[f]]
        abaixo = [f for f in comparadas if a in saida["fontes"][f]["por_ano"] and saida["fontes"][f]["por_ano"][a]["ic95"][1] < pz[f]]
        if max(len(acima), len(abaixo)) * 2 >= len(comparadas):
            saltos[a] = {"acima": acima, "abaixo": abaixo}
    registro = (p_fontes is not None and p_fontes >= 0.01) or bool(saltos)
    saida["saltos_comuns"] = saltos
    saida["rearme_estavel_entre_anos"] = estaveis
    saida["leitura"] = ("os dois padrões" if rearme and registro else "parada segura com rearme rápido" if rearme
                        else "artefato de registro" if registro else "inconclusiva")
    return saida


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
    # ---------------- Spec 018: renovação e duração por linha × fonte (estrato com menos de MIN_ESTRATO herda da rede)
    fontes = sorted({r["fonte"] for r in ev})
    pf = pd.read_csv("dados/derivados/modelos/painel_modelo.csv.gz", sep=";", usecols=["data_servico", "linha", "hora"] + [f"mu_{f}" for f in fontes])
    resultado["reescala_fonte"], resultado["ttr_fonte"] = {}, {}

    def intervalos(l, f):
        p = pf[pf.linha == l].sort_values(["data_servico", "hora"])
        mu = p[f"mu_{f}"].to_numpy()
        if mu.sum() <= 0:
            return None
        acum = np.concatenate([[0.0], np.cumsum(mu)])
        pos = {k: i for i, k in enumerate(zip(p.data_servico, p.hora))}
        lam = []
        for r in ev:
            if r["linha"] == l and r["fonte"] == f:
                m = minuto_servico(r)
                i = pos.get((r["data_servico"], m // 60))
                if i is not None:
                    lam.append(acum[i] + mu[i] * (m % 60) / 60)
        return np.maximum(np.diff(np.sort(np.array(lam))), 1e-6) if len(lam) > 1 else np.array([])

    def weibull(tau):
        wb = stats.weibull_min.fit(tau, floc=0)
        bw = [stats.weibull_min.fit(rng.choice(tau, len(tau)), floc=0) for _ in range(min(B, 100))]
        return {"forma": round(float(wb[0]), 4), "escala": round(float(wb[2]), 4),
                "forma_ic95": [round(float(np.percentile([x[0] for x in bw], q)), 4) for q in (2.5, 97.5)],
                "escala_ic95": [round(float(np.percentile([x[2] for x in bw], q)), 4) for q in (2.5, 97.5)]}

    for f in fontes:
        taus = {l: intervalos(l, f) for l in LINHAS}
        juntos = np.concatenate([t for t in taus.values() if t is not None and len(t)])
        rede_w = weibull(juntos) if len(juntos) >= MIN_ESTRATO else None
        dur_rede = np.array([int(r["duracao_min"]) for r in ev if r["fonte"] == f])
        for l in LINHAS:
            tau = taus[l]
            if tau is None:
                continue  # a fonte não existe nesta linha (frota que não roda nela)
            proprio = len(tau) >= MIN_ESTRATO
            w = weibull(tau) if proprio else rede_w
            resultado["reescala_fonte"][f"{l}|{f}"] = {
                "n": int(len(tau)), "weibull_reescalado": w or {"forma": 1.0, "escala": 1.0, "forma_ic95": None, "escala_ic95": None},
                "origem": "linha" if proprio else ("rede (estrato pequeno)" if w else "Poisson (sem dados para a forma)")}
            d = np.array([int(r["duracao_min"]) for r in ev if r["linha"] == l and r["fonte"] == f])
            base_d = d if (d > 0).sum() >= MIN_ESTRATO else dur_rede
            pos_ = base_d[base_d > 0]
            lg = np.log(pos_) if len(pos_) else np.array([0.0])
            resultado["ttr_fonte"][f"{l}|{f}"] = {
                "n": int(len(d)), "p_zero": round(float((base_d == 0).mean()), 4), "p_zero_ic95": wilson(int((base_d == 0).sum()), len(base_d)),
                "lognormal_positivos": {"mu_log": round(float(lg.mean()), 4), "sigma_log": round(float(lg.std(ddof=1)) if len(lg) > 1 else 1.0, 4)},
                "positivos": sorted(int(x) for x in pos_), "origem": "linha" if base_d is d else "rede (estrato pequeno)"}
        print(f"fonte {f}: forma na rede {rede_w['forma'] if rede_w else '—'}", flush=True)

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
    # Spec 018: β com o denominador da família de cada evento (40 dos 45 eventos são de equipamentos fixos).
    por_linha_fam = defaultdict(int)
    for r in ev:
        por_linha_fam[(r["linha"], r["causa"])] += 1
    resultado["causa_comum_beta_familia"] = {}
    for a, b in pares:
        for fam_ in ("MR", "EF"):
            k = sum(1 for r in cc if {a, b} <= set(r["linhas"].split(",")) and r["causa"] == fam_)
            if k:
                resultado["causa_comum_beta_familia"][f"{a}-{b}|{fam_}"] = {
                    "eventos": k, "beta_a": round(k / (k + por_linha_fam[(a, fam_)]), 5), "beta_a_ic95": clopper(k, k + por_linha_fam[(a, fam_)]),
                    "beta_b": round(k / (k + por_linha_fam[(b, fam_)]), 5), "beta_b_ic95": clopper(k, k + por_linha_fam[(b, fam_)])}
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
    resultado["massa_em_zero"] = massa_em_zero(ev)  # spec 020, D62
    os.makedirs("dados/derivados/modelos", exist_ok=True)
    with open("dados/derivados/modelos/distribuicoes.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=1)
    escreve_relatorio(resultado)


def chave(k):
    """Chave "linha|causa|..." legível numa célula de tabela Markdown (o `|` partiria a célula)."""
    return k.replace("|", " · ")


def escreve_relatorio(r):
    L = ["# Distribuições do tempo entre falhas, do tempo até restabelecer e da causa comum (spec 006)", "",
         f"Gerado por `pipeline/distribuicoes.py`, semente {r['semente']}, bootstrap paramétrico com {r['bootstrap_b']} reamostras. "
         "Tempo em horas de operação (20 h por dia).", "", "## Tempo entre falhas por estrato", "",
         "| Estrato (linha, causa, frota, condição) | n | Média (h) | CV | Melhor por AIC | ΔAIC Weibull | ΔAIC exponencial | KS | p KS | AD | p AD |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in r["tbf"].items():
        if "herda_de" in v:
            L.append(f"| {chave(k)} | {v['n']} | | | herda de {chave(v['herda_de'])} | | | | | | |")
            continue
        a = v["aderencia_melhor"]
        L.append(f"| {chave(k)} | {v['n']} | {v['media_h']} | {v['cv']} | {v['melhor']} | {v['delta_aic']['weibull']} | {v['delta_aic']['exponencial']} | "
                 f"{a['ks']} | {a['p_ks_bootstrap']} | {a['ad']} | {a['p_ad_bootstrap']} |")
    L += ["", "## Teste de reescala do tempo (o agrupamento é só heterogeneidade?)", "",
          "Com a taxa horária da spec 005, os intervalos reescalados deveriam seguir uma exponencial de média 1 se as falhas fossem um processo de Poisson com taxa variável.", "",
          "| Linha e causa | n | Média reescalada | KS contra Exp(1) | p | Forma da Weibull reescalada | Processo usado no simulador |", "|---|---|---|---|---|---|---|"]
    for k, v in r["reescala"].items():
        L.append(f"| {chave(k)} | {v['n']} | {v['media']} | {v['ks_exp1']} | {v['p_ks']:.2g} | {v['weibull_reescalado']['forma']} | {v['processo_no_simulador']} |")
    L += ["", "## Tempo até o serviço voltar", "", "| Linha e causa | n | Sem interrupção (IC 95%) | μ log (IC 95%) | σ log | Média (min) | p90 (min) |", "|---|---|---|---|---|---|---|"]
    for k, v in r["ttr"].items():
        ln = v["lognormal_positivos"]
        L.append(f"| {chave(k)} | {v['n']} | {v['p_zero']} ({v['p_zero_ic95'][0]}–{v['p_zero_ic95'][1]}) | {ln['mu_log']} ({ln['mu_log_ic95'][0]}–{ln['mu_log_ic95'][1]}) | "
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
    L += relatorio_por_fonte(r)
    L += relatorio_massa_em_zero(r["massa_em_zero"])
    open("fontes/verificacao/distribuicoes.md", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")


def relatorio_por_fonte(r):
    """Spec 018: β da causa comum pelo denominador da família, e renovação e duração de cada linha × fonte."""
    n = lambda x, c=4: f"{x:.{c}f}".replace(".", ",")
    L = ["", "## Causa comum: fator β pelo denominador da família (spec 018)", "",
         "O evento conta na família da sua fonte (trem ou fixo), e o β divide pelas falhas daquela família na linha. 40 dos 45 eventos são de equipamento fixo.", "",
         "| Par e família | Eventos | β da 1ª (IC 95%) | β da 2ª (IC 95%) |", "|---|---|---|---|"]
    for k, v in r["causa_comum_beta_familia"].items():
        L.append(f"| {k.replace('|', ' · ')} | {v['eventos']} | {n(v['beta_a'])} ({n(v['beta_a_ic95'][0])}–{n(v['beta_a_ic95'][1])}) | "
                 f"{n(v['beta_b'])} ({n(v['beta_b_ic95'][0])}–{n(v['beta_b_ic95'][1])}) |")
    L += ["", "## Renovação e duração por linha × fonte (spec 018)", "",
          f"Forma da Weibull no tempo reescalado pela taxa da fonte (spec 018) e duração (sem interrupção e média quando para). Herda da mesma fonte na rede "
          f"(colunas de origem): a renovação, o estrato com menos de {MIN_ESTRATO} intervalos; a duração, o estrato com menos de {MIN_ESTRATO} durações positivas.", "",
          "| Linha · fonte | Falhas | Forma (IC 95%) | Origem da renovação | Sem interrupção (IC 95%) | Média quando para (min) | Origem da duração |", "|---|---|---|---|---|---|---|"]
    for k, v in r["reescala_fonte"].items():
        t = r["ttr_fonte"].get(k, {})
        w = v["weibull_reescalado"]
        pos = t.get("positivos") or []
        media = n(sum(pos) / len(pos), 1) if pos else "—"
        pz = f"{n(t['p_zero'], 3)} ({n(t['p_zero_ic95'][0], 3)}–{n(t['p_zero_ic95'][1], 3)})" if t else "—"
        L.append(f"| {k.replace('|', ' · ')} | {v['n']} | {n(w['forma'])} ({n(w['forma_ic95'][0])}–{n(w['forma_ic95'][1])}) | {v['origem']} | {pz} | {media} | {t.get('origem', '—')} |")
    return L


def relatorio_massa_em_zero(m):
    pct = lambda x: f"{100 * x:.1f}".replace(".", ",")
    ic = lambda c: f"{pct(c[0])}–{pct(c[1])}"
    pv = lambda p: "—" if p is None else "< 0,0001" if p < 1e-4 else f"{p:.2g}".replace(".", ",")
    L = ["", "## Falhas de zero minuto por fonte e ano (spec 020, D62)", "",
         "A massa em zero vem de parada segura com rearme rápido (Almeida Jr. et al., 2008) ou de artefato de registro? Proporções em %, com IC 95% de "
         "Clopper–Pearson; p do qui-quadrado de homogeneidade. A leitura foi fixada na spec 020 antes de calcular:",
         "- **parada segura com rearme rápido:** fontes heterogêneas (p < 0,01), a menor proporção entre controle de trens e frotas acima da maior entre via, "
         "estações e TCPE, e essas quatro fontes estáveis entre os anos;",
         "- **artefato de registro:** fontes homogêneas, ou um ano em que pelo menos metade das fontes tem o IC inteiro acima ou abaixo da própria proporção.",
         "", f"**Leitura: {m['leitura']}.** Homogeneidade entre as fontes comparadas: p {pv(m['p_homogeneo_entre_fontes']) if pv(m['p_homogeneo_entre_fontes']).startswith('<') else '= ' + pv(m['p_homogeneo_entre_fontes'])}. "
         f"Controle de trens e frotas estáveis entre os anos: {'sim' if m['rearme_estavel_entre_anos'] else 'não'}. "
         f"Anos com salto comum: {', '.join(m['saltos_comuns']) or 'nenhum'}. \"Controle de trens\" (Service aux trains) é dedução até a resposta da STM.", "",
         "| Fonte | n | Duração zero (IC 95%) | Até 1 min (IC 95%) | p entre anos |", "|---|---|---|---|---|"]
    for f, v in m["fontes"].items():
        L.append(f"| {f} | {v['n']} | {pct(v['p_zero'])} ({ic(v['p_zero_ic95'])}) | {pct(v['p_ate_1min'])} ({ic(v['p_ate_1min_ic95'])}) | {pv(v['p_homogeneo_entre_anos'])} |")
    L += ["", "Duração zero por ano (%):", "", "| Fonte | " + " | ".join(m["anos"]) + " |", "|---|" + "---|" * len(m["anos"])]
    for f, v in m["fontes"].items():
        L.append(f"| {f} | " + " | ".join(pct(v["por_ano"][a]["p_zero"]) + f" ({v['por_ano'][a]['n']})" if a in v["por_ano"] else "" for a in m["anos"]) + " |")
    L += ["", "Entre parênteses, o número de falhas da fonte no ano. `mr_outros` fica fora das comparações; o salto de 2024 da via com sintoma de trem já era conhecido (D56)."]
    return L


if __name__ == "__main__":
    main()
