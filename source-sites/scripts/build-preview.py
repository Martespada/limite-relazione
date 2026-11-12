"""Generate the private review area without changing the current Atlas pages."""
from pathlib import Path
from html.parser import HTMLParser
import collections
import html
import json
import re

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
OUT = SITE / 'anteprima'
OUT.mkdir(exist_ok=True)
(OUT / 'articoli').mkdir(exist_ok=True)
esc = lambda value: html.escape(str(value), quote=True)


class Node:
    def __init__(self, tag, attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []
    def find(self, predicate):
        return [n for c in self.children if isinstance(c, Node) for n in ([c] if predicate(c) else []) + c.find(predicate)]
    def text(self):
        return ' '.join(c.text() if isinstance(c, Node) else c for c in self.children).strip()
    def render(self):
        attrs = ''.join(' ' + k + ('' if v is None else '="' + esc(v) + '"') for k, v in self.attrs.items())
        inside = ''.join(c.render() if isinstance(c, Node) else html.escape(c, quote=False) for c in self.children)
        return '<' + self.tag + attrs + '>' + inside + ('' if self.tag in Parser.VOID else '</' + self.tag + '>')


class Parser(HTMLParser):
    VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self, text):
        super().__init__(); self.root = Node('root'); self.stack = [self.root]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs); self.stack[-1].children.append(node)
        if tag not in self.VOID: self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs))
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]; break
    def handle_data(self, data):
        self.stack[-1].children.append(data)


def cls(name):
    return lambda n: name in (n.attrs.get('class') or '').split()


posters = json.loads((SITE / 'data.js').read_text().removeprefix('window.ATLAS_POSTERS = ').strip().removesuffix(';'))
for p in posters:
    if not p.get('section'):
        p['section'] = 'Gestione dello Stress' if p['family'] == 'Risposte di difesa' else 'Mente, esperienza e relazione'
    if p['name'] == 'Stratagemma paradossale':
        p['section'] = 'Psicologia Strategica'
    section = p['section']
    if section == 'Mente, esperienza e relazione':
        if p['family'] == 'Emozioni': topic = 'Emozioni e processi affettivi'
        elif p['family'] in ['Coscienza','Memoria','Informazione']: topic = 'Percezione, coscienza e memoria'
        elif p['family'] in ['Identità','Motivazione'] or p['id'] in ['mental-social-representation','reality-of-reality','tall-poppy-syndrome']: topic = 'Identità, rappresentazioni e motivazione'
        else: topic = 'Relazioni, legami e dinamiche sociali'
    elif section == 'Gestione dello Stress':
        topic = 'Risposte di difesa' if p['family'] == 'Risposte di difesa' else 'Il tema' if p['id'] == 'stress-management' else 'Consapevolezza e regolazione' if p['id'] == 'mindfulness' else 'Strategie di coping'
    elif section == 'Persuasione':
        topic = 'Altri processi d’influenza' if p['id'] in ['persuasion-contrast','persuasion-mere-exposure'] else 'I principi di Cialdini'
    elif section == 'Psicologia Strategica': topic = 'Assiomi della comunicazione' if p['id'].startswith('communication-axiom-') else 'Modelli e strategie'
    elif section == 'Tratti di personalità (OCEAN)': topic = 'Il modello' if p['id'] == 'ocean-big-five' else 'I cinque tratti'
    elif section == 'L.I.M.I.T. Model': topic = 'Il modello' if p['id'] == 'limit-model' else 'Le cinque dimensioni'
    else: topic = p['family']
    p['topic'] = topic

THEMES = [
    dict(slug='limit-model', title='L.I.M.I.T. Model', short='L.I.M.I.T. Model', image='limit-model', description='Carico, identità, mentalizzazione, inibizione e tensione: cinque dimensioni compresenti nell’esperienza sotto pressione.'),
    dict(slug='bias-cognitivi', title='Bias cognitivi', short='Bias cognitivi', image='confirmation', description='Metafore animali per riconoscere come selezioniamo le informazioni, formuliamo giudizi e prendiamo decisioni.'),
    dict(slug='persuasione', title='Persuasione', short='Persuasione', image='persuasion-reciprocity', description='Principi e processi d’influenza: comprendere che cosa orienta una scelta e conservare spazio per valutarla.'),
    dict(slug='mente-esperienza-relazione', title='Mente, esperienza e relazione', short='Mente, esperienza e relazione', image='intersubjectivity', description='Emozioni, coscienza, memoria, identità, motivazione e legami: le connessioni che danno forma all’esperienza.'),
    dict(slug='gestione-dello-stress', title='Gestione dello Stress', short='Gestione dello Stress', image='stress-management', description='Riconoscere le risposte di difesa ed esplorare strategie di coping, consapevolezza e regolazione, mantenendole distinte.'),
    dict(slug='tratti-di-personalita', title='Tratti di personalità (OCEAN)', short='Tratti di personalità', image='ocean-big-five', description='Il modello dei Big Five e le cinque dimensioni con cui descrivere le differenze di personalità.'),
    dict(slug='psicologia-strategica', title='Psicologia Strategica', short='Psicologia Strategica', image='strategic-double-bind', description='Comunicazione, retroazione, paradosso e cambiamento: osservare le dinamiche che mantengono o trasformano una relazione.'),
]
by_id = {p['id']:p for p in posters}
for theme in THEMES:
    theme['count'] = sum(p['section'] == theme['title'] for p in posters)
    theme['thumb'] = '../' + by_id[theme['image']]['thumb']

articles = []
order = ['dal-what-if-al-what-is','lo-slogun-batte-largomento','la-zebra-il-leone-e-lerba','l-ombra-e-la-voce','archetipi-e-individuazione','la-soglia-della-radicalizzazione']
for slug in order:
    source = (SITE / 'articoli' / (slug+'.html')).read_text()
    tree = Parser(source).root
    title = tree.find(lambda n:n.tag == 'h1')[0].text()
    subtitle = tree.find(cls('article-subtitle'))[0].text()
    cover = tree.find(cls('article-poster'))[0].find(lambda n:n.tag == 'img')[0].attrs['src']
    duration = re.search(r'Circa [^<]+minuti? di lettura',source)
    articles.append(dict(slug=slug,title=title,subtitle=subtitle,cover=cover,url='articoli/'+slug+'.html',reading=duration.group(0) if duration else 'Articolo',concepts=sorted(set(re.findall(r'#bias=([a-z0-9-]+)',source)))))

author = Parser((SITE/'autore.html').read_text()).root
books = author.find(cls('author-books'))[0].render().replace('author-books','v2-books').replace('author-book','v2-book')
biography = author.find(cls('author-biography'))[0].render()
publications = author.find(cls('author-publications'))[0].render()
tables = author.find(cls('author-tables'))[0].render().replace('href="index.html#catalogue"','href="atlante.html"').replace('href="index.html#limit-model"','href="atlante.html?sezione=limit-model"').replace('src="assets/','src="../assets/').replace('href="assets/','href="../assets/')
universe = author.find(cls('author-library'))[0].find(cls('author-visual'))[0].render().replace('src="assets/','src="../assets/').replace('href="assets/','href="../assets/')
docs = json.loads((SITE/'author-documents.json').read_text())

ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M7 7h10v10"/></svg>'
SEARCH_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg>'


def header(active, base=''):
    nav = [('index.html','Home'),('atlante.html','Atlante'),('articoli.html','Articoli'),('saggi.html','Saggi'),('autore.html','Autore')]
    links = ''.join(f'<a href="{base+file}"'+(' aria-current="page"' if active==label else '')+f'>{label}</a>' for file,label in nav)
    return f'''<div class="v2-review"><span>ANTEPRIMA PRIVATA</span><a href="{base}../index.html">Confronta la versione attuale {ICON}</a></div><header class="v2-header"><a class="v2-brand" href="{base}index.html" aria-label="Limite e Relazione, Home"><span class="limite">LIMITE</span><span>&amp;</span><span class="relazione">RELAZIONE</span></a><nav class="v2-nav" aria-label="Navigazione principale">{links}</nav></header>'''


def footer(base=''):
    return f'<footer class="v2-footer"><a href="{base}autore.html">Limite &amp; Relazione · Tommaso Corona</a><span>Un progetto di psicologia, comunicazione e relazione.</span><a href="{base}../index.html">Versione attuale {ICON}</a></footer>'


def viewer():
    return '<dialog id="media-viewer" class="v2-viewer" aria-labelledby="media-title"><div class="v2-viewer-bar"><h2 id="media-title">Poster ingrandito</h2><button type="button" data-close-media aria-label="Chiudi poster ingrandito">×</button></div><img id="media-image" alt=""><div class="v2-viewer-end"><a id="media-original" href="#">Apri immagine originale '+ICON+'</a></div></dialog>'


def page(file,title,active,body,extra='',scripts=''):
    text=f'''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><meta name="theme-color" content="#263025"><meta name="description" content="Limite e Relazione di Tommaso Corona: atlante di poster, articoli, saggi e percorso dell’autore. Anteprima privata."><title>{esc(title)} · Limite &amp; Relazione</title><link rel="stylesheet" href="../styles.css">{extra}<link rel="stylesheet" href="preview.css"><script defer src="preview.js"></script>{scripts}</head><body class="v2"><a class="skip-link" href="#contenuto">Vai al contenuto</a>{header(active)}<main id="contenuto" class="v2-main">{body}</main>{footer()}{viewer()}</body></html>'''
    (OUT/file).write_text(text)


def article_card(article):
    return f'''<article class="v2-reading-card"><a href="{article['url']}" class="v2-reading-image" tabindex="-1" aria-hidden="true"><img src="{article['cover']}" alt="" loading="lazy"></a><div><p class="v2-kicker">ARTICOLO · {esc(article['reading'].replace('Circa ',''))}</p><h3><a href="{article['url']}">{esc(article['title'])}</a></h3><p>{esc(article['subtitle'])}</p><a class="v2-inline" href="{article['url']}">Leggi l’articolo {ICON}</a></div></article>'''


def pdf_card(document, compact=False):
    size=f"{document['size']/1000000:.1f}".replace('.',',')
    note='Il PDF comprende anche il contributo «Volantini sulla Libia».' if document['year']==2012 else 'L’operazione Aquila Omnia nel racconto dei Fucilieri dell’Aria.'
    return f'''<article class="v2-reading-card v2-pdf-card"><img class="v2-pdf-cover" src="../{document['cover']}" width="{document['width']}" height="{document['height']}" loading="lazy" alt="Prima pagina di {esc(document['title'])}"><div><p class="v2-kicker">{document['year']} · PDF · {document['pages']} PAGINE · {size} MB</p><h3>{esc(document['title'])}</h3><p>{note}</p><div class="v2-pdf-actions"><a class="v2-inline" href="../{document['original']}" target="_blank" rel="noopener noreferrer" aria-label="Apri PDF: {esc(document['title'])}, nuova scheda">Apri PDF {ICON}</a><a class="v2-inline" href="../{document['original']}?download=1" download="{document['filename']}" aria-label="Scarica PDF: {esc(document['title'])}">Scarica PDF ↓</a></div></div></article>'''


theme_cards=''.join(f'''<a class="v2-theme-card{' v2-theme-first' if i==0 else ''}" href="atlante.html?sezione={t['slug']}"><img src="{t['thumb']}" width="96" height="171" loading="lazy" alt=""><div><p class="v2-kicker">{'IL PUNTO DI PARTENZA · ' if i==0 else ''}{t['count']} POSTER</p><h3>{esc(t['short'])}</h3><p>{esc(t['description'])}</p><span class="v2-inline">Esplora {ICON}</span></div></a>''' for i,t in enumerate(THEMES))
hero_posters=''.join(f'<a href="atlante.html#bias={id}" aria-label="Apri {esc(by_id[id]["name"])}"><img src="../{by_id[id]["thumb"]}" width="420" height="747" fetchpriority="high" alt="{esc(by_id[id]["english"])}"></a>' for id in ['limit-load','limit-mentalizing','limit-tension'])
home=f'''<section class="v2-home-hero"><div><p class="v2-kicker"><span class="v2-dot"></span> PSICOLOGIA, COMUNICAZIONE, ESPERIENZA</p><h1><span class="limite">Limite</span><br>&amp; <span class="relazione">Relazione</span><span class="v2-red">.</span></h1><div class="v2-home-signature"><a class="v2-home-logo" href="autore.html" aria-label="Tommaso Corona, scopri l’autore"><img src="../assets/autore/logo-display.webp" width="512" height="512" alt="Logo di Tommaso Corona: un profilo umano e un elmo in un cerchio dorato." decoding="async"></a><p class="v2-byline">Un progetto di <a href="autore.html" rel="author">Tommaso Corona</a></p></div><p class="v2-lead">Esplorare come giudichiamo, comunichiamo e rispondiamo alla pressione. Un atlante visivo che collega concetti, esperienza e relazioni.</p><form class="v2-home-search" action="atlante.html" role="search"><label class="sr-only" for="home-search">Cerca nei poster dell’Atlante</label>{SEARCH_ICON}<input id="home-search" type="search" name="q" placeholder="Cerca un tema, un animale, un autore…"><button type="submit">Cerca {ICON}</button></form><p class="v2-search-note">127 poster definitivi · 7 sezioni · <a href="atlante.html">Esplora tutta la raccolta</a></p></div><div class="v2-hero-posters">{hero_posters}<span>L.I.M.I.T. MODEL · CINQUE DIMENSIONI, UN SISTEMA</span></div></section><section class="v2-block" aria-labelledby="aree-title"><div class="v2-section-heading"><div><p class="v2-kicker">L’ATLANTE</p><h2 id="aree-title">Da dove vuoi iniziare?</h2></div><a class="v2-inline" href="atlante.html">Tutti i poster {ICON}</a></div><div class="v2-theme-grid">{theme_cards}</div></section><section class="v2-block"><div class="v2-section-heading"><div><p class="v2-kicker">ARTICOLI E RIFLESSIONI</p><h2>Oltre il poster<span class="v2-red">.</span></h2></div><a class="v2-inline" href="articoli.html">Tutte le letture {ICON}</a></div><div class="v2-reading-grid">{''.join(article_card(a) for a in articles[:2])}</div></section><section class="v2-author-strip"><img src="../assets/autore/ritratto-display.webp" width="900" height="972" loading="lazy" alt="Tommaso Corona"><div><p class="v2-kicker">IL PERCORSO, I SAGGI, IL PROGETTO</p><h2>Tommaso Corona</h2><p>Ufficiale dell’Aeronautica Militare, formatore e autore. Un percorso tra esperienza operativa, psicologia e comunicazione.</p><div class="v2-strip-links"><a class="v2-inline" href="autore.html">Conosci l’autore {ICON}</a><a class="v2-inline" href="saggi.html">Esplora i saggi {ICON}</a></div></div></section>'''
page('index.html','Home','Home',home)

atlas='''<section class="v2-page-heading"><p class="v2-kicker">127 POSTER · SETTE PERCORSI</p><h1>L’Atlante<span class="v2-red">.</span></h1><p>Concetti da esplorare, personaggi da riconoscere. Cerca nella raccolta o scegli una sezione.</p></section><section class="v2-atlas" aria-label="Ricerca e raccolta dei poster"><form id="atlas-search-form" class="v2-atlas-search" role="search"><label class="sr-only" for="atlas-search">Cerca nei poster</label>'''+SEARCH_ICON+'''<input id="atlas-search" type="search" placeholder="Tema, animale, autore o frase del poster…" autocomplete="off"><button type="button" id="clear-search" aria-label="Cancella la ricerca" hidden>×</button></form><div id="section-tabs" class="v2-section-tabs" role="group" aria-label="Sezioni dell’Atlante"></div><div id="theme-intro" class="v2-theme-intro" hidden></div><div class="v2-catalogue-tools"><label>Tema<select id="topic"><option value="all">Tutti i temi</option></select></label><label>Ordina<select id="atlas-sort"><option value="series">Ordine della serie</option><option value="name">Nome A → Z</option></select></label><details id="advanced-filters" class="v2-advanced"><summary>Altri filtri</summary><div class="v2-advanced-fields"><label>Animale<select id="atlas-animal"><option value="all">Tutti gli animali</option></select></label><label>Autore di riferimento<select id="atlas-author"><option value="all">Tutti gli autori</option></select></label><label id="status-label" hidden>Stato<select id="atlas-status"><option value="all">Tutti gli stati</option></select></label></div></details></div><div class="v2-results-bar"><p id="atlas-count" role="status" aria-live="polite"></p><button type="button" id="reset-filters" class="v2-text-button" hidden>Azzera i filtri</button></div><div id="active-filters" class="v2-active-filters" aria-label="Filtri applicati"></div><div id="atlas-grid" class="v2-poster-grid"></div><div id="atlas-empty" class="v2-empty" hidden><h2>Nessun poster con questi filtri.</h2><p>Prova un’altra parola o amplia la selezione.</p><button type="button" data-reset class="v2-button">Mostra tutta la raccolta</button></div><div class="v2-more"><button id="load-more" type="button" class="v2-button">Mostra altri poster</button><span id="shown-count"></span></div></section><dialog id="poster-detail" class="v2-detail" aria-labelledby="detail-heading"><button class="v2-detail-close" id="detail-close" type="button" aria-label="Chiudi scheda">×</button><div id="poster-detail-body"></div><div class="v2-detail-nav"><button id="detail-prev" type="button">← Precedente</button><span id="detail-position"></span><button id="detail-next" type="button">Successivo →</button></div></dialog><p id="atlas-toast" class="v2-toast" role="status" hidden></p><noscript><p>Attiva JavaScript per consultare e filtrare i poster.</p></noscript>'''
page('atlante.html','Atlante','Atlante',atlas,scripts='<script defer src="data.js"></script><script defer src="meta.js"></script><script defer src="atlas-engine.js"></script><script defer src="atlas.js"></script>')

reading_cards=''.join('<div class="v2-archive-item" data-kind="articolo" data-search="'+esc(a['title']+' '+a['subtitle'])+'">'+article_card(a)+'</div>' for a in articles)
pdf_cards=''.join('<div class="v2-archive-item" data-kind="pdf" data-search="'+esc(d['title']+' '+str(d['year']))+'">'+pdf_card(d)+'</div>' for d in docs)
archive=f'''<section class="v2-page-heading"><p class="v2-kicker">LETTURE E APPROFONDIMENTI</p><h1>Articoli <em>e riflessioni</em><span class="v2-red">.</span></h1><p>Sei articoli da leggere online e due contributi originali in PDF. Concetti, contesti ed esperienza nel percorso di Tommaso Corona.</p></section><div class="v2-archive-tools"><label for="reading-search">Cerca una lettura<input id="reading-search" type="search" placeholder="Titolo o argomento…"></label><label for="reading-type">Formato<select id="reading-type"><option value="all">Tutte le letture</option><option value="articolo">Articoli online</option><option value="pdf">Documenti PDF</option></select></label></div><p id="reading-count" class="v2-muted" role="status" aria-live="polite">8 letture</p><div class="v2-reading-grid v2-archive-grid">{reading_cards}</div><section id="documenti" class="v2-block v2-pdf-section"><p class="v2-kicker">DALL’ARCHIVIO DELL’AUTORE</p><h2>Articoli e contributi in PDF</h2><p class="v2-muted">Apri il documento in una nuova scheda oppure scarica il file originale.</p><div class="v2-reading-grid">{pdf_cards}</div></section><p id="reading-empty" class="v2-empty" hidden>Nessuna lettura corrisponde alla ricerca. Prova un’altra parola.</p>'''
page('articoli.html','Articoli e riflessioni','Articoli',archive)

book = json.loads((SITE/'book-previews.json').read_text())[0]
book_pdf = '../' + esc(book['original'])
book_contents = [
    (7, 'Indice degli argomenti'),
    (15, 'Prefazione del dott. Marco Strano'),
    (25, 'Presentazione del dott. Kristian Talamonti'),
    (29, 'Nota dell’Autore'),
    (33, 'Introduzione'),
]
book_links = ''.join(
    f'<li><a href="{book_pdf}#page={number}" target="_blank" rel="noopener noreferrer">'
    f'<span>{esc(label)}</span><span class="v2-book-preview-page">p. {number}</span></a></li>'
    for number, label in book_contents
)
book_preview = f'''<section class="v2-book-preview" id="{esc(book['id'])}" aria-labelledby="book-preview-title">
    <img class="v2-book-preview-cover" src="../{esc(book['cover'])}" width="{book['width']}" height="{book['height']}" alt="Prima di copertina di Psiche &amp; Thanatos" decoding="async">
    <div class="v2-book-preview-copy">
        <p class="v2-kicker">ANTEPRIMA DEL LIBRO · {book['pages']} PAGINE</p>
        <h2 id="book-preview-title">{esc(book['title'])}</h2>
        <p class="v2-book-preview-subtitle">Psicologia e comunicazione vs. coercizione negli interrogatori militari</p>
        <div class="v2-pdf-actions">
            <a class="v2-button" href="{book_pdf}" target="_blank" rel="noopener noreferrer">Leggi l’anteprima {ICON}</a>
            <a class="v2-inline" href="{book_pdf}?download=1" download="{esc(book['filename'])}">Scarica il PDF</a>
        </div>
        <nav class="v2-book-preview-contents" aria-labelledby="book-preview-contents-title">
            <h3 id="book-preview-contents-title">Nell’anteprima</h3>
            <ul>{book_links}</ul>
        </nav>
    </div>
</section>'''

saggi=f'''<section class="v2-page-heading"><p class="v2-kicker">UNIVERSO PSICHE &amp; THANATOS</p><h1>Quattro saggi,<br><em>percorsi connessi</em><span class="v2-red">.</span></h1><p>Comunicazione, influenza, identità e pensiero critico. Quattro prospettive sui meccanismi della mente e sul rapporto con l’altro.</p></section>{book_preview}<section class="v2-saggi-layout" aria-label="I saggi dell’autore"><div class="v2-universe">{universe}</div><div>{books}<p class="v2-muted v2-small">I collegamenti portano alle schede Amazon e si aprono in una nuova scheda.</p></div></section><div class="v2-next-reading"><h2>Dai saggi ai concetti</h2><p>Le schede dell’Atlante indicano il rimando a <em>Psiche &amp; Thanatos</em> per gli argomenti di cui l’autore ha confermato la trattazione.</p><a class="v2-button" href="atlante.html">Esplora l’Atlante {ICON}</a></div>'''
page('saggi.html','Saggi','Saggi',saggi,extra='<link rel="stylesheet" href="../author.css">')

author_body=f'''<section class="v2-author-top"><div><p class="v2-kicker">L’AUTORE / IL PROGETTO</p><h1>Tommaso<br>Corona<span class="v2-red">.</span></h1><p class="v2-lead">Ufficiale dell’Aeronautica Militare, formatore e autore. Un percorso tra esperienza operativa, psicologia e comunicazione.</p><div class="v2-signature"><img src="../assets/autore/logo-display.webp" width="512" height="512" alt="Logo di Tommaso Corona"><p>“Il significato nasce nella relazione.”</p></div><nav class="v2-local-nav" aria-label="Nella pagina Autore"><a href="#percorso">Il percorso ↓</a><a href="#pubblicazioni">Le pubblicazioni ↓</a><a href="#tavole">Le tavole ↓</a></nav></div><figure class="author-portrait"><img src="../assets/autore/ritratto-display.webp" width="900" height="972" alt="Ritratto di Tommaso Corona davanti a una libreria." fetchpriority="high"><figcaption>TOMMASO CORONA</figcaption></figure></section><section id="percorso" class="v2-block"><p class="v2-kicker">ESPERIENZA E FORMAZIONE</p><h2>Il percorso dell’autore</h2>{biography}</section><section id="pubblicazioni" class="v2-block"><p class="v2-kicker">SCRITTURA E APPROFONDIMENTO</p><h2>Le pubblicazioni</h2>{publications}<div class="v2-strip-links"><a class="v2-button" href="saggi.html">I quattro saggi {ICON}</a><a class="v2-inline" href="articoli.html">Articoli e riflessioni {ICON}</a></div><div class="v2-reading-grid v2-author-docs">{''.join(pdf_card(d) for d in docs)}</div></section><section id="tavole" class="v2-block"><p class="v2-kicker">LE MAPPE DEL PROGETTO</p><h2>Limite, relazione, pressione</h2><p class="v2-muted">Due tavole per orientarsi tra i concetti del progetto e le cinque dimensioni del L.I.M.I.T. Model.</p>{tables}</section>'''
page('autore.html','Tommaso Corona · Autore','Autore',author_body,extra='<link rel="stylesheet" href="../author.css">')

for article in articles:
    source=(SITE/'articoli'/(article['slug']+'.html')).read_text()
    source=source.replace('href="../styles.css"','href="../../styles.css"').replace('href="../article.css"','href="../../article.css"')
    source=source.replace('src="../assets/','src="../../assets/').replace('href="../assets/','href="../../assets/')
    source=source.replace('href="../index.html#bias=','href="../atlante.html#bias=').replace('href="../index.html#articoli-e-riflessioni"','href="../articoli.html"').replace('href="../index.html"','href="../atlante.html"')
    source=re.sub(r'(<nav class="article-breadcrumb".*?</nav>)',lambda m:m.group(0).replace('href="../atlante.html">Atlante</a>','href="../index.html">Home</a>'),source,flags=re.S)
    source=re.sub(r'<header class="masthead">.*?</header>',lambda _:header('Articoli','../'),source,flags=re.S)
    source=re.sub(r'<footer>.*?</footer>',lambda _:footer('../'),source,flags=re.S)
    source=source.replace('class="article-page"','class="article-page v2"').replace('</head>','<link rel="stylesheet" href="../preview.css"><script defer src="../preview.js"></script></head>')
    (OUT/'articoli'/(article['slug']+'.html')).write_text(source)

(OUT/'data.js').write_text('window.ATLAS_PREVIEW_POSTERS = '+json.dumps(posters,ensure_ascii=False,separators=(',',':'))+';\n')
(OUT/'meta.js').write_text('window.ATLAS_PREVIEW_META = '+json.dumps(dict(themes=THEMES,articles=articles),ensure_ascii=False,separators=(',',':'))+';\n')
counts=collections.Counter(p['section'] for p in posters)
assert len(posters)==127 and sum(counts.values())==127 and len(counts)==7
print('Preview generated:',dict(counts),'· 5 main pages · 6 unchanged articles · 2 original PDFs')
