"""Monta dados/derivados/simulador/parametros.json, o contrato entre o pipeline e o simulador.

Uso (da raiz do repositório): python -I pipeline/parametros.py
Entradas: modelos (taxa_MR.json, taxa_EF.json, distribuicoes.json), eventos (spec 001), locais (spec 002),
          painel (frota e trens necessários). Contrato: contratos/parametros.schema.json
Todo número sai como Parametro: valor, ic95, n, unidade, método, fontes, script e status.
"""
import csv
import json
import hashlib
from collections import defaultdict

import numpy as np
from scipy import stats

M = "dados/derivados/modelos"
LINHAS = ("verde", "laranja", "amarela", "azul")
FONTES_TAXA = ["stm_incidentes", "stm_km_reel", "gtfs_stm", "eccc_horario", "eventos"]


def P(valor, status, metodo, fontes, script, ic95=None, n=None, unidade="", faixa=None):
    p = {"valor": valor, "ic95": ic95, "n": n, "unidade": unidade, "metodo": metodo, "fontes": fontes, "script": script, "status": status}
    if faixa:
        p["faixa"] = faixa
    return p


def amostra(duracoes, origem):
    """Amostra ordenada das durações positivas observadas: o simulador sorteia uma delas (distribuição empírica).
    Decisão de 2026-10-21 (spec 009): a lognormal subestima a média por causa da cauda (até 3,4 vezes na Azul, EF)."""
    pos = sorted(int(d) for d in duracoes if d > 0)
    return {"minutos": pos, "n": len(pos), "media_min": round(float(np.mean(pos)), 3),
            "metodo": "distribuição empírica das durações positivas (reamostragem)", "fontes": ["stm_incidentes"],
            "script": "pipeline/parametros.py", "status": "ajustado", "origem": origem}


SCRIPTS_DO_CONTRATO = ("pipeline/modelo_taxa.py", "pipeline/distribuicoes.py", "pipeline/parametros.py")


def commit():
    """Identifica o código que gerou o contrato: SHA-256 dos scripts com fim de linha normalizado.
    Igual em qualquer máquina e commit com o mesmo código (o hash do git mudava a cada commit e quebrava a reprodução)."""
    h = hashlib.sha256()
    for s in SCRIPTS_DO_CONTRATO:
        h.update(open(s, "rb").read().replace(b"\r\n", b"\n"))
    return "sha256-scripts:" + h.hexdigest()[:16]


def taxa(causa):
    t = json.load(open(f"{M}/taxa_{causa}.json", encoding="utf-8"))
    script = "pipeline/modelo_taxa.py"
    metodo = f"GLM {t['modelo_escolhido']} com deslocamento log(trens-hora); IC por bootstrap em blocos semanais (B={t['bootstrap_b']})"
    mult = defaultdict(dict)
    for fator, nivel in t["referencia"].items():
        if fator not in ("linha", "ano"):
            mult[fator][nivel] = P(1.0, "ajustado", "nível de referência do modelo", FONTES_TAXA, script, [1.0, 1.0], t["n_horas"])
    for c in t["coeficientes"]:
        termo = c["termo"]
        if termo == "const" or termo.startswith(("linha=", "ano=")):
            continue
        fator, nivel = termo.split("=", 1) if "=" in termo else (termo, "1")
        if nivel == "sem_dado":
            # categoria de dado ausente: controla o ajuste, mas não é um cenário possível (e, com poucas horas,
            # o multiplicador vai a zero). Fica no relatório da spec 005, não no contrato.
            continue
        if fator == "greve":
            # a spec 005 concluiu que a greve atua só pela exposição (IC do multiplicador contém 1); no simulador,
            # a greve reduz a oferta e não muda a taxa por trem-hora (decisão D42, 2026-10-21)
            continue
        mult[fator][nivel] = P(c["multiplicador"], "ajustado", metodo, FONTES_TAXA, script, c["ic95"], t["n_horas"], "multiplicador da taxa")
    base = {l: P(v["valor"], "ajustado", metodo + f"; condições de referência no ano {t['ano_base']}", FONTES_TAXA, script, v["ic95"],
                 t["n_horas"], "falhas por trem-hora") for l, v in t["base_por_trem_hora"].items()}
    return {"modelo": t["modelo_escolhido"], "referencia": t["referencia"],
            "alpha": P(t["alpha_nb"], "ajustado", "máxima verossimilhança da binomial negativa (NB2)", FONTES_TAXA, script, None, t["n_horas"]),
            "base_por_trem_hora": base, "multiplicadores": mult}


def main():
    d = json.load(open(f"{M}/distribuicoes.json", encoding="utf-8"))
    sd = "pipeline/distribuicoes.py"
    renov, ttr, cc = {}, {}, {}
    for k, v in d["reescala"].items():
        w = v["weibull_reescalado"]
        met = "Weibull ajustada aos intervalos reescalados pela taxa da spec 005; IC por bootstrap"
        renov[k] = {"forma": P(w["forma"], "ajustado", met, ["stm_incidentes"], sd, w["forma_ic95"], v["n"]),
                    "escala": P(w["escala"], "ajustado", met, ["stm_incidentes"], sd, w["escala_ic95"], v["n"]),
                    "processo": v["processo_no_simulador"]}
    duracoes = defaultdict(list)
    with open("dados/derivados/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            duracoes[f"{r['linha']}|{r['causa']}"].append(int(r["duracao_min"]))
    for k, v in d["ttr"].items():
        ln = v["lognormal_positivos"]
        ttr[k] = {"p_zero": P(v["p_zero"], "ajustado", "proporção de falhas sem interrupção; IC de Wilson", ["stm_incidentes"], sd, v["p_zero_ic95"], v["n"]),
                  "mu_log": P(ln["mu_log"], "ajustado", "lognormal das durações positivas (minutos); IC por bootstrap", ["stm_incidentes"], sd, ln["mu_log_ic95"], v["n"], "log(minutos)"),
                  "sigma_log": P(ln["sigma_log"], "ajustado", "lognormal das durações positivas; IC por bootstrap", ["stm_incidentes"], sd, ln["sigma_log_ic95"], v["n"], "log(minutos)"),
                  "amostra_positivos": amostra(duracoes[k], f"eventos técnicos {k}")}
    # Fontes de causa comum do simulador: um grupo por conjunto exato de linhas atingidas (cada evento conta uma vez).
    dc = d["causa_comum_duracao_conjunta"]
    duracao_cc = {"p_zero": P(dc["p_zero"], "ajustado", "proporção sem interrupção nos 45 eventos multilinha; IC de Wilson", ["stm_incidentes"], sd, dc["p_zero_ic95"], dc["n"]),
                  "mu_log": P(dc["mu_log"], "ajustado", "lognormal das durações positivas dos 45 eventos multilinha", ["stm_incidentes"], sd, None, dc["n"], "log(minutos)"),
                  "sigma_log": P(dc["sigma_log"], "ajustado", "lognormal das durações positivas dos 45 eventos multilinha", ["stm_incidentes"], sd, None, dc["n"], "log(minutos)"),
                  "amostra_positivos": amostra([int(r["duracao_min"]) for r in csv.DictReader(open("dados/derivados/eventos/eventos_causa_comum.csv", encoding="utf-8"), delimiter=";")],
                                               "45 eventos de causa comum")}
    for k, v in d["causa_comum_grupos"].items():
        cc[k] = {"linhas": v["linhas"],
                 "taxa_por_hora_op": P(v["taxa_por_hora_op"], "ajustado", "eventos que pararam exatamente este grupo de linhas, por hora de operação; IC exato de Garwood",
                                       ["stm_incidentes"], sd, v["taxa_ic95"], v["eventos"], "eventos por hora"),
                 "duracao": duracao_cc}
    beta = {}
    for k, v in d["causa_comum"].items():
        beta[k] = {"eventos": v["eventos"],
                   "beta_a": P(v["beta_a"], "ajustado", "fator β da 1ª linha do par; IC de Clopper-Pearson", ["stm_incidentes"], sd, v["beta_a_ic95"], v["eventos"]),
                   "beta_b": P(v["beta_b"], "ajustado", "fator β da 2ª linha do par; IC de Clopper-Pearson", ["stm_incidentes"], sd, v["beta_b_ic95"], v["eventos"])}

    # Onde ocorrem as falhas de equipamento fixo: código de local -> km na linha (spec 002), peso = falhas EF
    # Estação de correspondência citada por uma falha de outra linha: usa o km da mesma estação na linha da falha.
    locais = {x["codigo"]: x for x in json.load(open("dados/derivados/geo/locais.json", encoding="utf-8"))}
    km_estacao = {(f["properties"]["linha"], f["properties"]["estacao"]): f["properties"]["km_linha"]
                  for f in json.load(open("dados/derivados/geo/estacoes.geojson", encoding="utf-8"))["features"]}
    peso = defaultdict(lambda: defaultdict(int))
    pos = {}
    sem_posicao = defaultdict(int)
    with open("dados/derivados/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["causa"] != "EF":
                continue
            loc, l = locais.get(r["local_codigo"]), r["linha"]
            km = None
            if loc and loc["km_linha"] is not None and loc["linha"] == l:
                km, status = loc["km_linha"], loc["status"]
            elif loc and len(loc.get("estacoes") or []) == 1 and (l, loc["estacoes"][0]) in km_estacao:
                km, status = km_estacao[(l, loc["estacoes"][0])], loc["status"] + " (estação na linha da falha)"
            if km is None:
                sem_posicao[l] += 1
                continue
            peso[l][r["local_codigo"]] += 1
            pos[(l, r["local_codigo"])] = (km, status)
    locais_ef = {l: [{"km": pos[(l, c)][0], "peso": n, "codigo": c, "status": pos[(l, c)][1]} for c, n in sorted(peso[l].items())] for l in LINHAS}

    painel = {r["linha"]: r for r in json.load(open("dados/derivados/painel/linhas.json", encoding="utf-8"))}
    frota = {}
    for l in LINHAS:
        r = painel[l]
        k = None
        with open("dados/derivados/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
            k = sum(1 for e in csv.DictReader(f, delimiter=";") if e["linha"] == l and e["causa"] == "MR" and e["data_servico"] <= "2023-09-30")
        T = k / r["lambda_trem_dia"]
        lo, hi = stats.chi2.ppf(0.025, 2 * k) / 2 / T, stats.chi2.ppf(0.975, 2 * k + 2) / 2 / T
        frota[l] = {"trens_necessarios": P(r["trens_dia_util"], "ajustado", "mediana de composições distintas por dia útil no km real", ["stm_km_reel"],
                                           "pipeline/analise_confiabilidade.py", None, None, "trens"),
                    "lambda_trem_dia": P(r["lambda_trem_dia"], "ajustado", "falhas de material rodante por trem-dia (2019-01 a 2023-09); IC exato de Garwood",
                                         ["stm_incidentes", "stm_km_reel"], "pipeline/analise_confiabilidade.py", [round(lo, 6), round(hi, 6)], k, "falhas por trem-dia")}

    H = "hipótese do autor, sem dado; ajustável na interface"
    hip = {
        "reparo_oficina_dias": P(1.0, "hipótese", H + ": tempo médio de reparo de um trem retirado", [], "pipeline/parametros.py", None, None, "dias", [0.5, 4.0]),
        "p_retirada": P(1.0, "hipótese", H + ": parcela das falhas de material rodante que retira o trem de serviço (1 = mesmo critério do painel)", [], "pipeline/parametros.py", None, None, "", [0.0, 1.0]),
        "reservas_por_linha": P(2, "hipótese", H + ": trens de reserva por linha", [], "pipeline/parametros.py", None, None, "trens", [0, 8]),
        "intervalo_minimo_s": P(90, "hipótese", H + ": separação mínima entre trens no mesmo trecho", [], "pipeline/parametros.py", None, None, "s", [60, 180]),
        "sentidos_bloqueio_ef": P(2, "hipótese", H + ": falha de equipamento fixo bloqueia 1 ou 2 sentidos", [], "pipeline/parametros.py", None, None, "sentidos", [1, 2]),
        "fator_velocidade_degradada": P(1.25, "hipótese", H + ": multiplica o tempo de percurso no trecho em operação degradada (até o fim do reparo)", [], "pipeline/parametros.py", None, None, "", [1.0, 2.0]),
        "tempo_retirada_min": P(10, "hipótese", H + ": política de retirada, tempo-alvo para tirar o trem falho da via", [], "pipeline/parametros.py", None, None, "min", [5, 30]),
        "tempo_ativacao_degradada_min": P(5, "hipótese", H + ": política de operação degradada, parada antes de liberar a marcha lenta", [], "pipeline/parametros.py", None, None, "min", [2, 15]),
        "reducao_causa_comum_politica": P(0.5, "hipótese", H + ": redução da taxa de causa comum aplicada pela política de causa comum", [], "pipeline/parametros.py", None, None, "", [0.0, 1.0]),
        "fator_tracado_candidata": P(1.2, "hipótese", H + ": km de via ÷ distância em linha reta numa linha candidata", [], "pipeline/parametros.py", None, None, "", [1.0, 1.6]),
        "km_minimo_candidata": P(0.3, "hipótese", H + ": ligação candidata mais curta aceita na busca exaustiva", [], "pipeline/parametros.py", None, None, "km", [0.1, 2.0]),
        "tempo_transferencia_min": P(4, "hipótese", H + ": tempo de transferência nas estações de correspondência", [], "pipeline/parametros.py", None, None, "min", [2, 8]),
        "reducao_causa_comum": P(0.0, "hipótese", H + ": redução da taxa de causa comum por alimentação ou controle redundante", [], "pipeline/parametros.py", None, None, "", [0.0, 1.0]),
        "velocidade_comercial_candidata_kmh": P(36, "hipótese", H + ": velocidade comercial de uma linha candidata (média das linhas atuais, 35 a 38 km/h)", [], "pipeline/parametros.py", None, None, "km/h", [30, 45]),
    }
    out = {"versao": 1, "codigo_commit": commit(), "ano_base": int(json.load(open(f"{M}/taxa_MR.json", encoding="utf-8"))["ano_base"]),
           "janela_operacao_h": P(20, "hipótese", "inferida do horário dos incidentes (05:00 a 01:00)", ["stm_incidentes"], "pipeline/analise_confiabilidade.py", None, None, "h"),
           "taxas": {"MR": taxa("MR"), "EF": taxa("EF")}, "renovacao": renov, "ttr": ttr, "causa_comum": cc, "causa_comum_beta": beta,
           "locais_ef": locais_ef, "locais_ef_sem_posicao": dict(sem_posicao), "frota": frota, "hipoteses": hip}
    with open("dados/derivados/simulador/parametros.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("parametros.json:", {k: (len(v) if isinstance(v, dict) else v) for k, v in out.items() if k != "codigo_commit"})


if __name__ == "__main__":
    main()
