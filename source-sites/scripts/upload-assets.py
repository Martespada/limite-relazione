from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib
import json
import sys
import termios
import time
import urllib.error
import urllib.parse
import urllib.request

root=Path(__file__).resolve().parent.parent
settings=termios.tcgetattr(sys.stdin.fileno())
settings[3] &= ~termios.ECHO
termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,settings)
print('Ready for private Site service configuration on hidden stdin.',flush=True)
config=json.loads(sys.stdin.readline())
origin=config['origin'].rstrip('/')
assert origin=='https://atlante-bias-limite-relazione.tommasocorona.chatgpt.site'
token=config['token']
verify_ids=config.get('verify_ids',[])
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        return None
def request(path,method='GET',body=None,extra=None):
    headers={'OAI-Sites-Authorization':'Bearer '+token,'X-Atlas-Maintenance-Key':config['maintenance_key'],**(extra or {})}
    req=urllib.request.Request(origin+path,data=body,method=method,headers=headers)
    return urllib.request.build_opener(NoRedirect()).open(req,timeout=120)
text=(root/'site/data.js').read_text()
posters=json.loads(text.removeprefix('window.ATLAS_POSTERS = ').rstrip().removesuffix(';'))
author_media=json.loads((root/'site/author-media.json').read_text())
documents=json.loads((root/'site/author-documents.json').read_text()) + json.loads((root/'site/book-previews.json').read_text())
records=posters+author_media+documents
files={p['thumb'] for p in posters+author_media}|{p['original'] for p in records}
digests={key:hashlib.sha256((root/'site'/key).read_bytes()).hexdigest() for key in files}
with request('/__atlas/assets/status') as response:
    existing=json.load(response)['assets']
ready={key for key in files if existing.get(key)==digests[key]}
print(f'Resuming: {len(ready)}/{len(files)} files already match.',flush=True)
def upload(key):
    body=(root/'site'/key).read_bytes()
    sha=hashlib.sha256(body).hexdigest()
    for attempt in range(3):
        try:
            with request('/__atlas/assets/'+urllib.parse.quote(key,safe='/'),method='PUT',body=body,extra={'X-Content-Sha256':sha,'Content-Type':'application/octet-stream'}) as response:
                result=json.load(response)
                assert result.get('stored') and result['sha256']==sha and result['size']==len(body)
                return key,sha
        except urllib.error.HTTPError as error:
            if error.code not in [429,502,503,504] or attempt==2:
                detail=error.read(300).decode(errors='replace')
                raise RuntimeError(f'Upload failed ({error.code}) for {key}: {detail}') from None
            time.sleep(2*(attempt+1))
        except urllib.error.URLError:
            if attempt==2:
                raise
            time.sleep(2*(attempt+1))

completed=len(ready)
pending=files-ready
for group in [sorted(k for k in pending if k.endswith('.webp')),sorted((k for k in pending if k.endswith('.png')),key=lambda k:(not any(id in k for id in verify_ids),k)),sorted(k for k in pending if k.endswith('.pdf'))]:
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(upload,key) for key in group]
        for future in as_completed(futures):
            key,sha=future.result()
            digests[key]=sha
            completed+=1
            if completed%15==0 or completed==len(files):
                print(f'Uploaded and verified {completed}/{len(files)} private media files.',flush=True)

with request('/__atlas/assets/status') as response:
    saved=json.load(response)['assets']
assert all(saved.get(key)==digests[key] for key in files)
for id in verify_ids:
    p=next(p for p in records if p['id']==id)
    with request('/'+p['original']) as response:
        assert hashlib.sha256(response.read()).hexdigest()==digests[p['original']]
        if p in documents:
            assert response.headers.get('Content-Type')=='application/pdf'
            assert response.headers.get('Content-Disposition')=='inline; filename="'+p['filename']+'"'
    if p in documents:
        with request('/'+p['original']+'?download=1',method='HEAD') as response:
            assert response.headers.get('Content-Type')=='application/pdf'
            assert response.headers.get('Content-Disposition')=='attachment; filename="'+p['filename']+'"'
            assert int(response.headers.get('Content-Length'))==p['size']
for document in documents:
    with request('/'+document['cover']) as response:
        assert response.headers.get('Content-Type')=='image/webp'
        assert response.read()==(root/'site'/document['cover']).read_bytes()
with request('/data.js') as response:
    data=response.read().decode()
    live=json.loads(data.removeprefix('window.ATLAS_POSTERS = ').rstrip().removesuffix(';'))
    assert len(live)==len(posters)
    assert live==posters
for page in ['autore.html','author.css','author.js']:
    with request('/'+page) as response:
        canonical=root/'site/main'/page
        assert response.read()==(canonical if canonical.exists() else root/'site'/page).read_bytes()
with request('/') as response:
    html=response.read().decode()
    assert 'class="v2-home-logo"' in html and 'href="autore.html"' in html
print(json.dumps({'verified_media_files':len(files),'live_posters':len(live),'originals_verified':verify_ids,'new_originals_identical':bool(verify_ids)}),flush=True)
