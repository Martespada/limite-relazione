#!/usr/bin/env python3
"""Build the Atlas page from Tommaso Corona's final Jung article.

Keep Word prose, emphasis, footnote, reference list and both revised drawings.
Only navigation, contextual styling and cross-article linking are added.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
from pathlib import Path
import re
from zipfile import ZipFile

from docx import Document
from docx.text.hyperlink import Hyperlink
from lxml import etree


NOTE_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
NOTE_REF_ID = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id"


def rich_text(paragraph) -> str:
    parts = []
    for piece in paragraph.iter_inner_content():
        if isinstance(piece, Hyperlink):
            parts.append(f'<a href="{escape(piece.address, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(piece.text)}</a>')
            continue
        content = escape(piece.text).replace("\n", "<br>")
        if piece.italic:
            content = f"<em>{content}</em>"
        if piece.bold:
            content = f"<strong>{content}</strong>"
        parts.append(content)
        for ref in piece._element.xpath(".//w:footnoteReference"):
            assert ref.get(NOTE_REF_ID) == "1"
            parts.append('<sup class="footnote-ref" id="richiamo-mandala"><a href="#nota-mandala" aria-label="Vai alla nota 1 sul mandala">1</a></sup>')
    return "".join(parts)


def mandala_note(docx: Path) -> str:
    with ZipFile(docx) as package:
        root = etree.fromstring(package.read("word/footnotes.xml"))
    notes = root.xpath(".//w:footnote[@w:id='1']", namespaces=NOTE_NS)
    assert len(notes) == 1
    note = "".join(node.text or "" for node in notes[0].xpath(".//w:t", namespaces=NOTE_NS)).strip()
    assert note.startswith("Il mandala è un termine derivato dal sanscrito")
    return note


def render(docx: Path) -> str:
    document = Document(docx)
    with ZipFile(docx) as package:
        diagram_revision = sha256(package.read("word/media/image2.png")).hexdigest()[:16]
    paragraphs = document.paragraphs
    assert paragraphs[1].text.strip() == "ARCHETIPI E INDIVIDUAZIONE"
    assert paragraphs[2].text.strip() == "il percorso junghiano della crescita psicologica"
    assert paragraphs[3].text.strip() == "di Tommaso Corona"
    assert paragraphs[28].text.strip() == "RIFERIMENTI BIBLIOGRAFICI"
    assert paragraphs[37].text.strip() == "UNA RIFLESSIONE SULL’APPARTENENZA"
    assert "L’ombra e la voce" in paragraphs[38].text

    words = len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", " ".join(p.text for p in paragraphs[4:])))
    reading_minutes = max(1, round(words / 220))
    toc = [
        ("il-testo", "Archetipi e individuazione"),
        ("schema-individuazione", "Il percorso illustrato"),
        ("riferimenti-bibliografici", "Riferimenti bibliografici"),
        ("una-riflessione-sullappartenenza", "Una riflessione sull’appartenenza"),
    ]

    body = ['<section class="article-section" id="il-testo">']
    preserved_prose = []
    for i in range(4, 26):
        paragraph = paragraphs[i]
        assert paragraph.text.strip(), i
        preserved_prose.append(paragraph.text.strip())
        body.append(f'<p>{rich_text(paragraph)}</p>')

    note = mandala_note(docx)
    body.append(f'<aside class="article-footnote" id="nota-mandala" aria-label="Nota 1"><p><sup>1</sup> {escape(note)} <a href="#richiamo-mandala" aria-label="Torna al punto del testo che richiama la nota">↑</a></p></aside>')
    body.append("</section>")
    body.append(f'''<section class="article-section article-figure-section" id="schema-individuazione">
      <h2>Il percorso di individuazione</h2>
      <figure class="article-diagram">
        <div class="article-diagram-crop"><img src="../assets/articoli/archetipi-percorso.png?v={diagram_revision}" width="941" height="1672" loading="lazy" alt="Schema del percorso di individuazione: un cammino verso il Sé, circondato da Persona, Ombra, Anima e Animus, Grande Madre, Bambino divino, Eroe, Trickster e Vecchio Saggio."></div>
        <figcaption>Il percorso di individuazione — illustrazione originale.</figcaption>
      </figure>
    </section>''')

    body.append('<section class="article-section references-section" id="riferimenti-bibliografici"><h2>Riferimenti bibliografici</h2>')
    references = [p.text.strip() for p in paragraphs[29:37] if p.text.strip()]
    assert len(references) == 6
    for paragraph in paragraphs[29:37]:
        if paragraph.text.strip():
            body.append(f'<p class="article-reference">{rich_text(paragraph)}</p>')
    body.append("</section>")

    body.append('<section class="article-section further-section" id="una-riflessione-sullappartenenza"><h2>Una riflessione sull’appartenenza</h2>')
    further = rich_text(paragraphs[38])
    further, count = re.subn("L’ombra e la voce", '<a href="l-ombra-e-la-voce.html">L’ombra e la voce</a>', further, count=1)
    assert count == 1
    body.append(f'<p class="article-further">{further}</p></section>')

    assert len(preserved_prose) == 22
    assert "Non è una tappa raggiunta una volta per tutte" in preserved_prose[-3]
    assert "Nella formulazione originaria di Jung" in preserved_prose[7]

    toc_html = "\n".join(f'<a href="#{ident}">{escape(title)}</a>' for ident, title in toc)
    return f'''<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow, noarchive">
  <meta name="description" content="Archetipi e individuazione di Tommaso Corona: un'introduzione alle figure archetipiche e al processo di crescita psicologica nel pensiero di Jung.">
  <meta name="theme-color" content="#263025">
  <title>Archetipi e individuazione · Atlante di Limite &amp; Relazione</title>
  <link rel="stylesheet" href="../styles.css">
  <link rel="stylesheet" href="../article.css">
</head>
<body class="article-page">
  <a class="skip-link" href="#il-testo">Vai al testo dell'articolo</a>
  <header class="masthead">
    <a href="../index.html" class="brand" aria-label="Atlante di Limite e Relazione, torna all'inizio"><span class="limite">LIMITE</span><span class="amp">&amp;</span><span class="relazione">RELAZIONE</span></a>
    <div class="edition">TOMMASO CORONA <span>ATLANTE VISIVO / 2026</span></div>
    <span class="private-badge"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg> Raccolta privata</span>
  </header>
  <main>
    <nav class="article-breadcrumb" aria-label="Percorso di navigazione"><a href="../index.html">Atlante</a><span aria-hidden="true">/</span><a href="../index.html#articoli-e-riflessioni">Articoli e riflessioni</a><span aria-hidden="true">/</span><span>Archetipi e individuazione</span></nav>
    <section class="article-hero" aria-labelledby="article-title">
      <div class="article-hero-copy">
        <p class="eyebrow"><span></span> ARTICOLI E RIFLESSIONI</p>
        <h1 id="article-title">Archetipi <em>e individuazione</em></h1>
        <p class="article-subtitle">Il percorso junghiano della crescita psicologica</p>
        <div class="article-meta"><strong>Tommaso Corona</strong><span aria-hidden="true">·</span><span>Circa {reading_minutes} minuti di lettura</span></div>
        <a class="primary-link" href="#il-testo">Inizia la lettura <span aria-hidden="true">↓</span></a>
      </div>
      <figure class="article-poster"><img src="../assets/articoli/archetipi-cover.png" width="941" height="1672" alt="Copertina Archetipi e individuazione: attorno al Sé sono raffigurati il Saggio, l'Eroe, l'Ombra, la Persona, Anima e Animus, la Grande Madre, il Bambino divino e il Trickster." fetchpriority="high"><figcaption>Illustrazione originale dell'articolo</figcaption></figure>
    </section>
    <div class="article-reading" id="articolo">
      <details class="article-mobile-toc"><summary>Indice dell'articolo</summary><nav aria-label="Indice dell'articolo su schermo piccolo">{toc_html}</nav></details>
      <aside class="article-sidebar"><nav class="article-toc" aria-label="Indice dell'articolo"><p class="eyebrow">NEL TESTO</p>{toc_html}</nav><a class="article-sidebar-back" href="../index.html#articoli-e-riflessioni">← Torna all’Atlante</a></aside>
      <article class="article-body" aria-label="Testo integrale dell'articolo">{''.join(body)}</article>
    </div>
    <section class="article-endnote"><span class="closing-mark" aria-hidden="true">&amp;</span><div><p class="eyebrow">UN APPROFONDIMENTO SULL'IDENTITÀ</p><p>Per continuare dal percorso di individuazione alla relazione con il gruppo, leggi anche <a href="l-ombra-e-la-voce.html">L’ombra e la voce</a>.</p><a class="primary-link" href="../index.html">Torna all’Atlante <span aria-hidden="true">↗</span></a></div></section>
  </main>
  <footer><span><b class="limite">LIMITE</b> &amp; <b class="relazione">RELAZIONE</b> · Tommaso Corona</span><span>Atlante di Limite &amp; Relazione · Articoli e riflessioni</span></footer>
</body>
</html>
'''


def extract_images(docx: Path, cover: Path, diagram: Path) -> None:
    with ZipFile(docx) as package:
        media = sorted(name for name in package.namelist() if name.startswith("word/media/"))
        assert media == ["word/media/image1.png", "word/media/image2.png"], media
        cover.parent.mkdir(parents=True, exist_ok=True)
        diagram.parent.mkdir(parents=True, exist_ok=True)
        cover.write_bytes(package.read(media[0]))
        diagram.write_bytes(package.read(media[1]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("output_html", type=Path)
    parser.add_argument("output_cover", type=Path)
    parser.add_argument("output_diagram", type=Path)
    args = parser.parse_args()
    args.output_html.parent.mkdir(parents=True, exist_ok=True)
    args.output_html.write_text(render(args.docx), encoding="utf-8")
    extract_images(args.docx, args.output_cover, args.output_diagram)
    print(f"Generated article and extracted both original illustrations: {args.output_html}")
