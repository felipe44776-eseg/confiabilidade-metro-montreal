"""Spec 012: validação contra o histórico. Ajusta com dados até o corte e prevê cada linha e mês do período de teste.

Uso (da raiz do repositório): .venv/Scripts/python -I pipeline/backtest.py [--bootstrap N]
Entradas: as mesmas da spec 005 (eventos, exposição, clima e eventos externos) e as durações da spec 001.
Saídas: dados/derivados/modelos/backtest.json, fontes/verificacao/backtest.md e fontes/verificacao/backtest_pit*.svg

Processo previsto (o mesmo do simulador, specs 006 e 007, implementado aqui de forma independente):
  taxa horária do modelo da spec 005 ajustado só no período de treino, com o clima e a oferta observados no teste;
  falhas como renovação Weibull no tempo reescalado Λ(t), forma ajustada no treino e escala com média 1;
  incerteza dos parâmetros: cada caminho usa um vetor de coeficientes do bootstrap em blocos semanais.
Greve atua só pela exposição. O efeito do ano no teste segue a regra de cada versão (VERSOES).
"""
import csv
import gc
import json
import math
import os
import sys
import time
from collections import defaultdict
from datetime import date

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelo_taxa as mt  # noqa: E402

SEMENTE = 20261022
B = int(sys.argv[sys.argv.index("--bootstrap") + 1]) if "--bootstrap" in sys.argv else 100
CAMINHOS_POR_VETOR = 20
LINHAS = ("verde", "laranja", "amarela", "azul")
MESES_GREVE = {"2025-06", "2025-09", "2025-10", "2025-11"}
SAIDA = "dados/derivados/modelos/backtest.json"
# A e B: definidas antes de ver o teste (pré-registradas). C e D: registradas em 2026-10-21, depois de ver A:
# o efeito do ano passa a ser sorteado entre os anos do treino, e a regra é testada de novo num período diferente (D).
VERSOES = {
    "A": {"corte": "2024-12-31", "teste": ("2025-01-01", "2026-06-30"), "ano": ("persistencia", "2024"), "pre_registrada": True,
          "descricao": "treino até 2024-12; no teste, efeito do ano de 2024"},
    "B": {"corte": "2023-09-30", "teste": ("2025-01-01", "2026-06-30"), "ano": ("persistencia", "2023"), "pre_registrada": True,
          "descricao": "treino até 2023-09 (só exposição medida); no teste, efeito do ano de 2023"},
    "C": {"corte": "2024-12-31", "teste": ("2025-01-01", "2026-06-30"), "ano": ("sorteio", None), "pre_registrada": False,
          "descricao": "treino até 2024-12; efeito do ano sorteado entre 2019 e 2024 a cada caminho"},
    "D": {"corte": "2022-12-31", "teste": ("2023-01-01", "2024-06-30"), "ano": ("sorteio", None), "pre_registrada": False,
          "descricao": "reteste da regra C em outro período: treino até 2022-12, teste de 2023-01 a 2024-06"},
}


def desenho(df, colunas=None):
    """Matriz de covariáveis; com `colunas`, alinha às colunas do treino (nível ausente = 0)."""
    partes = [pd.get_dummies(df[c].astype(str), prefix=c, prefix_sep="=", dtype=float) for c in mt.CATEGORICAS]
    X = pd.concat(partes + [df[mt.INDICADORES].astype(float)], axis=1)
    X.insert(0, "const", 1.0)
    if colunas is not None:
        return X.reindex(columns=colunas, fill_value=0.0)
    X = X.drop(columns=[f"{c}={mt.REFERENCIA[c]}" for c in mt.CATEGORICAS if f"{c}={mt.REFERENCIA[c]}" in X.columns])
    return X.loc[:, (X != 0).any()]  # ex.: greve não existe no treino


def ajusta_com_bootstrap(treino, causa, B, rng):
    X = desenho(treino)
    colunas, Xv = list(X.columns), X.to_numpy(float)
    y, off = treino[f"y_{causa}"].to_numpy(float), np.log(treino["exposicao"].to_numpy(float))
    pois = sm.GLM(y, Xv, family=sm.families.Poisson(), offset=off).fit()
    alpha, _, _ = mt.perfil_alpha(y, Xv, off, pois.params)
    fam = sm.families.NegativeBinomial(alpha=alpha)
    final = sm.GLM(y, Xv, family=fam, offset=off).fit(start_params=pois.params)
    beta = np.asarray(final.params, float)
    unicas, idx = np.unique(treino["semana"].to_numpy(), return_inverse=True)
    por_semana = [np.flatnonzero(idx == k) for k in range(len(unicas))]
    vetores = []
    for b in range(B):
        ii = np.concatenate([por_semana[k] for k in rng.integers(0, len(unicas), len(unicas))])
        Xb = Xv[ii]
        for tentativa in range(4):  # falta de memória passageira: repete a MESMA reamostra
            try:
                bb = np.asarray(sm.GLM(y[ii], Xb, family=fam, offset=off[ii]).fit(start_params=beta).params, float)
                vazias = Xb.sum(axis=0) == 0
                bb[vazias] = beta[vazias]  # nível ausente na reamostra: usa a estimativa pontual
                vetores.append(bb)
                break
            except MemoryError:
                if tentativa == 3:
                    raise
                print(f"   reamostra {b}: sem memória, tentativa {tentativa + 1}", flush=True)
                gc.collect()
                time.sleep(30)
            except Exception as ex:
                print(f"   reamostra {b} descartada: {ex}", flush=True)
                break
        del Xb
        gc.collect()  # o statsmodels cria ciclos modelo↔resultado: sem isto, cada reamostra (≈60 MB) fica presa na memória
    return colunas, np.array(vetores), alpha, np.asarray(final.fittedvalues)


def minuto_servico(inicio_local, data_servico):
    h = int(inicio_local[11:13]) + (24 if inicio_local[:10] != data_servico else 0)
    return h * 60 + int(inicio_local[14:16])


def forma_renovacao(painel_l, mu_l, eventos_l):
    """Forma da Weibull dos intervalos reescalados no treino (mesmo método da spec 006)."""
    pos = {k: i for i, k in enumerate(zip(painel_l["data_servico"], painel_l["hora"]))}
    acum = np.concatenate([[0.0], np.cumsum(mu_l)])
    lam = []
    for d, ini in eventos_l:
        m = minuto_servico(ini, d)
        i = pos.get((d, m // 60))
        if i is not None:
            lam.append(acum[i] + mu_l[i] * (m % 60) / 60)
    tau = np.maximum(np.diff(np.sort(lam)), 1e-6)
    return float(stats.weibull_min.fit(tau, floc=0)[0])


def renovacao(T, k, rng):
    """Um caminho de renovação Weibull(k, média 1) em [0, T], com início estacionário."""
    escala = 1 / math.gamma(1 + 1 / k)
    # início estacionário: intervalo com viés de tamanho (X^k/escala^k ~ Gama(1 + 1/k)) e posição uniforme nele
    t = [escala * rng.gamma(1 + 1 / k) ** (1 / k) * rng.uniform()]
    bloco = int(T * 1.3) + 50
    while t[-1] < T:
        t = np.concatenate([t, t[-1] + np.cumsum(escala * rng.weibull(k, bloco))])
    t = np.asarray(t)
    return t[t < T]


def ttr_treino(ev_treino, l, c):
    """Massa em zero e amostra das durações positivas do treino (o simulador sorteia da amostra observada)."""
    d = np.array([int(r["duracao_min"]) for r in ev_treino if r["linha"] == l and r["causa"] == c])
    return float((d == 0).mean()), d[d > 0].astype(float)


def cobertura(lista):
    k, n = sum(c["dentro"] for c in lista), len(lista)
    if n == 0:
        return None
    lo = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    hi = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return {"dentro": k, "casos": n, "cobertura": round(k / n, 4), "ic95": [round(float(lo), 4), round(float(hi), 4)]}


def avalia(nome, cfg, painel, ev, cc, rng):
    corte, (ini, fim), (modo_ano, ano_fixo) = cfg["corte"], cfg["teste"], cfg["ano"]
    treino = painel[painel["data_servico"] <= corte].copy()
    anos_treino = sorted(treino["ano"].unique())
    teste = painel[(painel["data_servico"] >= ini) & (painel["data_servico"] <= fim)].copy()
    teste["ano"] = ano_fixo if modo_ano == "persistencia" else mt.REFERENCIA["ano"]  # no sorteio, o ano entra por caminho
    teste = teste.sort_values(["linha", "data_servico", "hora"]).reset_index(drop=True)
    teste["mes"] = teste["data_servico"].str[:7]
    meses = sorted(teste["mes"].unique())
    ano_min = ini[:4]  # minutos parados: primeiro ano do teste
    ev_treino = [r for r in ev if r["data_servico"] <= corte]
    contagens = {c: {l: [] for l in LINHAS} for c in ("MR", "EF")}
    minutos = {c: {l: [] for l in LINHAS} for c in ("MR", "EF")}
    formas, n_vetores = {}, {}
    for causa in ("MR", "EF"):
        colunas, vetores, alpha, mu_treino = ajusta_com_bootstrap(treino, causa, B, rng)
        n_vetores[causa] = len(vetores)  # reamostras válidas (as descartadas não contam)
        print(f"{nome} {causa}: alpha={alpha:.3f}, {len(vetores)} vetores", flush=True)
        Xt = desenho(teste, colunas).to_numpy(float)
        off_t = np.log(teste["exposicao"].to_numpy(float))
        j_ano = {a: (colunas.index(f"ano={a}") if f"ano={a}" in colunas else None) for a in anos_treino}
        treino_ord = treino.assign(mu=mu_treino).sort_values(["linha", "data_servico", "hora"])
        for l in LINHAS:
            tl = treino_ord[treino_ord["linha"] == l]
            k = forma_renovacao(tl, tl["mu"].to_numpy(), [(r["data_servico"], r["inicio_local"]) for r in ev_treino if r["linha"] == l and r["causa"] == causa])
            formas[f"{l}|{causa}"] = round(k, 4)
            p0, positivos = ttr_treino(ev_treino, l, causa)
            sel = (teste["linha"] == l).to_numpy()
            mes_idx = np.searchsorted(meses, teste.loc[sel, "mes"].to_numpy())
            no_ano_min = teste.loc[sel, "data_servico"].str.startswith(ano_min).to_numpy()
            for v in vetores:
                eta = Xt[sel] @ v + off_t[sel]
                for _ in range(CAMINHOS_POR_VETOR):
                    if modo_ano == "sorteio":
                        j = j_ano[anos_treino[rng.integers(len(anos_treino))]]
                        acum = np.cumsum(np.exp(eta + (v[j] if j is not None else 0.0)))
                    else:
                        acum = np.cumsum(np.exp(eta))
                    hora = np.searchsorted(acum, renovacao(acum[-1], k, rng), side="right")
                    contagens[causa][l].append(np.bincount(mes_idx[hora], minlength=len(meses)))
                    n1 = int(no_ano_min[hora].sum())
                    dur = np.where(rng.uniform(size=n1) < p0, 0.0, rng.choice(positivos, n1))
                    minutos[causa][l].append(float(dur.sum()))
    # MR + EF caminho a caminho; se o bootstrap descartou reamostras numa causa, corta no menor número de caminhos
    n = min(len(contagens[c][l]) for c in ("MR", "EF") for l in LINHAS)
    total = {l: np.array(contagens["MR"][l][:n]) + np.array(contagens["EF"][l][:n]) for l in LINHAS}
    m_tec = {l: np.array(minutos["MR"][l][:n]) + np.array(minutos["EF"][l][:n]) for l in LINHAS}
    # causa comum no primeiro ano do teste: Poisson com a taxa do treino por hora de operação, duração do treino
    horas_treino = ((date.fromisoformat(corte) - date(2019, 1, 1)).days + 1) * 20
    cc_min = {l: np.zeros(n) for l in LINHAS}
    for l in LINHAS:
        sel = [r for r in cc if r["data_servico"] <= corte and l in r["linhas"].split(",")]
        if not sel:
            continue
        d = np.array([int(r["duracao_min"]) for r in sel])
        p0 = float((d == 0).mean())
        positivos = d[d > 0].astype(float)
        ks = rng.poisson(len(sel) / horas_treino * 365 * 20, n)
        cc_min[l] = np.array([np.sum(np.where(rng.uniform(size=k) < p0, 0, rng.choice(positivos, k))) for k in ks])

    obs = teste.groupby(["linha", "mes"])[["y_MR", "y_EF"]].sum()
    casos = []
    for l in LINHAS:
        for j, m in enumerate(meses):
            y = int(obs.loc[(l, m)].sum())
            s = total[l][:, j]
            q05, q50, q95 = np.percentile(s, [5, 50, 95])
            F = lambda v: float(np.mean(s <= v))
            pit = F(y - 1) + rng.uniform() * (F(y) - F(y - 1))
            casos.append({"linha": l, "mes": m, "observado": y, "mediana": float(q50), "ip90": [float(q05), float(q95)],
                          "dentro": bool(q05 <= y <= q95), "acima": bool(y > q95), "pit": round(pit, 4), "greve": m in MESES_GREVE})
    observado_min = defaultdict(float)
    horas_teste = set(zip(teste["data_servico"], teste["hora"]))
    for r in ev:
        if r["data_servico"].startswith(ano_min) and (r["data_servico"], minuto_servico(r["inicio_local"], r["data_servico"]) // 60) in horas_teste:
            observado_min[r["linha"]] += int(r["duracao_min"])
    for r in cc:
        if r["data_servico"].startswith(ano_min):
            for l in r["linhas"].split(","):
                observado_min[l] += int(r["duracao_min"])
    minutos_ano = {}
    for l in LINHAS:
        s = m_tec[l] + cc_min[l]
        lo, hi = np.percentile(s, [2.5, 97.5])
        minutos_ano[l] = {"observado": observado_min[l], "mediana": round(float(np.median(s)), 1), "ic95": [round(float(lo), 1), round(float(hi), 1)],
                          "dentro": bool(lo <= observado_min[l] <= hi)}
    pits = np.array([c["pit"] for c in casos])
    return {
        **{k: cfg[k] for k in ("corte", "teste", "pre_registrada", "descricao")}, "regra_ano": modo_ano, "ano_fixo": ano_fixo,
        "vetores_bootstrap": min(n_vetores.values()), "caminhos_por_vetor": CAMINHOS_POR_VETOR, "caminhos": n,
        "forma_renovacao_treino": formas, "cobertura_total": cobertura(casos),
        "cobertura_sem_greve": cobertura([c for c in casos if not c["greve"]]), "cobertura_meses_greve": cobertura([c for c in casos if c["greve"]]),
        "cobertura_por_linha": {l: cobertura([c for c in casos if c["linha"] == l]) for l in LINHAS},
        "fora_acima": sum(c["acima"] for c in casos), "fora_abaixo": sum(not c["dentro"] and not c["acima"] for c in casos),
        "pit_histograma_10": np.histogram(pits, bins=10, range=(0, 1))[0].tolist(), "pit_ks_p": float(stats.kstest(pits, "uniform").pvalue),
        "ano_minutos": ano_min, "minutos_ano": minutos_ano, "casos": casos,
    }


def svg_pit(hist, titulo):
    w, h, m = 520, 260, 40
    n = sum(hist)
    esperado = n / len(hist)
    topo = max(max(hist), esperado) * 1.15
    bw = (w - 2 * m) / len(hist)
    barras = "".join(
        f'<rect x="{m + i * bw + 2:.1f}" y="{h - m - v / topo * (h - 2 * m):.1f}" width="{bw - 4:.1f}" height="{v / topo * (h - 2 * m):.1f}" rx="2" fill="#4a6fa5"/>'
        f'<text x="{m + i * bw + bw / 2:.1f}" y="{h - m - v / topo * (h - 2 * m) - 4:.1f}" font-size="11" text-anchor="middle" fill="#333">{v}</text>'
        for i, v in enumerate(hist))
    y_esp = h - m - esperado / topo * (h - 2 * m)
    eixo = "".join(f'<text x="{m + i * bw:.1f}" y="{h - m + 14}" font-size="10" text-anchor="middle" fill="#555">{i / 10:.1f}</text>' for i in range(11))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="sans-serif">'
            f'<rect width="{w}" height="{h}" fill="#fff"/><text x="{m}" y="20" font-size="13" fill="#111">{titulo}</text>'
            f'<line x1="{m}" y1="{h - m}" x2="{w - m}" y2="{h - m}" stroke="#999"/>{barras}'
            f'<line x1="{m}" y1="{y_esp:.1f}" x2="{w - m}" y2="{y_esp:.1f}" stroke="#c0392b" stroke-dasharray="5 4"/>'
            f'<text x="{w - m}" y="{y_esp - 5:.1f}" font-size="10" text-anchor="end" fill="#c0392b">uniforme: {esperado:.1f} por faixa</text>{eixo}</svg>')


def relatorio(r):
    pct = lambda x: f"{x:.1%}".replace(".", ",")
    cob = lambda c: "—" if c is None else f"{pct(c['cobertura'])} ({c['dentro']}/{c['casos']})"
    L = ["# Validação contra o histórico (spec 012)", "",
         f"Gerado por `pipeline/backtest.py`, semente {SEMENTE}, {B} vetores do bootstrap × {CAMINHOS_POR_VETOR} caminhos. "
         "Conta as falhas técnicas (material rodante e equipamentos fixos) nas horas com serviço programado.", "",
         "O processo previsto é o mesmo do simulador: taxa horária do modelo da spec 005 ajustado só no treino, com o clima e a oferta observados no teste, "
         "e falhas como renovação Weibull no tempo reescalado (spec 006). As durações saem da amostra observada no treino, como no simulador. A incerteza dos parâmetros entra pelo bootstrap em blocos semanais.", "",
         "## Cobertura do intervalo de predição de 90%", "", "Critério da spec: entre 80% e 98% dos casos linha × mês, no corte em 2024-12 (versão A).", "",
         "| Versão | Regra | Pré-registrada | Total (IC 95%) | Sem greve | Meses de greve | Fora acima / abaixo | Entre 80% e 98% |", "|---|---|---|---|---|---|---|---|"]
    for v, x in r.items():
        t = x["cobertura_total"]
        L.append(f"| {v} | {x['descricao']} | {'sim' if x['pre_registrada'] else 'não (2026-10-21)'} | {pct(t['cobertura'])} ({t['dentro']}/{t['casos']}; "
                 f"{pct(t['ic95'][0])}–{pct(t['ic95'][1])}) | {cob(x['cobertura_sem_greve'])} | {cob(x['cobertura_meses_greve'])} | "
                 f"{x['fora_acima']} / {x['fora_abaixo']} | {'sim' if 0.80 <= t['cobertura'] <= 0.98 else 'não'} |")
    L += ["", "## Registro de mudança (2026-10-21)", "",
          "A versão A, definida antes de ver o teste, usa no teste o efeito do último ano de treino. O segundo semestre de 2024 teve cerca de 1.000 falhas "
          "técnicas, contra cerca de 500 nos semestres vizinhos (a Amarela teve 403 em 2024, contra 76 a 186 nos demais anos). A versão A herda esse pico. "
          "Depois de ver o resultado, registramos a versão C, que sorteia o efeito do ano entre os anos do treino a cada caminho, e, como pede a spec, "
          "a testamos de novo num período diferente (versão D). O resultado oficial do critério é o da versão A.", "",
          "## Cobertura por linha", "", "| Linha | " + " | ".join(r) + " |", "|---|" + "---|" * len(r)]
    for l in LINHAS:
        L.append(f"| {l} | " + " | ".join(cob(x["cobertura_por_linha"][l]) for x in r.values()) + " |")
    L += ["", "## Onde o modelo falhou (versão A)", "", "| Linha | Meses fora do intervalo (observado contra IP 90%) |", "|---|---|"]
    for l in LINHAS:
        fora = [f"{c['mes']} ({c['observado']} contra {c['ip90'][0]:.0f}–{c['ip90'][1]:.0f})" for c in r["A"]["casos"] if c["linha"] == l and not c["dentro"]]
        L.append(f"| {l} | {'; '.join(fora) or 'nenhum'} |")
    L += ["", "## PIT", ""]
    for v in r:
        L.append(f"- Versão {v}: histograma em 10 faixas {r[v]['pit_histograma_10']}; KS contra a uniforme p = {r[v]['pit_ks_p']:.2g}.")
    L += ["", "![PIT da versão A](backtest_pit.svg)", "", "![PIT da versão C](backtest_pit_C.svg)", "",
          "## Minutos parados no primeiro ano do teste", "",
          "Soma das durações dos eventos técnicos de uma linha nas horas com serviço e dos eventos de causa comum que incluem a linha (sem descontar sobreposições).", "",
          "| Versão | Ano | Linha | Observado | Mediana prevista | IC 95% | Dentro |", "|---|---|---|---|---|---|---|"]
    for v, x in r.items():
        for l, m in x["minutos_ano"].items():
            L.append(f"| {v} | {x['ano_minutos']} | {l} | {m['observado']:.0f} | {m['mediana']:.0f} | {m['ic95'][0]:.0f}–{m['ic95'][1]:.0f} | {'sim' if m['dentro'] else 'não'} |")
    L += ["", "## Forma da renovação ajustada no treino", ""]
    for v, x in r.items():
        L.append(f"- {v}: " + ", ".join(f"{k} {f}" for k, f in x["forma_renovacao_treino"].items()))
    L += ["", "## Todos os casos da versão A", "", "| Linha | Mês | Observado | Mediana | IP 90% | Dentro | PIT | Greve |", "|---|---|---|---|---|---|---|---|"]
    for c in r["A"]["casos"]:
        L.append(f"| {c['linha']} | {c['mes']} | {c['observado']} | {c['mediana']:.0f} | {c['ip90'][0]:.0f}–{c['ip90'][1]:.0f} | {'sim' if c['dentro'] else 'não'} | {c['pit']} | {'sim' if c['greve'] else ''} |")
    open("fontes/verificacao/backtest.md", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    open("fontes/verificacao/backtest_pit.svg", "w", encoding="utf-8", newline="\n").write(
        svg_pit(r["A"]["pit_histograma_10"], "PIT das 72 previsões linha × mês, versão A (oficial)") + "\n")
    open("fontes/verificacao/backtest_pit_C.svg", "w", encoding="utf-8", newline="\n").write(
        svg_pit(r["C"]["pit_histograma_10"], "PIT das 72 previsões linha × mês, versão C (ano sorteado)") + "\n")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rng = np.random.default_rng(SEMENTE)
    painel, _ = mt.monta_painel()
    with open("dados/derivados/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
        ev = list(csv.DictReader(f, delimiter=";"))
    with open("dados/derivados/eventos/eventos_causa_comum.csv", encoding="utf-8") as f:
        cc = list(csv.DictReader(f, delimiter=";"))
    r = {v: avalia(v, cfg, painel, ev, cc, rng) for v, cfg in VERSOES.items()}
    with open(SAIDA, "w", encoding="utf-8", newline="\n") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    relatorio(r)
    for v, x in r.items():
        print(v, x["cobertura_total"], {l: m["dentro"] for l, m in x["minutos_ano"].items()})


if __name__ == "__main__":
    main()
