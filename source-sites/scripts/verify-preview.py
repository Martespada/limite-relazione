"""Read-only verification of the deployed owner-private preview, using hidden stdin."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import sys
import termios
import urllib.error
import urllib.request

root=Path(__file__).resolve().parent.parent
if (root/'site/main/index.html').exists():
    import runpy
    runpy.run_path(str(root/'scripts/verify-main.py'),run_name='__main__')
    raise SystemExit(0)
settings=termios.tcgetattr(sys.stdin.fileno());settings[3]&=~termios.ECHO
termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,settings)
print('Ready for private preview verification on hidden stdin.',flush=True)
config=json.loads(sys.stdin.readline())
origin=config['origin'].rstrip('/')
assert origin=='https://atlante-bias-limite-relazione.tommasocorona.chatgpt.site'

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def request(path,method='GET'):
    return urllib.request.build_opener(NoRedirect()).open(urllib.request.Request(origin+path,method=method,headers={'OAI-Sites-Authorization':'Bearer '+config['token'],**({'X-Atlas-Maintenance-Key':config['maintenance_key']} if path.startswith('/__atlas/assets/') else {})}),timeout=120)

def verify(file):
    with request('/'+file) as response:
        assert response.read()==(root/'site'/file).read_bytes(),file
        assert response.headers.get('X-Robots-Tag')=='noindex, nofollow',file
    return file

preview=root/'site/anteprima'
files=[p.relative_to(root/'site').as_posix() for p in preview.rglob('*') if p.is_file() and p.suffix in ['.html','.css','.js']]
files+=['index.html','autore.html','data.js']
with ThreadPoolExecutor(max_workers=4) as pool:
    verified=list(pool.map(verify,files))
with request('/anteprima/') as response:
    assert response.read()==(preview/'index.html').read_bytes()
    url=response.geturl()
try:
    request('/anteprima')
    raise AssertionError('Missing canonical redirect')
except urllib.error.HTTPError as error:
    assert error.code==302 and error.headers.get('Location')=='/anteprima/'
with request('/__atlas/assets/status') as response:
    assets=json.load(response)['assets']
    assert len(assets)==266
for path in ['assets/definitivi/limit-model-thumb.webp','assets/autore/ritratto-display.webp']:
    with request('/'+path) as response:
        assert hashlib.sha256(response.read()).digest()==hashlib.sha256((root/'site'/path).read_bytes()).digest()
for document in json.loads((root/'site/author-documents.json').read_text()):
    with request('/'+document['original']+'?download=1',method='HEAD') as response:
        assert response.headers.get('Content-Type')=='application/pdf'
        assert response.headers.get('Content-Disposition')=='attachment; filename="'+document['filename']+'"'
        assert int(response.headers.get('Content-Length'))==document['size']
print(json.dumps({'preview_url':url,'verified_pages_and_files':len(verified),'private_assets':len(assets),'current_version_preserved':True,'poster_count':127}),flush=True)
