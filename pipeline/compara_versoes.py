"""Spec 020 (D60): tabela antes e depois da revisão de 2026-11, gerada dos arquivos derivados das duas versões.

Uso (da raiz do repositório): .venv/Scripts/python -I pipeline/compara_versoes.py [--antes v1.1.0]
Lê cada arquivo na etiqueta da versão anterior (git show) e no disco, e lista os números publicados que mudaram,
com o valor antigo, o novo e a variação. Saída: fontes/verificacao/revisao_2026-11.md
"""
import json
import subprocess
import sys

ANTES = sys.argv[sys.argv.index("--antes") + 1] if "--antes" in sys.argv else "v1.1.0"
SAIDA = "fontes/verificacao/revisao_2026-11.md"
LINHAS = ("verde", "laranja", "amarela", "azul", "rede")


def le(caminho, versao=None):
    try:
        if versao:
            texto = subprocess.run(["git", "show", f"{versao}:{caminho}"], capture_output=True, check=True, timeout=60).stdout.decode("utf-8")
        else:
            texto = open(caminho, encoding="utf-8").read()
        return json.loads(texto)
    except Exception:
        return None


def coef(t):
    return {c["termo"]: c["multiplicador"] for c in t.get("coeficientes", [])} if t else {}


def linhas_tabela(titulo, pares, casas=3, explicacao=""):
    """pares: lista de (rótulo, antes, depois)."""
    L = [f"## {titulo}", ""]
    if explicacao:
        L += [explicacao, ""]
    L += ["| Número | v1.1.0 | Após a revisão | Variação |", "|---|---|---|---|"]
    n = 0
    for rot, a, d in pares:
        if a is None and d is None:
            continue
        if isinstance(a, (int, float)) and isinstance(d, (int, float)):
            if round(a, casas) == round(d, casas):
                continue
            var = f"{(d / a - 1) * 100:+.1f}%".replace(".", ",") if a else "—"
        else:
            if a == d:
                continue
            var = "—"
        f = lambda x: "—" if x is None else (f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".") if isinstance(x, (int, float)) else str(x))
        L.append(f"| {rot} | {f(a)} | {f(d)} | {var} |")
        n += 1
    if n == 0:
        L.append("| (nenhum número mudou) | | | |")
    return L + [""]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    L = ["# Revisão de 2026-11: números antes e depois", "",
         f"Gerado por `pipeline/compara_versoes.py`, comparando os arquivos derivados da etiqueta `{ANTES}` (versão anterior, publicada em `/versoes/{ANTES}/`) "
         "com os atuais. Os números revistos vêm da ressegmentação por frota e setor (specs 017 e 018), da duração pela faixa oficial (D55), do km real "
         "republicado pela STM em 2026-10-23 (exposição medida em todo o período) e do simulador com várias fontes (spec 019). Só aparecem os números que mudaram.", ""]
    # normalização (spec 001 e 017)
    a, d = le("dados/derivados/eventos/resumo_normalizacao.json", ANTES), le("dados/derivados/eventos/resumo_normalizacao.json")
    if d:
        L += linhas_tabela("Normalização (specs 001 e 017)", [
            ("Falhas técnicas de uma linha", a and a["tecnicos_uma_linha"], d["tecnicos_uma_linha"]),
            ("Duração máxima (min)", a and a["duracao_max_min"], d["duracao_max_min"]),
            # na v1.1.0 a duração era a calculada pelos horários, que a 017 guarda em duracao_calculada_min
            ("Minutos parados das falhas técnicas", d.get("minutos_total_calculada"), d.get("minutos_total_final")),
            ("Minutos das 100 exceções (calculados → regra)", d.get("minutos_excecoes_calculada"), d.get("minutos_excecoes_final")),
        ], 0)
    # exposição (spec 004)
    a, d = le("dados/derivados/exposicao/resumo_exposicao.json", ANTES), le("dados/derivados/exposicao/resumo_exposicao.json")
    if a and d:
        L += linhas_tabela("Exposição (spec 004)", [(k, a.get(k), d.get(k)) for k in ("meses_comparados", "meses_com_erro_acima_de_10pct", "pct_meses_dentro", "dias_medidos", "dias_estimados")], 4)
    # painel (números do site)
    a, d = le("dados/derivados/painel/linhas.json", ANTES), le("dados/derivados/painel/linhas.json")
    if a and d:
        A, D = {x["linha"]: x for x in a}, {x["linha"]: x for x in d}
        campos = ("mttr_min", "mediana_ttr_min", "p90_ttr_min", "min_fora_ano", "disponibilidade", "a_markov", "pct_sem_interrupcao")
        L += linhas_tabela("Painel do site, por linha", [(f"{l} · {c}", A.get(l, {}).get(c), D.get(l, {}).get(c)) for l in LINHAS for c in campos], 4)
    a, d = le("dados/derivados/painel/corredor.json", ANTES), le("dados/derivados/painel/corredor.json")
    if a and d:
        A, D = {x["cenario"]: x for x in a}, {x["cenario"]: x for x in d}
        L += linhas_tabela("Painel do site: corredor Verde e Laranja (minutos por ano)", [(f"{k} · {c}", A[k].get(c), D[k].get(c)) for k in A for c in ("min_ano_analitico", "sim_min_ano")], 2)
    # modelo da taxa por família (spec 005)
    for c in ("MR", "EF"):
        a, d = le(f"dados/derivados/modelos/taxa_{c}.json", ANTES), le(f"dados/derivados/modelos/taxa_{c}.json")
        if a and d:
            ca, cd = coef(a), coef(d)
            termos = [t for t in ca if t != "const" and not t.endswith("sem_dado")]
            pares = [("α", a["alpha_nb"], d["alpha_nb"])] + [(f"multiplicador {t}", ca[t], cd.get(t)) for t in termos]
            pares += [(f"taxa-base {l} (falhas por trem-hora, 2025)", a["base_por_trem_hora"][l]["valor"], d["base_por_trem_hora"][l]["valor"]) for l in LINHAS[:4]]
            L += linhas_tabela(f"Modelo da taxa, família {c} (spec 005)", pares, 3,
                               "Mesma especificação da v1.1.0; muda a exposição (medida em todo o período) e, nos multiplicadores, só o que isso move.")
    # distribuições (spec 006)
    a, d = le("dados/derivados/modelos/distribuicoes.json", ANTES), le("dados/derivados/modelos/distribuicoes.json")
    if a and d:
        pares = [(f"forma da renovação {k}", a["reescala"][k]["weibull_reescalado"]["forma"], d["reescala"][k]["weibull_reescalado"]["forma"]) for k in a["reescala"]]
        pares += [(f"sem interrupção {k}", a["ttr"][k]["p_zero"], d["ttr"][k]["p_zero"]) for k in a["ttr"]]
        pares += [(f"duração média {k} (min)", a["ttr"][k]["media_min"], d["ttr"][k]["media_min"]) for k in a["ttr"]]
        pares += [(f"β {k} (1ª linha)", a["causa_comum"][k]["beta_a"], d["causa_comum"][k]["beta_a"]) for k in a["causa_comum"]]
        L += linhas_tabela("Tempo entre falhas, duração e causa comum (spec 006)", pares, 4)
        if "causa_comum_beta_familia" in d:
            L += ["### β com o denominador da família (novo, spec 018)", "", "| Par e família | Eventos | β da 1ª linha (IC 95%) | β da 2ª linha (IC 95%) |", "|---|---|---|---|"]
            for k, v in d["causa_comum_beta_familia"].items():
                L.append(f"| {k} | {v['eventos']} | {v['beta_a']:.4f} ({v['beta_a_ic95'][0]:.4f}–{v['beta_a_ic95'][1]:.4f}) | {v['beta_b']:.4f} ({v['beta_b_ic95'][0]:.4f}–{v['beta_b_ic95'][1]:.4f}) |".replace(".", ","))
            L.append("")
    # backtest (spec 012)
    a, d = le("dados/derivados/modelos/backtest.json", ANTES), le("dados/derivados/modelos/backtest.json")
    if a and d:
        pares = [(f"versão {v} · cobertura do IP 90%", a[v]["cobertura_total"]["cobertura"], d[v]["cobertura_total"]["cobertura"]) for v in a]
        pares += [(f"versão {v} · minutos previstos no 1º ano, {l} (mediana)", a[v]["minutos_ano"][l]["mediana"], d[v]["minutos_ano"][l]["mediana"]) for v in a for l in LINHAS[:4]]
        pares += [(f"versão {v} · minutos observados no 1º ano, {l}", a[v]["minutos_ano"][l]["observado"], d[v]["minutos_ano"][l]["observado"]) for v in a for l in LINHAS[:4]]
        L += linhas_tabela("Validação contra o histórico (spec 012), refeita após a revisão (pós-hoc)", pares, 3,
                           "Mesmas versões e regras da spec 012; mudam os dados de entrada (durações pela faixa oficial e exposição medida). O resultado oficial da spec 012 continua sendo o da v1.1.0.")
    # simulador (specs 008, 009)
    a, d = le("dados/derivados/simulador/politicas.json", ANTES), le("dados/derivados/simulador/politicas.json")
    if a and d:
        def folhas(o, p=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    yield from folhas(v, f"{p}.{k}" if p else k)
            elif isinstance(o, (int, float)) and not isinstance(o, bool):
                yield p, o
        fa, fd = dict(folhas(a)), dict(folhas(d))
        L += linhas_tabela("Simulador: políticas e Monte Carlo (specs 008 e 009)", [(k, fa[k], fd.get(k)) for k in fa if not k.endswith(("semente", "rodadas_por_politica", "rodadas_por_tipo_dia"))], 3)
    open(SAIDA, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("gravado", SAIDA)


if __name__ == "__main__":
    main()
