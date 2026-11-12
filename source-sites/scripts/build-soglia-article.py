#!/usr/bin/env python3
"""Render the definitive Word article for the private Atlante.

The author's prose, citations and emphasis are copied without edits. The
section headings and navigational connections are web-only editorial aids.
"""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re
from zipfile import ZipFile

from docx import Document
from docx.text.hyperlink import Hyperlink


SECTIONS = [
    (4, "Quando il conflitto cambia natura", "il-conflitto"),
    (5, "Il nemico e la coesione del gruppo", "il-nemico-e-il-gruppo"),
    (8, "Polarizzazione e identità digitale", "polarizzazione-digitale"),
    (13, "La soglia della radicalizzazione", "la-soglia"),
    (23, "Riferimenti bibliografici", "riferimenti-bibliografici"),
    (30, "Altre letture", "altre-letture"),
]

RELATED = [
    ("Polarizzazione di gruppo", "Quando il confronto irrigidisce le posizioni", "polarization"),
    ("Etnocentrismo", "Il confine fra noi e loro", "ethnocentrism"),
    ("Disimpegno morale · Ristrutturazione cognitiva del comportamento", "La giustificazione delle proprie azioni", "moral-disengagement-conduct"),
    ("Disimpegno morale · Rappresentazione della vittima", "La rappresentazione dell'avversario", "moral-disengagement-victim"),
    ("Pensiero di gruppo", "La pressione verso il consenso", "groupthink"),
    ("Bias di attribuzione ostile", "Leggere l'altro come minaccia", "hostile-attribution"),
]


def rich_text(paragraph) -> str:
    parts: list[str] = []
    for piece in paragraph.iter_inner_content():
        if isinstance(piece, Hyperlink):
            label = escape(piece.text)
            # In the author's Word file the displayed Psiche & Thanatos URL
            # points through an old Facebook outbound redirect. Link to the
            # canonical book URL instead, as explicitly confirmed by author.
            address = "https://www.amazon.it/dp/B0DVCC1HY6" if "B0DVCC1HY6" in piece.text or "B0DVCC1HY6" in piece.address else piece.address
            target = escape(address, quote=True)
            parts.append(f'<a href="{target}" target="_blank" rel="noopener noreferrer">{label}</a>')
        else:
            value = escape(piece.text).replace("\n", "<br>")
            if not value:
                continue
            if piece.italic:
                value = f"<em>{value}</em>"
            if piece.bold:
                value = f"<strong>{value}</strong>"
            parts.append(value)
    return "".join(parts)


def render(path: Path) -> str:
    paragraphs = Document(path).paragraphs
    assert paragraphs[1].text.startswith("LA SOGLIA DELLA RADICALIZZAZIONE\n")
    assert paragraphs[2].text == "di Tommaso CORONA"
    assert paragraphs[3].text.startswith("Quando le opinioni smettono")
    assert "lì comincia la radicalizzazione" in paragraphs[20].text
    assert paragraphs[23].text.strip() == "RIFERIMENTI BIBLIOGRAFICI"

    # The author's opening paragraph is used only as the introductory pull
    # quote. Every subsequent non-empty paragraph occurs exactly once below.
    opening = rich_text(paragraphs[3])
    heading_by_pos = {index: (heading, ident) for index, heading, ident in SECTIONS}
    body: list[str] = []
    toc = [(ident, title) for _, title, ident in SECTIONS]
    body_indices: list[int] = []
    section_open = False
    for index in range(4, 35):
        paragraph = paragraphs[index]
        if not paragraph.text.strip():
            continue
        if index in heading_by_pos:
            if section_open:
                body.append("</section>")
            title, ident = heading_by_pos[index]
            klass = " references-section" if index == 23 else (" further-section" if index == 30 else "")
            body.append(f'<section class="article-section{klass}" id="{ident}"><h2>{escape(title)}</h2>')
            section_open = True
            if index == 23:
                # Paragraph 22 is retained above as the author's lead-in.
                continue
        if index == 23:
            continue  # Displayed as the section heading, preserving its words.
        css = ' class="article-reference"' if 24 <= index <= 28 or 31 <= index <= 34 else ''
        if index == 20:
            css = ' class="article-conclusion"'
        if index == 22:
            css = ' class="article-further"'
        body.append(f"<p{css}>{rich_text(paragraph)}</p>")
        body_indices.append(index)
    if section_open:
        body.append("</section>")

    assert body_indices == [i for i in range(4, 35) if paragraphs[i].text.strip() and i != 23]
    assert sum(1 for fragment in body if fragment.startswith("<p")) == len(body_indices)
    assert "lì comincia la radicalizzazione" in "".join(body)

    article_links = '''<section class="article-section article-crosslinks" id="letture-collegate">
      <h2>Altre riflessioni nell’Atlante</h2>
      <p>Per proseguire l’esplorazione del rapporto fra prospettive, appartenenza e conflitto:</p>
      <div class="article-inline-links article-inline-links--three">
        <a href="la-zebra-il-leone-e-lerba.html"><strong>La zebra, il leone e l’erba</strong><span>Come si costruisce e si difende una lettura della realtà <span aria-hidden="true">↗</span></span></a>
        <a href="l-ombra-e-la-voce.html"><strong>L’ombra e la voce</strong><span>Appartenenza, autonomia e spazio per il dissenso <span aria-hidden="true">↗</span></span></a>
        <a href="lo-slogun-batte-largomento.html"><strong>Lo “slogun” batte l’argomento</strong><span>Il messaggio manipolativo che orienta lo schieramento <span aria-hidden="true">↗</span></span></a>
      </div>
    </section>'''
    concepts = "\n".join(
        f'<a class="related-item" href="../index.html#bias={ident}"><span class="related-title">{escape(label)}</span><span class="related-why">{escape(why)}</span><span class="related-arrow" aria-hidden="true">↗</span></a>'
        for label, why, ident in RELATED
    )
    concept_section = f'''<section class="article-section article-concept-links" id="esplora-i-concetti">
      <h2>Esplora i concetti nell’Atlante</h2>
      <p>Alcune schede aiutano a riconoscere, uno alla volta, i meccanismi richiamati in questa riflessione.</p>
      <div class="related-grid">{concepts}</div>
    </section>'''
    toc.extend([("letture-collegate", "Altre riflessioni"), ("esplora-i-concetti", "Esplora i concetti")])
    toc_html = "\n".join(f'<a href="#{ident}">{escape(label)}</a>' for ident, label in toc)
    count = len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", " ".join(p.text for p in paragraphs[3:35])))
    minutes = max(1, round(count / 220))
    return f'''<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow, noarchive">
  <meta name="description" content="La soglia della radicalizzazione, di Tommaso Corona: costruzione del nemico, polarizzazione e identità collettiva.">
  <meta name="theme-color" content="#263025">
  <title>La soglia della radicalizzazione · Atlante di Limite &amp; Relazione</title>
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
    <nav class="article-breadcrumb" aria-label="Percorso di navigazione"><a href="../index.html">Atlante</a><span aria-hidden="true">/</span><a href="../index.html#articoli-e-riflessioni">Articoli e riflessioni</a><span aria-hidden="true">/</span><span>La soglia della radicalizzazione</span></nav>
    <section class="article-hero" aria-labelledby="article-title">
      <div class="article-hero-copy">
        <p class="eyebrow"><span></span> ARTICOLI E RIFLESSIONI</p>
        <h1 id="article-title">La soglia <em>della radicalizzazione</em></h1>
        <p class="article-subtitle">Costruzione del nemico: quando la polarizzazione diventa struttura</p>
        <div class="article-meta"><strong>Tommaso Corona</strong><span aria-hidden="true">·</span><span>Circa {minutes} minuti di lettura</span></div>
        <a class="primary-link" href="#articolo">Inizia la lettura <span aria-hidden="true">↓</span></a>
      </div>
      <figure class="article-poster"><img src="../assets/articoli/la-soglia-cover.jpg" alt="Immagine originale che accompagna La soglia della radicalizzazione" fetchpriority="high"><figcaption>Immagine dell'articolo originale</figcaption></figure>
    </section>
    <section class="article-abstract" aria-labelledby="opening-title"><div><p class="eyebrow">IN APERTURA</p><h2 id="opening-title">La soglia del conflitto<span class="title-dot">.</span></h2></div><div><p class="article-epigraph">{opening}</p></div></section>
    <div class="article-reading" id="articolo">
      <details class="article-mobile-toc"><summary>Indice dell'articolo</summary><nav aria-label="Indice dell'articolo su schermo piccolo">{toc_html}</nav></details>
      <aside class="article-sidebar"><nav class="article-toc" aria-label="Indice dell'articolo"><p class="eyebrow">NEL TESTO</p>{toc_html}</nav><a class="article-sidebar-back" href="../index.html#articoli-e-riflessioni">← Torna all’Atlante</a></aside>
      <article class="article-body" aria-label="Testo integrale dell'articolo">{''.join(body)}{article_links}{concept_section}</article>
    </div>
    <section class="article-endnote"><span class="closing-mark" aria-hidden="true">&amp;</span><div><p class="eyebrow">CONFLITTO E APPARTENENZA</p><p>Dal confronto tra idee alla costruzione di identità contrapposte: riconoscere il momento in cui il conflitto cambia natura.</p><a class="primary-link" href="../index.html">Torna all’Atlante <span aria-hidden="true">↗</span></a></div></section>
  </main>
  <footer><span><b class="limite">LIMITE</b> &amp; <b class="relazione">RELAZIONE</b> · Tommaso Corona</span><span>Atlante di Limite &amp; Relazione · Articoli e riflessioni</span></footer>
</body>
</html>
'''


def extract_cover(source: Path, target: Path) -> None:
    with ZipFile(source) as archive:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read("word/media/image1.jpg"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("output_html", type=Path)
    parser.add_argument("output_cover", type=Path)
    args = parser.parse_args()
    args.output_html.parent.mkdir(parents=True, exist_ok=True)
    args.output_html.write_text(render(args.docx), encoding="utf-8")
    extract_cover(args.docx, args.output_cover)
    print(f"Generated {args.output_html} and the original cover {args.output_cover}")
