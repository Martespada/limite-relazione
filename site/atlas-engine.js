(function(root) {
  'use strict';
  const normalize = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim();
  const defaults = {q:'',section:'all',topic:'all',animal:'all',author:'all',status:'all',sort:'series'};
  function searchable(p) {
    return normalize([p.name,p.english,p.animal,...p.animals,p.family,p.section,p.topic,p.bookTitle,p.slogan,p.closing,p.description,p.example,...p.authors,...p.references.map(r=>r.label),...(p.aliases||[])].join(' '));
  }
  function filter(posters,state) {
    const words = normalize(state.q).split(' ').filter(Boolean);
    return posters.filter(p => (state.section==='all'||p.section===state.section)&&(state.topic==='all'||p.topic===state.topic)&&(state.animal==='all'||p.animals.includes(state.animal))&&(state.author==='all'||p.authors.includes(state.author))&&(state.status==='all'||p.status===state.status)&&words.every(w=>searchable(p).includes(w))).sort((a,b)=>state.sort==='name'?a.name.localeCompare(b.name,'it'):a.order-b.order);
  }
  function related(posters,p,count=3) {
    return posters.filter(x=>x.id!==p.id).map(x=>({p:x,score:(x.section===p.section?8:0)+(x.topic===p.topic?4:0)+(x.family===p.family?2:0)+(x.authors.some(a=>p.authors.includes(a))?1:0)})).filter(x=>x.score>=8).sort((a,b)=>b.score-a.score||a.p.order-b.p.order).slice(0,count).map(x=>x.p);
  }
  root.PreviewAtlasEngine={normalize,defaults,filter,related};
  if(typeof module!=='undefined')module.exports=root.PreviewAtlasEngine;
})(typeof window!=='undefined'?window:globalThis);
