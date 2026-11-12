"""Publish the approved layout at canonical URLs, retaining the original content sources."""
from pathlib import Path
import re

root=Path(__file__).resolve().parent.parent
source=root/'site/anteprima'
output=root/'site/main'
output.mkdir(exist_ok=True)
(output/'articoli').mkdir(exist_ok=True)
names={'preview.css':'site.css','preview.js':'site.js','data.js':'atlas-data.js','meta.js':'catalogue-meta.js'}

legacy_routes=r'''
(() => {
  const hash=location.hash;
  const home=location.pathname==='/'||location.pathname==='/index.html';
  const author=location.pathname==='/autore.html';
  const themes=['limit-model','bias-cognitivi','persuasione','mente-esperienza-relazione','gestione-dello-stress','tratti-di-personalita','psicologia-strategica'];
  let destination;
  if(home){
    if(/^#bias=[a-z0-9-]+$/.test(hash))destination='atlante.html'+location.search+hash;
    else if(hash==='#catalogue')destination='atlante.html'+location.search+'#catalogue';
    else if(hash==='#articoli-e-riflessioni')destination='articoli.html';
    else {
      const theme=hash.startsWith('#tema=')?hash.slice(6):hash.slice(1);
      if(themes.includes(theme)){
        const params=new URLSearchParams(location.search);params.set('sezione',theme);
        destination='atlante.html?'+params.toString();
      }
    }
  }else if(author&&hash==='#saggi')destination='saggi.html';
  if(destination)location.replace(new URL(destination,location.href).href);
})();
'''

for file in source.rglob('*'):
    if not file.is_file() or file.suffix not in ['.html','.css','.js']:continue
    relative=file.relative_to(source)
    destination=output/(names.get(relative.name,relative.name) if len(relative.parts)==1 else relative)
    text=file.read_text()
    if file.suffix=='.html':
        text=re.sub(r'<div class="v2-review">.*?</div>','',text,flags=re.S)
        text=re.sub(r'<a\b[^>]*>Versione attuale\s*<svg.*?</svg></a>','',text,flags=re.S)
        text=text.replace(' Anteprima privata.','')
        if len(relative.parts)==1:
            text=text.replace('href="../styles.css"','href="styles.css"').replace('href="../author.css"','href="author.css"')
            text=text.replace('src="../assets/','src="assets/').replace('href="../assets/','href="assets/')
            for old,new in names.items():
                text=text.replace('src="'+old+'"','src="'+new+'"').replace('href="'+old+'"','href="'+new+'"')
        else:
            text=text.replace('href="../../styles.css"','href="../styles.css"').replace('href="../../article.css"','href="../article.css"')
            text=text.replace('src="../../assets/','src="../assets/').replace('href="../../assets/','href="../assets/')
            text=text.replace('href="../preview.css"','href="../site.css"').replace('src="../preview.js"','src="../site.js"')
        if relative.as_posix()=='autore.html':
            text=text.replace('<section class="v2-author-top">','<section class="v2-author-top" id="autore">')
            text=text.replace('<div class="v2-reading-grid v2-author-docs">','<div class="v2-reading-grid v2-author-docs" id="articoli-pdf">')
        assert 'ANTEPRIMA PRIVATA' not in text and 'Versione attuale' not in text
    elif relative.name=='preview.js':text=legacy_routes+text
    elif relative.name=='preview.css':text+='\n.v2 #articoli-pdf{scroll-margin-top:130px}\n'
    destination.write_text(text)
print('Approved layout generated at canonical URLs: Home, Atlas, Articles, Essays and Author; legacy links preserved.')
