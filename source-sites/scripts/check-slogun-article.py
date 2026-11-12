#!/usr/bin/env python3
"""Check full Word fidelity and reciprocal Atlas article/concept navigation."""

import json
from pathlib import Path
import sys

from docx import Document
from lxml import html

root = Path(__file__).resolve().parent.parent
pages = root / "site/articoli"
source = Document(Path(sys.argv[1])).paragraphs
article = html.fromstring((pages / "lo-slogun-batte-largomento.html").read_text())
opening = article.xpath('//section[contains(@class,"article-abstract")]//p[contains(@class,"article-epigraph")]')
assert len(opening) == 1 and opening[0].text_content() == source[7].text

authored = article.xpath('//article[@class="article-body"]/section[not(contains(@class,"article-crosslinks")) and not(contains(@class,"article-concept-links"))]/p')
expected = [p.text for i, p in enumerate(source) if 9 <= i <= 46 and i != 37 and p.text.strip()]
assert [p.text_content() for p in authored] == expected

data = (root / "site/data.js").read_text().removeprefix("window.ATLAS_POSTERS = ").strip().removesuffix(";")
ids = {item["id"] for item in json.loads(data)}
cards = article.xpath('//section[@id="esplora-i-concetti"]//a[contains(@class,"related-item")]')
assert len(cards) == 7 and all(card.get("href").split("#bias=")[1] in ids for card in cards)

for name in ("la-zebra-il-leone-e-lerba.html", "l-ombra-e-la-voce.html", "la-soglia-della-radicalizzazione.html"):
    other = html.fromstring((pages / name).read_text())
    assert article.xpath(f'//a[@href="{name}"]'), name
    assert other.xpath('//a[@href="lo-slogun-batte-largomento.html"]'), name

app = (root / "site/app.js").read_text()
assert "slogunConnections" in app and "lo-slogun-batte-largomento.html" in app
assert all(f"'{card.get('href').split('#bias=')[1]}'" in app or f"{card.get('href').split('#bias=')[1]}:" in app for card in cards)
assert article.xpath('//section[@id="esplora-i-concetti"]')[0] == article.xpath('//article[@class="article-body"]/section')[-1]

for page in [root / "site/index.html", *sorted(pages.glob("*.html"))]:
    parsed = html.fromstring(page.read_text())
    for anchor in parsed.xpath('//a[@href]'):
        href = anchor.get("href")
        if href.startswith(("http:", "https:", "mailto:", "#")):
            continue
        target = href.split("#", 1)[0]
        if target:
            assert (page.parent / target).exists(), (page.name, href)

assert (root / "site/assets/articoli/slogun-cover.webp").stat().st_size > 20_000
print(f"Verificati {len(expected)+1} paragrafi fedeli, {len(cards)} schede e tutti i collegamenti interni e reciproci.")
