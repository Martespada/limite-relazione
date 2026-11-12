from pathlib import Path
import base64
import json
import re

root=Path(__file__).resolve().parent.parent
site=root/'site'
text= (site/'data.js').read_text()
posters=json.loads(text.removeprefix('window.ATLAS_POSTERS = ').rstrip().removesuffix(';'))
author_media=json.loads((site/'author-media.json').read_text())
documents=json.loads((site/'author-documents.json').read_text()) + json.loads((site/'book-previews.json').read_text())
assets={}
for name,kind in [('index.html','text/html'),('styles.css','text/css'),('article.css','text/css'),('articoli/la-zebra-il-leone-e-lerba.html','text/html'),('articoli/l-ombra-e-la-voce.html','text/html'),('articoli/archetipi-e-individuazione.html','text/html'),('articoli/la-soglia-della-radicalizzazione.html','text/html'),('articoli/lo-slogun-batte-largomento.html','text/html'),('articoli/dal-what-if-al-what-is.html','text/html'),('data.js','text/javascript'),('engine.js','text/javascript'),('app.js','text/javascript')]:
    assets[name]={'body':(site/name).read_text(),'type':kind+'; charset=utf-8'}
for name,kind in [('autore.html','text/html'),('author.css','text/css'),('author.js','text/javascript')]:
    assets[name]={'body':(site/name).read_text(),'type':kind+'; charset=utf-8'}
for file in sorted((site/'anteprima').rglob('*')):
    if file.is_file() and file.suffix in ['.html','.css','.js']:
        kind={'.html':'text/html','.css':'text/css','.js':'text/javascript'}[file.suffix]
        assets[file.relative_to(site).as_posix()]={'body':file.read_text(),'type':kind+'; charset=utf-8'}
for file in sorted((site/'main').rglob('*')):
    if file.is_file() and file.suffix in ['.html','.css','.js']:
        kind={'.html':'text/html','.css':'text/css','.js':'text/javascript'}[file.suffix]
        assets[file.relative_to(site/'main').as_posix()]={'body':file.read_text(),'type':kind+'; charset=utf-8'}
binary_assets={
    'assets/articoli/la-zebra-cover.jpeg':{
        'body':base64.b64encode((site/'assets/articoli/la-zebra-cover.jpeg').read_bytes()).decode(),
        'type':'image/jpeg',
    },
    'assets/articoli/l-ombra-e-la-voce-cover.png':{
        'body':base64.b64encode((site/'assets/articoli/l-ombra-e-la-voce-cover.png').read_bytes()).decode(),
        'type':'image/png',
    },
    'assets/articoli/archetipi-cover.png':{
        'body':base64.b64encode((site/'assets/articoli/archetipi-cover.png').read_bytes()).decode(),
        'type':'image/png',
    },
    'assets/articoli/archetipi-percorso.png':{
        'body':base64.b64encode((site/'assets/articoli/archetipi-percorso.png').read_bytes()).decode(),
        'type':'image/png',
    },
    'assets/articoli/la-soglia-cover.jpg':{
        'body':base64.b64encode((site/'assets/articoli/la-soglia-cover.jpg').read_bytes()).decode(),
        'type':'image/jpeg',
    },
    'assets/articoli/slogun-cover.webp':{
        'body':base64.b64encode((site/'assets/articoli/slogun-cover.webp').read_bytes()).decode(),
        'type':'image/webp',
    },
    'assets/articoli/dal-what-if-al-what-is-cover.jpg':{
        'body':base64.b64encode((site/'assets/articoli/dal-what-if-al-what-is-cover.jpg').read_bytes()).decode(),
        'type':'image/jpeg',
    },
}
for document in documents:
    binary_assets[document['cover']]={'body':base64.b64encode((site/document['cover']).read_bytes()).decode(),'type':'image/webp'}
document_assets={document['original']:{'title':document['title'],'filename':document['filename']} for document in documents}
media={}
for p in posters:
    for key in set([p['image'],p['original'],p['thumb']]):
        media[key]={'thumb':p['thumb'],'animal':p['animal']}
for item in author_media:
    for key in [item['original'],item['thumb']]:
        media[key]={'thumb':item['thumb'],'animal':item['title']}
previews={}
for item in author_media:
    previews[item['thumb']]=base64.b64encode((site/item['thumb']).read_bytes()).decode()
featured={'strategic-double-bind','ocean-big-five','persuasion-reciprocity','limit-model','limit-mentalizing','limit-tension','intersubjectivity','stress-management','confirmation','truth-bias','normalcy-bias','status-quo','anchoring-mussel','negativity','intrinsic-motivation','extrinsic-motivation'}
for p in posters:
    if p['id'] in featured:
        previews[p['thumb']]=base64.b64encode((site/p['thumb']).read_bytes()).decode()
embedded='\n'.join('const '+name+'='+json.dumps(value,ensure_ascii=False,separators=(',',':'))+';' for name,value in [('TEXT_ASSETS',assets),('BINARY_ASSETS',binary_assets),('PREVIEWS',previews),('MEDIA',media),('DOCUMENTS',document_assets)])
worker=root/'worker/index.js'
source,count=re.subn(r'// EMBED_START.*?// EMBED_END',lambda _: '// EMBED_START\n'+embedded+'\n// EMBED_END',worker.read_text(),flags=re.S)
assert count==1
worker.write_text(source)
print(f'Embedded {len(assets)} application files, {len(binary_assets)} embedded images and {len(previews)} previews; {len(media)} private media objects and {len(documents)} PDF documents declared.')
