"""Verificacao das fontes de dados do projeto: integridade, origem e recalculo dos numeros publicados.

Uso (da raiz do repositorio):
  python -I pipeline/verifica_fontes.py                    confere SHA-256 dos arquivos locais contra fontes/fontes_manifesto.json
  python -I pipeline/verifica_fontes.py --baixa-release    baixa os dados brutos da Release do GitHub e confere cada hash
  python -I pipeline/verifica_fontes.py --online           baixa de novo cada fonte na origem e compara com a copia local
  python -I pipeline/verifica_fontes.py --baixa-origem     baixa para dados/brutos as fontes que nao vao na Release (--completo inclui as grandes)
  python -I pipeline/verifica_fontes.py --recalcula        recalcula dos dados brutos numeros publicados, sem usar os scripts de analise
  python -I pipeline/verifica_fontes.py --gera-manifesto   regrava o manifesto a partir dos arquivos atuais

Sai com codigo 1 se algum arquivo distribuido faltar ou divergir, ou se algum numero recalculado nao bater.
Python puro, de proposito: e a segunda implementacao, independente do pipeline (constituicao, principio IV).
"""
import csv
import hashlib
import json
import os
import sys
import tempfile
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MANIFESTO = "fontes/fontes_manifesto.json"
REPO = "felipe44776-eseg/confiabilidade-metro-montreal"
RELEASE = "dados-2026-10-20"       # fontes da fase 0
RELEASE_F1 = "dados-2026-10-21"    # fontes acrescentadas na fase 1 (clima horário, expansão)
B = "dados/brutos"
D = "dados/derivados"
ECCC = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=51157&Year={ano}&Month=1&Day=1&time=&timeframe=2&submit=Download+Data"
WB = "https://web.archive.org/web/{ts}id_/{url}"
RA = {
    2019: ("20200813103544", "http://stm.info/fr/a-propos/informations-entreprise-et-financieres/rapport-annuel-2019/rapport-dactivite-2019"),
    2020: ("20210419053621", "http://www.stm.info/fr/a-propos/informations-entreprise-et-financieres/rapport-annuel-2020/rapport-dactivite-2020"),
    2021: ("20220811145211", "https://www.stm.info/fr/a-propos/informations-entreprise-et-financieres/rapport-annuel-2021/rapport-dactivite-2021"),
    2022: ("20230609165442", "https://www.stm.info/fr/a-propos/informations-entreprise-et-financieres/rapport-annuel-2022/rapport-dactivite-2022"),
    2023: ("20240502220012", "https://www.stm.info/fr/a-propos/informations-entreprise-et-financieres/rapport-annuel-2023/rapport-dactivite"),
}
OVERPASS_Q = ('[out:json][timeout:150];(relation["route"="subway"](45.40,-73.80,45.62,-73.45);)->.r;.r out body geom;'
              'node["railway"="station"]["station"="subway"](45.40,-73.80,45.62,-73.45);out body;')
WIKIDATA_Q = ('SELECT ?s ?sLabel ?coord WHERE { ?s wdt:P16 wd:Q392377; wdt:P625 ?coord. ?s wdt:P31/wdt:P279* wd:Q928830. '
              'SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". } }')
OVERPASS_EXP_Q = ('[out:json][timeout:120];('
                  'way["railway"="construction"]["construction"="subway"](45.40,-73.90,45.70,-73.40);'
                  'way["railway"="proposed"]["proposed"="subway"](45.40,-73.90,45.70,-73.40);'
                  'node["railway"="construction"](45.40,-73.90,45.70,-73.40);'
                  'node["construction:railway"="station"](45.40,-73.90,45.70,-73.40);'
                  'node["railway"="station"]["construction"="yes"](45.40,-73.90,45.70,-73.40);'
                  'node["public_transport"="station"]["subway"="yes"]["construction"](45.40,-73.90,45.70,-73.40);'
                  ');out body geom;')
ECCC_H = ("https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={est}&Year={ano}&Month={mes}"
          "&Day=1&timeframe=1&submit=Download+Data")
ECCC_ESTACOES = {"10761": "MCTAVISH (Climate ID 7024745)", "30165": "MONTREAL/PIERRE ELLIOTT TRUDEAU INTL (Climate ID 7025250)",
                 "51157": "MONTREAL INTL A (Climate ID 7025251)"}

# distribuicao: "release" = copia exata publicada na Release do GitHub; "origem" = baixar da fonte (licenca nao permite
# redistribuir ou nao foi verificada); "terceiros" = arquivo de biblioteca versionado no repositorio.
FONTES = [
    {"id": "stm_incidentes", "papel": "painel e simulador", "arquivo": f"{B}/stm/incidents_metro.csv", "distribuicao": "release",
     "url": "https://donneesouvertes.stm.info/fichiers/Incidents%20m%C3%A9tro.csv",
     "catalogo": ["https://www.donneesquebec.ca/recherche/dataset/vmtl-incidents-du-reseau-du-metro",
                  "https://donnees.montreal.ca/dataset/incidents-du-reseau-du-metro"],
     "editor": "Société de transport de Montréal (STM)", "licenca": "CC BY 4.0", "formato": "csv;", "pula_linhas": 1,
     "uso": "Todas as falhas, tempos e duracoes; locais dos incidentes (geo_base.py)"},
    {"id": "stm_km_reel", "papel": "painel e simulador", "arquivo": f"{B}/stm/km_reel.csv", "distribuicao": "release",
     "url": "https://donneesouvertes.stm.info/fichiers/Kilom%C3%A9trage%20r%C3%A9el.csv",
     "catalogo": ["https://donnees.montreal.ca/dataset/stm-kilometrage-realise-par-les-voitures-de-metro-de-la-stm"],
     "editor": "STM", "licenca": "CC BY 4.0", "formato": "csv,",
     "uso": "Exposicao (km-carro) por linha e frota, trens em servico por dia, taxas por km, modelo k-de-n"},
    {"id": "stm_km_planifie", "papel": "apoio", "arquivo": f"{B}/stm/km_planifie.csv", "distribuicao": "release",
     "url": "https://donneesouvertes.stm.info/fichiers/Kilom%C3%A9trage%20m%C3%A9tro%20planif%C3%A9.csv",
     "catalogo": ["https://donnees.montreal.ca/dataset/stm-kilometrage-metro-des-periodes-de-service"],
     "editor": "STM", "licenca": "CC BY 4.0", "formato": "csv,",
     "uso": "Km planejado e tipo de dia no painel diario (monta_painel.py)"},
    {"id": "stm_km_budgete", "papel": "nao usado", "arquivo": f"{B}/stm/km_budgete.csv", "distribuicao": "release",
     "url": "https://donneesouvertes.stm.info/fichiers/Kilom%C3%A9trage%20m%C3%A9tro%20budg%C3%A9t%C3%A9.csv",
     "catalogo": ["https://donnees.montreal.ca/dataset/stm-kilometrage-du-budget-d-exploitation-du-metro-de-la-stm"],
     "editor": "STM", "licenca": "CC BY 4.0", "formato": "bruto",
     "uso": "Baixado e descartado: substituido pelo km real"},
    {"id": "gtfs_stm", "papel": "painel e simulador", "arquivo": f"{B}/gtfs/gtfs_stm_mdb-2126_latest.zip", "distribuicao": "release",
     "url": "https://files.mobilitydatabase.org/mdb-2126/latest.zip",
     "catalogo": ["https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip (original, inacessivel desta maquina)",
                  "https://files.mobilitydatabase.org/feeds_v2.csv (catalogo do Mobility Database, feed mdb-2126)"],
     "editor": "STM, espelhado pelo Mobility Database", "licenca": "CC BY 4.0 (STM)", "formato": "zip", "muda_com_tempo": True,
     "uso": "Estacoes, horarios e coordenadas (extrai_gtfs_metro.py)"},
    {"id": "osm_metro", "papel": "simulador", "arquivo": f"{B}/osm/overpass_metro_mtl.json", "distribuicao": "release",
     "url": "https://overpass-api.de/api/interpreter", "post": {"data": OVERPASS_Q},
     "catalogo": ["https://www.openstreetmap.org/relation/58433 (exemplo: linha verde)"],
     "editor": "Colaboradores do OpenStreetMap", "licenca": "ODbL 1.0", "formato": "json", "muda_com_tempo": True,
     "uso": "Tracado real das linhas e nos de estacao (geo_base.py)"},
    {"id": "wikidata_estacoes", "papel": "validacao", "arquivo": f"{B}/wikidata/estacoes_metro_mtl.json", "distribuicao": "release",
     "url": "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": WIKIDATA_Q}), "aceita": "application/sparql-results+json",
     "catalogo": ["https://www.wikidata.org/wiki/Q392377"],
     "editor": "Wikidata", "licenca": "CC0", "formato": "json", "muda_com_tempo": True,
     "uso": "Segunda referencia de coordenadas das estacoes (geo_base.py)"},
    {"id": "google_mobilidade", "papel": "painel", "arquivo": f"{B}/google/google_Region_Mobility_Report_CSVs.zip", "distribuicao": "origem",
     "url": "https://www.gstatic.com/covid19/mobility/Region_Mobility_Report_CSVs.zip",
     "catalogo": ["https://www.google.com/covid19/mobility/"],
     "editor": "Google LLC", "licenca": "Termos do Google, com citacao; redistribuicao nao verificada", "formato": "zip", "grande": True,
     "uso": "Correlacao diaria com mobilidade em estacoes (extrai_mobilidade.py)"},
]
for ano in range(2019, 2027):
    FONTES.append({"id": f"eccc_{ano}", "papel": "painel e simulador", "arquivo": f"{B}/eccc/eccc_diario_{ano}.csv", "distribuicao": "release",
                   "url": ECCC.format(ano=ano), "catalogo": ["https://climate.weather.gc.ca/historical_data/search_historic_data_e.html"],
                   "editor": "Environment and Climate Change Canada, estacao MONTREAL INTL A (Climate ID 7025251)",
                   "licenca": "Licenca de Governo Aberto do Canada", "formato": "csv,", "muda_com_tempo": ano == 2026,
                   "uso": "Temperatura e neve por dia (perfil e correlacoes)"})
for ano in range(2019, 2027):
    FONTES.append({"id": f"nager_{ano}", "papel": "apoio", "arquivo": f"{B}/nager/nager_CA_{ano}.json", "distribuicao": "origem",
                   "url": f"https://date.nager.at/api/v3/PublicHolidays/{ano}/CA", "catalogo": ["https://date.nager.at/"],
                   "editor": "Nager.Date", "licenca": "nao verificada", "formato": "json",
                   "uso": "Feriados no painel diario"})
for ano, (ts, url) in RA.items():
    FONTES.append({"id": f"stm_relatorio_{ano}", "papel": "apoio", "arquivo": f"{B}/stm_relatorios/ra{ano}.html", "distribuicao": "origem",
                   "url": WB.format(ts=ts, url=url), "catalogo": [url + " (original, inacessivel desta maquina)"],
                   "editor": "STM, copia do Internet Archive", "licenca": "Documento publico da STM; redistribuicao nao verificada", "formato": "html",
                   "uso": "Totais anuais de entradas citados na documentacao; nao entra no painel"})
# Fase 1 (specs 003 e 014). Clima horário: os 90 CSV mensais de cada estação vão num zip determinístico;
# a verificação online baixa dois meses de amostra e compara com o membro do zip.
for est, nome in ECCC_ESTACOES.items():
    FONTES.append({"id": f"eccc_horario_{est}", "papel": "simulador", "arquivo": f"{B}/eccc_horario/eccc_horario_{est}.zip",
                   "distribuicao": "release", "release_tag": RELEASE_F1, "url": ECCC_H.format(est=est, ano=2019, mes=1),
                   "online_amostra": [[ECCC_H.format(est=est, ano=a, mes=m), f"{est}/{a}-{m:02d}.csv"] for a, m in ((2019, 1), (2025, 12))],
                   "catalogo": ["https://climate.weather.gc.ca/historical_data/search_historic_data_e.html"],
                   "editor": f"Environment and Climate Change Canada, estacao {nome}", "licenca": "Licenca de Governo Aberto do Canada",
                   "formato": "zip", "uso": "Clima horario 2019-01 a 2026-06, 90 meses (pipeline/clima_eventos.py, spec 003)"})
FONTES.append({"id": "osm_expansao", "papel": "simulador", "arquivo": f"{B}/osm/overpass_expansao.json", "distribuicao": "release",
               "release_tag": RELEASE_F1, "url": "https://overpass-api.de/api/interpreter", "post": {"data": OVERPASS_EXP_Q},
               "catalogo": ["https://www.openstreetmap.org/way/492375119 (Ligne Bleue, prolongement)"],
               "editor": "Colaboradores do OpenStreetMap", "licenca": "ODbL 1.0", "formato": "json", "muda_com_tempo": True,
               "uso": "Trechos de metro em obras ou propostos: candidatas da spec 014"})
for ano in range(2018, 2026):
    t = f"{ano}{ano + 1}"
    FONTES.append({"id": f"nhl_{t}", "papel": "simulador", "arquivo": f"{B}/eventos/nhl_MTL_{t}.json", "distribuicao": "origem",
                   "url": f"https://api-web.nhle.com/v1/club-schedule-season/MTL/{t}", "catalogo": ["https://www.nhl.com/canadiens/schedule"],
                   "editor": "National Hockey League (API publica nao documentada)", "licenca": "Termos da NHL; redistribuicao nao verificada",
                   "formato": "json", "muda_com_tempo": ano == 2025, "uso": "Jogos do Canadiens em casa (clima_eventos.py)"})
FONTES.append({"id": "f1_villeneuve", "papel": "simulador", "arquivo": f"{B}/eventos/f1_villeneuve.json", "distribuicao": "origem",
               "url": "https://api.jolpi.ca/ergast/f1/circuits/villeneuve/races.json?limit=100", "catalogo": ["https://github.com/jolpica/jolpica-f1"],
               "editor": "Jolpica (base comunitaria sucessora da Ergast)", "licenca": "nao verificada", "formato": "json", "muda_com_tempo": True,
               "uso": "Datas do GP do Canada (clima_eventos.py)"})
FONTES.append({"id": "greves_stm", "papel": "simulador", "arquivo": "dados/manuais/greves_stm.csv", "distribuicao": "repositorio", "manual": True,
               "url": "dados/manuais/LEIAME.md (uma URL de imprensa por linha)", "catalogo": [],
               "editor": "Tabela manual do projeto a partir da imprensa", "licenca": "fatos publicos; tabela do projeto", "formato": "csv;",
               "uso": "Faixas com servico nos dias de greve de 2025 (exposicao.py, clima_eventos.py)"})
FONTES.append({"id": "candidatas_expansao", "papel": "simulador", "arquivo": "dados/manuais/candidatas_expansao.csv", "distribuicao": "repositorio",
               "manual": True, "url": "dados/manuais/candidatas_expansao_LEIAME.md (URLs por linha; respostas em dados/brutos/expansao/manifesto.json)",
               "catalogo": [], "editor": "Tabela do projeto: coordenadas do OSM (ODbL) e do Wikidata (CC0), traçados de documentos públicos",
               "licenca": "ODbL 1.0 (coordenadas do OSM)", "formato": "csv;", "uso": "Linhas candidatas da spec 014"})
FONTES.append({"id": "d3", "papel": "painel", "arquivo": "painel/vendor/d3.v7.9.0.min.js", "distribuicao": "terceiros",
               "url": "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js", "catalogo": ["https://github.com/d3/d3"],
               "editor": "Mike Bostock e colaboradores", "licenca": "ISC", "formato": "js",
               "uso": "Graficos do painel, embutidos no site publico (gera_site.py)"})

PAINEL = ("linhas", "ajustes", "tbf_curvas", "tbf_hist", "anual", "frota_anual", "ttr_faixas", "perfil", "correlacoes",
          "locais", "pareto", "causa_comum", "corredor", "sim_hist", "sim_amostra", "kdn", "estacoes")
DERIVADOS = [
    {"arquivo": f"{D}/gtfs/metro_sequencias.csv", "de": ["gtfs_stm"], "script": "pipeline/extrai_gtfs_metro.py"},
    {"arquivo": f"{D}/gtfs/stops.txt", "de": ["gtfs_stm"], "script": "pipeline/extrai_gtfs_metro.py"},
    {"arquivo": f"{D}/mobilidade/google_mobilidade_montreal_2020_2022.csv", "de": ["google_mobilidade"], "script": "pipeline/extrai_mobilidade.py"},
    {"arquivo": f"{D}/painel_diario_linha.csv", "de": ["stm_incidentes", "stm_km_reel", "stm_km_planifie", "eccc_*", "nager_*", "google_mobilidade"],
     "script": "pipeline/monta_painel.py"},
] + [{"arquivo": f"{D}/painel/{n}.json", "de": ["stm_incidentes", "stm_km_reel", "eccc_*", "google_mobilidade", "gtfs_stm"],
      "script": "pipeline/analise_confiabilidade.py"} for n in PAINEL] + [
    {"arquivo": f"{D}/geo/{n}", "de": ["osm_metro", "wikidata_estacoes", "gtfs_stm", "stm_incidentes"], "script": "pipeline/geo_base.py"}
    for n in ("linhas.geojson", "estacoes.geojson", "locais.json")] + [
    {"arquivo": f"{D}/eventos/{n}", "de": ["stm_incidentes"], "script": "pipeline/normaliza.py"}
    for n in ("eventos_tecnicos.csv", "eventos_causa_comum.csv", "eventos_sem_linha.csv", "excecoes.csv", "resumo_normalizacao.json")] + [
    {"arquivo": f"{D}/exposicao/{n}", "de": ["gtfs_stm", "stm_km_reel", "nager_*", "greves_stm"], "script": "pipeline/exposicao.py"}
    for n in ("perfil_horario.csv", "exposicao_diaria.csv", "calibracao_mensal.csv", "frota_mensal.csv", "resumo_exposicao.json")] + [
    {"arquivo": f"{D}/clima/{n}", "de": ["eccc_horario_*", "eccc_*", "nhl_*", "f1_villeneuve", "nager_*", "greves_stm"], "script": "pipeline/clima_eventos.py"}
    for n in ("painel_horario.csv", "eventos_externos.csv", "resumo_clima.json")] + [
    {"arquivo": f"{D}/modelos/{n}", "de": ["stm_incidentes", "gtfs_stm", "stm_km_reel", "eccc_horario_*", "nhl_*", "f1_villeneuve", "greves_stm"],
     "script": "pipeline/modelo_taxa.py"} for n in ("taxa_MR.json", "taxa_EF.json", "painel_modelo.csv.gz")] + [
    {"arquivo": f"{D}/modelos/distribuicoes.json", "de": ["stm_incidentes"], "script": "pipeline/distribuicoes.py"},
    {"arquivo": f"{D}/simulador/rede.json", "de": ["gtfs_stm", "osm_metro"], "script": "pipeline/horario_simulador.py"},
    {"arquivo": f"{D}/simulador/parametros.json", "de": ["stm_incidentes", "stm_km_reel", "gtfs_stm", "eccc_horario_*"], "script": "pipeline/parametros.py"},
    {"arquivo": f"{D}/simulador/candidatas.json", "de": ["candidatas_expansao", "gtfs_stm", "osm_metro"], "script": "pipeline/candidatas.py"},
    {"arquivo": f"{D}/modelos/comparacao_mr_ef.json", "de": ["stm_incidentes", "eccc_horario_*"], "script": "pipeline/modelo_taxa.py"},
    {"arquivo": f"{D}/modelos/backtest.json", "de": ["stm_incidentes", "gtfs_stm", "stm_km_reel", "eccc_horario_*"], "script": "pipeline/backtest.py"},
    {"arquivo": f"{D}/simulador/politicas.json", "de": ["stm_incidentes", "gtfs_stm", "stm_km_reel", "eccc_horario_*"], "script": "app/relatorios/politicas.relatorio.ts"},
    {"arquivo": f"{D}/simulador/expansao.json", "de": ["stm_incidentes", "gtfs_stm", "candidatas_expansao", "osm_metro"], "script": "app/relatorios/expansao.relatorio.ts"},
]


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def contar_linhas(caminho, formato, pula=0):
    if not formato.startswith("csv"):
        return None
    with open(caminho, encoding="utf-8-sig", errors="replace", newline="") as f:
        linhas = list(csv.reader(f, delimiter=formato[3:] or ","))
    dados = [r for r in linhas[1 + pula:] if any(c.strip() for c in r)]
    return {"linhas": len(dados), "colunas": [c for c in linhas[pula] if c.strip()]}


def baixar(url, destino, post=None, aceita=None, limite=300):
    cab = {"User-Agent": "ESEG-SistemasTolerantesFalha/1.0 (verificacao academica)"}
    if aceita:
        cab["Accept"] = aceita
    corpo = urllib.parse.urlencode(post).encode() if post else None
    req = urllib.request.Request(url, data=corpo, headers=cab)
    with urllib.request.urlopen(req, timeout=limite) as r, open(destino, "wb") as f:
        while True:
            bloco = r.read(1 << 20)
            if not bloco:
                break
            f.write(bloco)
        return r.status


def url_release(e):
    return f"https://github.com/{REPO}/releases/download/{e.get('release_tag', RELEASE)}/{os.path.basename(e['arquivo'])}"


def gera_manifesto():
    entradas = []
    for fo in FONTES:
        e = dict(fo)
        if e["distribuicao"] == "release":
            e["release"] = url_release(e)
        if os.path.exists(fo["arquivo"]):
            e["bytes"] = os.path.getsize(fo["arquivo"])
            e["sha256"] = sha256(fo["arquivo"])
            c = contar_linhas(fo["arquivo"], fo["formato"], fo.get("pula_linhas", 0))
            if c:
                e.update(c)
        else:
            e["ausente"] = True
        entradas.append(e)
    derivados = []
    for d in DERIVADOS:
        e = dict(d)
        if os.path.exists(d["arquivo"]):
            e["bytes"] = os.path.getsize(d["arquivo"])
            e["sha256"] = sha256(d["arquivo"])
        derivados.append(e)
    releases = sorted({e.get("release_tag", RELEASE) for e in entradas if e["distribuicao"] == "release"})
    json.dump({"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "release": RELEASE, "releases": releases,
               "fontes": entradas, "derivados": derivados}, open(MANIFESTO, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(f"{MANIFESTO}: {len(entradas)} fontes primarias, {len(derivados)} arquivos derivados")


def baixa_release(man):
    print(f"== Download da Release {man['release']}")
    problemas = 0
    for e in man["fontes"]:
        if e.get("distribuicao") != "release":
            continue
        os.makedirs(os.path.dirname(e["arquivo"]), exist_ok=True)
        try:
            baixar(e["release"], e["arquivo"])
        except Exception as ex:
            print(f"  ERRO    {e['id']}: {ex}")
            problemas += 1
            continue
        ok = sha256(e["arquivo"]) == e["sha256"]
        problemas += not ok
        print(f"  {'OK     ' if ok else 'DIFERE '} {e['id']}")
    return problemas


def baixa_origem(man):
    """Baixa da origem as fontes que não vão na Release (licença não verificada). Mudança na origem é aviso, não erro."""
    print("== Download das fontes de origem (não redistribuídas)")
    for e in man["fontes"]:
        if e.get("distribuicao") != "origem":
            continue
        if e.get("grande") and "--completo" not in sys.argv:
            print(f"  PULADA  {e['id']}: arquivo grande; use --completo")
            continue
        os.makedirs(os.path.dirname(e["arquivo"]), exist_ok=True)
        st, erro = baixar_valido(e, e["arquivo"] + ".parcial")
        if erro:
            print(f"  ERRO    {e['id']}: {erro}")
            continue
        os.replace(e["arquivo"] + ".parcial", e["arquivo"])
        igual = sha256(e["arquivo"]) == e.get("sha256")
        print(f"  {'IGUAL  ' if igual else 'MUDOU  '} {e['id']}" + ("" if igual else " (a origem mudou desde o manifesto; derivados podem diferir)"))


def confere_local(man):
    print("== Integridade local (SHA-256 contra o manifesto)")
    problemas = 0
    for e in man["fontes"] + man["derivados"]:
        if "sha256" not in e:
            continue
        distribuido = e.get("distribuicao", "repositorio") in ("release", "terceiros", "repositorio")
        if not os.path.exists(e["arquivo"]):
            if distribuido:
                print(f"  FALTA   {e['arquivo']}")
                problemas += 1
            else:
                print(f"  ORIGEM  {e['arquivo']} (nao distribuido: baixar da origem para conferir)")
            continue
        ok = sha256(e["arquivo"]) == e["sha256"]
        problemas += not ok
        print(f"  {'OK     ' if ok else 'DIFERE '} {e['arquivo']}")
    print(f"  -> {problemas} problema(s)")
    return problemas


def conteudo_valido(e, caminho):
    """O servidor do ECCC as vezes devolve uma pagina HTML no lugar do CSV: confere a 1a coluna esperada."""
    if e["formato"].startswith("csv") and e.get("colunas"):
        with open(caminho, encoding="utf-8-sig", errors="replace") as f:
            cabecalho = [f.readline() for _ in range(e.get("pula_linhas", 0) + 1)][-1]
        return e["colunas"][0] in cabecalho
    return True


def baixar_valido(e, destino, tentativas=3):
    """Baixa com novas tentativas: conteudo invalido espera 10 s; HTTP 429 espera o Retry-After (ou 65 s)."""
    import time
    import urllib.error
    st, erro = None, None
    for n in range(tentativas):
        try:
            st = baixar(e["url"], destino, e.get("post"), e.get("aceita"))
        except urllib.error.HTTPError as ex:
            st, erro = None, f"HTTP {ex.code}: {ex.reason}"
            if ex.code == 429 and n + 1 < tentativas:
                time.sleep(int(ex.headers.get("Retry-After") or 65))
                continue
            return st, erro
        except Exception as ex:
            return None, str(ex)
        if conteudo_valido(e, destino):
            return st, None
        erro = "o servidor devolveu outro conteúdo no lugar do arquivo esperado (ex.: página HTML)"
        time.sleep(10)
    return st, erro


def confere_online(man):
    print("== Fontes na internet (baixa de novo e compara com a copia do manifesto)")
    tmp = tempfile.mkdtemp(prefix="verifica_fontes_")
    for e in man["fontes"]:
        if e.get("manual"):
            print(f"  MANUAL  {e['id']}: tabela do projeto; as URLs de cada linha estao no proprio arquivo")
            continue
        if e.get("online_amostra"):
            import zipfile
            for url, membro in e["online_amostra"]:
                destino = os.path.join(tmp, e["id"] + "_" + os.path.basename(membro))
                st, erro = baixar_valido({**e, "url": url, "formato": "csv,", "colunas": ["Longitude (x)"]}, destino)
                if erro:
                    print(f"  {'INVALIDO' if st else 'ERRO    '} {e['id']} {membro}: {erro}")
                    continue
                local = hashlib.sha256(zipfile.ZipFile(e["arquivo"]).read(membro)).hexdigest()
                print(f"  {'IGUAL  ' if sha256(destino) == local else 'MUDOU  '} {e['id']} {membro}: HTTP {st} (amostra do zip)")
            continue
        if e.get("grande") and "--completo" not in sys.argv:
            try:
                req = urllib.request.Request(e["url"], method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    tam = int(r.headers.get("Content-Length", -1))
                print(f"  {'IGUAL  ' if tam == e.get('bytes') else 'TAMANHO'} {e['id']}: HTTP {r.status}, {tam} bytes (manifesto {e.get('bytes')}); use --completo para o hash")
            except Exception as ex:
                print(f"  ERRO    {e['id']}: {ex}")
            continue
        destino = os.path.join(tmp, e["id"])
        st, erro = baixar_valido(e, destino)
        if erro:
            print(f"  {'INVALIDO' if st else 'ERRO    '} {e['id']}: {erro}")
            continue
        if sha256(destino) == e.get("sha256"):
            print(f"  IGUAL   {e['id']}: HTTP {st}, conteudo identico")
            continue
        extra = ""
        c_novo = contar_linhas(destino, e["formato"], e.get("pula_linhas", 0))
        if c_novo and "linhas" in e:
            extra = f" | linhas: manifesto {e['linhas']}, agora {c_novo['linhas']}"
        aviso = "esperado: a fonte e atualizada; vale o snapshot da Release" if e.get("muda_com_tempo") or e["id"].startswith("stm_") else "verificar"
        print(f"  MUDOU   {e['id']}: HTTP {st}, hash diferente ({aviso}){extra}")


def recalcula():
    """Refaz dos dados brutos numeros publicados, com codigo proprio (nao importa nada do pipeline)."""
    print("== Recalculo independente de numeros publicados")
    pub = {r["linha"]: r for r in json.load(open(f"{D}/painel/linhas.json", encoding="utf-8"))}
    with open(f"{B}/stm/incidents_metro.csv", encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    cab = linhas[1]
    ev = [dict(zip(cab, (c.strip() for c in r))) for r in linhas[2:] if len(r) >= len(cab) and r[0].strip()]
    nomes = {"Ligne verte": "verde", "Ligne orange": "laranja", "Ligne jaune": "amarela", "Ligne bleue": "azul"}
    tecnica = ("Matériel roulant", "Équipements fixes")
    tec = [e for e in ev if e["Cause primaire"] in tecnica and e["Ligne"] in nomes]
    fora = [e for e in ev if e["Cause primaire"] in tecnica and e["Ligne"] not in nomes]
    multi = [e for e in fora if sum(ch.isdigit() for ch in e["Ligne"]) >= 2]
    dias = (date(2026, 6, 30) - date(2019, 1, 1)).days + 1
    datas = sorted(e["Jour calendaire"] for e in ev)
    checks = [("incidentes no arquivo (todas as causas)", len(ev), 45785),
              ("periodo", f"{datas[0]} a {datas[-1]}", "2019-01-01 a 2026-06-30"),
              ("falhas tecnicas de uma linha (rede)", len(tec), pub["rede"]["falhas"]),
              ("tecnicos fora: sem linha", len(fora) - len(multi), pub["rede"]["tecnicos_sem_linha"]),
              ("tecnicos fora: mais de uma linha", len(multi), pub["rede"]["tecnicos_multilinha"]),
              ("MTBF da rede, h de operacao (20 h/dia)", round(dias * 20 / len(tec), 2), pub["rede"]["mtbf_op_h"])]
    for chave, l in nomes.items():
        checks.append((f"falhas tecnicas, linha {l}", sum(1 for e in tec if e["Ligne"] == chave), pub[l]["falhas"]))
        checks.append((f"falhas de material rodante, linha {l}",
                       sum(1 for e in tec if e["Ligne"] == chave and e["Cause primaire"] == "Matériel roulant"), pub[l]["falhas_mr"]))
    km = 0.0
    with open(f"{B}/stm/km_reel.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["Ligne"] in nomes:
                try:
                    km += float(r["Km voiture"].replace(",", "."))
                except ValueError:
                    pass
    checks.append(("km-carro real 2019-01 a 2023-09 (milhoes)", round(km / 1e6, 2), pub["rede"]["km_carro_milhoes"]))
    # Base geoespacial (spec 002)
    with open(f"{D}/gtfs/metro_sequencias.csv", encoding="utf-8") as f:
        est_gtfs = sum(1 for r in csv.DictReader(f, delimiter=";") if r["direction_id"] == "0")
    est_geo = len(json.load(open(f"{D}/geo/estacoes.geojson", encoding="utf-8"))["features"])
    checks.append(("estacoes no GTFS (sentido 0) e no estacoes.geojson", est_gtfs, est_geo))
    soma_locais = sum(x["n_tecnicos"] for x in json.load(open(f"{D}/geo/locais.json", encoding="utf-8")))
    checks.append(("falhas tecnicas somadas em locais.json", len(tec), soma_locais))
    cont_local = Counter(e["Code de lieu"] for e in tec)
    checks.append(("falhas no codigo 4S50 (plataforma da Amarela em Berri-UQAM)", cont_local["4S50"],
                   next(x["n_tecnicos"] for x in json.load(open(f"{D}/geo/locais.json", encoding="utf-8")) if x["codigo"] == "4S50")))
    # Fase 1 (specs 001, 003 e 004): mesmos números por outro caminho, direto dos brutos
    import io
    import zipfile
    if os.path.exists(f"{D}/eventos/eventos_tecnicos.csv"):
        with open(f"{D}/eventos/eventos_tecnicos.csv", encoding="utf-8") as f:
            checks.append(("eventos normalizados (spec 001) contra falhas tecnicas de uma linha", sum(1 for _ in csv.DictReader(f, delimiter=";")), len(tec)))
        resumo = json.load(open(f"{D}/eventos/resumo_normalizacao.json", encoding="utf-8"))
        checks.append(("falhas tecnicas iniciadas depois da meia-noite (24:xx ou 25:xx)",
                       sum(1 for e in tec if int(e["Heure de l'incident"][:2]) >= 24), resumo["inicio_depois_da_meia_noite"]))
    if os.path.exists(f"{D}/exposicao/resumo_exposicao.json"):
        z = zipfile.ZipFile(f"{B}/gtfs/gtfs_stm_mdb-2126_latest.zip")
        rota = {"1": "verde", "2": "laranja", "4": "amarela", "5": "azul"}
        viagens = {t["trip_id"]: rota[t["route_id"]] for t in csv.DictReader(io.TextIOWrapper(z.open("trips.txt"), encoding="utf-8-sig"))
                   if t["route_id"] in rota and t["service_id"] == "26N-GLOBAUX-01-S"}
        ini, fim = {}, {}
        seg = lambda s: sum(int(x) * m for x, m in zip(s.split(":"), (3600, 60, 1)))
        for st in csv.DictReader(io.TextIOWrapper(z.open("stop_times.txt"), encoding="utf-8-sig")):
            if st["trip_id"] in viagens:
                ini[st["trip_id"]] = min(ini.get(st["trip_id"], 10 ** 9), seg(st["departure_time"]))
                fim[st["trip_id"]] = max(fim.get(st["trip_id"], -1), seg(st["arrival_time"]))
        em = Counter(viagens[t] for t in viagens if ini[t] <= 8 * 3600 < fim[t])
        publ = json.load(open(f"{D}/exposicao/resumo_exposicao.json", encoding="utf-8"))["trens_em_viagem_08h_dia_util"]
        for l in ("verde", "laranja", "amarela", "azul"):
            checks.append((f"trens em viagem as 08:00 de dia util, linha {l} (GTFS)", em[l], publ[l]))
    if os.path.exists(f"{D}/clima/painel_horario.csv") and os.path.exists(f"{B}/eccc_horario/eccc_horario_51157.zip"):
        bruto = zipfile.ZipFile(f"{B}/eccc_horario/eccc_horario_51157.zip").read("51157/2023-04.csv").decode("utf-8-sig")
        horas = sum(1 for r in csv.DictReader(io.StringIO(bruto))
                    if r["Date/Time (LST)"][:10] == "2023-04-05" and 9 <= int(r["Date/Time (LST)"][11:13]) <= 20 and "Freezing Rain" in r["Weather"])
        with open(f"{D}/clima/painel_horario.csv", encoding="utf-8") as f:
            painel = sum(1 for r in csv.DictReader(f, delimiter=";")
                         if "2023-04-05T14:00Z" <= r["inicio_utc"] <= "2023-04-06T01:00Z" and r["chuva_congelante"] == "1")
        checks.append(("horas de chuva congelante em 2023-04-05, 09h-20h LST (ECCC 51157)", horas, painel))
    problemas = 0
    for nome, calc, publicado in checks:
        ok = str(calc) == str(publicado) or (isinstance(calc, float) and abs(calc - float(publicado)) < 0.011)
        problemas += not ok
        print(f"  {'OK    ' if ok else 'DIFERE'} {nome}: recalculado {calc} | publicado {publicado}")
    print(f"  -> {problemas} diferenca(s)")
    return problemas


if "--gera-manifesto" in sys.argv:
    gera_manifesto()
    sys.exit(0)
man = json.load(open(MANIFESTO, encoding="utf-8"))
print(f"manifesto gerado em {man['gerado_em']} | verificacao em {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
falhas = 0
if "--baixa-release" in sys.argv:
    falhas += baixa_release(man)
if "--baixa-origem" in sys.argv:
    baixa_origem(man)
falhas += confere_local(man)
if "--online" in sys.argv:
    confere_online(man)
if "--recalcula" in sys.argv:
    falhas += recalcula()
sys.exit(1 if falhas else 0)
