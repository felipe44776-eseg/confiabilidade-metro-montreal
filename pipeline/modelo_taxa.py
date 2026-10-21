"""Spec 005: modelo da taxa horária de falha por linha e causa, com a exposição como deslocamento.

Uso (da raiz do repositório): .venv/Scripts/python -I pipeline/modelo_taxa.py [--bootstrap N]
Entradas: eventos (spec 001), exposição (spec 004), painel horário de clima e eventos (spec 003).
Saídas: dados/derivados/modelos/taxa_<causa>.json, dados/derivados/modelos/painel_modelo.csv.gz (base do modelo)
        fontes/verificacao/modelo_taxa.md (relatório com os critérios da spec)
Modelo: contagem de falhas na hora ~ Poisson ou binomial negativa (NB2), log(trens-hora) como deslocamento.
Intervalos de 95% por bootstrap em blocos semanais (semana ISO do dia de operação), semente fixa.
"""
import csv
import gc
import json
import os
import sys
import time
from collections import defaultdict
from datetime import date

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import optimize, stats

SAIDA = "dados/derivados/modelos"
RELATORIO = "fontes/verificacao/modelo_taxa.md"
SEMENTE = 20261021
B = int(sys.argv[sys.argv.index("--bootstrap") + 1]) if "--bootstrap" in sys.argv else 200
FIM_KM = "2023-09-30"
ANO_BASE = "2025"  # ano completo mais recente: o simulador parte do estado atual da rede
FAIXAS = [(5, 6, "abertura"), (7, 9, "pico_manha"), (10, 15, "entrepico"), (16, 18, "pico_tarde"), (19, 22, "noite"), (23, 29, "fim")]
REFERENCIA = {"linha": "laranja", "faixa": "entrepico", "tipo_dia": "util", "estacao": "outono", "temp": "5a15", "precip": "0",
              "cond": "seco_ou_outro", "neve_solo": "0", "ano": "2019"}
CATEGORICAS = list(REFERENCIA)
INDICADORES = ["jogo", "gp_fds", "feriado", "greve"]


def faixa_de(h):
    return next(n for a, b, n in FAIXAS if a <= h <= b)


def temp_cat(t):
    if pd.isna(t):
        return "sem_dado"
    for lim, n in ((-15, "abaixo_-15"), (-5, "-15a-5"), (5, "-5a5"), (15, "5a15"), (25, "15a25")):
        if t < lim:
            return n
    return "25_ou_mais"


def precip_cat(p):
    if pd.isna(p):
        return "sem_dado"
    return "0" if p <= 0 else ("ate_1mm" if p <= 1 else "acima_1mm")


def cond_cat(c, chuva, neve, cong):
    if c == "":
        return "sem_dado"
    if cong == "1":
        return "chuva_congelante"
    if neve == "1":
        return "neve"
    if chuva == "1":
        return "chuva"
    return "seco_ou_outro"


def neve_cat(n, mes):
    if pd.isna(n):
        return "0" if 6 <= mes <= 9 else "sem_dado"
    return "0" if n < 1 else ("1a10" if n <= 10 else "acima_10")


def estacao_do_ano(mes):
    return {12: "inverno", 1: "inverno", 2: "inverno", 3: "primavera", 4: "primavera", 5: "primavera",
            6: "verao", 7: "verao", 8: "verao"}.get(mes, "outono")


def monta_painel():
    perfil = {}
    with open("dados/derivados/exposicao/perfil_horario.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            perfil[(r["linha"], r["tipo_dia"], int(r["hora"]))] = float(r["trens_hora"])
    clima = {}
    with open("dados/derivados/clima/painel_horario.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            clima.setdefault((r["data_servico"], int(r["hora_servico"])), r)
    falhas = defaultdict(int)
    fora = defaultdict(int)
    with open("dados/derivados/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            h = int(r["inicio_local"][11:13]) + (24 if r["inicio_local"][:10] != r["data_servico"] else 0)
            falhas[(r["data_servico"], r["linha"], h, r["causa"])] += 1
    linhas = []
    with open("dados/derivados/exposicao/exposicao_diaria.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            d, l, t = r["data_servico"], r["linha"], r["tipo_dia"]
            fator = float(r["fator"])
            for h in range(5, 26):
                th = perfil.get((l, t, h), 0.0)
                c = clima.get((d, h), {})
                frac = float(c.get("fracao_servico", 1.0) or 1.0)
                expo = th * fator * frac
                if expo <= 0:
                    for causa in ("MR", "EF"):
                        fora[causa] += falhas.pop((d, l, h, causa), 0)
                    continue
                mes = int(d[5:7])
                num = lambda k: pd.to_numeric(c.get(k, ""), errors="coerce")
                linhas.append({
                    "data_servico": d, "semana": date.fromisoformat(d).isocalendar()[:2], "linha": l, "hora": h, "exposicao": expo,
                    "status_exposicao": r["status"], "faixa": faixa_de(h), "tipo_dia": t, "estacao": estacao_do_ano(mes),
                    "temp": temp_cat(num("temp_c")), "precip": precip_cat(num("precip_mm")),
                    "cond": cond_cat(c.get("condicao", ""), c.get("chuva", ""), c.get("neve", ""), c.get("chuva_congelante", "")),
                    "neve_solo": neve_cat(num("neve_solo_cm"), mes), "ano": d[:4],
                    "jogo": int(c.get("jogo_canadiens", 0) or 0), "gp_fds": int(c.get("gp_f1_fim_de_semana", 0) or 0),
                    "feriado": int(c.get("feriado", 0) or 0), "greve": int(r["greve"]),
                    "y_MR": falhas.pop((d, l, h, "MR"), 0), "y_EF": falhas.pop((d, l, h, "EF"), 0),
                })
    for (d, l, h, causa), n in falhas.items():
        fora[causa] += n
    df = pd.DataFrame(linhas)
    df["semana"] = df["semana"].map(lambda s: f"{s[0]}-{s[1]:02d}")
    return df, dict(fora)


def matriz(df):
    partes = []
    for c in CATEGORICAS:
        d = pd.get_dummies(df[c].astype(str), prefix=c, prefix_sep="=", dtype=float)
        partes.append(d.drop(columns=f"{c}={REFERENCIA[c]}"))
    X = pd.concat(partes + [df[INDICADORES].astype(float)], axis=1)
    return sm.add_constant(X, has_constant="add")


def perfil_alpha(y, Xv, off, inicio):
    """α da binomial negativa (NB2) por verossimilhança perfilada: GLM com α fixo, máximo em log(α).
    Substitui o ajuste direto do statsmodels (discrete.NegativeBinomial), que não convergiu nesta base."""
    def llf(log_a):
        v = sm.GLM(y, Xv, family=sm.families.NegativeBinomial(alpha=float(np.exp(log_a))), offset=off).fit(start_params=inicio).llf
        gc.collect()  # libera o ciclo modelo↔resultado do statsmodels a cada ajuste
        return v
    grade = np.linspace(np.log(0.01), np.log(20), 12)
    valores = [llf(g) for g in grade]
    k = int(np.argmax(valores))
    lo, hi = grade[max(k - 1, 0)], grade[min(k + 1, len(grade) - 1)]
    r = optimize.minimize_scalar(lambda g: -llf(g), bounds=(lo, hi), method="bounded", options={"xatol": 1e-3})
    return float(np.exp(r.x)), float(-r.fun), [(round(float(np.exp(g)), 4), round(float(v), 2)) for g, v in zip(grade, valores)]


def ajusta(df, causa, B):
    y = df[f"y_{causa}"].to_numpy(float)
    X = matriz(df)
    colunas = list(X.columns)
    Xv = X.to_numpy(float)
    del X
    off = np.log(df["exposicao"].to_numpy(float))
    posto = int(np.linalg.matrix_rank(Xv.T @ Xv))
    if posto < Xv.shape[1]:
        raise ValueError(f"matriz de covariáveis sem posto completo: {posto} de {Xv.shape[1]} colunas")
    pois = sm.GLM(y, Xv, family=sm.families.Poisson(), offset=off).fit()
    alpha, llf_nb, grade = perfil_alpha(y, Xv, off, pois.params)
    aic_nb = 2 * (Xv.shape[1] + 1) - 2 * llf_nb
    lr = 2 * (llf_nb - pois.llf)
    p_lr = 0.5 * stats.chi2.sf(lr, 1)  # α = 0 está na fronteira: metade de qui-quadrado com 1 grau
    escolha = "binomial negativa" if (aic_nb < pois.aic and p_lr < 0.05) else "Poisson"
    familia = sm.families.NegativeBinomial(alpha=alpha) if escolha == "binomial negativa" else sm.families.Poisson()
    final = sm.GLM(y, Xv, family=familia, offset=off).fit(start_params=pois.params)
    params, bse = np.asarray(final.params), np.asarray(final.bse)
    # Bootstrap em blocos semanais (reamostra semanas inteiras com reposição), α fixo no valor estimado
    # Mesma semente nas duas causas: as mesmas semanas são sorteadas, e a razão MR/EF tem bootstrap pareado
    rng = np.random.default_rng(SEMENTE)
    unicas, idx_semana = np.unique(df["semana"].to_numpy(), return_inverse=True)
    linhas_por_semana = [np.flatnonzero(idx_semana == k) for k in range(len(unicas))]
    amostras, t0 = [], time.time()
    for b in range(B):
        sorteio = rng.integers(0, len(unicas), len(unicas))
        ii = np.concatenate([linhas_por_semana[k] for k in sorteio])
        Xb = Xv[ii]
        vazias = Xb.sum(axis=0) == 0  # nível ausente na reamostra (ex.: nenhuma hora de chuva congelante)
        fb = None
        for tentativa in range(4):  # falta de memória passageira: repete a MESMA reamostra, para o resultado não depender dela
            try:
                fb = np.asarray(sm.GLM(y[ii], Xb, family=familia, offset=off[ii]).fit(start_params=params).params, float)
                break
            except MemoryError:
                print(f"   reamostra {b}: sem memória, tentativa {tentativa + 1}", flush=True)
                gc.collect()
                time.sleep(30)
            except Exception as ex:
                print(f"   reamostra {b} descartada: {ex}", flush=True)
                break
        if fb is None:
            if tentativa == 3:
                raise MemoryError(f"reamostra {b} sem memória depois de 4 tentativas")
            amostras.append(np.full(Xv.shape[1], np.nan))  # mantém o alinhamento entre as causas
        else:
            fb[vazias] = np.nan
            amostras.append(fb)
        del Xb
        if b % 20 == 0:
            gc.collect()
    amostras = np.array(amostras)
    lo, hi = np.nanpercentile(amostras, [2.5, 97.5], axis=0)
    n_validas = np.sum(~np.isnan(amostras), axis=0)
    # Taxa-base por trem-hora de cada linha no ano-base, nas condições de referência, com IC do mesmo bootstrap
    base = {}
    for l in ("verde", "laranja", "amarela", "azul"):
        idx = [colunas.index("const")] + [colunas.index(t) for t in (f"linha={l}", f"ano={ANO_BASE}") if t in colunas]
        pt = float(np.exp(params[idx].sum()))
        bs = np.exp(amostras[:, idx].sum(axis=1))
        base[l] = {"valor": round(pt, 8), "ic95": [round(float(np.nanpercentile(bs, 2.5)), 8), round(float(np.nanpercentile(bs, 97.5)), 8)]}
    mu = np.asarray(final.fittedvalues)
    # Resíduos quantílicos aleatorizados (Dunn-Smyth) e rootograma
    if escolha == "binomial negativa":
        n_, p_ = 1 / alpha, 1 / (1 + alpha * mu)
        cdf = lambda k: stats.nbinom.cdf(k, n_, p_)
        pmf = lambda k: stats.nbinom.pmf(k, n_, p_)
    else:
        cdf = lambda k: stats.poisson.cdf(k, mu)
        pmf = lambda k: stats.poisson.pmf(k, mu)
    u = rng.uniform(cdf(y - 1), cdf(y))
    rq = stats.norm.ppf(np.clip(u, 1e-12, 1 - 1e-12))
    rootograma = [{"contagem": k if k < 3 else "3+", "observado": int((y == k).sum() if k < 3 else (y >= 3).sum()),
                   "esperado": round(float(pmf(k).sum() if k < 3 else (1 - cdf(2)).sum()), 1)} for k in range(4)]
    coef = []
    for j, nome in enumerate(colunas):
        coef.append({"termo": nome, "coef": round(float(params[j]), 6), "multiplicador": round(float(np.exp(params[j])), 6),
                     "ic95": [round(float(np.exp(lo[j])), 6), round(float(np.exp(hi[j])), 6)],
                     "ep_modelo": round(float(bse[j]), 6), "reamostras_validas": int(n_validas[j])})
    return {
        "causa": causa, "n_horas": int(len(y)), "n_falhas": int(y.sum()), "modelo_escolhido": escolha,
        "aic_poisson": round(float(pois.aic), 2), "aic_nb": round(float(aic_nb), 2), "alpha_nb": round(alpha, 6), "perfil_alpha": grade,
        "lr_dispersao": round(float(lr), 3), "p_lr_dispersao": float(p_lr), "bootstrap_b": int(len(amostras)),
        "bootstrap_segundos": round(time.time() - t0, 1), "semente": SEMENTE, "referencia": REFERENCIA, "coeficientes": coef,
        "residuos_quantilicos": {"media": round(float(rq.mean()), 4), "desvio": round(float(rq.std()), 4),
                                 "p05": round(float(np.percentile(rq, 5)), 3), "p95": round(float(np.percentile(rq, 95)), 3)},
        "rootograma": rootograma, "ano_base": ANO_BASE, "base_por_trem_hora": base,
    }, final, colunas, off, amostras


def efeito_defasagem(df, causa, familia_alpha):
    """Pergunta em aberto: a taxa depende de falha na mesma linha na hora anterior?"""
    d = df.sort_values(["linha", "data_servico", "hora"]).copy()
    y = d[f"y_{causa}"]
    total = d["y_MR"] + d["y_EF"]
    d["lag1"] = (total.groupby([d["linha"], d["data_servico"]]).shift(1).fillna(0) > 0).astype(float)
    X = matriz(d)
    X["lag1"] = d["lag1"].to_numpy()
    fam = sm.families.NegativeBinomial(alpha=familia_alpha) if familia_alpha else sm.families.Poisson()
    m = sm.GLM(y.to_numpy(float), X, family=fam, offset=np.log(d["exposicao"].to_numpy(float))).fit()
    b, se = float(m.params["lag1"]), float(m.bse["lag1"])
    return {"multiplicador": round(np.exp(b), 4), "ic95_modelo": [round(np.exp(b - 1.96 * se), 4), round(np.exp(b + 1.96 * se), 4)]}


def main():
    os.makedirs(SAIDA, exist_ok=True)
    df, fora = monta_painel()
    print(f"painel: {len(df)} horas-linha; falhas no modelo MR={df.y_MR.sum()} EF={df.y_EF.sum()}; fora do horário com serviço: {fora}", flush=True)
    resultados, amostras = {}, {}
    for causa in ("MR", "EF"):
        res, final, colunas, off, amostras[causa] = ajusta(df, causa, B)
        df[f"mu_{causa}"] = np.round(np.asarray(final.fittedvalues), 8)  # falhas esperadas na hora, usadas no teste de reescala (spec 006)
        res["falhas_fora_do_horario_com_servico"] = fora.get(causa, 0)
        res["defasagem_1h"] = efeito_defasagem(df, causa, res["alpha_nb"] if res["modelo_escolhido"] == "binomial negativa" else None)
        so_km = df[df["data_servico"] <= FIM_KM]
        y2, X2 = so_km[f"y_{causa}"].to_numpy(float), matriz(so_km)
        X2 = X2.reindex(columns=colunas, fill_value=0.0)
        X2 = X2.loc[:, (X2 != 0).any()]  # anos depois de 2023 e greves não existem no período com km real
        fam = sm.families.NegativeBinomial(alpha=res["alpha_nb"]) if res["modelo_escolhido"] == "binomial negativa" else sm.families.Poisson()
        m2 = sm.GLM(y2, X2, family=fam, offset=np.log(so_km["exposicao"].to_numpy(float))).fit()
        res["so_periodo_km_real"] = {t: round(float(np.exp(m2.params[t])), 4) for t in X2.columns if not t.startswith("ano=")}
        del X2, so_km
        gc.collect()
        resultados[causa] = res
        with open(f"{SAIDA}/taxa_{causa}.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print(f"{causa}: {res['modelo_escolhido']} | AIC Poisson {res['aic_poisson']} NB {res['aic_nb']} | alpha {res['alpha_nb']} | "
              f"B={res['bootstrap_b']} em {res['bootstrap_segundos']} s", flush=True)
    num = df.assign(inverno=(df.estacao == "inverno").astype(float))
    clima = pd.DataFrame({
        "frio_abaixo_-5": num["temp"].isin(["abaixo_-15", "-15a-5"]).astype(float), "inverno": num["inverno"],
        "neve_no_solo": num["neve_solo"].isin(["1a10", "acima_10"]).astype(float), "precipitacao": num["precip"].isin(["ate_1mm", "acima_1mm"]).astype(float),
    })
    resultados["correlacao_fatores"] = clima.corr().round(3).to_dict()
    resultados["comparacao_mr_ef"] = compara_causas(resultados, amostras)
    with open(f"{SAIDA}/comparacao_mr_ef.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(resultados["comparacao_mr_ef"], f, ensure_ascii=False, indent=1)
    escreve_relatorio(resultados, len(df))
    df.to_csv(f"{SAIDA}/painel_modelo.csv.gz", sep=";", index=False, compression={"method": "gzip", "mtime": 0})


COMPARA = [("faixa=pico_manha", "Pico da manhã"), ("faixa=pico_tarde", "Pico da tarde"), ("faixa=abertura", "Abertura (5 a 6 h)"),
           ("temp=abaixo_-15", "Abaixo de −15 °C"), ("temp=-15a-5", "−15 a −5 °C"), ("temp=-5a5", "−5 a 5 °C"),
           ("neve_solo=acima_10", "Mais de 10 cm de neve no solo"), ("precip=acima_1mm", "Precipitação acima de 1 mm/h"),
           ("cond=neve", "Neve"), ("cond=chuva_congelante", "Chuva congelante")]


def compara_causas(r, amostras):
    """Razão entre o multiplicador do material rodante e o dos equipamentos fixos, com IC do bootstrap pareado."""
    out = []
    colunas = [c["termo"] for c in r["MR"]["coeficientes"]]
    for termo, rotulo in COMPARA:
        if termo not in colunas:
            continue
        j = colunas.index(termo)
        d = amostras["MR"][:, j] - amostras["EF"][:, j]
        d = d[~np.isnan(d)]
        mr = next(c for c in r["MR"]["coeficientes"] if c["termo"] == termo)
        ef = next(c for c in r["EF"]["coeficientes"] if c["termo"] == termo)
        lo, hi = (float(np.exp(np.percentile(d, 2.5))), float(np.exp(np.percentile(d, 97.5)))) if len(d) else (float("nan"), float("nan"))
        conclusao = "eleva mais o material rodante" if lo > 1 else ("eleva mais os equipamentos fixos" if hi < 1 else "sem diferença detectável")
        out.append({"termo": termo, "fator": rotulo, "mult_MR": mr["multiplicador"], "mult_EF": ef["multiplicador"],
                    "razao_MR_EF": round(mr["multiplicador"] / ef["multiplicador"], 4), "ic95": [round(lo, 4), round(hi, 4)],
                    "reamostras": int(len(d)), "conclusao": conclusao})
    return out


def escreve_relatorio(r, n):
    def linha_coef(causa, termo):
        c = next(x for x in r[causa]["coeficientes"] if x["termo"] == termo)
        return f"{c['multiplicador']:.2f} ({c['ic95'][0]:.2f}–{c['ic95'][1]:.2f})"
    L = ["# Modelo da taxa horária de falha (spec 005)", "",
         f"Gerado por `pipeline/modelo_taxa.py`. Base: {n} horas-linha com serviço, de 2019-01-01 a 2026-06-30. "
         f"Deslocamento: log dos trens-hora (spec 004). Intervalos de 95% por bootstrap em blocos semanais, semente {SEMENTE}.", "",
         "## Poisson contra binomial negativa", "", "| Causa | Falhas no modelo | AIC Poisson | AIC binomial negativa | α | Razão de verossimilhança | p | Escolhido |",
         "|---|---|---|---|---|---|---|---|"]
    for c in ("MR", "EF"):
        x = r[c]
        L.append(f"| {c} | {x['n_falhas']} | {x['aic_poisson']} | {x['aic_nb']} | {x['alpha_nb']} | {x['lr_dispersao']} | {x['p_lr_dispersao']:.2g} | {x['modelo_escolhido']} |")
    L += ["", f"Falhas fora das horas com serviço programado (antes das 05:00 ou em horas sem trem no GTFS): MR {r['MR']['falhas_fora_do_horario_com_servico']}, "
               f"EF {r['EF']['falhas_fora_do_horario_com_servico']}. Ficam fora do modelo e são declaradas.", "",
          "## Multiplicadores principais (referência: Laranja, entrepico, dia útil, outono, 5 a 15 °C, sem precipitação, 2019)", "",
          "| Fator | Material rodante | Equipamentos fixos |", "|---|---|---|"]
    for termo, rot in (("faixa=pico_manha", "Pico da manhã"), ("faixa=pico_tarde", "Pico da tarde"), ("faixa=abertura", "Abertura (5 a 6 h)"),
                       ("temp=abaixo_-15", "Abaixo de −15 °C"), ("temp=-15a-5", "−15 a −5 °C"), ("temp=25_ou_mais", "25 °C ou mais"),
                       ("precip=acima_1mm", "Precipitação acima de 1 mm/h"), ("cond=chuva_congelante", "Chuva congelante"), ("cond=neve", "Neve"),
                       ("neve_solo=acima_10", "Mais de 10 cm de neve no solo"), ("jogo", "Jogo do Canadiens"), ("gp_fds", "Fim de semana do GP"),
                       ("feriado", "Feriado"), ("greve", "Dia de greve (por exposição)"), ("linha=verde", "Linha Verde"), ("linha=amarela", "Linha Amarela"),
                       ("linha=azul", "Linha Azul")):
        try:
            L.append(f"| {rot} | {linha_coef('MR', termo)} | {linha_coef('EF', termo)} |")
        except StopIteration:
            pass
    L += ["", "## Material rodante contra equipamentos fixos", "",
          "Razão entre os multiplicadores das duas causas. As duas usam as mesmas semanas sorteadas, então o intervalo da razão vem do bootstrap pareado.", "",
          "| Fator | MR | EF | Razão MR/EF (IC 95%) | Conclusão |", "|---|---|---|---|---|"]
    for x in r["comparacao_mr_ef"]:
        L.append(f"| {x['fator']} | {x['mult_MR']:.2f} | {x['mult_EF']:.2f} | {x['razao_MR_EF']:.2f} ({x['ic95'][0]:.2f}–{x['ic95'][1]:.2f}) | {x['conclusao']} |")
    L += ["", "## Greves", ""]
    for c in ("MR", "EF"):
        g = next(x for x in r[c]["coeficientes"] if x["termo"] == "greve")
        dentro = g["ic95"][0] <= 1 <= g["ic95"][1]
        L.append(f"- {c}: multiplicador da taxa por trem-hora em dia de greve {g['multiplicador']:.2f} (IC {g['ic95'][0]:.2f}–{g['ic95'][1]:.2f}). "
                 + ("O intervalo contém 1: a greve atua só pela exposição reduzida." if dentro else "O intervalo não contém 1: a taxa por exposição também muda em dia de greve."))
    L += ["", "## Resíduos quantílicos e rootograma", ""]
    for c in ("MR", "EF"):
        q = r[c]["residuos_quantilicos"]
        L.append(f"- {c}: média {q['media']}, desvio {q['desvio']} (esperado 0 e 1), percentis 5% e 95%: {q['p05']} e {q['p95']}.")
        L.append("  Rootograma (horas com 0, 1, 2 e 3+ falhas, observado/esperado): " +
                 ", ".join(f"{x['contagem']}: {x['observado']}/{x['esperado']}" for x in r[c]["rootograma"]))
    L += ["", "## Defasagem: falha na hora anterior (pergunta em aberto)", ""]
    for c in ("MR", "EF"):
        dd = r[c]["defasagem_1h"]
        L.append(f"- {c}: multiplicador {dd['multiplicador']} (IC do modelo {dd['ic95_modelo'][0]}–{dd['ic95_modelo'][1]}) quando houve falha técnica na mesma linha na hora anterior.")
    L += ["", "## Só o período com km real (2019-01 a 2023-09)", "", "| Fator | MR, período todo | MR, só km real | EF, período todo | EF, só km real |", "|---|---|---|---|---|"]
    for termo in ("faixa=pico_manha", "temp=abaixo_-15", "precip=acima_1mm", "linha=verde"):
        def todo(c):
            return next(x["multiplicador"] for x in r[c]["coeficientes"] if x["termo"] == termo)
        L.append(f"| {termo} | {todo('MR'):.2f} | {r['MR']['so_periodo_km_real'].get(termo, float('nan')):.2f} | {todo('EF'):.2f} | {r['EF']['so_periodo_km_real'].get(termo, float('nan')):.2f} |")
    L += ["", "## Correlação entre fatores de clima (horas com serviço)", "", "```", json.dumps(r["correlacao_fatores"], ensure_ascii=False, indent=1), "```", ""]
    os.makedirs(os.path.dirname(RELATORIO), exist_ok=True)
    open(RELATORIO, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
