const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..'),site=path.join(root,'site');
const context={window:{}};
for(const name of ['atlas-data.js','catalogue-meta.js'])vm.runInNewContext(fs.readFileSync(path.join(site,name),'utf8'),context);
const posters=JSON.parse(JSON.stringify(context.window.ATLAS_PREVIEW_POSTERS));
const meta=JSON.parse(JSON.stringify(context.window.ATLAS_PREVIEW_META));
const {defaults,filter,related,normalize}=require(path.join(site,'atlas-engine.js'));
let checks=0;const check=(value,message)=>{assert(value,message);checks++};
check(posters.length===127&&new Set(posters.map(p=>p.id)).size===127,'Poster completeness');
check(meta.themes.length===7&&meta.themes[0].slug==='limit-model','Seven sections; LIMIT first');
for(const theme of meta.themes)check(filter(posters,{...defaults,section:theme.title}).length===theme.count,theme.title);
for(const p of posters){
 check(filter(posters,{...defaults,q:p.name}).some(x=>x.id===p.id),'Search by title '+p.id);
 for(const image of [p.thumb,p.image,p.original,...p.variants.map(v=>v.image)])check(fs.existsSync(path.join(site,image)),'Poster/variant file '+image);
 check(p.references.every(r=>r.label&&r.citation&&/^https?:/.test(r.url)),'Reference data '+p.id);
 check(related(posters,p).every(x=>x.id!==p.id&&x.section===p.section),'Related concepts '+p.id);
}
check(filter(posters,{...defaults,q:'coccodrillo'}).some(p=>p.id==='truth-bias'),'Truth bias/crocodile');
check(filter(posters,{...defaults,q:'bradipo'}).some(p=>p.id==='normalcy-bias'),'Normalcy/sloth');
check(filter(posters,{...defaults,q:'LIMIT',author:'Tommaso Corona'}).length===6,'Combined filters');
check(filter(posters,{...defaults,status:'working'}).length===0,'Working state supported with no invented posters');
check(filter(posters,{...defaults,q:'zzzzzzzz'}).length===0,'Empty state');
check(normalize('VERITÀ · affinità')==='verita affinita','Accent normalization');
const alpha=filter(posters,{...defaults,sort:'name'});
check(alpha.every((p,i)=>!i||alpha[i-1].name.localeCompare(p.name,'it')<=0),'Alphabetical sorting');
check(!posters.find(p=>p.id==='continuing-bonds').bookUrl,'Continuing bonds attribution unchanged');
check(!posters.some(p=>['radical-constructivism','critical-constructivism','halo-ramirezi','sunk-cost-archive'].includes(p.id)),'Requested removals preserved');
check(meta.articles.length===7&&meta.articles.every(a=>fs.existsSync(path.join(site,a.url))),'All articles');
const source=fs.readFileSync(path.join(site,'site.js'),'utf8');
for(const prefix of ['/','/limite-relazione/']){
 for(const [file,hash,destination] of [['','#bias=truth-bias','atlante.html'],['index.html','#tema=bias-cognitivi','atlante.html'],['autore.html','#saggi','saggi.html']]){
  let target;const location={pathname:prefix+file,hash,search:'',href:'https://example.org'+prefix+file,replace:url=>target=url};
  vm.runInNewContext(source.slice(0,source.indexOf('})();')+5),{location,URL,URLSearchParams});
  check(new URL(target).pathname===prefix+destination,'Legacy route '+prefix+file+hash);
 }
}
console.log(JSON.stringify({checks,posters:posters.length,sections:meta.themes.length,articles:meta.articles.length,result:'PASS'},null,2));
