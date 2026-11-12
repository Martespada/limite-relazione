"""Build the independent site. This script does not publish, change DNS, or call Sites."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('--output',default='dist')
args=parser.parse_args()
source=ROOT/'site'
output=(ROOT/args.output).resolve()
assert output!=source and ROOT in output.parents, 'Output must be a project subfolder.'
if output.exists():
    shutil.rmtree(output)
shutil.copytree(source,output)
paths=list(output.rglob('*'))
assert not any(p.is_symlink() for p in paths), 'Pages artifacts cannot contain symbolic links.'
files=[p for p in paths if p.is_file()]
size=sum(p.stat().st_size for p in files)
assert size<1_000_000_000, f'Pages site exceeds the 1 GB limit: {size} bytes'
assert (output/'index.html').is_file()
assert not (output/'CNAME').exists(), 'Custom domain activation is intentionally deferred.'
assert not (output/'.openai').exists(), 'Hosting configuration must stay outside the public artifact.'
manifest=[{'path':p.relative_to(output).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
(ROOT/'docs/build-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'output':str(output),'files':len(files),'bytes':size,'limit':1_000_000_000,'published':False,'custom_domain_configured':False},indent=2))
