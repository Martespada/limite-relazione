#!/usr/bin/env python3
"""Publish the author's Word article without rewriting its prose.

Headings, navigation, links to the other articles and Atlas cards are web-only
editorial additions. The cover image is converted for efficient web display.
"""

from __future__ import annotations

import argparse
from html import escape
from io import BytesIO
from pathlib import Path
from hashlib import sha256
import re
from zipfile import ZipFile

from docx import Document
from docx.text.hyperlink import Hyperlink
from PIL import Image


SECTIONS = [
    (9, "Dall’argomentazione allo slogun", "dallargomentazione-allo-slogun"),
    (15, "Perché una frase così breve attecchisce", "le-scorciatoie-del-pensiero"),
    (18, "Competenza, appartenenza e identità", "identita-e-appartenenza"),
    (24, "Credenze e vulnerabilità alla manipolazione", "credenze-e-manipolazione"),
    (32, "Rallentare per tornare al confronto", "ritrovare-il-confronto"),
    (37, "Riferimenti bibliografici", "riferimenti-bibliografici"),
]

RELATED = [
    ("Bias di conferma", "Quando un messaggio rafforza ciò che già crediamo", "confirmation"),
    ("Effetto cornice", "La formulazione orienta la lettura dei fatti", "framing"),
    ("Dissonanza cognitiva", "Difendere una convinzione quando è messa in crisi", "dissonance"),
    ("Effetto illusorio della verità", "La familiarità può sembrare una prova", "illusory-truth"),
    ("Effetto Dunning–Kruger", "Competenza e consapevolezza dei propri limiti", "dunning-kruger"),
    ("Polarizzazione di gruppo", "Quando il confronto rafforza lo schieramento", "polarization"),
    ("Pensiero di gruppo", "Quando l’appartenenza riduce il dissenso", "groupthink"),
]


def rich_text(paragraph) -> str:
    parts: list[str] = []
    for piece in paragraph.iter_inner_content():
        if isinstance(piece, Hyperlink):
            label = escape(piece.text)
            target = escape(piece.address, quote=True)
            parts.append(f'<a href="{target}" target="_blank" rel="noopener noreferrer">{label}</a>')
        else:
            fragment = escape(piece.text).replace("\n", "<br>")
            if not fragment:
                continue
            if piece.italic:
                fragment = f"<em>{fragment}</em>"
            if piece.bold:
                fragment = f"<strong>{fragment}</strong>"
            parts.append(fragment)
    return "".join(parts)


def render(docx: Path) -> str:
    paragraphs = Document(docx).paragraphs
    assert paragraphs[1].text == "LO “SLOGUN” BATTE L’ARGOMENTO."
    assert paragraphs[2].text == "Scrolliamo emozioni, non argomentazioni."
    assert paragraphs[4].text.lower() == "di tommaso corona"
    assert paragraphs[7].text.startswith("“Lo slogun è uno slogan armato:")
    assert paragraphs[37].text == "RIFERIMENTI BIBLIOGRAFICI"
    assert "La manipolazione è deliberata in chi costruisce lo slogun" in paragraphs[12].text
    assert "Solo il dialogo può trasformare" in paragraphs[35].text

    heading_by_position = {index: (label, anchor) for index, label, anchor in SECTIONS}
    toc = [(anchor, label) for _, label, anchor in SECTIONS]
    body: list[str] = []
    copied_indices: list[int] = []
    section_open = False
    for index in range(9, 47):
        paragraph = paragraphs[index]
        if index in heading_by_position:
            if section_open:
                body.append("</section>")
            label, anchor = heading_by_position[index]
            css = " references-section" if index == 37 else ""
            body.append(f'<section class="article-section{css}" id="{anchor}"><h2>{escape(label)}</h2>')
            section_open = True
        if not paragraph.text.strip() or index == 37:
            continue
        css = ""
        if index in (18, 19, 24, 25):
            css = ' class="article-voice"'
        elif index in range(38, 47):
            css = ' class="article-reference"'
        elif index == 35:
            css = ' class="article-conclusion"'
        body.append(f"<p{css}>{rich_text(paragraph)}</p>")
        copied_indices.append(index)
    body.append("</section>")
    assert copied_indices == [index for index in range(9, 47) if index != 37 and paragraphs[index].text.strip()]

    readings = '''<section class="article-section article-crosslinks" id="altre-riflessioni">
      <h2>Altre riflessioni nell’Atlante</h2>
      <p>Tre prospettive collegate al rapporto tra ciò che crediamo, il gruppo al quale apparteniamo e il modo in cui discutiamo.</p>
      <div class="article-inline-links article-inline-links--three">
        <a href="la-soglia-della-radicalizzazione.html"><strong>La soglia della radicalizzazione</strong><span>Quando lo schieramento diventa parte stabile dell’identità <span aria-hidden="true">↗</span></span></a>
        <a href="la-zebra-il-leone-e-lerba.html"><strong>La zebra, il leone e l’erba</strong><span>Come selezioniamo i fatti e costruiamo le nostre interpretazioni <span aria-hidden="true">↗</span></span></a>
        <a href="l-ombra-e-la-voce.html"><strong>L’ombra e la voce</strong><span>Restare nel gruppo senza rinunciare alla propria voce <span aria-hidden="true">↗</span></span></a>
      </div>
    </section>'''
    concept_cards = "\n".join(
        f'<a class="related-item" href="../index.html#bias={ident}"><span class="related-title">{escape(title)}</span><span class="related-why">{escape(why)}</span><span class="related-arrow" aria-hidden="true">↗</span></a>'
        for title, why, ident in RELATED
    )
    concepts = f'''<section class="article-section article-concept-links" id="esplora-i-concetti">
      <h2>Esplora i concetti nell’Atlante</h2>
      <p>Le schede approfondiscono separatamente alcuni dei meccanismi richiamati nel testo.</p>
      <div class="related-grid">{concept_cards}</div>
    </section>'''
    toc += [("altre-riflessioni", "Altre riflessioni"), ("esplora-i-concetti", "Esplora i concetti")]
    nav_html = "\n".join(f'<a href="#{anchor}">{escape(title)}</a>' for anchor, title in toc)
    word_count = len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", " ".join(p.text for p in paragraphs[7:47])))
    minutes = round(word_count / 220)

    cover_path = Path(__file__).resolve().parent.parent / "site/assets/articoli/slogun-cover.webp"
    cover_version = sha256(cover_path.read_bytes()).hexdigest()[:12] if cover_path.exists() else "initial"

    return f'''<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow, noarchive">
  <meta name="description" content="Lo slogun batte l’argomento, di Tommaso Corona: manipolazione del messaggio, bias di conferma e appartenenza nei social.">
  <meta name="theme-color" content="#263025">
  <title>Lo “slogun” batte l’argomento · Atlante di Limite &amp; Relazione</title>
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
    <nav class="article-breadcrumb" aria-label="Percorso di navigazione"><a href="../index.html">Atlante</a><span aria-hidden="true">/</span><a href="../index.html#articoli-e-riflessioni">Articoli e riflessioni</a><span aria-hidden="true">/</span><span>Lo “slogun” batte l’argomento</span></nav>
    <section class="article-hero" aria-labelledby="article-title">
      <div class="article-hero-copy">
        <p class="eyebrow"><span></span> ARTICOLI E RIFLESSIONI</p>
        <h1 id="article-title">Lo “slogun” batte <em>l’argomento.</em></h1>
        <p class="article-subtitle">{escape(paragraphs[2].text)}</p>
        <div class="article-meta"><strong>Tommaso Corona</strong><span aria-hidden="true">·</span><span>Circa {minutes} minuti di lettura</span></div>
        <a class="primary-link" href="#articolo">Inizia la lettura <span aria-hidden="true">↓</span></a>
      </div>
      <figure class="article-poster"><img src="../assets/articoli/slogun-cover.webp?v={cover_version}" alt="Immagine di copertina dell’articolo Lo slogun batte l’argomento" fetchpriority="high"><figcaption>Immagine originale dell’articolo</figcaption></figure>
    </section>
    <section class="article-abstract" aria-labelledby="opening-title"><div><p class="eyebrow">IN APERTURA</p><h2 id="opening-title">Un messaggio che colpisce<span class="title-dot">.</span></h2></div><div><p class="article-epigraph">{rich_text(paragraphs[7])}</p></div></section>
    <div class="article-reading" id="articolo">
      <details class="article-mobile-toc"><summary>Indice dell'articolo</summary><nav aria-label="Indice dell'articolo su schermo piccolo">{nav_html}</nav></details>
      <aside class="article-sidebar"><nav class="article-toc" aria-label="Indice dell'articolo"><p class="eyebrow">NEL TESTO</p>{nav_html}</nav><a class="article-sidebar-back" href="../index.html#articoli-e-riflessioni">← Torna all’Atlante</a></aside>
      <article class="article-body" aria-label="Testo integrale dell'articolo">{''.join(body)}{readings}{concepts}</article>
    </div>
    <section class="article-endnote"><span class="closing-mark" aria-hidden="true">&amp;</span><div><p class="eyebrow">PENSIERO E RELAZIONE</p><p>Quando il messaggio cerca l’adesione prima della comprensione, rallentare e tornare al dialogo diventa una scelta.</p><a class="primary-link" href="../index.html">Torna all’Atlante <span aria-hidden="true">↗</span></a></div></section>
  </main>
  <footer><span><b class="limite">LIMITE</b> &amp; <b class="relazione">RELAZIONE</b> · Tommaso Corona</span><span>Atlante di Limite &amp; Relazione · Articoli e riflessioni</span></footer>
</body>
</html>
'''


def make_cover(source: Path, destination: Path, cover_source: Path | None = None) -> None:
    if cover_source is not None:
        # A separately approved cover takes precedence over the Word artwork.
        image = Image.open(cover_source)
    elif destination.exists():
        # Subsequent regenerations of the HTML must not roll back that cover.
        return
    else:
        with ZipFile(source) as archive:
            image = Image.open(BytesIO(archive.read("word/media/image1.png"))).convert("RGB")
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "WEBP", quality=96, method=6)


def refresh_cover_versions(cover: Path) -> None:
    version = sha256(cover.read_bytes()).hexdigest()[:12]
    site_root = Path(__file__).resolve().parent.parent / "site"
    for page in (site_root / "index.html", site_root / "articoli/lo-slogun-batte-largomento.html"):
        previous = page.read_text(encoding="utf-8")
        updated, count = re.subn(r"slogun-cover\.webp(?:\?v=[a-f0-9]{12})?", f"slogun-cover.webp?v={version}", previous)
        assert count == 1, page
        if updated != previous:
            page.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("output_html", type=Path)
    parser.add_argument("output_cover", type=Path)
    parser.add_argument("--cover-source", type=Path, help="Use a newly approved cover image instead of the Word cover")
    parser.add_argument("--cover-only", action="store_true", help="Update only the cover, retaining the already approved article text")
    args = parser.parse_args()
    make_cover(args.docx, args.output_cover, args.cover_source)
    if not args.cover_only:
        args.output_html.parent.mkdir(parents=True, exist_ok=True)
        args.output_html.write_text(render(args.docx), encoding="utf-8")
    refresh_cover_versions(args.output_cover)
    print(f"Updated {args.output_cover}" if args.cover_only else f"Generated {args.output_html} and {args.output_cover}")
