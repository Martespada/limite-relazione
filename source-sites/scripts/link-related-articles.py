#!/usr/bin/env python3
"""Add reversible, non-editorial cross-links to the existing Atlas articles."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "site/articoli"
DESTINATION = "la-soglia-della-radicalizzazione.html"
SLOGUN = "lo-slogun-batte-largomento.html"
BRIDGES = {
    "la-zebra-il-leone-e-lerba.html": (
        "Dalle prospettive contrapposte alla costruzione del nemico",
        "Quando la lettura degli eventi diventa un segno di appartenenza, il conflitto può cambiare natura.",
    ),
    "l-ombra-e-la-voce.html": (
        "Quando l’appartenenza si trasforma in contrapposizione",
        "Il bisogno di riconoscersi in un gruppo può anche irrigidire il confine fra «noi» e «loro».",
    ),
}

for file_name, (heading, introduction) in BRIDGES.items():
    file_path = ROOT / file_name
    source = file_path.read_text(encoding="utf-8")
    if 'class="article-bridge-links"' in source:
        continue
    links = f'''<div class="article-bridge-links">
        <a href="{DESTINATION}">Leggi «La soglia della radicalizzazione» <span aria-hidden="true">↗</span></a>
        <a href="{SLOGUN}">Leggi «Lo “slogun” batte l’argomento» <span aria-hidden="true">↗</span></a>
      </div>'''
    old_link = f'<a href="{DESTINATION}">Leggi «La soglia della radicalizzazione» <span aria-hidden="true">↗</span></a>'
    if 'class="article-bridge"' in source:
        assert source.count(old_link) == 1, file_name
        file_path.write_text(source.replace(old_link, links, 1), encoding="utf-8")
        print(f"Extended {file_name}")
        continue
    location = '    </div>\n    <section class="related-section"'
    assert source.count(location) == 1, file_name
    bridge = f'''    </div>
    <section class="article-bridge" aria-label="Lettura collegata">
      <div><p class="eyebrow">UN'ALTRA RIFLESSIONE</p><h2>{heading}</h2><p>{introduction}</p></div>
      {links}
    </section>
    <section class="related-section"'''
    file_path.write_text(source.replace(location, bridge, 1), encoding="utf-8")
    print(f"Linked {file_name}")
