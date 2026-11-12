import assert from 'node:assert/strict';
import {readFile,readdir,access} from 'node:fs/promises';
const source=await readFile('dist/server/index.js','utf8');
const worker=(await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'))).default;
let count=0;const check=v=>{assert(v);count++;};
const files=(await readdir('site/main')).filter(f=>/\.(html|css|js)$/.test(f)).concat((await readdir('site/main/articoli')).map(f=>'articoli/'+f));
const exists=async p=>{try{await access(p);return true;}catch{return false;}};
for(const file of files){
 const expected=await readFile('site/main/'+file,'utf8');
 const response=await worker.fetch(new Request('https://private.example/'+file),{});
 check(response.status===200&&response.headers.get('Cache-Control')==='no-store'&&response.headers.get('X-Robots-Tag')==='noindex, nofollow'&&(await response.text())===expected);
 if(!file.endsWith('.html'))continue;
 check(!expected.includes('ANTEPRIMA PRIVATA')&&!expected.includes('Versione attuale'));
 check((expected.match(/class="v2-nav"/g)||[]).length===1);
 for(const match of expected.matchAll(/\b(?:href|src)="([^"]+)"/g)){
  const raw=match[1].replaceAll('&amp;','&');const target=new URL(raw,'https://private.example/'+file);
  if(target.origin!=='https://private.example')continue;
  const key=target.pathname.slice(1)||'index.html';
  check(await exists('site/main/'+key)||await exists('site/'+key));
 }
}
let response=await worker.fetch(new Request('https://private.example/'),{});
check(response.status===200&&(await response.text())===await readFile('site/main/index.html','utf8'));
response=await worker.fetch(new Request('https://private.example/anteprima/atlante.html?q=bradipo'),{});
check(response.status===302&&response.headers.get('Location')==='/atlante.html?q=bradipo');
response=await worker.fetch(new Request('https://private.example/anteprima/articoli/dal-what-if-al-what-is.html'),{});
check(response.status===302&&response.headers.get('Location')==='/articoli/dal-what-if-al-what-is.html');
response=await worker.fetch(new Request('https://private.example/anteprima/?q=gioia'),{});
check(response.status===302&&response.headers.get('Location')==='/?q=gioia');
response=await worker.fetch(new Request('https://private.example/atlante.html',{method:'HEAD'}),{});
check(response.status===200&&(await response.arrayBuffer()).byteLength===0);
console.log(`${count} controlli della versione principale superati: pagine canoniche, menu, risorse, risposte private e compatibilità degli indirizzi.`);
