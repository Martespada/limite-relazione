#!/usr/bin/env python3
"""Render the author's final Word article as an accessible Atlas reading page.

The Word file is the textual source of truth. We preserve its paragraphs,
inline emphasis and bibliographic hyperlinks without editorial rewrites.
"""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re
import unicodedata

from docx import Document
from docx.text.hyperlink import Hyperlink


HEADINGS = {
    "Una scena naturale come metafora sociale",
    "Dalla percezione alla costruzione del significato",
    "Realtà di primo e di secondo livello",
    "La cornice che organizza il mondo",
    "Le immagini come cornici della realtà",
    "Le frasi interne e la costruzione del Sé",
    "Dissonanza cognitiva e difesa della coerenza",
    "Ragionamento motivato e bias di conferma",
    "Dalla realtà individuale alla realtà condivisa",
    "Le rappresentazioni sociali",
    "Ingroup, outgroup e auto-categorizzazione",
    "Dalla divergenza alla polarizzazione",
    "La distribuzione preventiva della colpa",
    "Moralizzazione e impossibilità del compromesso",
    "Funzionalità, devianza ed etica",
    "Il punto in cui il dialogo si interrompe",
    "Ritornare al poster",
    "La pillola rossa e la pillola blu",
    "Riferimenti bibliografici",
}

RELATED = [
    ("La realtà della realtà", "Evento e significato", "reality-of-reality"),
    ("Rappresentazione mentale e sociale", "Dal singolo al gruppo", "mental-social-representation"),
    ("Effetto cornice", "Selezione e salienza", "framing"),
    ("Dissonanza cognitiva", "Difesa della coerenza", "dissonance"),
    ("Polarizzazione di gruppo", "Identità e appartenenza", "polarization"),
    ("Realismo ingenuo", "La propria prospettiva", "naive-realism"),
    ("Intersoggettività", "Riconoscere l'altro", "intersubjectivity"),
]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def rich_text(paragraph) -> str:
    parts = []
    for piece in paragraph.iter_inner_content():
        if isinstance(piece, Hyperlink):
            label = escape(piece.text)
            url = escape(piece.address, quote=True)
            parts.append(f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>')
            continue
        value = escape(piece.text).replace("\n", "<br>")
        if not value:
            continue
        if piece.italic:
            value = f"<em>{value}</em>"
        if piece.bold:
            value = f"<strong>{value}</strong>"
        parts.append(value)
    return "".join(parts)


def render(docx_path: Path) -> str:
    doc = Document(docx_path)
    paragraphs = [p for p in doc.paragraphs if p.text.strip()]
    labels = [p.text.strip() for p in paragraphs]
    assert labels[0] == "LA ZEBRA, IL LEONE E L’ERBA"
    assert labels[3] == "Abstract"
    assert labels[6] == "Una scena naturale come metafora sociale"
    assert labels[-22] == "Riferimenti bibliografici"
    assert all(label in labels for label in HEADINGS)

    abstract = rich_text(paragraphs[4])
    keywords = rich_text(paragraphs[5])
    article_paragraphs = paragraphs[6:]
    word_count = len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", " ".join(labels[6:])))
    reading_minutes = round(word_count / 220)

    toc = []
    body = []
    section_open = False
    reference_mode = False
    preserved = []
    for paragraph in article_paragraphs:
        label = paragraph.text.strip()
        preserved.append(label)
        if label in HEADINGS:
            if section_open:
                body.append("</section>")
            ident = slugify(label)
            reference_mode = label == "Riferimenti bibliografici"
            body.append(f'<section class="article-section{" references-section" if reference_mode else ""}" id="{ident}">')
            body.append(f'<h2>{escape(label)}</h2>')
            toc.append((ident, label))
            section_open = True
        elif reference_mode:
            body.append(f'<p class="article-reference">{rich_text(paragraph)}</p>')
        elif label == "Ogni prospettiva può cogliere una parte autentica della realtà, pur restando parziale.":
            body.append(f'<p class="opening-line">{rich_text(paragraph)}</p>')
        else:
            body.append(f'<p>{rich_text(paragraph)}</p>')
    if section_open:
        body.append("</section>")

    # Verify all original body paragraphs are represented in the reading source.
    assert len(preserved) == len(article_paragraphs)
    assert sum(label in HEADINGS for label in preserved) == len(HEADINGS)
    assert any("ma anche quando non dispongono" in p for p in preserved)
    assert any("Nei conflitti umani, percezioni" in p for p in preserved)

    toc_html = "\n".join(
        f'<a href="#{ident}">{escape(title)}</a>' for ident, title in toc
    )
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
  <meta name="description" content="La zebra, il leone e l’erba di Tommaso Corona: percezione, realtà costruita e conflitto per il significato in una società polarizzata.">
  <meta name="theme-color" content="#263025">
  <title>La zebra, il leone e l’erba · Atlante di Limite & Relazione</title>
  <link rel="stylesheet" href="../styles.css">
  <link rel="stylesheet" href="../article.css">
</head>
<body class="article-page">
  <a class="skip-link" href="#articolo">Vai al testo dell'articolo</a>
  <header class="masthead">
    <a href="../index.html" class="brand" aria-label="Atlante di Limite e Relazione, torna all'inizio"><span class="limite">LIMITE</span><span class="amp">&</span><span class="relazione">RELAZIONE</span></a>
    <div class="edition">TOMMASO CORONA <span>ATLANTE VISIVO / 2026</span></div>
    <span class="private-badge"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg> Raccolta privata</span>
  </header>
  <main>
    <nav class="article-breadcrumb" aria-label="Percorso di navigazione"><a href="../index.html">Atlante</a><span aria-hidden="true">/</span><a href="../index.html#articoli-e-riflessioni">Articoli e riflessioni</a><span aria-hidden="true">/</span><span>La zebra, il leone e l’erba</span></nav>
    <section class="article-hero" aria-labelledby="article-title">
      <div class="article-hero-copy">
        <p class="eyebrow"><span></span> ARTICOLI E RIFLESSIONI</p>
        <h1 id="article-title">La zebra, il leone <em>e l’erba</em></h1>
        <p class="article-subtitle">Percezione, realtà costruita e conflitto per il significato in una società polarizzata</p>
        <div class="article-meta"><strong>Tommaso Corona</strong><span aria-hidden="true">·</span><span>Circa {reading_minutes} minuti di lettura</span></div>
        <a class="primary-link" href="#articolo">Inizia la lettura <span aria-hidden="true">↓</span></a>
      </div>
      <figure class="article-poster"><img src="../assets/articoli/la-zebra-cover.jpeg" width="900" height="1600" alt="Manifesto Questione di prospettiva: una zebra bruca l'erba mentre un leone si avvicina. La frase invita a considerare il punto di vista dell'erba." fetchpriority="high"><figcaption>Manifesto originale dell'articolo</figcaption></figure>
    </section>
    <section class="article-abstract" aria-labelledby="abstract-title"><div><p class="eyebrow">IN APERTURA</p><h2 id="abstract-title">Abstract<span class="title-dot">.</span></h2></div><div><p>{abstract}</p><p class="article-keywords">{keywords}</p></div></section>
    <div class="article-reading" id="articolo">
      <details class="article-mobile-toc"><summary>Indice dell'articolo</summary><nav aria-label="Indice dell'articolo su schermo piccolo">{toc_html}</nav></details>
      <aside class="article-sidebar"><nav class="article-toc" aria-label="Indice dell'articolo"><p class="eyebrow">NEL TESTO</p>{toc_html}</nav><a class="article-sidebar-back" href="../index.html#articoli-e-riflessioni">← Torna all’Atlante</a></aside>
      <article class="article-body" aria-label="Testo integrale dell'articolo">{''.join(body)}</article>
    </div>
    <section class="related-section" aria-labelledby="related-title"><p class="eyebrow">CONTINUA A ESPLORARE</p><h2 id="related-title">I concetti nell'Atlante<span class="title-dot">.</span></h2><p>Sette schede della raccolta per proseguire, da prospettive complementari, i temi affrontati nell'articolo.</p><div class="related-grid">{related_html}</div></section>
    <section class="article-endnote"><span class="closing-mark" aria-hidden="true">&</span><div><p class="eyebrow">UNO SGUARDO, NON UN’ETICHETTA</p><p>Comprendere una prospettiva non significa assolvere un comportamento. Il confronto aiuta a interrogare le cornici attraverso cui leggiamo il mondo.</p><a class="primary-link" href="../index.html">Torna all’Atlante <span aria-hidden="true">↗</span></a></div></section>
  </main>
  <footer><span><b class="limite">LIMITE</b> & <b class="relazione">RELAZIONE</b> · Tommaso Corona</span><span>Atlante di Limite & Relazione · Articoli e riflessioni</span></footer>
</body>
</html>
'''


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = render(args.docx)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"Generated {args.output} ({len(result)} characters)")
