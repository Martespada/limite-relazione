"""Read-only comparison with the original publication; never writes to the Site."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parent.parent
export=json.loads((ROOT/'docs/export-manifest.json').read_text())
origin=export['source_url']
worker=(ROOT/'source-sites/worker/index.js').read_text()
text=json.loads(re.search(r'^const TEXT_ASSETS=(.*);$',worker,re.M).group(1))
media=export['media_files']
cases=[('media',record['path'],record) for record in media]+[('text',key,value) for key,value in text.items() if not key.startswith('anteprima/')]
def check(case):
    kind,path,record=case
    head=kind=='media' and record['storage']=='R2'
    with tempfile.TemporaryDirectory() as tmp:
        headers=Path(tmp)/'headers';body=Path(tmp)/'body'
        args=['curl','-sS','--max-time','35','--dump-header',str(headers),'--output',str(body),origin+'/'+path]
        if head:args.insert(1,'--head')
        for attempt in range(2):
            result=subprocess.run(args,capture_output=True)
            if result.returncode==0:break
            if attempt:raise RuntimeError((path,'network failure',result.returncode))
        raw=headers.read_text()
        codes=re.findall(r'^HTTP/\S+ (\d+)',raw,re.M)
        assert codes and codes[-1]=='200',(path,codes)
        fields={k.lower():v.strip() for k,v in re.findall(r'^([^:\s]+):\s*(.*)$',raw,re.M)}
        if head:
            assert fields.get('x-atlas-sha256')==record['sha256'],(path,'live SHA-256 mismatch')
            assert int(fields['content-length'])==record['size'],(path,'live size mismatch')
        elif kind=='media':
            assert hashlib.sha256(body.read_bytes()).hexdigest()==record['sha256'],(path,'embedded image bytes mismatch')
        else:
            assert body.read_text()==record['body'],(path,'live application file mismatch')
    return {'path':path,'kind':kind,'result':'PASS'}
results=[]
with ThreadPoolExecutor(max_workers=8) as pool:
    jobs=[pool.submit(check,case) for case in cases]
    for job in as_completed(jobs):
        results.append(job.result())
        if len(results)%50==0:print(f'Live source verified: {len(results)}/{len(cases)}',flush=True)
report={'source_url':origin,'source_commit':export['source_commit'],'version':export['site_version'],'date':'2026-11-12','method':'267 media: live HTTP HEAD, SHA-256 and size headers; 10 embedded images: full byte hashes; 24 application files: full text comparison','checks':len(results),'result':'PASS','files':sorted(results,key=lambda x:x['path'])}
(ROOT/'docs/live-source-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(results),'media':len(media),'text':len(cases)-len(media),'result':'PASS'}),flush=True)
