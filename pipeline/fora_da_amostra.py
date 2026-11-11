"""Spec 018: o modelo por fonte prevê melhor que o da v1.1.0 o que não viu? Um ano de fora de cada vez.

Uso (da raiz do repositório, depois de pipeline/modelo_taxa.py): .venv/Scripts/python -I pipeline/fora_da_amostra.py
Para cada ano de 2019 a 2025: ajusta sem ele os dois modelos e prevê as falhas de cada linha naquele ano, com a
exposição e o clima observados (entradas). O efeito do ano deixado de fora é a média dos efeitos dos anos do treino
(o ano de referência vale 0). O α de cada binomial negativa fica fixo no do ajuste completo.
- v1.1.0: uma binomial negativa por família (MR, EF), com a linha como covariável (spec 005).
- por fonte: material rodante empilhado por frota (exposição × parcela da frota) mais `mr_outros` com taxa por linha;
  equipamento fixo como soma das fontes (próprias com as covariáveis da spec 005; reduzidas com a linha, a faixa e o
  preditor da família EF do mesmo ajuste).
Medida: log(observado ÷ esperado) por linha × ano deixado de fora; resumo pela raiz do erro quadrático médio.
Saída: fontes/verificacao/fora_da_amostra.md e dados/derivados/modelos/fora_da_amostra.json
"""
import gc
import json
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelo_taxa as mt  # noqa: E402

ANOS = [str(a) for a in range(2019, 2026)]
LINHAS = ("verde", "laranja", "amarela", "azul")


def sem_colinear(X):
    """Tira colunas nulas; se o ano de referência saiu do treino, o primeiro ano presente vira a referência (e a
    primeira interação frota × ano, que ficaria colinear com a frota)."""
    X = X.loc[:, (X != 0).any()]
    anos = sorted(c for c in X.columns if c.startswith("ano="))
    if anos and (X[anos].sum(axis=1) > 0).all():
        X = X.drop(columns=anos[0])
        inter = sorted(c for c in X.columns if c.startswith("frota=MR-73:ano="))
        if inter and "frota=MR-73" in X.columns and ((X[inter].sum(axis=1) > 0) == (X["frota=MR-73"] > 0)).all():
            X = X.drop(columns=inter[0])
    return X


def ajuste(y, X, off, alpha):
    fam = sm.families.NegativeBinomial(alpha=alpha) if alpha else sm.families.Poisson()
    p = pd.Series(np.asarray(sm.GLM(y, X.to_numpy(float), family=fam, offset=off).fit().params, float), index=X.columns)
    gc.collect()  # ciclo modelo↔resultado do statsmodels (ver modelo_taxa.ajusta)
    return p


def preve(params, X_te, off_te, prefixo_ano="ano=", anos_treino=(), extra=None):
    """μ previsto no ano deixado de fora: o efeito do ano é a média dos anos do treino (ano sem coluna vale 0)."""
    Xt = X_te.reindex(columns=params.index, fill_value=0.0).copy()
    for c in Xt.columns:
        if c.startswith(prefixo_ano) or c.startswith("frota=MR-73:ano="):
            Xt[c] = 0.0
    efeitos = [params.get(f"{prefixo_ano}{a}", 0.0) for a in anos_treino]
    eta = Xt.to_numpy(float) @ params.to_numpy(float) + off_te + float(np.mean(efeitos))
    if extra is not None:
        eta = eta + extra
    return np.exp(eta)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    df, _ = mt.monta_painel()
    t = {c: json.load(open(f"{mt.SAIDA}/taxa_{c}.json", encoding="utf-8")) for c in ("MR", "EF")}
    tf = json.load(open(f"{mt.SAIDA}/taxa_fontes.json", encoding="utf-8"))
    alpha = lambda r: r["alpha_nb"] if r["modelo_escolhido"] == "binomial negativa" else None
    st_todo, _ = mt.painel_mr_empilhado(df)
    fontes_ef = [f for f, x in tf["fontes"].items() if x["familia"] == "EF"]
    # matrizes montadas uma vez no painel inteiro e recortadas por linha: treino e teste ficam com as mesmas colunas, e
    # o ano de referência (2019) pode sair do treino sem que a coluna dele falte (sem_colinear troca a referência)
    XD, XM = mt.matriz(df), mt.matriz_mr(st_todo)
    casos = []
    for Y in ANOS:
        tr, te = df[df["ano"] != Y], df[df["ano"] == Y]
        treino = [a for a in ANOS + ["2026"] if a != Y]
        off_tr, off_te = np.log(tr["exposicao"].to_numpy(float)), np.log(te["exposicao"].to_numpy(float))
        X_tr, X_te = sem_colinear(XD.loc[tr.index]), XD.loc[te.index]
        prev = {"v1": {}, "fonte": {}}
        fam_ef = None
        for c in ("MR", "EF"):
            p = ajuste(tr[f"y_{c}"].to_numpy(float), X_tr, off_tr, alpha(t[c]))
            prev["v1"][c] = preve(p, X_te, off_te, anos_treino=treino)
            if c == "EF":
                fam_ef = (p, preve(p, X_te, off_te, anos_treino=treino))
        # material rodante por fonte
        st_tr, st_te = st_todo[st_todo["ano"] != Y], st_todo[st_todo["ano"] == Y]
        Xs = sem_colinear(XM.loc[st_tr.index])
        ps = ajuste(st_tr["y_mr_frota"].to_numpy(float), Xs, np.log(st_tr["exposicao"].to_numpy(float)), tf["mr_empilhado"]["alpha_nb"])
        efeito_frota_ano = float(np.mean([ps.get(f"frota=MR-73:ano={a}", 0.0) for a in treino]))
        mu_st = preve(ps, XM.loc[st_te.index], np.log(st_te["exposicao"].to_numpy(float)), anos_treino=treino,
                      extra=np.where(st_te["frota"].to_numpy() == "MR-73", efeito_frota_ano, 0.0))
        mu_mr = pd.Series(mu_st, index=st_te["_painel"].to_numpy()).groupby(level=0).sum().reindex(te.index, fill_value=0.0).to_numpy()
        taxa_outros = tr.groupby("linha")["y_mr_outros"].sum() / tr.groupby("linha")["exposicao"].sum()
        mu_mr = mu_mr + te["exposicao"].to_numpy(float) * te["linha"].map(taxa_outros).fillna(0.0).to_numpy(float)
        prev["fonte"]["MR"] = mu_mr
        # equipamento fixo por fonte
        p_ef, _ = fam_ef
        J = [c for c in p_ef.index if c.startswith(mt.PREFIXOS_HERDADOS)]
        mu_ef = np.zeros(len(te))
        for f in fontes_ef:
            x = tf["fontes"][f]
            y_tr = tr[f"y_{f}"].to_numpy(float)
            if x["modelo"] == "próprio":
                p = ajuste(y_tr, X_tr, off_tr, alpha(x))
                mu_ef += preve(p, X_te, off_te, anos_treino=treino)
            else:
                herd_tr = XD.loc[tr.index].reindex(columns=J, fill_value=0.0).to_numpy(float) @ p_ef[J].to_numpy(float)
                Xte_h = XD.loc[te.index].reindex(columns=J, fill_value=0.0)
                for c in Xte_h.columns:
                    if c.startswith("ano="):
                        Xte_h[c] = 0.0
                herd_te = Xte_h.to_numpy(float) @ p_ef[J].to_numpy(float) + float(np.mean([p_ef.get(f"ano={a}", 0.0) for a in treino]))
                cats = ["linha", "faixa"] if "faixa" in x["modelo"] else ["linha"]
                dummies = lambda d: sm.add_constant(pd.concat([pd.get_dummies(d[c].astype(str), prefix=c, prefix_sep="=", dtype=float).drop(columns=f"{c}={mt.REFERENCIA[c]}", errors="ignore") for c in cats], axis=1), has_constant="add")
                Xr_tr = dummies(tr)
                p = ajuste(y_tr, Xr_tr, off_tr + herd_tr, alpha(x))
                mu_ef += np.exp(dummies(te).reindex(columns=p.index, fill_value=0.0).to_numpy(float) @ p.to_numpy(float) + off_te + herd_te)
        prev["fonte"]["EF"] = mu_ef
        for l in LINHAS:
            sel = (te["linha"] == l).to_numpy()
            for c in ("MR", "EF"):
                obs = float(te.loc[sel, f"y_{c}"].sum())
                casos.append({"ano": Y, "linha": l, "familia": c, "observado": obs,
                              "esperado_v1": round(float(prev["v1"][c][sel].sum()), 2), "esperado_fonte": round(float(prev["fonte"][c][sel].sum()), 2)})
        print(f"ano {Y} fora: feito", flush=True)
    resumo = {}
    for c in ("MR", "EF"):
        for v in ("v1", "fonte"):
            erros = [np.log(x["observado"] / x[f"esperado_{v}"]) for x in casos if x["familia"] == c and x["observado"] > 0]
            resumo[f"{c}|{v}"] = {"rmse_log": round(float(np.sqrt(np.mean(np.square(erros)))), 4), "casos": len(erros)}
    json.dump({"casos": casos, "resumo": resumo}, open(f"{mt.SAIDA}/fora_da_amostra.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    v = lambda x: f"{x:.3f}".replace(".", ",")
    L = ["# Um ano de fora: modelo da v1.1.0 contra o modelo por fonte (spec 018)", "",
         "Gerado por `pipeline/fora_da_amostra.py`. Cada ano de 2019 a 2025 é tirado do ajuste e previsto com a exposição, o clima e o calendário observados; "
         "o efeito do ano ausente é a média dos anos do treino. Erro = log(observado ÷ esperado) por linha no ano tirado. Medido fora da amostra, "
         "para não premiar o modelo com mais parâmetros.", "",
         "| Família | Raiz do erro quadrático, v1.1.0 | Raiz do erro quadrático, por fonte | Casos |", "|---|---|---|---|"]
    for c in ("MR", "EF"):
        L.append(f"| {c} | {v(resumo[c + '|v1']['rmse_log'])} | {v(resumo[c + '|fonte']['rmse_log'])} | {resumo[c + '|v1']['casos']} |")
    L += ["", "## Por linha e ano (observado ÷ esperado)", "", "| Ano | Linha | Família | Observado | v1.1.0 | Por fonte |", "|---|---|---|---|---|---|"]
    for x in casos:
        L.append(f"| {x['ano']} | {x['linha']} | {x['familia']} | {x['observado']:.0f} | {v(x['observado'] / x['esperado_v1'])} | {v(x['observado'] / x['esperado_fonte'])} |")
    open("fontes/verificacao/fora_da_amostra.md", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print(resumo)


if __name__ == "__main__":
    main()
