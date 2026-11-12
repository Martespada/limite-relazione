"""Read-only verification of the promoted owner-private Site."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import sys
import termios
import urllib.error
import urllib.request

root=Path(__file__).resolve().parent.parent
settings=termios.tcgetattr(sys.stdin.fileno());settings[3]&=~termios.ECHO
termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,settings)
print('Ready for private main Site verification on hidden stdin.',flush=True)
config=json.loads(sys.stdin.readline());origin=config['origin'].rstrip('/')
assert origin=='https://atlante-bias-limite-relazione.tommasocorona.chatgpt.site'

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def request(path,method='GET'):
    return urllib.request.build_opener(NoRedirect()).open(urllib.request.Request(origin+path,method=method,headers={'OAI-Sites-Authorization':'Bearer '+config['token'],**({'X-Atlas-Maintenance-Key':config['maintenance_key']} if path.startswith('/__atlas/assets/') else {})}),timeout=120)

main=root/'site/main'
files=[p.relative_to(main).as_posix() for p in main.rglob('*') if p.is_file() and p.suffix in ['.html','.css','.js']]
def verify(file):
    with request('/'+file) as response:
        assert response.read()==(main/file).read_bytes(),file
        assert response.headers.get('X-Robots-Tag')=='noindex, nofollow'
    return file
with ThreadPoolExecutor(max_workers=4) as pool:verified=list(pool.map(verify,files))
with request('/') as response:
    body=response.read().decode();assert body==(main/'index.html').read_text()
    assert 'v2-home-logo' in body and 'ANTEPRIMA PRIVATA' not in body and 'Versione attuale' not in body
    url=response.geturl()
redirects={'/anteprima':'/','/anteprima/':'/','/anteprima/index.html':'/','/anteprima/atlante.html?q=bradipo':'/atlante.html?q=bradipo','/anteprima/autore.html':'/autore.html','/anteprima/saggi.html':'/saggi.html','/anteprima/articoli.html':'/articoli.html','/anteprima/articoli/dal-what-if-al-what-is.html':'/articoli/dal-what-if-al-what-is.html'}
for old,new in redirects.items():
    try:
        request(old,'HEAD');raise AssertionError('Missing redirect: '+old)
    except urllib.error.HTTPError as error:
        assert error.code==302 and error.headers.get('Location')==new,(old,error.code,error.headers.get('Location'))
        assert error.headers.get('Cache-Control')=='no-store'
books=json.loads((root/'site/book-previews.json').read_text())
with request('/__atlas/assets/status') as response:
    assets=json.load(response)['assets'];assert len(assets)==266+len(books)
for path in ['assets/autore/logo-display.webp','assets/definitivi/limit-model-thumb.webp',*(b['cover'] for b in books)]:
    with request('/'+path) as response:assert hashlib.sha256(response.read()).digest()==hashlib.sha256((root/'site'/path).read_bytes()).digest()
for document in json.loads((root/'site/author-documents.json').read_text())+books:
    with request('/'+document['original']+'?download=1','HEAD') as response:
        assert response.headers.get('Content-Type')=='application/pdf'
        assert response.headers.get('Content-Disposition')=='attachment; filename="'+document['filename']+'"'
        assert int(response.headers.get('Content-Length'))==document['size']
text=(main/'atlas-data.js').read_text();posters=json.loads(text.removeprefix('window.ATLAS_PREVIEW_POSTERS = ').strip().removesuffix(';'))
assert len(posters)==127 and all(p.get('section') for p in posters)
print(json.dumps({'main_url':url,'verified_files':len(verified),'verified_redirects':len(redirects),'private_assets':len(assets),'poster_count':len(posters),'main_format_active':True}),flush=True)
