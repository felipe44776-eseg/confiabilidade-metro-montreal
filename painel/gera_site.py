"""Gera a versao publica (GitHub Pages) do painel de confiabilidade do metro de Montreal.

Le a pagina do painel (painel/painel_index.html) e as tabelas (dados/derivados/painel/*.json) e grava
<saida>/index.html autocontido: d3, dados e um substituto minimo da API `dash` do painel embutidos.

Uso (da raiz do projeto): python -I painel/gera_site.py [pasta de saida, padrao _site]
"""
import glob
import json
import os
import re
import sys

REPO = "https://github.com/felipe44776-eseg/confiabilidade-metro-montreal"
SAIDA = sys.argv[1] if len(sys.argv) > 1 else "_site"
D3 = "painel/vendor/d3.v7.9.0.min.js"

pagina = open("painel/painel_index.html", encoding="utf-8").read()
estilo = re.search(r"<style>(.*?)</style>", pagina, re.S).group(1)
corpo = re.search(r"(<div class=\"mtl\">.*</div>)\s*<script>", pagina, re.S).group(1)
script = re.search(r"<script>(.*?)</script>", pagina, re.S).group(1)
d3 = open(D3, encoding="utf-8").read()
assert d3.startswith("// https://d3js.org v7"), "d3 inesperado"

corpo = corpo.replace(
    "Cálculos em pipeline/analise_confiabilidade.py.",
    f'Cálculos em <a href="{REPO}/blob/main/pipeline/analise_confiabilidade.py">pipeline/analise_confiabilidade.py</a>.',
)
assert REPO in corpo, "trecho do metodo nao encontrado"

dados = {}
for arq in sorted(glob.glob("dados/derivados/painel/*.json")):
    dados[os.path.splitext(os.path.basename(arq))[0]] = json.load(open(arq, encoding="utf-8"))
dados_js = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

TOKENS = """
:root{color-scheme:light;
  --color-bg:#f9f9f7;--color-panel:#fcfcfb;--color-fg:#0b0b0b;--color-fg-muted:#62615d;--color-border-line:#e1e0d9;--color-bad:#d03b3b;
  --cds-text-secondary:#52514e;--cds-surface-popover:#ffffff;--cds-border:#d6d5ce;--cds-shadow-popover:0 6px 24px rgba(20,20,18,.14);
  --cds-chart-grid:#e1e0d9;--cds-chart-axis:#c3c2b7;--cds-chart-reference:#898781;--cds-chart-muted:#a9a8a1;--cds-chart-status-critical:#d03b3b;
  --serie-1:#2a78d6;--serie-2:#eb6834;--serie-3:#1baf7a;--serie-4:#eda100;--serie-5:#e87ba4;--serie-6:#008300;--serie-7:#6250d6;--serie-8:#e34948;
  --cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:16px;--cds-gap-lg:24px;--cds-gap-xl:40px;
  --cds-pad-xs:4px;--cds-pad-sm:8px;--cds-pad-md:12px;--cds-pad-lg:20px;--cds-radius:10px;
  --cds-font-size-caption:.8125rem;--cds-font-size-body:1rem;--cds-font-size-heading:1.0625rem;--cds-font-size-title:1.75rem;--cds-font-weight-medium:600;
  --cds-dur-slow:.4s;--cds-ease-out:cubic-bezier(.2,.7,.2,1);
  --font-anthropic-sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --font-anthropic-serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif}
@media (prefers-color-scheme: dark){:root{color-scheme:dark;
  --color-bg:#0d0d0d;--color-panel:#1a1a19;--color-fg:#f0efec;--color-fg-muted:#a3a29b;--color-border-line:#2c2c2a;--color-bad:#e66767;
  --cds-text-secondary:#c3c2b7;--cds-surface-popover:#242422;--cds-border:#383835;--cds-shadow-popover:0 6px 24px rgba(0,0,0,.5);
  --cds-chart-grid:#2c2c2a;--cds-chart-axis:#383835;--cds-chart-reference:#898781;--cds-chart-muted:#6b6a65;--cds-chart-status-critical:#e66767;
  --serie-1:#3987e5;--serie-2:#d95926;--serie-3:#199e70;--serie-4:#c98500;--serie-5:#d55181;--serie-6:#008300;--serie-7:#9085e9;--serie-8:#e66767}}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);font-size:15px;line-height:1.5;
  padding-block:clamp(20px,4vw,48px);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
a{color:var(--serie-1)}
.mtl b{font-weight:var(--cds-font-weight-medium)}
.dash-skeleton{color:transparent}
.mtl-rodape{max-width:1240px;margin:var(--cds-gap-xl) auto 0;padding-top:var(--cds-gap-md);border-top:1px solid var(--color-border-line);
  font-size:var(--cds-font-size-caption);color:var(--color-fg-muted);line-height:1.6;display:grid;gap:var(--cds-gap-xs)}
.mtl-rodape p{margin:0;max-width:110ch}
"""

SHIM = """
window.dash = (() => {
  const PADRAO = {linha: 'laranja'};
  const cbs = [];
  let params = {...PADRAO};
  const rodar = () => cbs.forEach((fn) => fn());
  let espera;
  window.addEventListener('resize', () => { clearTimeout(espera); espera = setTimeout(rodar, 150); });
  return {
    data: (id) => (Object.prototype.hasOwnProperty.call(window.DADOS, id)
      ? {status: 'ok', data: window.DADOS[id], columns: Object.keys(window.DADOS[id][0] || {}), meta: [], refreshing: false}
      : {status: 'missing', data: [], columns: [], meta: []}),
    onData: (fn) => { cbs.push(fn); fn(); },
    params: () => ({...params}),
    setParams: (p) => { params = {...params, ...p}; rodar(); },
    resetParams: () => { params = {...PADRAO}; rodar(); },
    setLink: (nome) => { try { history.replaceState(null, '', '#' + nome); } catch (e) { /* sem historico */ } },
    refresh: () => {},
    colors: ['var(--serie-1)', 'var(--serie-2)', 'var(--serie-3)', 'var(--serie-4)', 'var(--serie-5)', 'var(--serie-6)', 'var(--serie-7)', 'var(--serie-8)'],
  };
})();
"""

RODAPE = f"""
<footer class="mtl-rodape">
  <p>Trabalho da disciplina Sistemas Tolerantes a Falhas, Engenharia de Produção, ESEG, 2026. Código e tabelas: <a href="{REPO}">{REPO.replace("https://", "")}</a>. Veja também: <a href="mapa/">mapa da rede</a>, <a href="fontes/">fontes e verificação</a>, <a href="specs/">especificações do projeto</a>.</p>
  <p>Dados: Société de transport de Montréal (STM), dados abertos, licença CC BY 4.0: incidentes do metrô, quilometragem real das voitures e GTFS. Clima: Environment and Climate Change Canada, estação MONTREAL INTL A, Licença de Governo Aberto do Canadá. Mobilidade: Google LLC, Google COVID-19 Community Mobility Reports. Os resultados são análise própria e não representam a STM.</p>
</footer>
"""

html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Confiabilidade do Metrô de Montreal</title>
<meta name="description" content="Tempo médio entre falhas, disponibilidade e tolerância a falhas das linhas do metrô de Montreal, com dados abertos da STM de 2019 a 2026.">
<meta property="og:title" content="Confiabilidade do Metrô de Montreal">
<meta property="og:description" content="MTBF, disponibilidade, redundância e simulação Monte Carlo das linhas do metrô de Montreal, com dados abertos da STM.">
<meta property="og:type" content="website">
<style>{TOKENS}
{estilo}</style>
</head>
<body>
{corpo}
{RODAPE}
<script>{d3}</script>
<script>window.DADOS = {dados_js};</script>
<script>{SHIM}</script>
<script>{script}</script>
</body>
</html>
"""

os.makedirs(SAIDA, exist_ok=True)
open(f"{SAIDA}/index.html", "w", encoding="utf-8", newline="\n").write(html)
print(f"{SAIDA}/index.html: {len(html.encode('utf-8')) / 1024:.0f} KB | tabelas: {len(dados)}")
