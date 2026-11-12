#!/usr/bin/env python3
"""Render the approved Word article on the private Atlas, preserving prose.

Headings and citations come from the DOCX. Navigation, article connections,
and concept cards are clearly separate editorial additions for the website.
"""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re
from zipfile import ZipFile

from docx import Document
from docx.text.hyperlink import Hyperlink
from lxml import etree


SECTIONS = {
    4: ("Dal pensiero all’azione", "dal-pensiero-allazione"),
    15: ("La forza degli Obiettivi nella Motivazione Umana", "la-forza-degli-obiettivi"),
    22: ("Dal Transazionale al Trasformazionale: il potere della visione condivisa", "dal-transazionale-al-trasformazionale"),
    30: ("Motivazione autentica e autodeterminazione: il cuore pulsante dell’impegno umano", "motivazione-e-autodeterminazione"),
    35: ("Visione, Obiettivi e Autodeterminazione - Le tre anime della motivazione efficace", "visione-obiettivi-autodeterminazione"),
    46: ("Riferimenti bibliografici", "riferimenti-bibliografici"),
    60: ("FOCUS TEORICO – Psicologia del lavoro e leadership", "focus-teorico"),
}
HEADINGS_PRESENT = {15, 22, 30, 35, 46, 60}
AUTHOR_TEXT_INDICES = {i for i in range(4, 66) if i not in HEADINGS_PRESENT}

RELATED = [
    ("Motivazione intrinseca", "Il piacere di svolgere l’attività", "intrinsic-motivation"),
    ("Motivazione estrinseca", "Dal premio esterno al valore riconosciuto", "extrinsic-motivation"),
    ("Soluzione pianificata del problema", "Trasformare l’idea in un percorso d’azione", "planful-problem-solving"),
    ("Fallacia della pianificazione", "Il divario fra previsione e realizzazione", "planning-fallacy"),
    ("Locus of control", "Come percepiamo il margine di influenza", "locus-of-control"),
    ("Pensiero di gruppo", "Quando il consenso soffoca le alternative", "groupthink"),
    ("Intersoggettività", "La visione condivisa nasce dal confronto", "intersubjectivity"),
]


def rich_text(paragraph, allow_footnote: bool = True) -> str:
    parts: list[str] = []
    for piece in paragraph.iter_inner_content():
        if isinstance(piece, Hyperlink):
            target = escape(piece.address, quote=True)
            parts.append(f'<a href="{target}" target="_blank" rel="noopener noreferrer">{escape(piece.text)}</a>')
            continue
        fragment = escape(piece.text).replace("\n", "<br>")
        if fragment:
            if piece.italic:
                fragment = f"<em>{fragment}</em>"
            if piece.bold:
                fragment = f"<strong>{fragment}</strong>"
            parts.append(fragment)
        if allow_footnote and piece._r.xpath(".//w:footnoteReference"):
            parts.append('<sup class="footnote-ref"><a href="#nota-commitment" id="richiamo-commitment" aria-label="Vai alla nota sul commitment">1</a></sup>')
    return "".join(parts)


def footnote_html(path: Path) -> str:
    with ZipFile(path) as archive:
        root = etree.fromstring(archive.read("word/footnotes.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    notes = root.xpath(".//w:footnote[@w:id='1']", namespaces=ns)
    assert len(notes) == 1, "Nota sul commitment mancante"
    parts = []
    for run in notes[0].xpath(".//w:r", namespaces=ns):
        chars = "".join(run.xpath(".//w:t/text()", namespaces=ns))
        if not chars:
            continue
        frag = escape(chars)
        if run.xpath("./w:rPr/w:i", namespaces=ns):
            frag = f"<em>{frag}</em>"
        if run.xpath("./w:rPr/w:b", namespaces=ns):
            frag = f"<strong>{frag}</strong>"
        parts.append(frag)
    text = "".join(parts).strip()
    assert "Meyer e Allen" in text
    return (
        '<aside class="article-footnote" id="nota-commitment" aria-label="Nota sul commitment">'
        '<p><sup>1</sup> ' + text
        + ' <a href="#richiamo-commitment" aria-label="Torna al richiamo della nota">↩</a></p></aside>'
    )


def render(source: Path) -> str:
    paragraphs = Document(source).paragraphs
    assert len(paragraphs) == 66
    assert paragraphs[1].text == 'DAL “WHAT IF” AL “WHAT IS”'
    assert paragraphs[2].text == "Perché avere un’idea non basta: bisogna farla vivere"
    assert paragraphs[3].text == "di Tommaso Corona"
    assert "metanalisi di Judge e Piccolo" in paragraphs[27].text
    assert "un operatore aeronautico" in paragraphs[34].text
    assert paragraphs[46].text == "RIFERIMENTI BIBLIOGRAFICI"
    assert paragraphs[60].text.startswith("FOCUS TEORICO")

    body: list[str] = []
    copied = []
    toc = [(slug, title) for _, (title, slug) in SECTIONS.items()]
    is_open = False
    note_added = False

    for index in range(4, 66):
        paragraph = paragraphs[index]
        if index in SECTIONS:
            if is_open:
                body.append("</section>")
            title, slug = SECTIONS[index]
            klass = " references-section" if index == 46 else ""
            body.append(f'<section class="article-section{klass}" id="{slug}"><h2>{escape(title)}</h2>')
            is_open = True
        if not paragraph.text.strip() or index in HEADINGS_PRESENT:
            continue
        if index == 5:
            body.append(f'<p class="article-epigraph">{rich_text(paragraph)}</p>')
            copied.append(index)
            continue
        css = ' class="article-reference"' if 47 <= index <= 58 else ""
        if index == 44:
            css = ' class="article-conclusion"'
        if 61 <= index <= 65:
            css = ' class="article-theory"'
        body.append(f"<p{css}>{rich_text(paragraph)}</p>")
        copied.append(index)
        if index == 21:
            body.append(footnote_html(source))
            note_added = True
    body.append("</section>")
    assert note_added
    assert copied == sorted(i for i in AUTHOR_TEXT_INDICES if paragraphs[i].text.strip())
    assert len(copied) == len(set(copied))
    assert sum('id="richiamo-commitment"' in s for s in body) == 1

    article_links = '''<section class="article-section article-crosslinks" id="altre-riflessioni">
      <h2>Altre riflessioni nell’Atlante</h2>
      <p>Due prospettive complementari sul rapporto tra partecipazione, autonomia di giudizio e comunicazione.</p>
      <div class="article-inline-links">
        <a href="l-ombra-e-la-voce.html"><strong>L’ombra e la voce</strong><span>Condividere una direzione senza rinunciare al proprio pensiero <span aria-hidden="true">↗</span></span></a>
        <a href="lo-slogun-batte-largomento.html"><strong>Lo “slogun” batte l’argomento</strong><span>La distanza fra una visione discussa e un messaggio che cerca adesione <span aria-hidden="true">↗</span></span></a>
      </div>
    </section>'''
    cards = "\n".join(
        f'<a class="related-item" href="../index.html#bias={slug}"><span class="related-title">{escape(name)}</span><span class="related-why">{escape(reason)}</span><span class="related-arrow" aria-hidden="true">↗</span></a>'
        for name, reason, slug in RELATED
    )
    concepts = f'''<section class="article-section article-concept-links" id="esplora-i-concetti">
      <h2>Esplora i concetti nell’Atlante</h2>
      <p>Le schede affrontano separatamente alcuni processi psicologici richiamati nell’articolo.</p>
      <div class="related-grid">{cards}</div>
    </section>'''
    toc.extend([
        ("altre-riflessioni", "Altre riflessioni"),
        ("esplora-i-concetti", "Esplora i concetti"),
    ])
    nav_html = "\n".join(f'<a href="#{slug}">{escape(title)}</a>' for slug, title in toc)
    count = len(re.findall(r"\b[\wÀ-ÿ’-]+\b", " ".join(p.text for p in paragraphs[4:66])))
    minutes = max(1, round(count / 220))

    return f'''<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow, noarchive">
  <meta name="description" content="Dal What If al What Is, di Tommaso Corona: dalla visione all’azione, leadership, obiettivi, motivazione autonoma e lavoro comune.">
  <meta name="theme-color" content="#263025">
  <title>Dal “What If” al “What Is” · Atlante di Limite &amp; Relazione</title>
  <link rel="stylesheet" href="../styles.css">
  <link rel="stylesheet" href="../article.css">
</head>
<body class="article-page">
  <a class="skip-link" href="#articolo">Vai al testo dell'articolo</a>
  <header class="masthead">
    <a href="../index.html" class="brand" aria-label="Atlante di Limite e Relazione, torna all'inizio"><span class="limite">LIMITE</span><span class="amp">&amp;</span><span class="relazione">RELAZIONE</span></a>
    <div class="edition">TOMMASO CORONA <span>ATLANTE VISIVO / 2026</span></div>
    <span class="private-badge"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg> Raccolta privata</span>
  </header>
  <main>
    <nav class="article-breadcrumb" aria-label="Percorso di navigazione"><a href="../index.html">Atlante</a><span aria-hidden="true">/</span><a href="../index.html#articoli-e-riflessioni">Articoli e riflessioni</a><span aria-hidden="true">/</span><span>Dal “What If” al “What Is”</span></nav>
    <section class="article-hero" aria-labelledby="article-title">
      <div class="article-hero-copy">
        <p class="eyebrow"><span></span> ARTICOLI E RIFLESSIONI</p>
        <h1 id="article-title">Dal “What If” <em>al “What Is”</em></h1>
        <p class="article-subtitle">{escape(paragraphs[2].text)}</p>
        <div class="article-meta"><strong>Tommaso Corona</strong><span aria-hidden="true">·</span><span>Circa {minutes} minuti di lettura</span></div>
        <a class="primary-link" href="#articolo">Inizia la lettura <span aria-hidden="true">↓</span></a>
      </div>
      <figure class="article-poster"><img src="../assets/articoli/dal-what-if-al-what-is-cover.jpg" alt="Copertina originale Dal What If al What Is: un germoglio cresce fra un paesaggio in rovina e una città" fetchpriority="high"><figcaption>Immagine originale dell’articolo</figcaption></figure>
    </section>
    <div class="article-reading" id="articolo">
      <details class="article-mobile-toc"><summary>Indice dell'articolo</summary><nav aria-label="Indice dell'articolo su schermo piccolo">{nav_html}</nav></details>
      <aside class="article-sidebar"><nav class="article-toc" aria-label="Indice dell'articolo"><p class="eyebrow">NEL TESTO</p>{nav_html}</nav><a class="article-sidebar-back" href="../index.html#articoli-e-riflessioni">← Torna all’Atlante</a></aside>
      <article class="article-body" aria-label="Testo integrale dell'articolo">{''.join(body)}{article_links}{concepts}</article>
    </div>
    <section class="article-endnote"><span class="closing-mark" aria-hidden="true">&amp;</span><div><p class="eyebrow">VISIONE E AZIONE</p><p>Una visione condivisa diventa concreta attraverso obiettivi, responsabilità e la partecipazione delle persone.</p><a class="primary-link" href="../index.html">Torna all’Atlante <span aria-hidden="true">↗</span></a></div></section>
  </main>
  <footer><span><b class="limite">LIMITE</b> &amp; <b class="relazione">RELAZIONE</b> · Tommaso Corona</span><span>Atlante di Limite &amp; Relazione · Articoli e riflessioni</span></footer>
</body>
</html>
'''


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("output_html", type=Path)
    args = parser.parse_args()
    page = render(args.docx)
    args.output_html.parent.mkdir(parents=True, exist_ok=True)
    args.output_html.write_text(page, encoding="utf-8")
    print(f"Generated {args.output_html} ({len(page):,} HTML characters)")
