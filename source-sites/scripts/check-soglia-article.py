#!/usr/bin/env python3
"""Verify the author's unchanged text and Atlas cross-link integrity."""

import json
from pathlib import Path
import sys

from docx import Document
from lxml import html

root = Path(__file__).resolve().parent.parent
docx = Path(sys.argv[1]) if len(sys.argv) > 1 else None
article = html.fromstring((root / "site/articoli/la-soglia-della-radicalizzazione.html").read_text())

if docx is not None:
    source = Document(docx).paragraphs
    assert article.xpath('//section[contains(@class,"article-abstract")]//p[contains(@class,"article-epigraph")]')[0].text_content() == source[3].text
    authored = article.xpath('//article[@class="article-body"]/section[not(contains(@class,"article-crosslinks")) and not(contains(@class,"article-concept-links"))]/p')
    expected = [p.text for index, p in enumerate(source) if 4 <= index <= 34 and index != 23 and p.text.strip()]
    actual = [p.text_content() for p in authored]
    assert actual == expected, [(i, a, b) for i, (a, b) in enumerate(zip(actual, expected)) if a != b]
    assert "lì comincia la radicalizzazione" in actual[16]

data = (root / "site/data.js").read_text().removeprefix("window.ATLAS_POSTERS = ").strip().removesuffix(";")
ids = {item["id"] for item in json.loads(data)}
cards = article.xpath('//section[@id="esplora-i-concetti"]//a[contains(@class,"related-item")]')
assert len(cards) == 6
assert all(a.get("href").split("#bias=")[1] in ids for a in cards)
psiche_links = article.xpath('//a[contains(text(),"B0DVCC1HY6")]')
assert len(psiche_links) == 1
assert psiche_links[0].get("href") == "https://www.amazon.it/dp/B0DVCC1HY6"

for name in ("la-zebra-il-leone-e-lerba.html", "l-ombra-e-la-voce.html"):
    linked = html.fromstring((root / "site/articoli" / name).read_text())
    assert linked.xpath('//a[@href="la-soglia-della-radicalizzazione.html"]')
    assert article.xpath(f'//a[@href="{name}"]')

app = (root / "site/app.js").read_text()
assert "${articleCrosslink(p)}" in app
assert all(f"'{card.get('href').split('#bias=')[1]}'" in app or f"{card.get('href').split('#bias=')[1]}:" in app for card in cards)
assert article.xpath('//section[@id="esplora-i-concetti"]')[0] == article.xpath('//article[@class="article-body"]/section')[-1]

for page in [root / "site/index.html", *sorted((root / "site/articoli").glob("*.html"))]:
    soup = html.fromstring(page.read_text())
    for a in soup.xpath('//a[@href]'):
        href = a.get("href")
        if href.startswith(("https:", "http:", "mailto:", "#")):
            continue
        path = href.split("#", 1)[0]
        if path:
            assert (page.parent / path).exists(), (page.name, href)

print(f"Verificati {len(expected) + 1 if docx else 'non confrontati'} paragrafi originali, {len(cards)} schede e tutti i collegamenti reciproci.")
