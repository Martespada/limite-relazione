(function(root) {
  'use strict';
  const labels = {definitive:'Definitivo',working:'In lavorazione',review:'Da verificare',archived:'Archiviato'};
  const normalize = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim();
  function searchable(p) { return normalize([p.name,p.english,p.animal,...p.animals,p.family,p.section,p.bookTitle,p.slogan,p.closing,p.description,p.example,p.note,...p.authors,...p.references.map(r=>r.label),...(p.aliases||[])].join(' ')); }
  function filterPosters(posters,state) {
    const words=normalize(state.query).split(' ').filter(Boolean);
    return posters.filter(p=>(!state.section||state.section==='all'||p.section===state.section)&&(state.status==='all'||p.status===state.status)&&(state.family==='all'||p.family===state.family)&&(state.animal==='all'||p.animals.includes(state.animal))&&(state.author==='all'||p.authors.includes(state.author))&&(!state.imageOnly||p.image)&&words.every(w=>searchable(p).includes(w))).sort((a,b)=>state.sort==='name'?a.name.localeCompare(b.name,'it'):state.sort==='status'?(Object.keys(labels).indexOf(a.status)-Object.keys(labels).indexOf(b.status)||a.order-b.order):a.order-b.order);
  }
  root.AtlasEngine={normalize,searchable,filterPosters,labels};
  if(typeof module!=='undefined')module.exports=root.AtlasEngine;
})(typeof window!=='undefined'?window:globalThis);
