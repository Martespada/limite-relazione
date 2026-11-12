#!/usr/bin/env python3
"""Publish L'ombra e la voce from the author's finalized Word document.

The Word file is the source of truth for every paragraph, emphasis and reference.
The embedded cover artwork is extracted unchanged, not redrawn or recompressed.
"""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re
import unicodedata
from zipfile import ZipFile

from docx import Document
from docx.text.hyperlink import Hyperlink


JUNG_HEADINGS = {
    "Dall’ombra dell’altro all’ombra interiore",
    "L’ombra e il cammino verso sé stessi",
}
HEADINGS = JUNG_HEADINGS | {
    "Riferimenti bibliografici",
    "PER APPROFONDIRE",
}

RELATED = [
    ("Identità", "Ruoli e senso di sé", "limit-identity"),
    ("Pensiero di gruppo", "Il peso del consenso", "groupthink"),
    ("Risposta compiacente", "L'adattamento all'altro", "fawn-response"),
    ("Deindividuazione", "L'io dentro il gruppo", "deindividuation"),
    ("Intersoggettività", "Il rapporto con l'altro", "intersubjectivity"),
    ("Autorità", "Il ruolo dell'influenza", "persuasion-authority"),
]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def rich_text(paragraph) -> str:
    parts = []
    for piece in paragraph.iter_inner_content():
        if isinstance(piece, Hyperlink):
            text = escape(piece.text)
            address = escape(piece.address, quote=True)
            parts.append(f'<a href="{address}" target="_blank" rel="noopener noreferrer">{text}</a>')
            continue
        text = escape(piece.text).replace("\n", "<br>")
        if not text:
            continue
        if piece.italic:
            text = f"<em>{text}</em>"
        if piece.bold:
            text = f"<strong>{text}</strong>"
        parts.append(text)
    return "".join(parts)


def render(input_docx: Path, secondary_article_available: bool = False) -> str:
    paragraphs = Document(input_docx).paragraphs
    assert paragraphs[1].text.strip().upper() == "L’OMBRA E LA VOCE"
    assert paragraphs[3].text.strip() == "di Tommaso Corona"
    assert "Ogni gruppo ha bisogno di appartenenza" in paragraphs[5].text
    assert paragraphs[57].text.strip() == "PER APPROFONDIRE"
    assert "Archetipi e individuazione" in paragraphs[58].text

    epigraph = rich_text(paragraphs[5])
    source = [p for p in paragraphs[7:] if p.text.strip()]
    labels = [p.text.strip() for p in source]
    assert "Riferimenti bibliografici" in labels
    assert "PER APPROFONDIRE" in labels
    assert len(JUNG_HEADINGS.intersection(labels)) == 1

    toc = [("la-riflessione", "Appartenenza e voce")]
    body = ['<section class="article-section" id="la-riflessione">']
    section_type = "prose"

    for paragraph in source:
        label = paragraph.text.strip()
        if label in HEADINGS:
            body.append("</section>")
            display_label = "L’ombra e il cammino verso sé stessi" if label in JUNG_HEADINGS else ("Per approfondire" if label == "PER APPROFONDIRE" else label)
            ident = slugify(display_label)
            section_type = "references" if label == "Riferimenti bibliografici" else ("further" if label == "PER APPROFONDIRE" else "prose")
            extra_class = " references-section" if section_type == "references" else (" further-section" if section_type == "further" else "")
            body.append(f'<section class="article-section{extra_class}" id="{ident}"><h2>{escape(display_label)}</h2>')
            toc.append((ident, display_label))
        else:
            content = rich_text(paragraph)
            if section_type == "further" and secondary_article_available:
                content, n = re.subn(
                    "Archetipi e individuazione",
                    '<a href="archetipi-e-individuazione.html">Archetipi e individuazione</a>',
                    content,
                    count=1,
                )
                assert n == 1
            css = " class=\"article-reference\"" if section_type == "references" else (" class=\"article-further\"" if section_type == "further" else "")
            body.append(f"<p{css}>{content}</p>")
    body.append("</section>")

    # The generated page must include every authored paragraph, including the
    # bibliography and the author's final invitation to deepen the subject.
    assert len(labels) == sum(1 for part in body if part.startswith("<p")) + sum(label in HEADINGS for label in labels)
    assert "l’ombra ci mostra gli aspetti di noi" in " ".join(labels)
    assert "Attraverso di essa, ciascuno può esprimere" in " ".join(labels)

    words = len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", " ".join(p.text for p in source)))
    reading_minutes = max(1, round(words / 220))
    toc_html = "\n".join(f'<a href="#{ident}">{escape(label)}</a>' for ident, label in toc)
    related_html = "\n".join(
        f'<a class="related-item" href="../index.html#bias={ident}"><span class="related-title">{escape(title)}</span><span class="related-why">{escape(why)}</span><span class="related-arrow" aria-hidden="true">↗</span></a>'
        for title, why, ident in RELATED
    )

    return f'''<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow, noarchive">
  <meta name="description" content="L’ombra e la voce di Tommaso Corona: identità, appartenenza, compiacenza, sicurezza psicologica e individuazione nel pensiero di Jung.">
  <meta name="theme-color" content="#263025">
  <title>L’ombra e la voce · Atlante di Limite &amp; Relazione</title>
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
    <nav class="article-breadcrumb" aria-label="Percorso di navigazione"><a href="../index.html">Atlante</a><span aria-hidden="true">/</span><a href="../index.html#articoli-e-riflessioni">Articoli e riflessioni</a><span aria-hidden="true">/</span><span>L’ombra e la voce</span></nav>
    <section class="article-hero" aria-labelledby="article-title">
      <div class="article-hero-copy">
        <p class="eyebrow"><span></span> ARTICOLI E RIFLESSIONI</p>
        <h1 id="article-title">L’ombra <em>e la voce</em></h1>
        <p class="article-subtitle">Appartenenza, identità e responsabilità della parola</p>
        <div class="article-meta"><strong>Tommaso Corona</strong><span aria-hidden="true">·</span><span>Circa {reading_minutes} minuti di lettura</span></div>
        <a class="primary-link" href="#articolo">Inizia la lettura <span aria-hidden="true">↓</span></a>
      </div>
      <figure class="article-poster"><img src="../assets/articoli/l-ombra-e-la-voce-cover.png" width="1055" height="1491" alt="Copertina L’ombra e la voce: una figura illuminata al centro di un gruppo, con le ombre proiettate in avanti e un filo di luce che esprime la voce." fetchpriority="high"><figcaption>Illustrazione originale dell'articolo</figcaption></figure>
    </section>
    <section class="article-abstract" aria-labelledby="opening-title"><div><p class="eyebrow">IN APERTURA</p><h2 id="opening-title">Un pensiero guida<span class="title-dot">.</span></h2></div><div><p class="article-epigraph">{epigraph}</p></div></section>
    <div class="article-reading" id="articolo">
      <details class="article-mobile-toc"><summary>Indice dell'articolo</summary><nav aria-label="Indice dell'articolo su schermo piccolo">{toc_html}</nav></details>
      <aside class="article-sidebar"><nav class="article-toc" aria-label="Indice dell'articolo"><p class="eyebrow">NEL TESTO</p>{toc_html}</nav><a class="article-sidebar-back" href="../index.html#articoli-e-riflessioni">← Torna all’Atlante</a></aside>
      <article class="article-body" aria-label="Testo integrale dell'articolo">{''.join(body)}</article>
    </div>
    <section class="related-section" aria-labelledby="related-title"><p class="eyebrow">CONTINUA A ESPLORARE</p><h2 id="related-title">I concetti nell'Atlante<span class="title-dot">.</span></h2><p>Sei schede per collegare i temi dell'articolo alle dinamiche dell'identità, della compiacenza e della vita nei gruppi.</p><div class="related-grid">{related_html}</div></section>
    <section class="article-endnote"><span class="closing-mark" aria-hidden="true">&amp;</span><div><p class="eyebrow">IDENTITÀ E RELAZIONE</p><p>Una riflessione sull'appartenere a un gruppo senza smarrire la propria voce.</p><a class="primary-link" href="../index.html">Torna all’Atlante <span aria-hidden="true">↗</span></a></div></section>
  </main>
  <footer><span><b class="limite">LIMITE</b> &amp; <b class="relazione">RELAZIONE</b> · Tommaso Corona</span><span>Atlante di Limite &amp; Relazione · Articoli e riflessioni</span></footer>
</body>
</html>
'''


def extract_cover(docx: Path, output: Path) -> None:
    with ZipFile(docx) as source:
        files = [n for n in source.namelist() if n.startswith("word/media/")]
        assert files == ["word/media/image1.png"], files
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(source.read(files[0]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("output_html", type=Path)
    parser.add_argument("output_cover", type=Path)
    args = parser.parse_args()
    args.output_html.parent.mkdir(parents=True, exist_ok=True)
    args.output_html.write_text(render(args.docx, (args.output_html.parent / "archetipi-e-individuazione.html").exists()), encoding="utf-8")
    extract_cover(args.docx, args.output_cover)
    print(f"Generated {args.output_html} and extracted original cover {args.output_cover}")
