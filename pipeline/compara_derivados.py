"""Spec 013: compara os derivados refeitos do zero com os publicados, com tolerância numérica declarada.

Uso: python -I pipeline/compara_derivados.py <pasta_publicada> <pasta_refeita>
Bytes iguais → IGUAL. Senão, compara o conteúdo: texto e categorias exatos; números com tolerância relativa
(TOL_PADRAO, ou TOL_MODELOS para os ajustes com bootstrap e otimização, que variam no último dígito entre
plataformas e versões de BLAS). Sai com código 1 se algum arquivo passar da tolerância, faltar na pasta
refeita ou sobrar nela (arquivo gerado que não foi publicado).
"""
import csv
import gzip
import io
import json
import math
import os
import sys

TOL_PADRAO = 1e-9
TOL_MODELOS = 1e-3  # modelos/ e simulador/parametros.json: bootstrap, verossimilhança perfilada e BFGS
LENTOS = ("modelos/", "simulador/parametros.json")
IGNORAR = {"bootstrap_segundos", "segundos"}  # tempo de execução; o código (codigo_commit) é hash dos scripts e é comparado


def num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) or math.isnan(v) else v
    except (TypeError, ValueError):
        return None


def perto(a, b, tol):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    x, y = num(a), num(b)
    if x is None or y is None:
        return a == b
    if math.isnan(x) and math.isnan(y):
        return True
    return abs(x - y) <= tol * max(1.0, abs(x), abs(y))


def compara_json(a, b, tol, caminho, dif):
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            dif.append(f"{caminho}: chaves diferentes {sorted(set(a) ^ set(b))[:5]}")
        for k in set(a) & set(b):
            if k in IGNORAR:
                continue
            compara_json(a[k], b[k], tol, f"{caminho}/{k}", dif)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            dif.append(f"{caminho}: {len(a)} contra {len(b)} itens")
        for i, (x, y) in enumerate(zip(a, b)):
            compara_json(x, y, tol, f"{caminho}[{i}]", dif)
    elif not perto(a, b, tol):
        dif.append(f"{caminho}: {a!r} contra {b!r}")


def linhas_csv(caminho):
    dados = open(caminho, "rb").read()
    if caminho.endswith(".gz"):
        dados = gzip.decompress(dados)
    texto = dados.decode("utf-8")
    return list(csv.reader(io.StringIO(texto), delimiter=";" if texto.count(";") > texto.count(",") else ","))


def compara(pub, novo, rel):
    if open(pub, "rb").read() == open(novo, "rb").read():
        return "IGUAL", []
    tol = TOL_MODELOS if rel.startswith(LENTOS) else TOL_PADRAO
    dif = []
    if rel.endswith((".json", ".geojson")):
        compara_json(json.load(open(pub, encoding="utf-8")), json.load(open(novo, encoding="utf-8")), tol, rel, dif)
    elif rel.endswith((".csv", ".csv.gz", ".txt")):
        a, b = linhas_csv(pub), linhas_csv(novo)
        if len(a) != len(b):
            dif.append(f"{rel}: {len(a)} contra {len(b)} linhas")
        for i, (x, y) in enumerate(zip(a, b)):
            if len(x) != len(y) or not all(perto(p, q, tol) for p, q in zip(x, y)):
                dif.append(f"{rel} linha {i + 1}: {x[:6]} contra {y[:6]}")
    else:
        dif.append(f"{rel}: bytes diferentes (formato sem comparação numérica)")
    return ("DENTRO DA TOLERÂNCIA" if not dif else "DIFERE"), dif


def relativos(raiz_base):
    """Caminhos relativos (com /) de todos os arquivos sob raiz_base."""
    saida = set()
    for raiz, _, arquivos in os.walk(raiz_base):
        for nome in arquivos:
            saida.add(os.path.relpath(os.path.join(raiz, nome), raiz_base).replace(os.sep, "/"))
    return saida


def percorre(pub_raiz, novo_raiz):
    """Compara as duas pastas. Conta como problema: arquivo que difere, que falta na refeita
    ou que sobra na refeita (gerado pelo pipeline e ausente do publicado; achado 14 da rodada 3)."""
    problemas = 0
    pubs, novos = relativos(pub_raiz), relativos(novo_raiz)
    for rel in sorted(pubs | novos):
        if rel not in novos:
            print(f"  FALTA   {rel}")
            problemas += 1
            continue
        if rel not in pubs:
            print(f"  SOBRA   {rel}")
            problemas += 1
            continue
        estado, dif = compara(os.path.join(pub_raiz, rel), os.path.join(novo_raiz, rel), rel)
        problemas += estado == "DIFERE"
        print(f"  {estado:<20} {rel}")
        for d in dif[:5]:
            print(f"      {d}")
        if len(dif) > 5:
            print(f"      ... mais {len(dif) - 5} diferenças")
    return problemas


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    problemas = percorre(sys.argv[1], sys.argv[2])
    print(f"  -> {problemas} arquivo(s) fora da tolerância, faltando ou sobrando (padrão {TOL_PADRAO}, modelos {TOL_MODELOS})")
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()
