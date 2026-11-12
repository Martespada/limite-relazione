(() => {
  'use strict';
  const posters=window.ATLAS_POSTERS;
  const {filterPosters,labels}=window.AtlasEngine;
  const byId=new Map(posters.flatMap(p=>[p.id,...(p.legacyIds||[])].map(id=>[id,p])));
  const $=id=>document.getElementById(id);
  const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const state={query:'',status:'all',section:'all',family:'all',animal:'all',author:'all',imageOnly:false,sort:'series'};
  const mindSlug='mente-esperienza-relazione';
  const themes={'limit-model':'L.I.M.I.T. Model','bias-cognitivi':'Bias cognitivi','persuasione':'Persuasione',[mindSlug]:'Mente, esperienza e relazione','gestione-dello-stress':'Gestione dello Stress','tratti-di-personalita':'Tratti di personalità (OCEAN)','psicologia-strategica':'Psicologia Strategica'};
  let results=[],activeId=null,toastTimer;
  const badge=p=>`<span class="status ${p.status}">${labels[p.status]}</span>`;
  const concept=p=>`<div class="concept-cover"><span class="mini-brand">LIMITE & RELAZIONE</span><div class="concept-center"><span class="animal-name">${escape(p.animal)}</span><span class="concept-bias">${escape(p.english)}</span></div><span class="concept-bottom">ABBINAMENTO RECUPERATO<br>POSTER DA RECUPERARE</span></div>`;
  function render(){
    results=filterPosters(posters,state);
    $('result-count').textContent=`${results.length} ${results.length===1?'scheda':'schede'} su ${posters.length}${state.section!=='all'?` · ${state.section}`:''}${state.query?` · “${state.query}”`:''}`;
    $('grid').innerHTML=results.map(p=>`<button type="button" class="poster-card" data-open="${p.id}" aria-label="Apri scheda: ${escape(p.name)}, ${escape(p.animal)}, ${labels[p.status]}"><div class="poster-frame">${p.image?`<img src="${p.thumb}" width="420" height="747" loading="lazy" decoding="async" alt="Poster ${escape(p.english)} con ${escape(p.animal)}">`:concept(p)}</div><div class="card-meta"><span class="card-index">${String(p.order+1).padStart(2,'0')} / ${escape(p.family).toUpperCase()}</span>${badge(p)}</div><h3>${escape(p.name)}</h3><p class="card-sub">${escape(p.animal)} <span class="card-arrow" aria-hidden="true">↗</span></p></button>`).join('');
    $('empty').hidden=results.length!==0;
    $('grid').hidden=results.length===0;
    const sectionPosters=posters.filter(p=>state.section==='all'||p.section===state.section);
    document.querySelectorAll('[data-status]').forEach(b=>{b.setAttribute('aria-pressed',String(b.dataset.status===state.status));b.querySelector('span').textContent=sectionPosters.filter(p=>b.dataset.status==='all'||p.status===b.dataset.status).length;});
    document.querySelectorAll('[data-family]').forEach(b=>{b.setAttribute('aria-pressed',String(b.dataset.family===state.family));const count=sectionPosters.filter(p=>b.dataset.family==='all'||p.family===b.dataset.family).length;b.querySelector('span').textContent=count;b.setAttribute('aria-label',`${b.dataset.family==='all'?'Tutti i temi':b.dataset.family}: ${count} poster`);});
    document.querySelectorAll('[data-section]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.section===state.section)));
    updateNavigation();
  }
  function reset(updateURL=true){
    Object.assign(state,{query:'',status:'all',section:'all',family:'all',animal:'all',author:'all',imageOnly:false,sort:'series'});
    $('search').value='';$('animal').value='all';$('author').value='all';$('sort').value='series';$('image-only').checked=false;
    if(updateURL&&Object.keys(themes).some(slug=>location.hash===`#tema=${slug}`))history.replaceState(null,'',location.pathname+location.search+'#catalogue');
    render();
  }
  function buildControls(){
    $('section-filters').innerHTML=[['all','Tutta la raccolta'],...Object.entries(themes)].map(([slug,label])=>`<button type="button" class="family-filter section-filter" data-section="${slug==='all'?'all':escape(label)}" data-section-slug="${slug}" aria-pressed="${slug==='all'}">${escape(label)}<span>${posters.filter(p=>slug==='all'||p.section===label).length}</span></button>`).join('');
    $('status-tabs').innerHTML=[['all','Tutti'],...Object.entries(labels)].map(([id,label])=>`<button type="button" class="status-tab" data-status="${id}" aria-pressed="${id==='all'}">${id==='all'?'Tutti':label}<span class="tab-count">${posters.filter(p=>id==='all'||p.status===id).length}</span></button>`).join('');
    const families=[...new Set(posters.map(p=>p.family))];
    $('family-filters').innerHTML=['all',...families].map(f=>`<button type="button" class="family-filter" data-family="${f}" aria-pressed="${f==='all'}">${f==='all'?'Tutti i temi':escape(f)}<span>${posters.filter(p=>f==='all'||p.family===f).length}</span></button>`).join('');
    const addOptions=(id,values)=>$(id).insertAdjacentHTML('beforeend',values.sort((a,b)=>a.localeCompare(b,'it')).map(v=>`<option value="${escape(v)}">${escape(v)}</option>`).join(''));
    addOptions('animal',[...new Set(posters.flatMap(p=>p.animals))]);
    addOptions('author',[...new Set(posters.flatMap(p=>p.authors))]);
    $('hero-stats').innerHTML=`<div><strong>${posters.length}</strong><span>schede nella raccolta</span></div><div><strong>${posters.filter(p=>p.image).length}</strong><span>poster disponibili</span></div><div><strong>${posters.filter(p=>p.status==='working').length}</strong><span>sviluppi in lavorazione</span></div>`;
    $('hero-art').innerHTML=['limit-model','limit-mentalizing','limit-tension'].map(id=>{const p=byId.get(id);return `<button type="button" class="hero-poster" data-open="${id}" data-space="limit-model" aria-label="Apri ${escape(p.name)}"><img src="${p.thumb}" width="420" height="747" alt="${escape(p.animal)} · ${escape(p.english)}" fetchpriority="high"><span class="hero-label">${escape(p.english).toUpperCase()}</span></button>`}).join('');
    const stress=posters.filter(p=>p.family==='Gestione dello Stress'),intro=byId.get('stress-management');
    $('stress-count').textContent=`${stress.length} POSTER DEFINITIVI`;
    $('stress-intro').innerHTML=`<button type="button" class="stress-poster" data-open="${intro.id}" aria-label="Apri Gestione dello stress, Scimmia"><img src="${intro.thumb}" width="420" height="747" loading="lazy" alt="Poster introduttivo sulla gestione dello stress con la scimmia"><span>Il poster introduttivo · Scimmia ↗</span></button>`;
    $('stress-strategies').innerHTML=stress.filter(p=>p.id!==intro.id).map(p=>`<button type="button" class="stress-strategy" data-open="${p.id}">${escape(p.name)}<small>${escape(p.animal)} ↗</small></button>`).join('');
    $('stress-browse').innerHTML=`Esplora ${stress.length} poster <span aria-hidden="true">↗</span>`;
    const model=posters.filter(p=>p.family===themes['limit-model']),overview=byId.get('limit-model');
    $('limit-count').textContent=`${model.length} POSTER DEFINITIVI`;
    $('limit-overview').innerHTML=`<button type="button" class="stress-poster" data-open="${overview.id}" data-space="limit-model" aria-label="Apri la tavola d’insieme del L.I.M.I.T. Model"><img src="${overview.thumb}" width="420" height="747" loading="lazy" alt="Tavola d’insieme: mulo, cervo, polpo, volpe e lince rappresentano le cinque dimensioni del L.I.M.I.T. Model"><span>La tavola d’insieme ↗</span></button>`;
    $('limit-components').innerHTML=model.filter(p=>p.id!==overview.id).map(p=>`<button type="button" class="stress-strategy limit-component" data-open="${p.id}" data-space="limit-model" aria-label="Apri ${escape(p.name)}, ${escape(p.animal)}"><span class="limit-letter" aria-hidden="true">${escape(p.modelLetter)}</span><span>${escape(p.modelTerm)}<small>${escape(p.modelTranslation)} · ${escape(p.animal)} ↗</small></span></button>`).join('');
    $('limit-browse').innerHTML=`Esplora i ${model.length} poster <span aria-hidden="true">↗</span>`;
    const mind=posters.filter(p=>p.section===themes[mindSlug]),featured=byId.get('intersubjectivity');
    $('mind-count').textContent=`${mind.length} POSTER DEFINITIVI`;
    $('mind-featured').innerHTML=`<button type="button" class="stress-poster" data-open="${featured.id}" data-space="${mindSlug}" aria-label="Apri Intersoggettività, Orso e Volpe"><img src="${featured.thumb}" width="420" height="747" loading="lazy" alt="Poster di Intersoggettività con l’orso e la volpe"><span>Intersoggettività · Orso e Volpe ↗</span></button>`;
    $('mind-concepts').innerHTML=mind.filter(p=>p.id!==featured.id).map(p=>`<button type="button" class="stress-strategy" data-open="${p.id}" data-space="${mindSlug}">${escape(p.name)}<small>${escape(p.animal)} ↗</small></button>`).join('');
    $('mind-browse').innerHTML=`Esplora i ${mind.length} poster <span aria-hidden="true">↗</span>`;
    const bias=posters.filter(p=>p.section===themes['bias-cognitivi']),confirmation=byId.get('confirmation');
    $('bias-count').textContent=`${bias.length} POSTER DEFINITIVI`;
    $('bias-featured').innerHTML=`<button type="button" class="stress-poster" data-open="${confirmation.id}" data-space="bias-cognitivi" aria-label="Apri Bias di conferma, Pappagallo"><img src="${confirmation.thumb}" width="420" height="747" loading="lazy" alt="Poster del bias di conferma con il pappagallo"><span>Bias di conferma · Pappagallo ↗</span></button>`;
    $('bias-highlights').innerHTML=['truth-bias','normalcy-bias','status-quo','anchoring-mussel','negativity'].map(id=>{const p=byId.get(id);return `<button type="button" class="stress-strategy" data-open="${p.id}" data-space="bias-cognitivi">${escape(p.name)}<small>${escape(p.animal)} ↗</small></button>`}).join('');
    $('bias-browse').innerHTML=`Esplora i ${bias.length} poster <span aria-hidden="true">↗</span>`;
    const persuasion=posters.filter(p=>p.section===themes.persuasione),persuasionFeatured=byId.get('persuasion-reciprocity');
    $('persuasion-count').textContent=`${persuasion.length} POSTER DEFINITIVI`;
    $('persuasion-featured').innerHTML=`<button type="button" class="stress-poster" data-open="${persuasionFeatured.id}" data-space="persuasione" aria-label="Apri Reciprocità, Volpe e Lupo"><img src="${persuasionFeatured.thumb}" width="420" height="747" loading="lazy" alt="Poster della reciprocità con la volpe e il lupo"><span>Reciprocità · Volpe e Lupo ↗</span></button>`;
    $('persuasion-concepts').innerHTML=persuasion.filter(p=>p.id!==persuasionFeatured.id).map(p=>`<button type="button" class="stress-strategy" data-open="${p.id}" data-space="persuasione">${escape(p.name)}<small>${escape(p.animal)} ↗</small></button>`).join('');
    $('persuasion-browse').innerHTML=`Esplora ${persuasion.length} poster <span aria-hidden="true">↗</span>`;
    const personality=posters.filter(p=>p.section===themes['tratti-di-personalita']),personalityOverview=byId.get('ocean-big-five');
    $('personality-count').textContent=`${personality.length} POSTER DEFINITIVI`;
    $('personality-overview').innerHTML=`<button type="button" class="stress-poster" data-open="${personalityOverview.id}" data-space="tratti-di-personalita" aria-label="Apri la tavola Big Five OCEAN"><img src="${personalityOverview.thumb}" width="420" height="747" loading="lazy" alt="Big Five: colibrì, ape, lemure, quokka e pangolino"><span>La tavola d’insieme · OCEAN ↗</span></button>`;
    $('personality-traits').innerHTML=personality.filter(p=>p.id!==personalityOverview.id).map(p=>`<button type="button" class="stress-strategy" data-open="${p.id}" data-space="tratti-di-personalita">${escape(p.oceanLetter)} · ${escape(p.name)}<small>${escape(p.english)} · ${escape(p.animal)} ↗</small></button>`).join('');
    $('personality-browse').innerHTML=`Esplora ${personality.length} poster <span aria-hidden="true">↗</span>`;
    const strategic=posters.filter(p=>p.section===themes['psicologia-strategica']),strategicFeatured=byId.get('strategic-double-bind');
    $('strategic-count').textContent=strategic.length+' POSTER DEFINITIVI';
    $('strategic-featured').innerHTML='<button type="button" class="stress-poster" data-open="'+strategicFeatured.id+'" data-space="psicologia-strategica" aria-label="Apri Doppio legame, canide adulto e cucciolo"><img src="'+strategicFeatured.thumb+'" width="420" height="747" loading="lazy" alt="Il canide adulto ordina al cucciolo fantasma di essere spontaneo"><span>Doppio legame · L’inizio del percorso ↗</span></button>';
    $('strategic-concepts').innerHTML=strategic.filter(p=>p.id!==strategicFeatured.id).map(p=>'<button type="button" class="stress-strategy" data-open="'+p.id+'" data-space="psicologia-strategica">'+escape(p.name)+'<small>'+escape(p.axiomNumber?p.axiomNumber+'° assioma · '+p.animal:'Regolazione ed equilibrio')+' ↗</small></button>').join('');
    $('strategic-browse').innerHTML='Esplora i '+strategic.length+' poster <span aria-hidden="true">↗</span>';
  }
  function selectTheme(slug){
    reset(false);state.section=themes[slug];render();
  }
  function openThemeSpace(slug,updateURL=true){
    if(!Object.hasOwn(themes,slug))return;
    if($('detail').open)closeDetail(false);
    selectTheme(slug);
    const hash=`#tema=${slug}`;
    if(updateURL&&location.hash!==hash)history.pushState(null,'',hash);
    $('catalogue').scrollIntoView({block:'start'});$('catalogue-title').focus({preventScroll:true});
  }
  function currentNavigation(){return results.some(p=>p.id===activeId)?results:posters;}
  function updateNavigation(){
    if(!activeId)return;
    const list=currentNavigation(),index=list.findIndex(p=>p.id===activeId);
    $('detail-position').textContent=`${index+1} / ${list.length}`;
    $('previous').disabled=index<=0;$('next').disabled=index>=list.length-1;
  }
  function referenceCopy(p){
    const attribution=p.modelAttribution?`<div class="reference model-attribution"><strong>${escape(p.authors.join(', '))}</strong><p>${escape(p.modelAttribution)}</p></div>`:'';
    const entries=p.references.map(r=>`<div class="reference"><a href="${escape(r.url)}" target="_blank" rel="noopener noreferrer">${escape(r.label)} ↗</a><p>${escape(r.citation)}</p></div>`).join('');
    const pending=!attribution&&!entries?`<p class="reference-pending">${p.authors.length?escape(p.authors.join(', '))+'. ':''}Riferimento specifico da completare.</p>`:'';
    const origin=attribution||entries?`<p class="reference-origin">${escape(p.referenceOrigin)}</p>`:'';
    return attribution+entries+pending+origin;
  }
  const radicalizationConnections={
    polarization:'Il passaggio dalle posizioni contrapposte alle appartenenze inconciliabili.',
    ethnocentrism:'La contrapposizione fra «noi» e «loro» come fattore di coesione.',
    'moral-disengagement-conduct':'Come si può arrivare a giustificare l’aggressione in nome di una causa.',
    'moral-disengagement-victim':'La rappresentazione dell’avversario come colpevole o indegno.',
    groupthink:'Il consenso interno e la difficoltà di dare spazio al dissenso.',
    'hostile-attribution':'La tendenza a interpretare l’altro come una minaccia.'
  };
  const slogunConnections={
    confirmation:'Il messaggio distorto può trovare conferma in ciò che già pensiamo.',
    framing:'La cornice seleziona alcuni aspetti dei fatti e ne lascia altri nell’ombra.',
    dissonance:'Il disaccordo può essere vissuto come una minaccia alla coerenza delle proprie credenze.',
    'illusory-truth':'La ripetizione di un messaggio può renderlo più familiare e credibile.',
    'dunning-kruger':'Sicurezza nel giudizio e competenza effettiva non coincidono sempre.',
    polarization:'Lo “slogun” rafforza l’identificazione e lo schieramento.',
    groupthink:'Quando il gruppo premia l’adesione, la discussione rischia di restringersi.'
  };
  const whatIfConnections={
    'intrinsic-motivation':'Il piacere per un’attività non coincide con ogni forma di motivazione autonoma.',
    'extrinsic-motivation':'Anche un compito poco gratificante può essere svolto per il valore che gli attribuiamo.',
    'planful-problem-solving':'Come passare dall’idea a un progetto realizzabile e correggerne il percorso.',
    'planning-fallacy':'La distanza tra una previsione ottimistica e l’esecuzione concreta.',
    'locus-of-control':'Riconoscere su quali aspetti possiamo realmente incidere.',
    groupthink:'Una visione condivisa può lasciare spazio al dubbio e al confronto.',
    intersubjectivity:'La partecipazione a un progetto comune richiede anche ascolto reciproco.'
  };
  function articleCrosslink(p){
    const radicalization=radicalizationConnections[p.id],slogun=slogunConnections[p.id],whatIf=whatIfConnections[p.id];
    if(!radicalization&&!slogun&&!whatIf)return '';
    return `<aside class="detail-article-note" aria-label="Articoli collegati"><span>PER APPROFONDIRE</span>${radicalization?`<div class="detail-article-entry"><p>${escape(radicalization)}</p><a href="articoli/la-soglia-della-radicalizzazione.html">Leggi «La soglia della radicalizzazione» ↗</a></div>`:''}${slogun?`<div class="detail-article-entry"><p>${escape(slogun)}</p><a href="articoli/lo-slogun-batte-largomento.html">Leggi «Lo “slogun” batte l’argomento» ↗</a></div>`:''}${whatIf?`<div class="detail-article-entry"><p>${escape(whatIf)}</p><a href="articoli/dal-what-if-al-what-is.html">Leggi «Dal “What If” al “What Is”» ↗</a></div>`:''}</aside>`;
  }
  function openDetail(id,updateURL=true){
    const p=byId.get(id);if(!p)return;id=p.id;
    activeId=id;
    $('detail-body').innerHTML=`<div class="detail-layout"><div class="detail-visual">${p.image?`<img src="${p.image}" alt="Poster originale della serie: ${escape(p.name)}, ${escape(p.animal)}">`:concept(p)}<div class="detail-actions">${p.image?`<button type="button" data-view="${p.image}" data-caption="${escape(p.name)} · ${escape(p.animal)}">Ingrandisci ↗</button><a href="${p.original||p.image}" download="${p.id}.${p.original?'png':'webp'}">${p.original?'Scarica originale PNG':'Scarica poster'} ↓</a>`:''}<button type="button" id="copy-link">Copia link</button></div>${p.image?`<p class="detail-source">${p.original?'Originale definitivo':'Versione recuperata'}: ${escape(p.sourceName)}</p>`:''}${p.variants.length?`<div class="detail-variants"><p class="detail-source">Altra versione recuperata</p>${p.variants.map(v=>`<button type="button" class="variant-link" data-view="${v.image}" data-caption="${escape(v.name)}">Apri altra versione ↗</button>`).join('')}</div>`:''}</div><div class="detail-copy">${badge(p)}<p class="eyebrow">${escape(p.family).toUpperCase()} · ${escape(p.animal).toUpperCase()}</p><h2 id="detail-title">${escape(p.name)}</h2><div class="detail-english">${escape(p.english)}</div>${p.bookTitle?`<p class="detail-book">Approfondito in ${p.bookUrl?`<a href="${escape(p.bookUrl)}" target="_blank" rel="noopener noreferrer" aria-label="${escape(p.bookTitle)} su Amazon, si apre in una nuova scheda"><strong>${escape(p.bookTitle)}</strong> ↗</a>`:`<strong>${escape(p.bookTitle)}</strong>`}.</p>`:''}${p.slogan?`<blockquote>${escape(p.slogan)}${p.closing?`<small class="poster-closing">${escape(p.closing)}</small>`:''}</blockquote>`:'<div class="missing-slogan">Slogan della serie da recuperare.</div>'}<h3>${p.detailHeading?escape(p.detailHeading):p.family==='Tratti di personalità'?(p.id==='ocean-big-five'?'IL MODELLO':'IL TRATTO'):p.family===themes['limit-model']?(p.id==='limit-model'?'IL MODELLO':'LA DIMENSIONE'):p.family==='Gestione dello Stress'?(p.id==='stress-management'?'IL TEMA':p.id==='mindfulness'?'LA PRATICA':'LA STRATEGIA'):p.family==='Persuasione'?(p.id==='persuasion-contrast'?'IL CONTRASTO':p.id==='persuasion-mere-exposure'?'IL MECCANISMO':'IL PRINCIPIO'):p.family==='Disimpegno morale'?'IL RAGGRUPPAMENTO':p.family==='Psicologia strategica'?'LA STRATEGIA':['Coscienza','Motivazione','Costruttivismo'].includes(p.family)?'IL CONCETTO':'IL MECCANISMO'}</h3><p>${escape(p.description)}</p><div class="example-box"><h3>UN ESEMPIO CONCRETO</h3><p>${escape(p.example)}</p><p class="question">${escape(p.question)}</p></div><h3>${escape(p.referenceHeading||(p.modelAttribution?'AUTORE E PROVENIENZA':'AUTORI E RIFERIMENTI'))}</h3>${referenceCopy(p)}${articleCrosslink(p)}${p.modelAttribution?'<a class="model-return" href="#tema=limit-model" data-theme="limit-model">Tutti i poster del modello ↗</a>':''}${p.section===themes[mindSlug]?`<a class="mind-return" href="#tema=${mindSlug}" data-theme="${mindSlug}">Tutti i poster di Mente, esperienza e relazione ↗</a>`:''}${p.section===themes['bias-cognitivi']?'<a class="mind-return" href="#tema=bias-cognitivi" data-theme="bias-cognitivi">Tutti i poster di Bias cognitivi ↗</a>':''}${p.section===themes.persuasione?'<a class="mind-return" href="#tema=persuasione" data-theme="persuasione">Tutti i poster di Persuasione ↗</a>':''}${p.section===themes['tratti-di-personalita']?'<a class="mind-return" href="#tema=tratti-di-personalita" data-theme="tratti-di-personalita">Tutti i poster dei Tratti di personalità (OCEAN) ↗</a>':''}${p.section===themes['psicologia-strategica']?'<a class="mind-return" href="#tema=psicologia-strategica" data-theme="psicologia-strategica">Tutti i poster di Psicologia Strategica ↗</a>':''}<div class="editorial-note"><strong>STATO DELLA SERIE · ${labels[p.status].toUpperCase()}</strong>${escape(p.note)}${!p.image?' Il poster non è disponibile nell’atlante.':''}</div></div></div>`;
    if(!$('detail').open)$('detail').showModal();
    $('detail').scrollTop=0;
    document.body.style.overflow='hidden';
    if(updateURL){const hash=`#bias=${id}`;if(location.hash!==hash)history.pushState({bias:id},'',hash);}
    updateNavigation();
    $('close-detail').focus({preventScroll:true});
  }
  function closeDetail(updateURL=true){
    if($('viewer').open)$('viewer').close();
    const former=activeId;$('detail').close();activeId=null;document.body.style.overflow='';
    if(updateURL&&location.hash.startsWith('#bias=')){const slug=Object.keys(themes).find(slug=>themes[slug]===state.section);history.replaceState(null,'',location.pathname+location.search+(slug?`#tema=${slug}`:'#catalogue'));}
    document.querySelector(`#grid [data-open="${former}"]`)?.focus({preventScroll:true});
  }
  function moveDetail(direction){const list=currentNavigation(),index=list.findIndex(p=>p.id===activeId);if(list[index+direction])openDetail(list[index+direction].id);}
  function syncRoute(){const theme=location.hash.match(/^#tema=([a-z0-9-]+)$/);if(theme&&Object.hasOwn(themes,theme[1])){openThemeSpace(theme[1],false);return;}const match=location.hash.match(/^#bias=([a-z0-9-]+)$/);if(match&&byId.has(match[1])){const p=byId.get(match[1]);if(p.section===themes['psicologia-strategica']&&(results.length===posters.length||!results.some(r=>r.id===p.id)))selectTheme('psicologia-strategica');else if(p.modelAttribution)selectTheme('limit-model');else if(p.section===themes['tratti-di-personalita']&&(results.length===posters.length||!results.some(r=>r.id===p.id)))selectTheme('tratti-di-personalita');else if(p.section===themes.persuasione&&(results.length===posters.length||!results.some(r=>r.id===p.id)))selectTheme('persuasione');else if(p.section===themes[mindSlug]&&(results.length===posters.length||!results.some(r=>r.id===p.id)))selectTheme(mindSlug);openDetail(match[1],false);}else{if($('detail').open)closeDetail(false);if(location.hash==='#catalogue')reset(false);}}
  function toast(text){clearTimeout(toastTimer);$('toast').textContent=text;$('toast').hidden=false;toastTimer=setTimeout(()=>$('toast').hidden=true,2500);}
  async function copyLink(){
    const url=location.origin+location.pathname+location.search+`#bias=${activeId}`;
    try{await navigator.clipboard.writeText(url);toast('Link della scheda copiato. L’accesso resta privato.');}
    catch{let field=$('copy-fallback');if(!field){field=document.createElement('input');field.id='copy-fallback';field.className='copy-fallback';field.readOnly=true;field.setAttribute('aria-label','Link privato della scheda da copiare');$('detail-body').querySelector('.detail-copy').prepend(field);}field.value=url;field.focus();field.select();toast('Seleziona e copia il link della scheda.');}
  }
  $('search').addEventListener('input',e=>{state.query=e.target.value;render();});
  for(const id of ['sort','animal','author'])$(id).addEventListener('change',e=>{state[id]=e.target.value;render();});
  $('image-only').addEventListener('change',e=>{state.imageOnly=e.target.checked;render();});
  $('status-tabs').addEventListener('click',e=>{const b=e.target.closest('[data-status]');if(b){state.status=b.dataset.status;render();}});
  $('family-filters').addEventListener('click',e=>{const b=e.target.closest('[data-family]');if(b){state.family=b.dataset.family;render();}});
  $('section-filters').addEventListener('click',e=>{const b=e.target.closest('[data-section]');if(b){if(b.dataset.section==='all')reset();else openThemeSpace(b.dataset.sectionSlug);}});
  $('reset').addEventListener('click',reset);$('empty-reset').addEventListener('click',reset);
  for(const [id,slug] of [['limit-browse','limit-model'],['bias-browse','bias-cognitivi'],['persuasion-browse','persuasione'],['mind-browse',mindSlug],['stress-browse','gestione-dello-stress'],['personality-browse','tratti-di-personalita'],['strategic-browse','psicologia-strategica']])$(id).addEventListener('click',e=>{e.preventDefault();openThemeSpace(slug);});
  $('filter-toggle').addEventListener('click',()=>{const expanded=$('filter-toggle').getAttribute('aria-expanded')!=='true';$('filter-toggle').setAttribute('aria-expanded',String(expanded));document.querySelector('.filters').classList.toggle('expanded',expanded);$('filter-toggle').lastElementChild.textContent=expanded?'−':'+';});
  document.addEventListener('click',e=>{const card=e.target.closest('[data-open]');if(card){if(Object.hasOwn(themes,card.dataset.space))selectTheme(card.dataset.space);openDetail(card.dataset.open);}const theme=e.target.closest('[data-theme]');if(theme){e.preventDefault();openThemeSpace(theme.dataset.theme);}const view=e.target.closest('[data-view]');if(view){$('viewer-image').src=view.dataset.view;$('viewer-image').alt=view.dataset.caption;$('viewer-caption').textContent=view.dataset.caption;$('viewer').showModal();}if(e.target.closest('#copy-link'))copyLink();});
  $('close-detail').addEventListener('click',()=>closeDetail());$('close-viewer').addEventListener('click',()=>$('viewer').close());
  $('close-method').addEventListener('click',()=>$('method').close());$('method-button').addEventListener('click',()=>$('method').showModal());
  $('detail').addEventListener('cancel',e=>{e.preventDefault();closeDetail();});
  $('previous').addEventListener('click',()=>moveDetail(-1));$('next').addEventListener('click',()=>moveDetail(1));
  for(const id of ['detail','viewer','method'])$(id).addEventListener('click',e=>{if(e.target!==$(id))return;const r=$(id).getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)id==='detail'?closeDetail():$(id).close();});
  document.addEventListener('keydown',e=>{if(e.key==='/'&&!$('detail').open&&!$('method').open&&!['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName)){e.preventDefault();$('search').focus();}if($('detail').open&&!$('viewer').open){if(e.key==='ArrowRight'){e.preventDefault();moveDetail(1);}if(e.key==='ArrowLeft'){e.preventDefault();moveDetail(-1);}}});
  window.addEventListener('hashchange',syncRoute);window.addEventListener('popstate',syncRoute);
  buildControls();render();syncRoute();
})();
