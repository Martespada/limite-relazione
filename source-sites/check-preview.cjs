const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const {defaults,filter,related,normalize}=require('./site/anteprima/atlas-engine.js');
const context={window:{}};
vm.runInNewContext(fs.readFileSync('site/anteprima/data.js','utf8'),context);
vm.runInNewContext(fs.readFileSync('site/anteprima/meta.js','utf8'),context);
const posters=JSON.parse(JSON.stringify(context.window.ATLAS_PREVIEW_POSTERS));
const meta=JSON.parse(JSON.stringify(context.window.ATLAS_PREVIEW_META));
const original=JSON.parse(fs.readFileSync('site/data.js','utf8').replace(/^window.ATLAS_POSTERS = /,'').trim().replace(/;$/,''));
let checks=0;const check=(value,message)=>{assert(value,message);checks++;};
check(posters.length===127&&new Set(posters.map(p=>p.id)).size===127,'Complete catalogue and stable IDs');
const counts={'L.I.M.I.T. Model':6,'Bias cognitivi':56,'Persuasione':9,'Mente, esperienza e relazione':29,'Gestione dello Stress':13,'Tratti di personalità (OCEAN)':6,'Psicologia Strategica':8};
check(meta.themes[0].slug==='limit-model'&&meta.themes.length===7,'LIMIT is first');
for(const [section,count] of Object.entries(counts))check(filter(posters,{...defaults,section}).length===count,section);
check(posters.every(p=>p.section&&p.topic&&counts[p.section]),'Every poster has a section and topic');
for(const p of posters){
 const before=original.find(x=>x.id===p.id);const after={...p};delete after.topic;delete after.section;const prior={...before};delete prior.section;
 check(JSON.stringify(after)===JSON.stringify(prior),'Preserved poster content: '+p.id);
}
check(filter(posters,{...defaults,q:'coccodrillo'}).some(p=>p.id==='truth-bias'),'Search by animal');
check(filter(posters,{...defaults,q:'gioia',section:'Mente, esperienza e relazione'}).some(p=>p.id==='emotion-joy'),'Emotion accessible in its section');
check(filter(posters,{...defaults,section:'Gestione dello Stress',topic:'Risposte di difesa'}).length===5,'Defense separate from coping');
check(filter(posters,{...defaults,section:'Gestione dello Stress',topic:'Strategie di coping'}).every(p=>p.family!=='Risposte di difesa'&&p.id!=='resilience'),'Coping classification');
check(filter(posters,{...defaults,q:'resilienza',section:'Mente, esperienza e relazione'}).some(p=>p.id==='resilience'),'Resilience remains a process');
check(!posters.find(p=>p.id==='continuing-bonds').bookUrl,'No invented book attribution');
check(!posters.some(p=>['radical-constructivism','critical-constructivism','halo-ramirezi','sunk-cost-archive'].includes(p.id)),'Removed posters remain absent');
check(filter(posters,{...defaults,q:'LIMIT',author:'Tommaso Corona'}).length===6,'Combined author and text search');
check(filter(posters,{...defaults,status:'working'}).length===0,'Empty states supported');
check(filter(posters,{...defaults,q:'zzzzzz'}).length===0,'No-result search');
const alphabetical=filter(posters,{...defaults,sort:'name'});check(alphabetical.every((p,i)=>!i||alphabetical[i-1].name.localeCompare(p.name,'it')<=0),'Alphabetical order');
check(normalize('VERITÀ · affinità')==='verita affinita','Accent-insensitive search');
for(const p of posters)check(related(posters,p).every(x=>x.id!==p.id&&x.section===p.section),'Related concepts stay relevant: '+p.id);
check(meta.articles.length===6,'All articles included');
for(const article of meta.articles){
 check(article.concepts.every(id=>posters.some(p=>p.id===id)),'Valid concept links in '+article.slug);
 const old=fs.readFileSync('site/articoli/'+article.slug+'.html','utf8');const next=fs.readFileSync('site/anteprima/'+article.url,'utf8');
 const text=s=>(s.match(/<article\b[^>]*>[\s\S]*<\/article>/)?.[0]||'').replace(/<[^>]*>/g,'').replace(/\s+/g,' ').trim();
 check(text(old)===text(next),'Article text unchanged: '+article.slug);
}
const htmlFiles=fs.readdirSync('site/anteprima').filter(x=>x.endsWith('.html')).map(x=>'site/anteprima/'+x).concat(fs.readdirSync('site/anteprima/articoli').map(x=>'site/anteprima/articoli/'+x));
for(const file of htmlFiles){
 const html=fs.readFileSync(file,'utf8');check((html.match(/class="v2-nav"/g)||[]).length===1,'Shared navigation: '+file);
 for(const attr of html.matchAll(/\b(?:href|src)="([^"]+)"/g)){
  const href=attr[1].replaceAll('&amp;','&');if(/^(?:https?:|data:|#)/.test(href))continue;
  const target=path.resolve(path.dirname(file),href.split(/[?#]/)[0]);check(fs.existsSync(target),'Existing resource: '+file+' '+href);
 }
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);check(ids.length===new Set(ids).size,'Unique IDs: '+file);
}
console.log(`${checks} controlli anteprima superati: classificazione completa, contenuti preservati, ricerca, correlazioni, navigazione e risorse.`);
