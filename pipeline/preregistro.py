"""Spec 020 (D61): pré-registro do teste fora da amostra.

Congela um modelo ajustado em todos os dados até o fim do retrato (2026-06-30) e fixa, em código, como ele será
avaliado nos meses que a STM publicar depois. O arquivo congelado vai para o repositório num commit anterior ao
download dos meses novos; o commit é a data do pré-registro.

Uso (da raiz do repositório):
  .venv/Scripts/python -I pipeline/preregistro.py congela v1 [--bootstrap N]
  .venv/Scripts/python -I pipeline/preregistro.py avalia v1 [--de AAAA-MM] [--ate AAAA-MM]

Protocolo fixado aqui (não muda depois de ver os meses novos):
  - Casos: cada linha × mês posterior ao corte, só nas horas com serviço programado. Alvos: falhas técnicas de uma
    linha (MR + EF) e as que têm 5 min ou mais pela faixa oficial da STM ("Incident en minutes").
  - Previsão: renovação Weibull no tempo reescalado pela taxa horária do modelo congelado, com o clima, a oferta e o
    calendário observados no mês (entradas, não resultados), como no backtest da spec 012. Cada caminho usa um vetor
    do bootstrap. Regra principal do efeito do ano: "C" (sorteado entre os anos do treino a cada caminho, D35);
    também se reporta "A" (efeito do último ano completo do treino).
  - Durações para o alvo de 5 min: sorteadas da amostra do treino de cada linha × causa, guardada no arquivo.
  - Critérios: cobertura do intervalo de predição de 90% entre 80% e 98% (o da spec 012), com IC de Clopper-Pearson;
    PIT com teste KS. Comparação entre versões do modelo: escore logarítmico médio nos mesmos casos (maior é melhor),
    com IC por bootstrap pareado dos casos.
  - A avaliação roda quando houver pelo menos 3 meses novos (12 casos por alvo) e é refeita a cada publicação.
"""
import csv
import json
import math
import os
import subprocess
import sys
from datetime import date

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASTA = "fontes/verificacao/preregistro"
SEMENTE = 20261110
CAMINHOS_POR_VETOR = 20
LINHAS = ("verde", "laranja", "amarela", "azul")
CAUSAS = ("MR", "EF")
FAIXAS_5_OU_MAIS = {"05 à 09 min", "10 à 14 min", "15 à 19 min", "20 à 24 min", "25 à 29 min", "30 min et plus"}
MESES_MINIMOS = 3


def arquivo(versao):
    return os.path.join(PASTA, f"modelo_{versao}.json")


def desenho(df, categoricas, indicadores, colunas):
    """Matriz de covariáveis alinhada às colunas congeladas (nível ausente = 0). Independente do pipeline atual."""
    import pandas as pd
    partes = [pd.get_dummies(df[c].astype(str), prefix=c, prefix_sep="=", dtype=float) for c in categoricas]
    X = pd.concat(partes + [df[indicadores].astype(float)], axis=1)
    X.insert(0, "const", 1.0)
    return X.reindex(columns=colunas, fill_value=0.0).to_numpy(float)


def renovacao(T, k, rng):
    """Um caminho de renovação Weibull(k, média 1) em [0, T], com início estacionário (cópia do backtest da spec 012)."""
    escala = 1 / math.gamma(1 + 1 / k)
    t = [escala * rng.gamma(1 + 1 / k) ** (1 / k) * rng.uniform()]
    bloco = int(T * 1.3) + 50
    while t[-1] < T:
        t = np.concatenate([t, t[-1] + np.cumsum(escala * rng.weibull(k, bloco))])
    t = np.asarray(t)
    return t[t < T]


def commit_atual():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return ""


def congela_v1(B):
    """Modelo v1 (o publicado até a revisão de 2026-11): MR e EF por linha, exposição por trens-hora."""
    import backtest as bt
    import modelo_taxa as mt
    rng = np.random.default_rng(SEMENTE)
    painel, _ = mt.monta_painel()
    with open("dados/derivados/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
        ev = list(csv.DictReader(f, delimiter=";"))
    corte = str(painel["data_servico"].max())
    anos = sorted(str(a) for a in painel["ano"].unique())
    ultimo_completo = max(a for a in anos if corte >= f"{a}-12-31") if any(corte >= f"{a}-12-31" for a in anos) else anos[-1]
    saida = {"versao_modelo": "v1", "descricao": "modelo publicado até a revisão de 2026-11: MR e EF por linha, deslocamento log(trens-hora)",
             "congelado_em": date.today().isoformat(), "commit_do_codigo": commit_atual(), "corte": corte,
             "categoricas": list(mt.CATEGORICAS), "indicadores": list(mt.INDICADORES), "referencia": dict(mt.REFERENCIA),
             "anos_treino": anos, "regras_ano": {"C": "sorteio entre os anos do treino (principal)", "A": f"efeito de {ultimo_completo}"},
             "ano_regra_A": ultimo_completo, "semente": SEMENTE, "caminhos_por_vetor": CAMINHOS_POR_VETOR, "causas": {}}
    for causa in CAUSAS:
        colunas, vetores, alpha, mu = bt.ajusta_com_bootstrap(painel, causa, B, rng)
        print(f"v1 {causa}: alpha={alpha:.3f}, {len(vetores)} vetores", flush=True)
        ordenado = painel.assign(mu=mu).sort_values(["linha", "data_servico", "hora"])
        formas, ttr = {}, {}
        for l in LINHAS:
            tl = ordenado[ordenado["linha"] == l]
            formas[l] = round(bt.forma_renovacao(tl, tl["mu"].to_numpy(), [(r["data_servico"], r["inicio_local"]) for r in ev if r["linha"] == l and r["causa"] == causa]), 6)
            d = np.array([int(r["duracao_min"]) for r in ev if r["linha"] == l and r["causa"] == causa])
            ttr[l] = {"p_zero": float((d == 0).mean()), "positivos": sorted(int(x) for x in d[d > 0])}
        saida["causas"][causa] = {"colunas": colunas, "alpha": float(alpha), "vetores": np.round(vetores, 10).tolist(), "formas": formas, "ttr": ttr}
    os.makedirs(PASTA, exist_ok=True)
    with open(arquivo("v1"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(saida, f, ensure_ascii=False, indent=0)
    print("gravado", arquivo("v1"))


def previsoes(modelo, painel, rng):
    """Caminhos simulados por linha × mês para os dois alvos e as duas regras do ano."""
    teste = painel.sort_values(["linha", "data_servico", "hora"]).reset_index(drop=True)
    teste["mes"] = teste["data_servico"].str[:7]
    meses = sorted(teste["mes"].unique())
    saida = {}
    for regra in ("C", "A"):
        tot = {l: None for l in LINHAS}
        cinco = {l: None for l in LINHAS}
        for causa in CAUSAS:
            m = modelo["causas"][causa]
            colunas = m["colunas"]
            j_ano = {a: (colunas.index(f"ano={a}") if f"ano={a}" in colunas else None) for a in modelo["anos_treino"]}
            base = teste.assign(ano=modelo["referencia"]["ano"])  # o ano entra pelo vetor, conforme a regra
            X = desenho(base, modelo["categoricas"], modelo["indicadores"], colunas)
            off = np.log(teste["exposicao"].to_numpy(float))
            for l in LINHAS:
                sel = (teste["linha"] == l).to_numpy()
                mes_idx = np.searchsorted(meses, teste.loc[sel, "mes"].to_numpy())
                k = m["formas"][l]
                p0, pos = m["ttr"][l]["p_zero"], np.array(m["ttr"][l]["positivos"], float)
                ct, c5 = [], []
                for v in np.array(m["vetores"]):
                    eta = X[sel] @ v + off[sel]
                    for _ in range(modelo["caminhos_por_vetor"]):
                        a = modelo["anos_treino"][rng.integers(len(modelo["anos_treino"]))] if regra == "C" else modelo["ano_regra_A"]
                        j = j_ano.get(a)
                        acum = np.cumsum(np.exp(eta + (v[j] if j is not None else 0.0)))
                        hora = np.searchsorted(acum, renovacao(acum[-1], k, rng), side="right")
                        dur = np.where(rng.uniform(size=len(hora)) < p0, 0.0, rng.choice(pos, len(hora)))
                        ct.append(np.bincount(mes_idx[hora], minlength=len(meses)))
                        c5.append(np.bincount(mes_idx[hora[dur >= 5]], minlength=len(meses)))
                ct, c5 = np.array(ct), np.array(c5)
                tot[l] = ct if tot[l] is None else tot[l][: len(ct)] + ct[: len(tot[l])]
                cinco[l] = c5 if cinco[l] is None else cinco[l][: len(c5)] + c5[: len(cinco[l])]
        saida[regra] = {"total": tot, "cinco": cinco}
    return meses, saida


def escore_log(s, y):
    """Escore logarítmico da previsão empírica com suavização de Laplace sobre 0..max."""
    topo = max(int(s.max()), y) + 1
    cont = np.bincount(s.astype(int), minlength=topo + 1).astype(float) + 0.5
    return float(np.log(cont[y] / cont.sum()))


def cobertura(dentro):
    k, n = int(sum(dentro)), len(dentro)
    lo = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    hi = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return {"dentro": k, "casos": n, "cobertura": round(k / n, 4) if n else None, "ic95": [round(float(lo), 4), round(float(hi), 4)],
            "entre_80_e_98": bool(n and 0.80 <= k / n <= 0.98)}


def avalia(versao, de=None, ate=None, interno=False):
    """Avalia o modelo congelado nos meses depois do corte. `interno=True` só serve ao teste automático: roda
    dentro do período de treino, não exige os 3 meses e não grava nada."""
    import modelo_taxa as mt
    caminho = arquivo(versao)
    if not os.path.exists(caminho):
        sys.exit(f"sem pré-registro: {caminho} não existe. A avaliação só roda contra um modelo congelado antes dos dados.")
    modelo = json.load(open(caminho, encoding="utf-8"))
    painel, _ = mt.monta_painel()
    if not interno:
        painel = painel[painel["data_servico"] > modelo["corte"]]
    if de:
        painel = painel[painel["data_servico"] >= de]
    if ate:
        painel = painel[painel["data_servico"].str[:7] <= ate]
    meses_disp = sorted(painel["data_servico"].str[:7].unique())
    if not meses_disp:
        sys.exit(f"nenhum mês depois de {modelo['corte']} nos dados: a STM ainda não publicou meses novos.")
    if len(meses_disp) < MESES_MINIMOS and not interno:
        sys.exit(f"só {len(meses_disp)} mês(es) depois de {modelo['corte']}: o protocolo pede pelo menos {MESES_MINIMOS}.")
    with open("dados/derivados/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
        ev = list(csv.DictReader(f, delimiter=";"))
    horas = set(zip(painel["data_servico"], painel["linha"], painel["hora"]))
    import backtest as bt
    obs_t, obs_5 = {}, {}
    for r in ev:
        h = bt.minuto_servico(r["inicio_local"], r["data_servico"]) // 60
        if (r["data_servico"], r["linha"], h) in horas:
            chave = (r["linha"], r["data_servico"][:7])
            obs_t[chave] = obs_t.get(chave, 0) + 1
            if r["faixa_oficial"] in FAIXAS_5_OU_MAIS:
                obs_5[chave] = obs_5.get(chave, 0) + 1
    rng = np.random.default_rng(SEMENTE)
    meses, prev = previsoes(modelo, painel, rng)
    resultado = {"versao_modelo": versao, "corte": modelo["corte"], "meses": meses, "regras": {}}
    for regra, alvos in prev.items():
        r_regra = {}
        for alvo, obs in (("total", obs_t), ("cinco", obs_5)):
            casos = []
            for l in LINHAS:
                for j, m in enumerate(meses):
                    s, y = alvos[alvo][l][:, j], obs.get((l, m), 0)
                    q05, q50, q95 = np.percentile(s, [5, 50, 95])
                    F = lambda v: float(np.mean(s <= v))
                    pit = F(y - 1) + rng.uniform() * (F(y) - F(y - 1))
                    casos.append({"linha": l, "mes": m, "observado": y, "mediana": float(q50), "ip90": [float(q05), float(q95)],
                                  "dentro": bool(q05 <= y <= q95), "pit": round(pit, 4), "escore_log": round(escore_log(s, y), 6)})
            pits = np.array([c["pit"] for c in casos])
            r_regra[alvo] = {"cobertura": cobertura([c["dentro"] for c in casos]), "pit_ks_p": float(stats.kstest(pits, "uniform").pvalue) if len(pits) > 1 else None,
                             "escore_log_medio": float(np.mean([c["escore_log"] for c in casos])), "casos": casos}
        resultado["regras"][regra] = r_regra
    if interno:
        return resultado
    saida = os.path.join(PASTA, f"avaliacao_{versao}_{meses[0]}_a_{meses[-1]}.json")
    with open(saida, "w", encoding="utf-8", newline="\n") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=1)
    for regra, rr in resultado["regras"].items():
        print(regra, {a: (x["cobertura"]["cobertura"], round(x["escore_log_medio"], 3)) for a, x in rr.items()})
    print("gravado", saida)
    return resultado


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    acao, versao = sys.argv[1], sys.argv[2]
    arg = lambda n: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else None
    if acao == "congela":
        if versao != "v1":
            sys.exit("a versão v2 é congelada pelo modelo da spec 018 (a acrescentar aqui)")
        if os.path.exists(arquivo(versao)) and "--refaz" not in sys.argv:
            sys.exit(f"{arquivo(versao)} já existe: um pré-registro não se refaz depois de commitado")
        congela_v1(int(arg("--bootstrap") or 100))
    elif acao == "avalia":
        avalia(versao, arg("--de"), arg("--ate"))
    else:
        sys.exit("ação desconhecida: use congela ou avalia")


if __name__ == "__main__":
    main()
