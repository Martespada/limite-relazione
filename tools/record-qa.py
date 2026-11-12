from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
checks=[
 'Home preserved under /limite-relazione/, including logo and first LIMIT section',
 'Home search for coccodrillo navigates to the catalogue and returns Truth bias',
 'Truth bias sheet displays slogan, explanation, example and bibliography',
 'Full-resolution Truth bias PNG loads from /limite-relazione/assets/',
 'PNG download completes without contacting Sites',
 'LIMIT section returns 6 posters',
 'Next and previous poster navigation changes the detail position',
 'No-result search displays the empty-state message',
 'Author page preserves 3 degrees, 3 masters and 10 specialist courses',
 'The 36-page book preview PDF downloads from the static site',
 'Article search for zebra returns the matching article',
 'Article text and local cover image load under the project prefix',
 'Mobile 390 x 844 iframe: bradipo search and Normalcy bias sheet',
 'Mobile full PNG opens from the project prefix',
 'Combined Coccodrillo and Timothy R. Levine filters return one poster',
 'Mobile document width has no horizontal overflow',
 'Root-domain legacy index.html#bias=truth-bias routes to the matching sheet',
]
(ROOT/'docs/browser-qa.json').write_text(json.dumps({'date':'2026-11-12','browser':'Chrome, managed browser','desktop':True,'mobile_viewport':'390x844 iframe, not a physical device','prefixes':['/','/limite-relazione/'],'checks':checks,'result':'PASS','publication_performed':False},ensure_ascii=False,indent=2)+'\n')
