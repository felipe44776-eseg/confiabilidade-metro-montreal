"""Monta o site publicado no GitHub Pages em _site/.

Uso (da raiz do repositorio, depois de `npm run build` em app/):
  python -I publicacao/monta_site.py [--relatorio caminho/da/saida/de/verifica_fontes.txt]

Estrutura publicada:
  /            painel de confiabilidade (painel/gera_site.py)
  /mapa/       mapa das linhas e dos locais de falha (app/, build do Vite em _site_app/)
  /dados/      tabelas derivadas (painel/, geo/) e o manifesto
  /fontes/     fontes, manifesto e resultado da ultima verificacao
  /specs/      lista das especificacoes do projeto (SDD)
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys

REPO = "https://github.com/felipe44776-eseg/confiabilidade-metro-montreal"
SAIDA = "_site"

if os.path.exists(SAIDA):
    shutil.rmtree(SAIDA)
subprocess.run([sys.executable, "-I", "painel/gera_site.py", SAIDA], check=True)

if not os.path.exists("_site_app/mapa/index.html"):
    sys.exit("faltou o build do app: rode `npm ci && npm run build` em app/")
shutil.copytree("_site_app", SAIDA, dirs_exist_ok=True)

for sub in ("painel", "geo", "simulador", "modelos"):
    if os.path.isdir(f"dados/derivados/{sub}"):
        shutil.copytree(f"dados/derivados/{sub}", f"{SAIDA}/dados/{sub}")
for rel in ("modelo_taxa.md", "modelo_taxa_por_faixa.md", "modelo_taxa_por_faixa.svg", "distribuicoes.md", "backtest.md", "backtest_pit.svg",
            "backtest_pit_C.svg", "exposicao.md", "politicas.md", "expansao.md", "validacao_geo.md"):
    if os.path.exists(f"fontes/verificacao/{rel}"):
        os.makedirs(f"{SAIDA}/fontes/verificacao", exist_ok=True)
        shutil.copy(f"fontes/verificacao/{rel}", f"{SAIDA}/fontes/verificacao/{rel}")
os.makedirs(f"{SAIDA}/fontes", exist_ok=True)
shutil.copy("fontes/fontes_manifesto.json", f"{SAIDA}/fontes/fontes_manifesto.json")
shutil.copy("fontes/fontes_manifesto.json", f"{SAIDA}/dados/fontes_manifesto.json")

ESTILO = """
:root{color-scheme:light;--bg:#f7f7f4;--panel:#ffffff;--fg:#1d1d1b;--muted:#5d5c57;--line:#e2e1da;--accent:#2a5bd7;--ok:#0b7a0b;--bad:#b42318}
@media (prefers-color-scheme: dark){:root{color-scheme:dark;--bg:#111110;--panel:#1a1a19;--fg:#f0efec;--muted:#b3b2aa;--line:#2c2c2a;--accent:#7aa2ff;--ok:#4cc24c;--bad:#ff7b72}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
  padding-block:32px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:1100px;margin:0 auto;display:grid;gap:20px}
h1{font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;font-weight:400;font-size:2rem;line-height:1.15;margin:0;text-wrap:balance}
h2{font-size:1.05rem;margin:0}
p{margin:0;max-width:78ch}
a{color:var(--accent)}
.voltar{font-size:13px;text-decoration:none}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px 20px;display:grid;gap:10px;min-width:0}
.tbl{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600}
code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12.5px}
pre{margin:0;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto;font-size:12.5px;line-height:1.45}
.ok{color:var(--ok);font-weight:600}.bad{color:var(--bad);font-weight:600}
.muted{color:var(--muted);font-size:13px}
"""


_EQ = json.load(open("docs/equipe.json", encoding="utf-8"))["integrantes"]
EQUIPE = ", ".join(p["nome"] for p in _EQ[:-1]) + " e " + _EQ[-1]["nome"]
_MAN = json.load(open("fontes/fontes_manifesto.json", encoding="utf-8"))
RELEASES = _MAN.get("releases", [_MAN["release"]])
VERSAO_DADOS = " e ".join(f'<a href="{REPO}/releases/tag/{r}">{r}</a>' for r in RELEASES)


def pagina(titulo, descricao, corpo):
    rodape = (f'<p class="muted" style="margin-top:32px">Sistemas Tolerantes a Falhas, Engenharia de Produção, ESEG, 2026. '
              f'Equipe: {html.escape(EQUIPE)}. Versão dos dados: {VERSAO_DADOS}. <a href="{REPO}/blob/main/fontes/FONTES.md">Fontes</a>.</p>')
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(titulo)}</title><meta name="description" content="{html.escape(descricao)}"><style>{ESTILO}</style></head>
<body><main>{corpo}{rodape}</main></body></html>
"""


# ------------------------------------------------------------------ /fontes/
man = json.load(open("fontes/fontes_manifesto.json", encoding="utf-8"))
linhas = []
for e in man["fontes"]:
    dist = {"release": f'<a href="{html.escape(e.get("release", ""))}">Release</a>', "origem": "baixar da origem",
            "terceiros": "no repositório"}.get(e["distribuicao"], e["distribuicao"])
    tam = f'{e["bytes"]:,}'.replace(",", ".") + " bytes" if "bytes" in e else ""
    if "linhas" in e:
        tam += f' · {e["linhas"]:,} linhas'.replace(",", ".")
    linhas.append(
        f'<tr><td><code>{html.escape(e["id"])}</code></td><td>{html.escape(e["editor"])}</td><td>{html.escape(e["licenca"])}</td>'
        f'<td><a href="{html.escape(e["url"])}">origem</a></td><td>{dist}</td><td>{tam}</td>'
        f'<td><code title="{html.escape(e.get("sha256", ""))}">{html.escape(e.get("sha256", "")[:16])}</code></td><td>{html.escape(e["uso"])}</td></tr>')
relatorio = ""
if "--relatorio" in sys.argv:
    caminho = sys.argv[sys.argv.index("--relatorio") + 1]
    texto = open(caminho, encoding="utf-8").read()
    ok = "-> 0 problema(s)" in texto and ("-> 0 diferenca(s)" in texto or "--recalcula" not in texto)
    estado = '<span class="ok">sem problemas</span>' if ok else '<span class="bad">com problemas: veja abaixo</span>'
    relatorio = f'<section class="card"><h2>Última verificação automática: {estado}</h2>' \
                f'<p class="muted">Feita pelo GitHub Actions nesta publicação: baixa os dados da Release, confere cada SHA-256 e recalcula os números publicados.</p>' \
                f'<pre>{html.escape(texto)}</pre></section>'
corpo = f"""
<a class="voltar" href="../">← Painel de confiabilidade</a>
<h1>Fontes e verificação</h1>
<p>Todo número publicado neste site vem dos arquivos abaixo. Cada um tem o SHA-256 registrado no manifesto e a cópia exata dos dados brutos está nas Releases {VERSAO_DADOS}.
Para conferir sozinho: <code>python -I pipeline/verifica_fontes.py --baixa-release --recalcula</code>.</p>
<p>Documentação completa, com APIs acessadas, auditoria independente e limites: <a href="{REPO}/blob/main/fontes/FONTES.md">FONTES.md</a>.
Relatórios de validação: <a href="{REPO}/blob/main/fontes/verificacao/validacao_geo.md">base geoespacial</a>,
<a href="{REPO}/blob/main/fontes/verificacao/exposicao.md">exposição</a>, <a href="{REPO}/blob/main/fontes/verificacao/modelo_taxa.md">modelo da taxa de falha</a>,
<a href="{REPO}/blob/main/fontes/verificacao/distribuicoes.md">distribuições</a> e <a href="{REPO}/blob/main/fontes/verificacao/backtest.md">validação contra o histórico</a>.
Dicionário de dados e fatores sem fonte: <a href="{REPO}/blob/main/docs/dicionario_dados.md">dicionario_dados.md</a>.
Manifesto: <a href="fontes_manifesto.json">fontes_manifesto.json</a>.</p>
{relatorio}
<section class="card"><h2>Fontes primárias</h2>
<p class="muted">Manifesto gerado em {html.escape(man['gerado_em'])}. Passe o mouse sobre o hash para ver o valor completo.</p>
<div class="tbl"><table><thead><tr><th>Id</th><th>Editor</th><th>Licença</th><th>Link</th><th>Cópia</th><th>Tamanho</th><th>SHA-256</th><th>Uso</th></tr></thead>
<tbody>{''.join(linhas)}</tbody></table></div></section>
"""
open(f"{SAIDA}/fontes/index.html", "w", encoding="utf-8").write(
    pagina("Fontes e verificação", "Fontes, hashes e verificação automática dos dados do projeto de confiabilidade do metrô de Montreal.", corpo))

# ------------------------------------------------------------------ /specs/
itens = []
for pasta in sorted(os.listdir("specs")):
    spec = os.path.join("specs", pasta, "spec.md")
    if not os.path.isfile(spec):
        continue
    texto = open(spec, encoding="utf-8").read()
    titulo = texto.splitlines()[0].lstrip("# ").strip()
    m = re.search(r"^\*\*Status:\*\*\s*(.+)$", texto, re.M)
    status = m.group(1).strip() if m else "rascunho"
    arquivos = [a for a in ("spec.md", "plan.md", "tasks.md", "research.md") if os.path.isfile(os.path.join("specs", pasta, a))]
    links = " · ".join(f'<a href="{REPO}/blob/main/specs/{pasta}/{a}">{a}</a>' for a in arquivos)
    itens.append(f"<tr><td>{html.escape(titulo)}</td><td>{html.escape(status)}</td><td>{links}</td></tr>")
corpo = f"""
<a class="voltar" href="../">← Painel de confiabilidade</a>
<h1>Especificações do projeto</h1>
<p>O projeto segue Spec-Driven Development: cada parte tem uma especificação (o quê e por quê, com critérios de aceite), um plano (como) e tarefas.
Ciclo e regras: <a href="{REPO}/blob/main/specs/README.md">specs/README.md</a>. Princípios: <a href="{REPO}/blob/main/specs/constitution.md">constitution.md</a>.</p>
<section class="card"><div class="tbl"><table><thead><tr><th>Especificação</th><th>Status</th><th>Documentos</th></tr></thead>
<tbody>{''.join(itens)}</tbody></table></div></section>
"""
os.makedirs(f"{SAIDA}/specs", exist_ok=True)
open(f"{SAIDA}/specs/index.html", "w", encoding="utf-8").write(
    pagina("Especificações do projeto", "Especificações (SDD) do simulador de tolerância a falhas do metrô de Montreal.", corpo))
# ------------------------------------------------------------------ /relatorio/
corpo = f"""
<a class="voltar" href="../">← Painel de confiabilidade</a>
<h1>Relatório do trabalho</h1>
<p>O relatório acadêmico (dados, métodos, resultados, validação e limitações) está em
<a href="{REPO}/blob/main/docs/relatorio/relatorio.md">docs/relatorio/relatorio.md</a>, renderizado pelo GitHub.</p>
<p>Relatórios de cada etapa: <a href="{REPO}/blob/main/fontes/verificacao/modelo_taxa.md">modelo da taxa</a>,
<a href="{REPO}/blob/main/fontes/verificacao/distribuicoes.md">distribuições</a>, <a href="{REPO}/blob/main/fontes/verificacao/politicas.md">políticas</a>,
<a href="{REPO}/blob/main/fontes/verificacao/expansao.md">expansão da rede</a> e <a href="{REPO}/blob/main/fontes/verificacao/backtest.md">validação contra o histórico</a>.</p>
<p><a href="../simulador/">Abrir o simulador</a>.</p>
"""
os.makedirs(f"{SAIDA}/relatorio", exist_ok=True)
open(f"{SAIDA}/relatorio/index.html", "w", encoding="utf-8").write(
    pagina("Relatório do trabalho", "Relatório acadêmico do projeto de confiabilidade do metrô de Montreal.", corpo))
print(f"{SAIDA}/ montado: painel, mapa, dados, fontes ({len(man['fontes'])} fontes), specs ({len(itens)})")
