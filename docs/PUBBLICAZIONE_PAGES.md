# Pubblicazione GitHub Pages

Attivazione autorizzata dall’autore il 12 novembre 2026.

- URL: https://martespada.github.io/limite-relazione/
- Ramo: `migration/github-pages-2026-11-12`; `main` non modificato.
- Workflow: `.github/workflows/pages.yml`, avvio sui push del ramo che modificano sito, strumenti, dipendenze o workflow.
- Artefatto pubblico: esclusivamente `dist/`, generato da `site/`.
- Nessun dominio personalizzato, CNAME o cambiamento DNS; sito ChatGPT Sites invariato.

## Verifiche locali prima dell’attivazione

- Build: 314 file, 760.779.102 byte, esattamente la misura della preparazione originale.
- Catalogo: 787 controlli superati, 127 poster, 7 sezioni, 6 articoli.
- Contenuti: 2.747 controlli superati, 360 sorgenti e 277 media verificati, 23 pagine HTML.
- Il bundle non include due output generati del vecchio server elencati nel manifesto: `source-sites/dist/.openai/hosting.json` e `source-sites/dist/server/index.js`. Non sono necessari alla build statica; il controllo li riporta esplicitamente come assenti. Nessun sorgente o media è stato ricostruito.
- I 7.623 byte in più osservati nella copia Windows sono coerenti con la conversione delle terminazioni di riga al checkout. Il checkout Linux produce esattamente la misura originale.

I rapporti precedenti restano documenti storici della preparazione. I log GitHub Actions documentano l’esito effettivo della pubblicazione.
