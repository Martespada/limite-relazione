import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const source=await readFile('dist/server/index.js','utf8');
const worker=(await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'))).default;
let count=0;
const check=(value)=>{assert(value);count++;};
const objects=new Map();
const bucket={
  async put(key,bytes,options){objects.set(key,{body:new Uint8Array(bytes),size:bytes.byteLength,...options});},
  async get(key){return objects.get(key)||null;},
  async head(key){return objects.get(key)||null;},
  async list(){return {objects:[...objects.entries()].map(([key,object])=>({key,customMetadata:object.customMetadata})),truncated:false};}
};
const maintenanceKey='f'.repeat(64);
const maintenanceHeaders={'X-Atlas-Maintenance-Key':maintenanceKey};
const env={BUCKET:bucket,ATLAS_MEDIA_MAINTENANCE_KEY:maintenanceKey},origin='https://atlas.example';
let r=await worker.fetch(new Request(origin+'/'),env);
check(r.status===200&&(await r.text()).includes('class="v2-home-logo"'));
r=await worker.fetch(new Request(origin+'/data.js'),env);
check((await r.text()).includes('intrinsic-motivation'));
r=await worker.fetch(new Request(origin+'/articoli/la-zebra-il-leone-e-lerba.html'),env);
const article=await r.text();
check(r.status===200&&article.includes('La zebra, il leone')&&article.includes('Riferimenti bibliografici')&&article.includes('Nei conflitti umani, percezioni'));
const articleCover=await readFile('site/assets/articoli/la-zebra-cover.jpeg');
r=await worker.fetch(new Request(origin+'/assets/articoli/la-zebra-cover.jpeg'),env);
check(r.status===200&&r.headers.get('Content-Type')==='image/jpeg'&&Buffer.compare(Buffer.from(await r.arrayBuffer()),articleCover)===0);
r=await worker.fetch(new Request(origin+'/articoli/lo-slogun-batte-largomento.html'),env);
const slogunArticle=await r.text();
check(r.status===200&&slogunArticle.includes('La manipolazione è deliberata in chi costruisce lo slogun')&&slogunArticle.includes('Esplora i concetti nell’Atlante')&&slogunArticle.includes('href="../atlante.html#bias=confirmation"'));
const slogunCover=await readFile('site/assets/articoli/slogun-cover.webp');
r=await worker.fetch(new Request(origin+'/assets/articoli/slogun-cover.webp'),env);
check(r.status===200&&r.headers.get('Content-Type')==='image/webp'&&Buffer.compare(Buffer.from(await r.arrayBuffer()),slogunCover)===0);
r=await worker.fetch(new Request(origin+'/articoli/dal-what-if-al-what-is.html'),env);
const whatIfArticle=await r.text();
check(r.status===200&&whatIfArticle.includes('Motivazione autentica e autodeterminazione')&&whatIfArticle.includes('metanalisi di Judge e Piccolo')&&whatIfArticle.includes('operatore aeronautico')&&whatIfArticle.includes('Esplora i concetti nell’Atlante')&&whatIfArticle.includes('#bias=intrinsic-motivation')&&whatIfArticle.includes('id="nota-commitment"'));
const whatIfCover=await readFile('site/assets/articoli/dal-what-if-al-what-is-cover.jpg');
r=await worker.fetch(new Request(origin+'/assets/articoli/dal-what-if-al-what-is-cover.jpg'),env);
check(r.status===200&&r.headers.get('Content-Type')==='image/jpeg'&&Buffer.compare(Buffer.from(await r.arrayBuffer()),whatIfCover)===0);
r=await worker.fetch(new Request(origin+'/articoli/l-ombra-e-la-voce.html'),env);
const ombraArticle=await r.text();
check(r.status===200&&ombraArticle.includes('L’ombra e la voce')&&ombraArticle.includes('L’ombra e il cammino verso sé stessi')&&!ombraArticle.includes('Dall’ombra dell’altro all’ombra interiore')&&ombraArticle.includes('Riferimenti bibliografici')&&ombraArticle.includes('Per approfondire')&&ombraArticle.includes('Archetipi e individuazione')&&ombraArticle.includes('Attraverso di essa, ciascuno può esprimere'));
const ombraCover=await readFile('site/assets/articoli/l-ombra-e-la-voce-cover.png');
r=await worker.fetch(new Request(origin+'/assets/articoli/l-ombra-e-la-voce-cover.png'),env);
check(r.status===200&&r.headers.get('Content-Type')==='image/png'&&Buffer.compare(Buffer.from(await r.arrayBuffer()),ombraCover)===0);
r=await worker.fetch(new Request(origin+'/articoli/archetipi-e-individuazione.html'),env);
const archetipiArticle=await r.text();
check(r.status===200&&archetipiArticle.includes('Archetipi e individuazione')&&archetipiArticle.includes('Una riflessione sull’appartenenza')&&archetipiArticle.includes('nota-mandala')&&archetipiArticle.includes('href="l-ombra-e-la-voce.html"')&&archetipiArticle.includes('archetipi-percorso.png?v=2bf56bceac46dc7a')&&archetipiArticle.includes('class="article-diagram-crop"')&&!archetipiArticle.includes('Apri lo schema illustrato'));
check(ombraArticle.includes('href="archetipi-e-individuazione.html"'));
for(const name of ['archetipi-cover.png','archetipi-percorso.png']){
  const asset=await readFile('site/assets/articoli/'+name);
  r=await worker.fetch(new Request(origin+'/assets/articoli/'+name),env);
  check(r.status===200&&r.headers.get('Content-Type')==='image/png'&&r.headers.get('Cache-Control')==='no-store'&&Buffer.compare(Buffer.from(await r.arrayBuffer()),asset)===0);
}
r=await worker.fetch(new Request(origin+'/__atlas/assets/unknown.png',{method:'PUT',body:'test',headers:maintenanceHeaders}),env);
check(r.status===404&&objects.size===0);
const key='assets/definitivi/intrinsic-motivation-original.png';
const bytes=await readFile('site/'+key);
const sha=Buffer.from(await crypto.subtle.digest('SHA-256',bytes)).toString('hex');
for(const headers of [{}, {'X-Atlas-Maintenance-Key':'0'.repeat(64)}]){
  r=await worker.fetch(new Request(origin+'/__atlas/assets/status',{headers}),env);
  check(r.status===404);
  r=await worker.fetch(new Request(origin+'/__atlas/assets/'+key,{method:'PUT',body:bytes,headers:{...headers,'X-Content-Sha256':sha}}),env);
  check(r.status===404&&objects.size===0);
}
r=await worker.fetch(new Request(origin+'/__atlas/assets/status',{headers:maintenanceHeaders}),{BUCKET:bucket});
check(r.status===404);
r=await worker.fetch(new Request(origin+'/__atlas/assets/'+key,{method:'PUT',body:bytes,headers:{...maintenanceHeaders,'X-Content-Sha256':'0'.repeat(64)}}),env);
check(r.status===400&&objects.size===0);
r=await worker.fetch(new Request(origin+'/__atlas/assets/'+key,{method:'PUT',body:bytes,headers:{...maintenanceHeaders,'X-Content-Sha256':sha}}),env);
check(r.status===200&&(await r.json()).sha256===sha&&objects.size===1);
r=await worker.fetch(new Request(origin+'/'+key),env);
check(r.status===200&&r.headers.get('Content-Type')==='image/png'&&Buffer.compare(Buffer.from(await r.arrayBuffer()),bytes)===0);
r=await worker.fetch(new Request(origin+'/'+key,{method:'HEAD'}),env);
check(r.status===200&&r.headers.get('X-Atlas-Sha256')===sha&&(await r.arrayBuffer()).byteLength===0);
r=await worker.fetch(new Request(origin+'/__atlas/assets/status',{headers:maintenanceHeaders}),env);
check(r.status===200&&(await r.json()).assets[key]===sha);
r=await worker.fetch(new Request(origin+'/assets/definitivi/extrinsic-motivation-original.png'),env);
check(r.status===503);
for(const removedId of ['radical-constructivism','critical-constructivism']){
  for(const suffix of ['-original.png','-thumb.webp']){
    r=await worker.fetch(new Request(origin+'/assets/definitivi/'+removedId+suffix),env);
    check(r.status===404);
  }
}
for(const [path,type] of [['autore.html','text/html'],['author.css','text/css'],['author.js','text/javascript']]){
  r=await worker.fetch(new Request(origin+'/'+path),env);
  check(r.status===200&&r.headers.get('Content-Type').startsWith(type)&&r.headers.get('Cache-Control')==='no-store'&&(await r.text())===await readFile(path==='autore.html'?'site/main/'+path:'site/'+path,'utf8'));
}
const authorMedia=JSON.parse(await readFile('site/author-media.json','utf8'));
for(const item of authorMedia){
  r=await worker.fetch(new Request(origin+'/'+item.thumb),{});
  const preview=await readFile('site/'+item.thumb);
  check(r.status===200&&r.headers.get('Content-Type')==='image/webp'&&Buffer.compare(Buffer.from(await r.arrayBuffer()),preview)===0);
  const original=await readFile('site/'+item.original);
  const hash=Buffer.from(await crypto.subtle.digest('SHA-256',original)).toString('hex');
  r=await worker.fetch(new Request(origin+'/__atlas/assets/'+item.original,{method:'PUT',body:original,headers:{...maintenanceHeaders,'X-Content-Sha256':hash}}),env);
  check(r.status===200&&(await r.json()).sha256===hash);
  r=await worker.fetch(new Request(origin+'/'+item.original),env);
  check(r.status===200&&r.headers.get('Content-Type')==='image/png'&&Buffer.compare(Buffer.from(await r.arrayBuffer()),original)===0);
}
r=await worker.fetch(new Request(origin+'/assets/autore/curriculum-per-web.docx'),env);
check(r.status===404);
const documents=JSON.parse(await readFile('site/author-documents.json','utf8'));
for(const document of documents){
  r=await worker.fetch(new Request(origin+'/'+document.original),{});
  check(r.status===503&&r.headers.get('Content-Type').startsWith('text/plain'));
  const cover=await readFile('site/'+document.cover);
  r=await worker.fetch(new Request(origin+'/'+document.cover),{});
  check(r.status===200&&r.headers.get('Content-Type')==='image/webp'&&Buffer.compare(Buffer.from(await r.arrayBuffer()),cover)===0);
  const pdf=await readFile('site/'+document.original);
  check(Buffer.from(await crypto.subtle.digest('SHA-256',pdf)).toString('hex')===document.sha256&&pdf.length===document.size);
  r=await worker.fetch(new Request(origin+'/__atlas/assets/'+document.original,{method:'PUT',body:pdf,headers:{...maintenanceHeaders,'X-Content-Sha256':document.sha256}}),env);
  check(r.status===200&&(await r.json()).sha256===document.sha256);
  r=await worker.fetch(new Request(origin+'/'+document.original),env);
  check(r.status===200&&r.headers.get('Content-Type')==='application/pdf'&&r.headers.get('Content-Disposition')===`inline; filename="${document.filename}"`&&Buffer.compare(Buffer.from(await r.arrayBuffer()),pdf)===0);
  r=await worker.fetch(new Request(origin+'/'+document.original+'?download=1'),env);
  check(r.status===200&&r.headers.get('Content-Disposition')===`attachment; filename="${document.filename}"`&&Buffer.compare(Buffer.from(await r.arrayBuffer()),pdf)===0);
  r=await worker.fetch(new Request(origin+'/'+document.original+'?download=1',{method:'HEAD'}),env);
  check(r.status===200&&r.headers.get('Content-Length')===String(document.size)&&(await r.arrayBuffer()).byteLength===0);
  r=await worker.fetch(new Request(origin+'/__atlas/assets/status',{headers:maintenanceHeaders}),env);
  check((await r.json()).assets[document.original]===document.sha256);
}
r=await worker.fetch(new Request(origin+'/assets/autore/articoli/unlisted.pdf'),env);
check(r.status===404);
console.log(`${count} controlli Worker superati: file privati, pagina Autore, apertura e download PDF, checksum e originali identici.`);
