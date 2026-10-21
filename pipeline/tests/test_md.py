"""O conversor de Markdown do site escapa o texto e cobre as marcações usadas nos documentos."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "publicacao"))
import md  # noqa: E402


def test_titulos_paragrafos_e_enfase():
    h, titulo = md.converte("# Título `x`\n\nUm **forte** e *leve* com `código`.\n")
    assert titulo == "Título x"
    assert '<h1 id="título-x">' in h and "<strong>forte</strong>" in h and "<em>leve</em>" in h and "<code>código</code>" in h


def test_tabela_lista_e_codigo():
    texto = "| a | b |\n|---|---|\n| 1 | **2** |\n\n- um\n  - sub\n- dois\n\n1. primeiro\n\n```bash\necho <x>\n```\n"
    h, _ = md.converte(texto)
    assert "<table>" in h and "<td><strong>2</strong></td>" in h
    assert "<ul><li>um<ul><li>sub</li></ul></li><li>dois</li></ul>" in h
    assert "<ol><li>primeiro</li></ol>" in h
    assert '<pre class="lang-bash"><code>echo &lt;x&gt;</code></pre>' in h


def test_links_relativos_e_escape():
    h, _ = md.converte("Veja [o arquivo](../x.md) e <script>alert(1)</script>.", link=lambda u: "https://ex/" + u)
    assert '<a href="https://ex/../x.md">o arquivo</a>' in h
    assert "<script>" not in h and "&lt;script&gt;" in h


def test_link_com_codigo_no_rotulo():
    h, _ = md.converte("Ver [`0001-adr.md`](0001-adr.md) e **[forte](x.md)**.", link=lambda u: "/p/" + u)
    assert '<a href="/p/0001-adr.md"><code>0001-adr.md</code></a>' in h
    assert '<strong><a href="/p/x.md">forte</a></strong>' in h


def test_asterisco_em_formula_nao_vira_italico():
    h, _ = md.converte("Peso = 2 * 3 * 4 e km = linha reta × 1,2.")
    assert "<em>" not in h
