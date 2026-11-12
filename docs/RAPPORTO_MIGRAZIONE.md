# Rapporto di migrazione — Limite & Relazione

Data: **12 novembre 2026**  
Destinazione richiesta: **https://github.com/Martespada/limite-relazione**  
Ramo predisposto localmente: **migration/github-pages-2026-11-12**

## Esito

È stata preparata e collaudata una copia statica completa del catalogo, indipendente da ChatGPT Sites per la consultazione e per i file pubblicati. Non è una ricostruzione visiva: pagine, testi, dati e immagini provengono dal codice originale recuperato.

**La pubblicazione su GitHub Pages non è stata attivata.** Non sono stati modificati il sito originale, il suo pubblico, i suoi file, i DNS di limite-relazione.it o le impostazioni di GitHub Pages.

Il repository GitHub di destinazione non è accessibile con un'identità autenticata in questa sessione. Non sono quindi verificati il contenuto del suo ramo principale, i permessi di scrittura o le impostazioni Pages. Nessun ramo remoto, commit remoto, pull request o modifica di main è stato creato. La copia è consegnata in un ramo Git locale esportabile, non dichiarato come pubblicato.

## Provenienza verificabile

- Pubblicazione di origine: https://atlante-bias-limite-relazione.tommasocorona.chatgpt.site
- Versione Sites: **73**, invariata al termine dei controlli.
- Commit originale: **5c889ca3efbb6fbd4e5826765b55884ca8b3e550**.
- **362 file tracciati** del progetto originale recuperati in source-sites/.
- Snapshot senza cronologia Git, credenziali di repository, token di accesso o valori dei segreti di manutenzione.
- Il manifesto docs/export-manifest.json registra percorso, dimensione e SHA-256 di ogni file originale e di ogni risorsa pubblicata.
- La copia in source-sites/ è immutata. La versione indipendente modificabile è in site/.

## Contenuti trasferiti

| Contenuto | Quantità | Conservazione |
| --- | ---: | --- |
| Poster attivi con scheda | 127 | Identificatori, immagini originali, anteprime, testi, esempi, slogan, riferimenti e note |
| Sezioni tematiche | 7 | Nomi, ordine e classificazione originali |
| Articoli da leggere online | 6 | Testo integrale, copertine, riferimenti e collegamenti ai concetti |
| Immagini della pagina Autore | 5 | Originale e anteprima di ritratto, logo e tre tavole |
| PDF | 3 | File originali, senza modifica dei byte |
| Risorse multimediali pubblicate complessive | 277 | PNG, WebP, JPEG e PDF confrontati con SHA-256 |
| Pagine principali | 5 | Home, Atlante, Articoli, Saggi e Autore |

Le sette sezioni restano: L.I.M.I.T. Model (6 poster), Bias cognitivi (56), Persuasione (9), Mente, esperienza e relazione (29), Gestione dello Stress (13), Tratti di personalità (OCEAN) (6), Psicologia Strategica (8).

I PDF sono:
- Cultural Awareness: Comunicazione e PSYOPS (18 pagine, 2012);
- Aquila Omnia: Diario di Bordo dei Fucilieri dell’Aria (4 pagine, 2021);
- Psiche & Thanatos: anteprima di 36 pagine, con copertina, indice, prefazione, presentazione, Nota dell’Autore e Introduzione.

Tutti i 127 poster attualmente presenti sono definitivi. Il filtro per lo stato rimane implementato: non sono state inventate voci in lavorazione. Sono preservate le rimozioni già richieste dall'autore e l'assenza dell'attribuzione a Psiche & Thanatos per Continuing bonds.

La pagina Autore conserva il ritratto, il logo, la biografia, gli elenchi delle tre lauree e dei tre master, i dieci corsi specialistici e le tavole. La sezione precedentemente rimossa «Come nasce Limite & Relazione» non è stata reintrodotta.

I file d'archivio ancora presenti nei sorgenti originali, ma non dichiarati dalla pubblicazione, restano nello snapshot source-sites/ e non sono pubblicati dalla build indipendente.

## Funzioni che restano operative

- Ricerca per titolo, animale, autore, slogan e testo, con normalizzazione degli accenti.
- Selezione delle sezioni e filtri per tema, animale, autore e stato.
- Combinazione dei filtri, azzeramento, ordinamento alfabetico e ordine della serie.
- Caricamento progressivo dei risultati e stato vuoto.
- Schede sintetiche con descrizione, esempio, slogan, riferimenti e concetti correlati.
- Navigazione al poster precedente e successivo, collegamenti diretti e cronologia del browser.
- Copia del collegamento della scheda.
- Ingrandimento dei poster, chiusura del visualizzatore e download dei PNG originali.
- Ricerca e filtro dell'archivio articoli/PDF.
- Navigazione fra articoli, poster, saggi e pagina Autore.
- Lettura e download dei PDF, con collegamenti alle pagine dell'anteprima.
- Impaginazione responsive originale.

La consultazione usa HTML, CSS, JavaScript, dati locali e file statici. Non richiede l'abbonamento ChatGPT Plus, un login ChatGPT, il Worker originale, l'archivio R2 originale o i suoi endpoint di manutenzione.

## Adattamenti circoscritti

1. Le immagini e i link generati dal catalogo usano percorsi relativi alla pagina, compatibili sia con /limite-relazione/ sia con un dominio alla radice.
2. Il riconoscimento dei vecchi link Home/Autore è adattato ai percorsi di progetto.
3. La conferma di copia del link non dichiara più che l'accesso resta privato.
4. I vecchi percorsi /anteprima/ sono conservati con pagine statiche di reindirizzamento che mantengono parametri e frammenti.
5. È aggiunta una pagina 404 essenziale.
6. È incluso .nojekyll. Non sono inclusi endpoint di scrittura, credenziali o configurazione Sites nella cartella pubblicabile.

Il contenuto di 22 dei 24 file applicativi principali coincide integralmente con la pubblicazione originale. Le sole due modifiche ai file applicativi sono in atlas.js e site.js, per i percorsi e la dicitura sul link. Tutte le immagini e tutti i PDF pubblicati conservano gli stessi byte.

## Verifiche eseguite

| Verifica | Esito |
| --- | --- |
| 2.752 controlli su sorgenti, hash, immagini decodificabili, riferimenti locali, ancore, assenza di API Sites e conservazione dei testi | Superati |
| 787 controlli sui dati, titoli, sezioni, ricerche, filtri, ordinamento, correlazioni e percorsi legacy | Superati |
| 301 confronti con la pubblicazione originale: 277 media e 24 file applicativi | Superati |
| 17 prove funzionali in Chrome, desktop e viewport mobile 390×844 | Superate |
| Build statica, integrità dei file e limite dimensionale | Superata |
| GitHub remoto, scrittura del ramo e pubblicazione Pages | Non eseguiti: connessione GitHub assente |

Il confronto con la pubblicazione originale usa:
- per 267 oggetti del catalogo e dei PDF, richieste HEAD con confronto di dimensione e intestazione SHA-256 servita dal Worker;
- per le 10 immagini incorporate nel Worker, download e confronto completo dello SHA-256;
- per i 24 file applicativi principali, download e confronto integrale del testo.

Il confronto non ha scritto alcun file sul sito di origine. Tutti i file recuperati dal repository originale sono stati inoltre verificati localmente tramite SHA-256.

Le prove nel browser comprendono Home e ricerca «coccodrillo», scheda Truth bias, originale e download PNG, sei poster del L.I.M.I.T. Model e navigazione precedente/successivo, ricerca senza risultati, pagina Autore ed elenchi, download del PDF di 36 pagine, ricerca e apertura dell'articolo sulla zebra, ricerca «bradipo» e apertura di Normalcy bias su mobile, filtri combinati Coccodrillo + Timothy R. Levine e assenza di overflow orizzontale. Test responsive nel browser, non su dispositivo fisico.

## Dimensioni e compatibilità con Pages

La cartella pubblicabile contiene **314 file e 760.779.102 byte**: circa **761 MB decimali** o **726 MiB**. Comprende gli originali, senza ricompressione o ridimensionamento aggiuntivi.

È inferiore al limite pubblicato di **1 GB** per un sito GitHub Pages. La crescita del catalogo dovrà essere verificata prima di futuri aggiornamenti; la build si ferma se supera 1.000.000.000 byte. Il repository contiene anche lo snapshot originale, ma Git conserva una sola copia degli oggetti identici nei due percorsi.

Il modello di workflow è docs/pages-workflow.yml.example, deliberatamente fuori da .github/workflows/. Non può avviarsi o pubblicare. Prevede un successivo avvio manuale, non la pubblicazione a ogni push. Non è stato creato un file CNAME.

## Limiti e differenze da conoscere

- Il passaggio a Pages non è stato provato su una pubblicazione reale: è stato provato su un server statico locale ai percorsi radice e /limite-relazione/. La verifica del sito GitHub definitivo avverrà soltanto dopo l'autorizzazione alla pubblicazione.
- I collegamenti bibliografici esterni e Amazon sono preservati; non è stata verificata singolarmente la disponibilità di ogni sito esterno.
- I reindirizzamenti legacy diventano reindirizzamenti HTML/JavaScript, non risposte HTTP 302.
- Il download PDF usa l'attributo download del collegamento. Un server statico non replica l'intestazione Content-Disposition del Worker; l'apertura diretta del PDF dipende dal browser.
- Non vengono trasferiti i servizi amministrativi di Sites, l'autenticazione o il caricamento via endpoint privato. Gli aggiornamenti della copia indipendente avvengono sui file e, in seguito, tramite Git.
- I metadati noindex originali sono mantenuti: l'indicizzazione nei motori di ricerca andrà decisa separatamente.
- Non è possibile dedurre se il repository remoto sia vuoto, privato, già configurato per Pages o scrivibile senza collegare GitHub. Non è stato tentato un caricamento anonimo o una ricostruzione del repository.
- GitHub Pages è disponibile gratuitamente da repository pubblici; l'uso da repository privati dipende dal piano GitHub. Non è richiesto ChatGPT Plus per servire il sito già esportato.

## Passaggi futuri, non eseguiti

1. Abilitare GitHub e autorizzare l'accesso a Martespada/limite-relazione.
2. Verificare il ramo principale e le impostazioni esistenti, creare un ramo separato e caricare il progetto senza sovrascritture.
3. Revisionare le differenze ed eventualmente aprire una pull request.
4. Solo dopo una nuova autorizzazione, attivare GitHub Pages e provare il sito pubblicato.
5. In una fase successiva, verificare la proprietà del dominio, configurare www.limite-relazione.it e abilitare HTTPS.

Non modificare ora i DNS: l'attivazione del dominio è rinviata.

## Documentazione ufficiale consultata

- [Limiti di GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- [Workflow personalizzati per Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [HTTPS per Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https)
- [Dominio personalizzato](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
