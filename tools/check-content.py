"""Check exact source preservation, media hashes and internal static links."""
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, urljoin
from PIL import Image
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent.parent
site=ROOT/'site'
export=json.loads((ROOT/'docs/export-manifest.json').read_text())
checks=0
def check(condition,message):
    global checks
    assert condition,message
    checks+=1
for record in export['source_files']:
    path=ROOT/'source-sites'/record['path']
    check(path.is_file() and path.stat().st_size==record['size'],'Source file missing or size changed: '+record['path'])
    check(hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'],'Source checksum: '+record['path'])
for record in export['media_files']:
    path=site/record['path']
    check(path.is_file() and path.stat().st_size==record['size'],'Media missing: '+record['path'])
    check(hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'],'Media checksum: '+record['path'])
    if record['mime'].startswith('image/'):
        with Image.open(path) as img:
            img.verify()
        checks+=1
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.refs=[];self.ids=[];self.tags=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);self.tags.append(tag)
        if attrs.get('id'):self.ids.append(attrs['id'])
        for key in ('href','src','poster'):
            if attrs.get(key):self.refs.append((tag,key,unescape(attrs[key])))
pages={p.relative_to(site).as_posix():Page(p.read_text()) for p in site.rglob('*.html')}
for name,page in pages.items():
    check(len(page.ids)==len(set(page.ids)),'Duplicate HTML IDs: '+name)
    for tag,attr,ref in page.refs:
        url=urlsplit(ref)
        if url.scheme or url.netloc:
            check('chatgpt.site' not in url.netloc,'Sites dependency: '+name+' '+ref)
            continue
        resolved=urlsplit(urljoin('https://example.org/limite-relazione/'+name,ref))
        check(resolved.path.startswith('/limite-relazione/'),'Link escapes project path: '+name+' '+ref)
        relative=unquote(resolved.path.removeprefix('/limite-relazione/'))
        if relative.endswith('/'):relative+='index.html'
        check((site/relative).is_file(),'Broken local reference: '+name+' '+ref)
        if resolved.fragment and relative in pages and not relative.startswith('anteprima/'):
            fragment=unquote(resolved.fragment)
            # Catalogue detail/legacy anchors are resolved by client-side routing.
            if not fragment.startswith(('bias=','tema=')) and relative not in ('index.html','autore.html'):
                check(fragment in pages[relative].ids,'Missing anchor: '+name+' '+ref)
for p in site.rglob('*'):
    if not p.is_file() or p.suffix not in ('.html','.js','.css'):continue
    text=p.read_text()
    check(not re.search(r'https?://[^\s\"\x27<>]*chatgpt(?:\.site|\.com)',text),'Live platform dependency: '+str(p))
    check(not re.search(r'\b(?:fetch|XMLHttpRequest)\s*\(',text),'Unexpected API call: '+str(p))
    check('OAI-Sites-Authorization' not in text and 'ATLAS_MEDIA_MAINTENANCE_KEY' not in text,'Maintenance code in static site')
# Exact data and article copy: changes are restricted to path/privacy wording in two scripts.
worker=(ROOT/'source-sites/worker/index.js').read_text()
texts=json.loads(re.search(r'^const TEXT_ASSETS=(.*);$',worker,re.M).group(1))
for name,asset in texts.items():
    if name.startswith('anteprima/') or name in ('atlas.js','site.js'):continue
    check((site/name).read_text()==asset['body'],'Unexpected text change: '+name)
check('L’accesso resta privato' not in (site/'atlas.js').read_text(),'Obsolete private-site notice')
check('../${p.thumb}' not in (site/'atlas.js').read_text(),'Parent-relative dynamic image path')
check(not (site/'CNAME').exists(),'Custom domain unexpectedly activated')
check(not list((ROOT/'.github').rglob('*.yml')) if (ROOT/'.github').exists() else True,'Workflow must remain outside .github until activation')
print(json.dumps({'checks':checks,'source_files_verified':len(export['source_files']),'media_verified':len(export['media_files']),'html_pages':len(pages),'external_links':'preserved, not individually crawled','result':'PASS'},indent=2))
