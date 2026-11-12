import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
const source=await readFile('dist/server/index.js','utf8');
const worker=(await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'))).default;
let checks=0;const check=v=>{assert(v);checks++;};
const files=(await readdir('site/anteprima')).filter(f=>/\.(html|css|js)$/.test(f)).map(f=>'anteprima/'+f).concat((await readdir('site/anteprima/articoli')).map(f=>'anteprima/articoli/'+f));
for(const file of files){
 const r=await worker.fetch(new Request('https://private.example/'+file),{});
 if(file.endsWith('.html')){
  const destination=file==='anteprima/index.html'?'/':'/'+file.slice('anteprima/'.length);
  check(r.status===302&&r.headers.get('Location')===destination&&r.headers.get('Cache-Control')==='no-store');
 }else check(r.status===200&&r.headers.get('Cache-Control')==='no-store'&&r.headers.get('X-Robots-Tag')==='noindex, nofollow'&&(await r.text())===await readFile('site/'+file,'utf8'));
}
let r=await worker.fetch(new Request('https://private.example/anteprima/'),{});
check(r.status===302&&r.headers.get('Location')==='/');
r=await worker.fetch(new Request('https://private.example/anteprima'),{});
check(r.status===302&&r.headers.get('Location')==='/');
r=await worker.fetch(new Request('https://private.example/anteprima/missing.html'),{});
check(r.status===404);
r=await worker.fetch(new Request('https://private.example/anteprima/atlante.html',{method:'HEAD'}),{});
check(r.status===302&&r.headers.get('Location')==='/atlante.html'&&(await r.arrayBuffer()).byteLength===0);
console.log(`${checks} controlli compatibilità anteprima superati: reindirizzamenti, script, stili, HEAD e risorse non previste.`);
