# Limite & Relazione — copia statica per GitHub Pages

Copia indipendente del catalogo di Tommaso Corona, preparata il 12 novembre 2026.
**Pubblicazione GitHub Pages autorizzata il 12 novembre 2026; DNS e sito originale invariati.**

Configurazione operativa e verifiche aggiornate: [docs/PUBBLICAZIONE_PAGES.md](docs/PUBBLICAZIONE_PAGES.md). Le sezioni sullo stato iniziale qui sotto descrivono la consegna del bundle, prima dell’attivazione.

- **site/**: sito statico modificabile, con immagini e PDF originali.
- **source-sites/**: copia integrale dei 362 file tracciati dal progetto originale, senza cronologia Git e credenziali.
- **tools/**: verifiche, build ed audit della pubblicazione originale.
- **docs/**: provenienza, checksum, rapporto e risultati del collaudo.
- **dist/**: output locale della build, escluso da Git.

Il sito può essere pubblicato sia sotto /limite-relazione/ sia alla radice di un dominio.
Non contiene chiamate API a ChatGPT Sites, R2 remoto, funzioni server o procedure di login.
Le citazioni e i collegamenti esterni ai saggi rimangono gli originali.

## Verifica e build

Richiede Python 3.12 o successivo, Node.js 22 o successivo e Pillow per verificare le immagini.

    python -m pip install -r requirements.txt
    python tools/check-content.py
    node tools/check-catalogue.cjs
    python tools/build-static.py

La build genera solo file locali. Non apre GitHub Pages e non modifica il sito originale.
Per una consultazione locale, servire dist/ con un server statico (non aprire i file con file://).

## Aggiornamenti futuri

Modificare site/, non dist/. La copia in source-sites/ è una testimonianza immutabile dell'esportazione e non è necessaria all'esecuzione del sito indipendente.
I dati e i riferimenti dei poster sono in site/atlas-data.js; le categorie e gli articoli in site/catalogue-meta.js.
Le nuove immagini devono essere locali a site/assets/. Aggiornare i controlli e i manifesti se cambia il patrimonio documentale verificato.

## Stato di GitHub

Destinazione richiesta: https://github.com/Martespada/limite-relazione

Al momento dell'esportazione non era disponibile un'autorizzazione GitHub, e gh non aveva un account autenticato.
Il contenuto del repository remoto, i permessi di scrittura e le impostazioni Pages **non sono stati verificati**.
Nessun push, modifica di main, pull request, impostazione Pages o DNS è stato eseguito.
È predisposto soltanto un ramo locale migration/github-pages-2026-11-12.

## Attivazione rinviata

Il modello docs/pages-workflow.yml.example è volontariamente fuori da .github/workflows/: non può eseguire o pubblicare nulla.
Prima di attivarlo:
1. collegare GitHub e verificare contenuto, permessi e impostazioni del repository;
2. importare le modifiche in un ramo separato e rivedere il confronto con main;
3. solo dopo l'approvazione spostare il workflow nella posizione operativa e configurare Pages;
4. verificare il dominio e configurare www.limite-relazione.it e HTTPS in una fase successiva.

Nessun file CNAME è stato creato. I DNS di limite-relazione.it non sono stati toccati.
Il modello richiede avvio manuale, non pubblica a ogni push.

Vedere [il rapporto completo](docs/RAPPORTO_MIGRAZIONE.md).
