"""Conversor mínimo de Markdown para HTML, sem dependência (Python puro), para as páginas de documentação do site.

Cobre o que os documentos do projeto usam: títulos, parágrafos, listas (com um nível de recuo), tabelas,
blocos de código (mermaid vira bloco de código), citações simples, regra horizontal, negrito, itálico,
código em linha, links e imagens. Todo texto é escapado; só as marcações acima viram HTML.
"""
import html
import re

_LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)")
_CODIGO = re.compile(r"`([^`]+)`")
_NEGRITO = re.compile(r"\*\*(.+?)\*\*")
_ITALICO = re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])")
_TITULO = re.compile(r"^(#{1,6})\s+(.*)$")
_ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
_MARCA = re.compile(r"\x00(\d+)\x00")


def ancora(texto):
    t = re.sub(r"[^\w\s-]", "", texto.lower(), flags=re.UNICODE)
    return re.sub(r"\s+", "-", t.strip())


def em_linha(texto, link):
    """Formatação dentro de uma linha. `link(url)` decide o destino de links relativos.
    Links e código viram marcadores; negrito e itálico valem sobre o texto inteiro; os marcadores voltam no fim."""
    guardados = []

    def guarda(fragmento):
        guardados.append(fragmento)
        return f"\x00{len(guardados) - 1}\x00"

    def troca_link(m):
        imagem, rotulo, url = m.group(1), m.group(2), link(m.group(3))
        if imagem:
            return guarda(f'<img src="{html.escape(url)}" alt="{html.escape(rotulo)}" loading="lazy">')
        return guarda(f'<a href="{html.escape(url)}">{em_linha(rotulo, link)}</a>')

    t = _LINK.sub(troca_link, texto)
    t = _CODIGO.sub(lambda m: guarda(f"<code>{html.escape(m.group(1))}</code>"), t)
    t = _enfase(html.escape(t))
    return _MARCA.sub(lambda m: guardados[int(m.group(1))], t)


def _enfase(t):
    t = _NEGRITO.sub(r"<strong>\1</strong>", t)
    return _ITALICO.sub(r"<em>\1</em>", t)


def _celulas(linha):
    linha = linha.strip()
    if linha.startswith("|"):
        linha = linha[1:]
    if linha.endswith("|"):
        linha = linha[:-1]
    return [c.strip() for c in linha.split("|")]


def converte(md, link=lambda u: u):
    """Markdown → HTML (fragmento). Devolve (html, titulo_do_primeiro_h1)."""
    linhas = md.replace("\r\n", "\n").split("\n")
    out, i, titulo = [], 0, None
    while i < len(linhas):
        ln = linhas[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("```"):
            lang = ln[3:].strip()
            bloco = []
            i += 1
            while i < len(linhas) and not linhas[i].startswith("```"):
                bloco.append(linhas[i])
                i += 1
            i += 1
            classe = f' class="lang-{html.escape(lang)}"' if lang else ""
            if lang == "mermaid":  # o site não carrega script externo: o GitHub desenha o diagrama no arquivo de origem
                out.append('<p class="muted">Diagrama em Mermaid: o GitHub o desenha no arquivo de origem (link no fim da página).</p>')
            out.append(f"<pre{classe}><code>{html.escape(chr(10).join(bloco))}</code></pre>")
            continue
        m = _TITULO.match(ln)
        if m:
            nivel, texto = len(m.group(1)), m.group(2).strip()
            if nivel == 1 and titulo is None:
                titulo = re.sub(r"[`*]", "", texto)
            out.append(f'<h{nivel} id="{ancora(texto)}">{em_linha(texto, link)}</h{nivel}>')
            i += 1
            continue
        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", ln):
            out.append("<hr>")
            i += 1
            continue
        if ln.lstrip().startswith("|") and i + 1 < len(linhas) and re.match(r"^\s*\|?\s*:?-{2,}", linhas[i + 1]):
            cab = _celulas(ln)
            i += 2
            corpo = []
            while i < len(linhas) and linhas[i].lstrip().startswith("|"):
                corpo.append(_celulas(linhas[i]))
                i += 1
            th = "".join(f"<th>{em_linha(c, link)}</th>" for c in cab)
            trs = "".join("<tr>" + "".join(f"<td>{em_linha(c, link)}</td>" for c in r) + "</tr>" for r in corpo)
            out.append(f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
            continue
        if ln.startswith(">"):
            bloco = []
            while i < len(linhas) and linhas[i].startswith(">"):
                bloco.append(linhas[i][1:].strip())
                i += 1
            out.append(f"<blockquote><p>{em_linha(' '.join(bloco), link)}</p></blockquote>")
            continue
        if _ITEM.match(ln):
            out.append(_lista(linhas, i, link))
            while i < len(linhas) and (_ITEM.match(linhas[i]) or (linhas[i].startswith("  ") and linhas[i].strip())):
                i += 1
            continue
        par = [ln.strip()]
        i += 1
        while i < len(linhas) and linhas[i].strip() and not (_TITULO.match(linhas[i]) or _ITEM.match(linhas[i])
                                                            or linhas[i].startswith(("```", "|", ">"))):
            par.append(linhas[i].strip())
            i += 1
        out.append(f"<p>{em_linha(' '.join(par), link)}</p>")
    return "\n".join(out), titulo


def _lista(linhas, i, link):
    """Lista com um nível de sublista (recuo de 2 ou mais espaços)."""
    m = _ITEM.match(linhas[i])
    ordenada = m.group(2)[0].isdigit()
    tag = "ol" if ordenada else "ul"
    itens = []
    while i < len(linhas):
        m = _ITEM.match(linhas[i])
        if m and len(m.group(1)) < 2:
            itens.append([m.group(3), []])
            i += 1
        elif m and itens:
            itens[-1][1].append(m.group(3))
            i += 1
        elif linhas[i].startswith("  ") and linhas[i].strip() and itens:
            alvo = itens[-1][1] if itens[-1][1] else None
            if alvo is not None:
                alvo[-1] += " " + linhas[i].strip()
            else:
                itens[-1][0] += " " + linhas[i].strip()
            i += 1
        else:
            break
    partes = []
    for texto, subs in itens:
        sub = ("<ul>" + "".join(f"<li>{em_linha(s, link)}</li>" for s in subs) + "</ul>") if subs else ""
        partes.append(f"<li>{em_linha(texto, link)}{sub}</li>")
    return f"<{tag}>{''.join(partes)}</{tag}>"
