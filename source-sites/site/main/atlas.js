(() => {
  'use strict';
  const posters = window.ATLAS_PREVIEW_POSTERS;
  const {themes,articles} = window.ATLAS_PREVIEW_META;
  const {defaults,filter,related} = window.PreviewAtlasEngine;
  const $ = id => document.getElementById(id);
  const escape = v => String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M7 7h10v10"/></svg>';
  const labels = {definitive:'Definitivo',working:'In lavorazione',review:'Da verificare',archived:'Archiviato'};
  const byId = new Map(posters.flatMap(p=>[p.id,...(p.legacyIds||[])].map(id=>[id,p])));
  const storageKey = 'limite-relazione-preview-atlas-v1';
  let state = {...defaults}, results = [], limit = 24, active = null, opener = null, originalOverflow = '', toastTimer;
  const paramKeys = {q:'q',section:'sezione',topic:'tema',animal:'animale',author:'autore',status:'stato',sort:'ordine'};

  function readState() {
    const url = new URL(location.href);
    const next = {...defaults};
    for (const [key,param] of Object.entries(paramKeys)) if (url.searchParams.has(param)) next[key] = url.searchParams.get(param);
    const section = themes.find(t=>t.slug === next.section || t.title === next.section);
    next.section = section?.title || 'all';
    if (!['series','name'].includes(next.sort)) next.sort = 'series';
    const oldTheme = location.hash.match(/^#tema=([a-z0-9-]+)$/);
    if (oldTheme) next.section = themes.find(t=>t.slug===oldTheme[1])?.title || 'all';
    return next;
  }
  function setURL(push=false,hash=location.hash) {
    const url = new URL(location.href); url.search = '';
    for (const [key,param] of Object.entries(paramKeys)) {
      let value = state[key];
      if (key==='section') value = themes.find(t=>t.title===value)?.slug || 'all';
      if (value !== defaults[key] && value) url.searchParams.set(param,value);
    }
    url.hash = hash;
    history[push?'pushState':'replaceState'](null,'',url.pathname+url.search+url.hash);
  }
  function remember() {
    try { sessionStorage.setItem(storageKey,JSON.stringify({state,limit,scroll:window.scrollY})); } catch {}
  }
  function options(id,values,label,value) {
    const select=$(id); select.innerHTML='<option value="all">'+label+'</option>'+[...new Set(values)].sort((a,b)=>a.localeCompare(b,'it')).map(v=>`<option value="${escape(v)}">${escape(v)}</option>`).join('');
    select.value = values.includes(value) ? value : 'all';
  }
  function controls() {
    $('atlas-search').value=state.q; $('atlas-sort').value=state.sort;
    const scope=posters.filter(p=>state.section==='all'||p.section===state.section);
    options('topic',scope.map(p=>p.topic),'Tutti i temi',state.topic);
    const topicScope=scope.filter(p=>state.topic==='all'||p.topic===state.topic);
    options('atlas-animal',topicScope.flatMap(p=>p.animals),'Tutti gli animali',state.animal);
    options('atlas-author',topicScope.flatMap(p=>p.authors),'Tutti gli autori',state.author);
    const statuses=[...new Set(posters.map(p=>p.status))];
    $('status-label').hidden=statuses.length<2;
    $('atlas-status').innerHTML='<option value="all">Tutti gli stati</option>'+statuses.map(s=>`<option value="${s}">${labels[s]}</option>`).join('');
    $('atlas-status').value=state.status;
    $('section-tabs').innerHTML=[{title:'all',short:'Tutti',count:posters.length},...themes].map(t=>`<button type="button" data-section="${escape(t.title)}" aria-pressed="${state.section===t.title}">${t.short}<span>${t.count}</span></button>`).join('');
    const theme=themes.find(t=>t.title===state.section);
    $('theme-intro').hidden=!theme;
    if(theme) $('theme-intro').innerHTML=`<div><h2>${escape(theme.title)}</h2><p>${escape(theme.description)}</p>${theme.slug==='limit-model'?'<p class="v2-small">Proposta teorica e formativa personale di Tommaso Corona, non ancora validata empiricamente. Le cinque dimensioni interagiscono e non costituiscono una sequenza di fasi. <a href="autore.html#tavole">Consulta le tavole del progetto</a>.</p>':theme.slug==='gestione-dello-stress'?'<p class="v2-small">Le risposte di difesa descrivono reazioni allo stress; le strategie di coping riguardano modi di affrontare la situazione. Usa il filtro Tema per distinguerle.</p>':''}</div>`;
  }
  function renderGrid() {
    $('atlas-grid').innerHTML=results.slice(0,limit).map(p=>`<button class="v2-poster-card" type="button" data-poster="${p.id}" aria-label="Apri scheda: ${escape(p.name)}, ${escape(p.animal)}"><img src="../${p.thumb}" width="420" height="747" loading="lazy" decoding="async" alt="Poster ${escape(p.name)} con ${escape(p.animal)}"><p class="v2-card-topic">${escape(p.topic)}</p><h3>${escape(p.name)}</h3><p class="v2-card-animal">${escape(p.animal)}${p.status!=='definitive'?' · '+labels[p.status]:''}</p></button>`).join('');
    $('atlas-grid').hidden=results.length===0;
    $('atlas-empty').hidden=results.length!==0;
    $('load-more').hidden=limit>=results.length;
    $('shown-count').textContent=results.length?`${Math.min(limit,results.length)} di ${results.length} poster mostrati`:'';
    $('load-more').textContent=`Mostra altri ${Math.min(24,Math.max(0,results.length-limit))} poster`;
  }
  function render() {
    results=filter(posters,state);
    $('atlas-count').textContent=`${results.length} ${results.length===1?'poster':'poster'} su ${posters.length}${state.section!=='all'?' · '+state.section:''}`;
    $('clear-search').hidden=!state.q;
    const applied=Object.entries(state).filter(([k,v])=>k!=='sort'&&v!==defaults[k]);
    $('reset-filters').hidden=applied.length===0;
    $('active-filters').innerHTML=applied.map(([key,value])=>`<button type="button" data-remove="${key}" aria-label="Rimuovi filtro: ${escape(labels[value]||value)}">${escape(labels[value]||value)} <span aria-hidden="true">×</span></button>`).join('');
    renderGrid(); remember();
  }
  function change(key,value) {
    state[key]=value; limit=24;
    if (key==='section') Object.assign(state,{topic:'all',animal:'all',author:'all'});
    if (key==='topic') Object.assign(state,{animal:'all',author:'all'});
    controls(); render(); setURL(false,'');
  }
  function reset() { state={...defaults};limit=24;controls();render();setURL(false,''); }
  function heading(p) {
    if(p.detailHeading)return p.detailHeading;
    if(p.modelAttribution)return p.id==='limit-model'?'IL MODELLO':'LA DIMENSIONE';
    if(p.family==='Tratti di personalità')return p.id==='ocean-big-five'?'IL MODELLO':'IL TRATTO';
    if(p.family==='Gestione dello Stress')return p.id==='stress-management'?'IL TEMA':p.id==='mindfulness'?'LA PRATICA':'LA STRATEGIA';
    if(p.family==='Risposte di difesa')return 'LA RISPOSTA';
    if(p.family==='Persuasione')return p.id==='persuasion-contrast'?'IL CONTRASTO':p.id==='persuasion-mere-exposure'?'IL MECCANISMO':'IL PRINCIPIO';
    if(p.family==='Disimpegno morale')return 'IL RAGGRUPPAMENTO';
    if(p.family==='Psicologia strategica')return 'LA STRATEGIA';
    if(['Coscienza','Motivazione','Emozioni'].includes(p.family))return 'IL CONCETTO';
    return 'IL MECCANISMO';
  }
  function updateNavigation() {
    const i=results.findIndex(p=>p.id===active);
    $('detail-prev').disabled=i<=0; $('detail-next').disabled=i<0||i>=results.length-1;
    $('detail-position').textContent=i>=0?`${i+1} / ${results.length}`:'';
  }
  function open(id,push=true) {
    const p=byId.get(id);if(!p)return;
    if(!results.some(x=>x.id===p.id)) {
      state={...defaults,section:p.section};limit=24;controls();render();
    }
    const i=results.findIndex(x=>x.id===p.id);
    if(i>=limit){limit=Math.ceil((i+1)/24)*24;renderGrid();}
    if(!$('poster-detail').open) { opener=document.querySelector(`[data-poster="${p.id}"]`); originalOverflow=document.body.style.overflow; }
    active=p.id;
    const readings=articles.filter(a=>a.concepts.includes(p.id));
    const entries=p.references.map(r=>`<div class="v2-detail-ref"><a href="${escape(r.url)}" target="_blank" rel="noopener noreferrer">${escape(r.label)} ${ICON}</a><p>${escape(r.citation)}</p></div>`).join('');
    const attribution=p.modelAttribution?`<div class="v2-detail-ref"><strong>${escape(p.authors.join(', '))}</strong><p>${escape(p.modelAttribution)}</p></div>`:'';
    const pending=!entries&&!attribution?`<p>${escape(p.authors.join(', '))}${p.authors.length?'. ':''}Riferimento specifico da completare.</p>`:'';
    const others=related(posters,p);
    $('poster-detail-body').innerHTML=`<div class="v2-detail-layout"><div class="v2-detail-visual"><img src="../${p.thumb}" width="420" height="747" alt="${escape(p.name)} · ${escape(p.animal)}"><div class="v2-detail-actions"><a href="../${p.original}" data-media="${escape(p.name)}">Ingrandisci ${ICON}</a><a href="../${p.original}" download="${p.id}.png">Scarica PNG ↓</a><button type="button" id="copy-poster-link">Copia link</button></div>${p.variants.map(v=>`<a class="v2-inline" href="../${v.image}" data-media="${escape(v.name)}">${escape(v.name)} ${ICON}</a>`).join('')}</div><div class="v2-detail-copy"><span class="status ${p.status}">${labels[p.status]}</span><p class="v2-kicker" style="margin-top:17px">${escape(p.section)}</p><h2 id="detail-heading">${escape(p.name)}</h2><div class="v2-detail-english">${escape(p.english)} · ${escape(p.animal)}</div>${p.bookTitle?`<p class="v2-detail-book">Approfondito in ${p.bookUrl?`<a href="${escape(p.bookUrl)}" target="_blank" rel="noopener noreferrer"><strong>${escape(p.bookTitle)}</strong> ${ICON}</a>`:`<strong>${escape(p.bookTitle)}</strong>`}.</p>`:''}${p.slogan?`<blockquote>${escape(p.slogan)}${p.closing?`<small>${escape(p.closing)}</small>`:''}</blockquote>`:''}<h3>${escape(heading(p))}</h3><p>${escape(p.description)}</p><div class="v2-detail-example"><h3>UN ESEMPIO CONCRETO</h3><p>${escape(p.example)}</p><p>${escape(p.question)}</p></div><h3>${escape(p.referenceHeading||(p.modelAttribution?'AUTORE E PROVENIENZA':'AUTORI E RIFERIMENTI'))}</h3>${attribution}${entries}${pending}<p class="v2-detail-origin">${escape(p.referenceOrigin)}</p>${readings.length?`<h3>LETTURE COLLEGATE</h3><div class="v2-related-list">${readings.map(a=>`<a href="${a.url}">${escape(a.title)} ${ICON}</a>`).join('')}</div>`:''}${others.length?`<h3>ESPLORA ANCHE</h3><div class="v2-related-list">${others.map(x=>`<a href="#bias=${x.id}" data-related="${x.id}">${escape(x.name)} ${ICON}</a>`).join('')}</div>`:''}<details class="v2-detail-note"><summary>Note sulla scheda</summary><p>${escape(p.note)}</p></details></div></div>`;
    if(!$('poster-detail').open)$('poster-detail').showModal();
    document.body.style.overflow='hidden';$('poster-detail').scrollTop=0;
    if(push)setURL(true,'#bias='+p.id); else setURL(false,'#bias='+p.id);
    updateNavigation();$('detail-close').focus({preventScroll:true});remember();
  }
  function close(update=true) {
    if($('media-viewer').open)$('media-viewer').close();
    $('poster-detail').close();document.body.style.overflow=originalOverflow;
    const prior=active;active=null;if(update)setURL(false,'');
    const target=opener?.isConnected?opener:document.querySelector(`[data-poster="${prior}"]`);
    target?.focus({preventScroll:true});remember();
  }
  function route() {
    state=readState();limit=24;controls();render();
    const id=location.hash.match(/^#bias=([a-z0-9-]+)$/)?.[1];
    if(id&&byId.has(id))open(id,false);else if($('poster-detail').open)close(false);
  }
  function toast(text) { clearTimeout(toastTimer);$('atlas-toast').textContent=text;$('atlas-toast').hidden=false;toastTimer=setTimeout(()=>$('atlas-toast').hidden=true,3000); }
  async function copy() {
    try { await navigator.clipboard.writeText(location.href);toast('Link della scheda copiato. L’accesso resta privato.'); }
    catch { let input=$('copy-link-fallback');if(!input){input=document.createElement('input');input.id='copy-link-fallback';input.readOnly=true;input.setAttribute('aria-label','Link privato della scheda');$('poster-detail-body').querySelector('.v2-detail-copy').prepend(input);}input.value=location.href;input.focus();input.select();toast('Seleziona e copia il link della scheda.'); }
  }
  $('atlas-search-form').addEventListener('submit',e=>e.preventDefault());
  $('atlas-search').addEventListener('input',e=>change('q',e.target.value));
  $('clear-search').addEventListener('click',()=>{change('q','');$('atlas-search').focus();});
  for(const [id,key] of [['topic','topic'],['atlas-sort','sort'],['atlas-animal','animal'],['atlas-author','author'],['atlas-status','status']])$(id).addEventListener('change',e=>change(key,e.target.value));
  $('section-tabs').addEventListener('click',e=>{const button=e.target.closest('[data-section]');if(button)change('section',button.dataset.section);});
  $('active-filters').addEventListener('click',e=>{const button=e.target.closest('[data-remove]');if(button)change(button.dataset.remove,defaults[button.dataset.remove]);});
  $('reset-filters').addEventListener('click',reset);
  $('atlas-empty').querySelector('[data-reset]').addEventListener('click',reset);
  $('load-more').addEventListener('click',()=>{const firstNew=limit;limit+=24;renderGrid();remember();document.querySelectorAll('.v2-poster-card')[firstNew]?.focus({preventScroll:true});});
  $('atlas-grid').addEventListener('click',e=>{const button=e.target.closest('[data-poster]');if(button)open(button.dataset.poster);});
  $('poster-detail').addEventListener('click',e=>{
    const link=e.target.closest('[data-related]');if(link){e.preventDefault();open(link.dataset.related);}
    if(e.target.closest('#copy-poster-link'))copy();
    if(e.target!==$('poster-detail'))return;const r=$('poster-detail').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)close();
  });
  $('detail-close').addEventListener('click',()=>close());
  $('poster-detail').addEventListener('cancel',e=>{e.preventDefault();close();});
  for(const [id,direction] of [['detail-prev',-1],['detail-next',1]])$(id).addEventListener('click',()=>{const i=results.findIndex(p=>p.id===active);if(results[i+direction])open(results[i+direction].id);});
  document.addEventListener('keydown',e=>{
    if(e.key==='/'&&!$('poster-detail').open&&!['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName)){e.preventDefault();$('atlas-search').focus();}
    if($('poster-detail').open&&!$('media-viewer').open&&!['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName)&&['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();const i=results.findIndex(p=>p.id===active)+(e.key==='ArrowRight'?1:-1);if(results[i])open(results[i].id);}
  });
  window.addEventListener('pagehide',remember);
  window.addEventListener('popstate',route);window.addEventListener('hashchange',route);
  const explicit=location.search||location.hash;
  let saved;
  if(!explicit)try{saved=JSON.parse(sessionStorage.getItem(storageKey));}catch{}
  state=saved?.state?{...defaults,...saved.state}:readState();limit=Math.min(posters.length,Math.max(24,saved?.limit||24));controls();render();
  const deep=location.hash.match(/^#bias=([a-z0-9-]+)$/)?.[1];
  if(deep&&byId.has(deep)){
    if(!location.search){state={...defaults,section:byId.get(deep).section};controls();render();}
    open(deep,false);
  }else{setURL(false,'');if(saved?.scroll)requestAnimationFrame(()=>window.scrollTo({top:saved.scroll,behavior:'instant'}));}
})();
