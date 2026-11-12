# Importare il progetto completo da un bundle Git

Il file limite-relazione-github-pages.bundle contiene il ramo locale completo, con sito statico, immagini, PDF, snapshot originale, verifiche e rapporto. Non contiene credenziali.

Per recuperarlo in una nuova cartella:

    git clone --branch migration/github-pages-2026-11-12 limite-relazione-github-pages.bundle limite-relazione-esportato
    cd limite-relazione-esportato

Per verificare e creare il sito pubblicabile:

    python -m pip install -r requirements.txt
    python tools/check-content.py
    node tools/check-catalogue.cjs
    python tools/build-static.py

Il sito completo è generato in dist/. Può essere servito da un normale server statico. La generazione non pubblica nulla.

## Collegamento al repository di destinazione

Non eseguire un push sul ramo main. Prima verificare e scaricare il repository remoto, compresi contenuto e impostazioni Pages.

Il ramo nel bundle ha una cronologia indipendente. Il percorso consigliato è clonare Martespada/limite-relazione con un'identità autorizzata, creare un ramo separato dal suo ramo principale e importare i file del progetto, preservando gli eventuali file già presenti. In caso di conflitti non sovrascrivere il remoto.

Non attivare Pages o il workflow e non aggiungere CNAME o modificare i DNS finché non è stata approvata la pubblicazione.
