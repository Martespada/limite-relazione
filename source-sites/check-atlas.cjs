const fs = require('fs');
const vm = require('vm');
const assert = require('node:assert/strict');
const context = {window: {}};
vm.runInNewContext(fs.readFileSync('site/data.js', 'utf8'), context);
const posters = context.window.ATLAS_POSTERS;
const {filterPosters, normalize, labels} = require('./site/engine.js');
const base = {query:'',status:'all',section:'all',family:'all',animal:'all',author:'all',imageOnly:false,sort:'series'};
let count = 0;
function check(state, predicate) {
  const result = filterPosters(posters, {...base, ...state});
  assert(predicate(result), JSON.stringify(state)); count++;
}
assert.equal(posters.length, new Set(posters.map(p=>p.id)).size); count++;
for (const p of posters) {
  assert(p.name && p.description && p.example && p.question && p.note);
  assert(labels[p.status]);
  for (const src of [p.image,p.thumb,p.original,...p.variants.flatMap(v=>[v.image,v.thumb])].filter(Boolean)) assert(fs.existsSync('site/'+src));
  for (const ref of p.references) assert.equal(new URL(ref.url).protocol, 'https:');
  count++;
}
check({query:'coccodrillo'},r=>r.some(p=>p.id==='truth-bias'));
check({query:'normalcy bradipo'},r=>r.length===1 && r[0].status==='definitive');
check({query:'verità illusoria'},r=>r.some(p=>p.id==='illusory-truth'));
check({query:'Levine'},r=>r.length===1 && r[0].id==='truth-bias');
check({query:'l’emozione dalla verità'},r=>r.some(p=>p.id==='truth-bias'));
check({query:'COZZA'},r=>r.some(p=>p.id==='anchoring-mussel'));
check({query:'affinita'},r=>r.some(p=>p.id==='affinity'));
check({query:'zz-no-match-zz'},r=>r.length===0);
check({status:'definitive'},r=>r.length===127 && r.every(p=>p.status==='definitive'));
check({status:'working'},r=>r.length===0);
check({status:'archived'},r=>r.length===0);
check({imageOnly:true},r=>r.length===127 && r.every(p=>p.image));
check({family:'Relazione',animal:'Lupo'},r=>r.length===1 && r[0].id==='ethnocentrism');
check({status:'definitive',author:'Timothy R. Levine'},r=>r.length===1);
check({status:'definitive',query:'bradipo'},r=>r.length===1&&r[0].id==='normalcy-bias');
check({family:'Informazione',animal:'Picchio',imageOnly:true},r=>r.length===1);
check({query:'asino',status:'definitive'},r=>r.length===3 && r.some(p=>p.id==='sunk-cost') && r.some(p=>p.id==='lollapalooza') && r.some(p=>p.id==='persuasion-commitment'));
check({sort:'name'},r=>r.every((p,i)=>!i || r[i-1].name.localeCompare(p.name,'it')<=0));
check({sort:'status'},r=>r.length===127 && r.every(p=>p.status==='definitive'));
assert.equal(normalize('Verità · AFFINITÀ'), 'verita affinita'); count++;
const batch = [
  ['confirmation','Pappagallo'], ['status-quo','Tartaruga'], ['blind-spot','Camaleonte'],
  ['hyperbolic-discounting','Scoiattolo'], ['anchoring-mussel','Cozza'], ['negativity','Riccio'],
  ['groupthink','Pinguini'], ['peacock','Pavone'], ['ikea-effect','Castoro'], ['ostrich-bias','Struzzo'],
  ['survivorship','Salmone'], ['sour-grapes','Volpe'], ['hindsight','Gufo'], ['false-consensus','Gallo'],
  ['sunk-cost','Asino'], ['halo-cat','Gatto'], ['unrealistic-optimism','Cicala'], ['illusory-superiority','Aquila'],
  ['reactive-devaluation','Avvoltoio'], ['loss-aversion','Polpo'],
  ['probability-neglect','Elefante'], ['attribution','Suricato'], ['backfire','Armadillo'],
  ['illusory-truth','Picchio'], ['polarization','Due gruppi di animali'], ['framing','Serpente'],
  ['affect','Ragno'], ['self-serving','Leone'], ['affinity','Fenicotteri'], ['gamblers-fallacy','Coccinella'],
  ['hostile-attribution','Panda'], ['attentional-bias','Pipistrello'], ['planning-fallacy','Pinguino'],
  ['prototype','Ornitorinco · Orso'], ['salience','Falena'], ['bandwagon','Pecore'],
  ['ulterior-motives','Maialino'], ['ambiguity','Pappagallo'], ['truth-bias','Coccodrillo'], ['normalcy-bias','Bradipo'],
  ['contrast','Elefante · Serpente · Formica · Uccellino'], ['dunning-kruger','Stambecco'],
  ['lollapalooza','Cane · Pecore · Gufo · Pavone · Asino'], ['twaddle-tendency','Ape'],
  ['dissonance','Procione'], ['noise','Capibara'], ['occasion-noise','Capibara'],
  ['wysiati','Cavallo'], ['ethnocentrism','Lupi'], ['risk-compensation','Cinghiale'],
  ['naive-realism','Ramirezi'], ['explanatory-depth','Pesce rosso'], ['uncertainty-intolerance','Ippopotamo'],
  ['fight-response','Toro'], ['flight-response','Gazzella'], ['freeze-response','Cerbiatto'],
  ['flop-faint-response','Capra'], ['fawn-response','Cane'],
  ['emotion-joy','Cane'], ['emotion-sadness','Koala'], ['emotion-fear','Lepre'],
  ['emotion-anger','Tasso'], ['emotion-surprise','Tarsio'], ['emotion-disgust','Lama'],
  ['emotional-contagion','Cane · Koala · Lepre · Tasso · Tarsio · Lama'],
  ['mental-social-representation','Delfino'],
  ['stress-management', 'Scimmia'],
  ['problem-focused-coping', 'Lontra'],
  ['planful-problem-solving', 'Corvo'],
  ['seeking-social-support', 'Formiche'],
  ['positive-reappraisal', 'Panda rosso'],
  ['escape-avoidance', 'Paguro'],
  ['emotion-focused-coping', 'Orso'],
  ['overprecision', 'Falco'],
  ['locus-of-control', 'Topolini'],
  ['reality-of-reality', 'Topolini'],
  ['illusion-of-transparency', 'Rana'],
  ['limit-model', 'Mulo · Cervo · Polpo · Volpe · Lince'],
  ['limit-load', 'Mulo'],
  ['limit-identity', 'Cervo'],
  ['limit-mentalizing', 'Polpo · Volpe'],
  ['limit-inhibition', 'Volpe'],
  ['limit-tension', 'Lince'],
  ['intersubjectivity', 'Orso · Volpe'],
  ['expectation-blindness', 'Segugio · Procione'],
  ['dodo-verdict', 'Dodo · Lepre · Varano · Volpe · Tasso · Gufo'],
  ['state-of-consciousness', 'Lemuri'],
  ['field-of-consciousness', 'Suricato · Serpente · Rapace'],
  ['mood-congruent-memory', 'Procioni'],
  ['empathy-emotional-intelligence', 'Elefante · Volpe'],
  ['apophenia', 'Corvo'],
  ['intrinsic-motivation', 'Cane'],
  ['extrinsic-motivation', 'Cane'],
  ['law-of-the-instrument', 'Scimpanzé'],
  ['paradoxical-stratagem', 'Canide · Orso · Procione · Cervo · Lepre'],
  ['deindividuation', 'Iene · Lepre'],
  ['moral-disengagement-conduct', 'Volpe · Galline'],
  ['moral-disengagement-responsibility', 'Scimmie · Gufo'],
  ['moral-disengagement-consequences', 'Cinghiale'],
  ['moral-disengagement-victim', 'Lupi · Coniglio'],
  ['tall-poppy-syndrome', 'Talpa giardiniera'],
  ['pareidolia', 'Uccello dal piumaggio a ventaglio'],
  ['persuasion-reciprocity', 'Volpe · Lupo'],
  ['persuasion-commitment', 'Asino · Volpe'],
  ['persuasion-scarcity', 'Uccello mercante · Pinguino'],
  ['persuasion-social-proof', 'Sardine · Pesce'],
  ['persuasion-authority', 'Uccello in camice · Pinguini'],
  ['persuasion-liking', 'Volpe · Lontra'],
  ['persuasion-contrast', 'Bulldog · Lepre · Volpe'],
  ['persuasion-unity', 'Pinguini'],
  ['persuasion-mere-exposure', 'Camaleonte'],
  ['mindfulness', 'Panda'],
  ['ocean-big-five', 'Colibrì · Ape · Lemure · Quokka · Pangolino'],
  ['ocean-openness', 'Colibrì'],
  ['ocean-conscientiousness', 'Ape'],
  ['ocean-extraversion', 'Lemure'],
  ['ocean-agreeableness', 'Quokka'],
  ['ocean-neuroticism', 'Pangolino']
];
for (const [index,[id,animal]] of batch.entries()) {
  const p=posters.find(p=>p.id===id);
  assert(p && p.animal===animal && p.status==='definitive' && p.original?.endsWith('.png') && p.slogan && p.closing);
  assert.equal(p.order,index); count++;
}
assert(!posters.some(p=>p.id==='anchoring-squirrel')); count++;
check({query:'Laibson scoiattolo',status:'definitive'},r=>r.length===1&&r[0].id==='hyperbolic-discounting');
check({query:'Ariely castoro',status:'definitive'},r=>r.length===1&&r[0].id==='ikea-effect');
check({query:'Seppi struzzo',status:'definitive'},r=>r.length===1&&r[0].id==='ostrich-bias');
check({query:'mimeticamente riflessiva'},r=>r.length===1&&r[0].id==='blind-spot');
check({query:'Wald salmone',status:'definitive'},r=>r.length===1&&r[0].id==='survivorship');
check({animal:'Asino',status:'archived'},r=>r.length===0);
check({query:'Sunstein elefante',status:'definitive'},r=>r.length===1&&r[0].id==='probability-neglect');
check({author:'Serge Moscovici',status:'definitive'},r=>r.length===2&&r.some(p=>p.id==='polarization')&&r.some(p=>p.id==='mental-social-representation'));
check({query:'framing serpente',status:'definitive'},r=>r.length===1&&r[0].id==='framing');
check({query:'Yantis pipistrello',status:'definitive'},r=>r.length===1&&r[0].id==='attentional-bias');
check({query:'Buehler pinguino',status:'definitive'},r=>r.length===1&&r[0].id==='planning-fallacy');
check({query:'Leibenstein pecore',status:'definitive'},r=>r.length===1&&r[0].id==='bandwagon');
check({query:'Kruger stambecco',status:'definitive'},r=>r.length===1&&r[0].id==='dunning-kruger');
check({query:'twaddle ape Munger',status:'definitive'},r=>r.length===1&&r[0].id==='twaddle-tendency');
check({query:'noise',animal:'Capibara',author:'Olivier Sibony'},r=>r.length===2);
check({query:'occasion noise capibara'},r=>r.length===1&&r[0].id==='occasion-noise');
check({query:'WYSIATI cavallo Kahneman'},r=>r.length===1&&r[0].id==='wysiati');
check({query:'Peltzman cinghiale'},r=>r.length===1&&r[0].id==='risk-compensation');
check({query:'convincentemente incompleta'},r=>r.length===1&&r[0].id==='wysiati');
check({query:'Festinger procione',status:'definitive'},r=>r.length===1&&r[0].id==='dissonance');
check({query:'lollapalooza Munger',status:'definitive'},r=>r.length===1&&r[0].id==='lollapalooza');
check({status:'review'},r=>r.length===0);
check({query:'Ramirezi'},r=>r.length===1&&r[0].id==='naive-realism');
assert(!posters.some(p=>p.id==='halo-ramirezi'||p.id==='sunk-cost-archive')); count++;
check({query:'naive Ward',animal:'Ramirezi',status:'definitive'},r=>r.length===1&&r[0].id==='naive-realism');
check({family:'Informazione',animal:'Pesce rosso',author:'Frank Keil'},r=>r.length===1&&r[0].id==='explanatory-depth');
check({query:'freezing Dugas',animal:'Ippopotamo'},r=>r.length===1&&r[0].id==='uncertainty-intolerance');
check({query:'apparentemente profondissima'},r=>r.length===1&&r[0].id==='explanatory-depth');
check({family:'Risposte di difesa',status:'definitive'},r=>r.length===5&&r.every(p=>p.approvalBatch===7));
check({query:'Kozlowska attacco',animal:'Toro'},r=>r.length===1&&r[0].id==='fight-response');
check({query:'flight antilope'},r=>r.length===1&&r[0].id==='flight-response');
check({family:'Risposte di difesa',query:'freeze cerbiatto'},r=>r.length===1&&r[0].id==='freeze-response');
check({query:'flop faint sovraccarico',animal:'Capra'},r=>r.length===1&&r[0].id==='flop-faint-response');
check({author:'Pete Walker',query:'accomodante',status:'definitive'},r=>r.length===1&&r[0].id==='fawn-response');
check({family:'Emozioni',status:'definitive'},r=>r.length===7&&r.every(p=>p.approvalBatch===8));
check({family:'Emozioni',author:'Paul Ekman'},r=>r.length===6&&r.every(p=>p.id.startsWith('emotion-')));
check({family:'Emozioni',query:'gioia luminosa',animal:'Cane'},r=>r.length===1&&r[0].id==='emotion-joy');
check({family:'Emozioni',query:'sadness malinconica',animal:'Koala'},r=>r.length===1&&r[0].id==='emotion-sadness');
check({family:'Emozioni',query:'fear allarmata',animal:'Lepre'},r=>r.length===1&&r[0].id==='emotion-fear');
check({family:'Emozioni',query:'anger infuocata',animal:'Tasso'},r=>r.length===1&&r[0].id==='emotion-anger');
check({family:'Emozioni',query:'surprise sospesa',animal:'Tarsio'},r=>r.length===1&&r[0].id==='emotion-surprise');
check({family:'Emozioni',query:'disgust schifata',animal:'Lama'},r=>r.length===1&&r[0].id==='emotion-disgust');
check({author:'Daniel Goleman',query:'contagio',animal:'Koala'},r=>r.length===1&&r[0].id==='emotional-contagion'&&r[0].animals.length===6);
check({family:'Relazione',animal:'Delfino',status:'definitive'},r=>r.length===1&&r[0].id==='mental-social-representation');
check({query:'rappresentazione Moscovici',animal:'Delfino'},r=>r.length===1&&r[0].id==='mental-social-representation');
check({query:'socialmente condivisa',author:'Philip N. Johnson-Laird'},r=>r.length===1&&r[0].id==='mental-social-representation');
check({family:'Gestione dello Stress',status:'definitive'},r=>r.length===8&&r.every(p=>p.approvalBatch===10||p.id==='mindfulness'));
check({family:'Gestione dello Stress',query:'problem focused',animal:'Lontra'},r=>r.length===1&&r[0].id==='problem-focused-coping');
check({family:'Gestione dello Stress',query:'planful',animal:'Corvo'},r=>r.length===1&&r[0].id==='planful-problem-solving');
check({family:'Gestione dello Stress',query:'social support',animal:'Formica'},r=>r.length===1&&r[0].id==='seeking-social-support');
check({family:'Gestione dello Stress',query:'positive reappraisal',animal:'Panda rosso'},r=>r.length===1&&r[0].id==='positive-reappraisal');
check({query:'prendere le distanze',animal:'Paguro'},r=>r.length===1&&r[0].id==='escape-avoidance');
check({family:'Gestione dello Stress',query:'emotion focused',animal:'Orso'},r=>r.length===1&&r[0].id==='emotion-focused-coping');
check({family:'Gestione dello Stress',author:'Susan Folkman'},r=>r.length===7);
assert.equal(posters.find(p=>p.id==='confirmation').description, 'Cerchiamo o interpretiamo informazioni in modo favorevole a un’ipotesi già presente. Le prove contrarie possono ricevere meno attenzione o essere reinterpretate in modo da non mettere in discussione l’ipotesi iniziale.'); count++;
check({family:'Informazione',animal:'Falco',author:'Don A. Moore',status:'definitive'},r=>r.length===1&&r[0].id==='overprecision');
check({query:'troppi decimali'},r=>r.length===1&&r[0].id==='overprecision');
check({family:'Identità',animal:'Topolino',author:'Julian B. Rotter'},r=>r.length===1&&r[0].id==='locus-of-control');
check({family:'Relazione',query:'secondo ordine',author:'Paul Watzlawick'},r=>r.length===1&&r[0].id==='reality-of-reality');
check({animal:'Topolino',status:'definitive'},r=>r.length===2&&r.every(p=>p.approvalBatch===12));
check({family:'Relazione',animal:'Rana',author:'Kenneth Savitsky',status:'definitive'},r=>r.length===1&&r[0].id==='illusion-of-transparency');
check({query:'apparentemente trasparente'},r=>r.length===1&&r[0].id==='illusion-of-transparency');
check({family:'L.I.M.I.T. Model',status:'definitive'},r=>r.length===6&&r.every(p=>p.approvalBatch===14&&p.authors.includes('Tommaso Corona')));
check({author:'Tommaso Corona'},r=>r.length===6);
check({query:'LIMIT Mentalizing',animal:'Polpo'},r=>r.some(p=>p.id==='limit-mentalizing'));
check({family:'L.I.M.I.T. Model',query:'Load',animal:'Mulo'},r=>r.some(p=>p.id==='limit-load'));
check({family:'L.I.M.I.T. Model',query:'Identity',animal:'Cervo'},r=>r.some(p=>p.id==='limit-identity'));
check({family:'L.I.M.I.T. Model',query:'Inhibition',animal:'Volpe'},r=>r.some(p=>p.id==='limit-inhibition'));
check({family:'L.I.M.I.T. Model',query:'Tension',animal:'Lince'},r=>r.some(p=>p.id==='limit-tension'));
check({family:'Relazione',animal:'Orso',author:'Jessica Benjamin'},r=>r.length===1&&r[0].id==='intersubjectivity');
check({query:'autenticamente intersoggettiva',author:'Daniel N. Stern'},r=>r.length===1&&r[0].id==='intersubjectivity');
check({family:'Informazione',animal:'Segugio',author:'Steven B. Most',status:'definitive'},r=>r.length===1&&r[0].id==='expectation-blindness');
check({query:'prevedibilmente distratta',animal:'Procione'},r=>r.length===1&&r[0].id==='expectation-blindness');
check({family:'Relazione',animal:'Dodo',author:'Saul Rosenzweig',status:'definitive'},r=>r.length===1&&r[0].id==='dodo-verdict');
check({query:'formalmente riuscita',animal:'Varano',author:'Bruce E. Wampold'},r=>r.length===1&&r[0].id==='dodo-verdict');
check({family:'Coscienza',status:'definitive'},r=>r.length===2&&r.every(p=>p.approvalBatch===18));
check({family:'Coscienza',animal:'Lemure',author:'Steven Laureys'},r=>r.length===1&&r[0].id==='state-of-consciousness');
check({query:'attentivamente situata',animal:'Suricato',author:'William James'},r=>r.length===1&&r[0].id==='field-of-consciousness');
check({query:'lucidamente variabile',author:'Amy F. T. Arnsten'},r=>r.length===1&&r[0].id==='state-of-consciousness');
check({family:'Memoria',animal:'Procione',author:'Gordon H. Bower',status:'definitive'},r=>r.length===1&&r[0].id==='mood-congruent-memory');
check({query:'emotivamente evocata',author:'Paul H. Blaney'},r=>r.length===1&&r[0].id==='mood-congruent-memory');
check({family:'Relazione',animal:'Elefante',author:'John D. Mayer',status:'definitive'},r=>r.length===1&&r[0].id==='empathy-emotional-intelligence');
check({query:'emotivamente sintonizzata',animal:'Volpe',author:'Jean Decety'},r=>r.length===1&&r[0].id==='empathy-emotional-intelligence');
check({family:'Informazione',animal:'Corvo',author:'Colin G. DeYoung',status:'definitive'},r=>r.length===1&&r[0].id==='apophenia');
check({query:'ironicamente interpretativa',author:'Jennifer A. Whitson'},r=>r.length===1&&r[0].id==='apophenia');
check({family:'Relazione',animal:'Elefante',author:'Daniel Goleman'},r=>r.length===1&&r[0].id==='empathy-emotional-intelligence');
const mindMembers=['intersubjectivity','expectation-blindness','dodo-verdict','state-of-consciousness','field-of-consciousness','mood-congruent-memory','empathy-emotional-intelligence','apophenia','intrinsic-motivation','extrinsic-motivation','paradoxical-stratagem','deindividuation','moral-disengagement-conduct','moral-disengagement-responsibility','moral-disengagement-consequences','moral-disengagement-victim','tall-poppy-syndrome','pareidolia','continuing-bonds','resilience'];
check({section:'Mente, esperienza e relazione'},r=>r.length===20&&r.every((p,i)=>p.id===mindMembers[i]));
check({section:'Mente, esperienza e relazione',family:'Coscienza'},r=>r.length===2);
check({section:'Mente, esperienza e relazione',family:'Memoria'},r=>r.length===1&&r[0].id==='mood-congruent-memory');
check({section:'Mente, esperienza e relazione',author:'Daniel Goleman'},r=>r.length===1&&r[0].id==='empathy-emotional-intelligence');
check({section:'Mente, esperienza e relazione',animal:'Corvo'},r=>r.length===1&&r[0].id==='apophenia');
check({section:'Mente, esperienza e relazione',query:'coccodrillo'},r=>r.length===0);
check({section:'Gestione dello Stress'},r=>r.length===8);
check({section:'Gestione dello Stress',author:'Jon Kabat-Zinn',query:'hic et nunc',animal:'Panda'},r=>r.length===1&&r[0].id==='mindfulness');
check({section:'L.I.M.I.T. Model'},r=>r.length===6);
check({section:'Bias cognitivi'},r=>r.length===56&&r.every(p=>p.order<=52||['overprecision','illusion-of-transparency','law-of-the-instrument'].includes(p.id)));
check({section:'Bias cognitivi',query:'truth',animal:'Coccodrillo'},r=>r.length===1&&r[0].id==='truth-bias');
check({section:'Bias cognitivi',author:'John D. Mayer'},r=>r.length===0);
check({section:'Bias cognitivi',family:'Coscienza'},r=>r.length===0);
check({section:'Mente, esperienza e relazione',family:'Motivazione',author:'Edward L. Deci',animal:'Cane'},r=>r.length===2&&r.every(p=>p.approvalBatch===21));
check({query:'felicemente autodeterminata',author:'Richard M. Ryan'},r=>r.length===1&&r[0].id==='intrinsic-motivation');
check({query:'dichiaratamente premiata',author:'Edward L. Deci'},r=>r.length===1&&r[0].id==='extrinsic-motivation');
check({section:'Bias cognitivi',family:'Motivazione'},r=>r.length===0);
check({section:'Bias cognitivi',query:'martello scimpanze',author:'Abraham H. Maslow'},r=>r.length===1&&r[0].id==='law-of-the-instrument');
check({family:'Decisione',author:'Abraham Kaplan',status:'definitive'},r=>r.length===1&&r[0].id==='law-of-the-instrument');
check({section:'Mente, esperienza e relazione',query:'paradossale Nardone',status:'definitive'},r=>r.length===1&&r[0].id==='paradoxical-stratagem');
check({family:'Psicologia strategica',author:'Giorgio Nardone'},r=>r.length===1&&r[0].references.length===3);
check({section:'Bias cognitivi',query:'stratagemma paradossale'},r=>r.length===0);
check({section:'Mente, esperienza e relazione',query:'deindividuazione Le Bon',animal:'Iena'},r=>r.length===1&&r[0].id==='deindividuation');
check({family:'Relazione',author:'Philip G. Zimbardo',query:'foulard'},r=>r.length===1&&r[0].authors.includes('Sigmund Freud'));
check({section:'Bias cognitivi',query:'deindividuazione'},r=>r.length===0);
check({family:'Disimpegno morale',author:'Albert Bandura',query:'giustificazione'},r=>r.length===1&&r[0].id==='moral-disengagement-conduct');
check({family:'Disimpegno morale',author:'Albert Bandura',query:'eseguito gli ordini'},r=>r.length===1&&r[0].id==='moral-disengagement-responsibility');
check({family:'Disimpegno morale',author:'Albert Bandura',query:'non è poi così grave'},r=>r.length===1&&r[0].id==='moral-disengagement-consequences');
check({family:'Disimpegno morale',author:'Albert Bandura',query:'microbo'},r=>r.length===1&&r[0].id==='moral-disengagement-victim');
check({section:'Mente, esperienza e relazione',family:'Disimpegno morale'},r=>r.length===4&&r.every(p=>p.approvalBatch===25));
check({section:'Bias cognitivi',family:'Disimpegno morale'},r=>r.length===0);
check({section:'Persuasione',author:'Robert B. Cialdini'},r=>r.length===8&&r.every(p=>p.status==='definitive'&&p.bookTitle==='Psiche & Thanatos'&&p.bookUrl==='https://www.amazon.it/dp/B0DVCC1HY6'));
check({section:'Persuasione',query:'scarsita francobollo',animal:'Pinguino'},r=>r.length===1&&r[0].id==='persuasion-scarcity');
check({section:'Persuasione',query:'richiesta dura'},r=>r.length===1&&r[0].id==='persuasion-contrast');
check({section:'Persuasione',query:'uno di noi'},r=>r.length===1&&r[0].id==='persuasion-unity');
check({section:'Persuasione',author:'Robert B. Zajonc',animal:'Camaleonte',query:'mera esposizione'},r=>r.length===1&&r[0].id==='persuasion-mere-exposure');
check({section:'Tratti di personalità (OCEAN)'},r=>r.length===6&&r.every(p=>p.id.startsWith('ocean-')&&p.status==='definitive'&&p.bookUrl==='https://www.amazon.it/dp/B0DVCC1HY6'));
check({section:'Tratti di personalità (OCEAN)',author:'Paul T. Costa Jr.',animal:'Quokka'},r=>r.length===2&&r.some(p=>p.id==='ocean-agreeableness')&&r.some(p=>p.id==='ocean-big-five'));
check({section:'Tratti di personalità (OCEAN)',author:'Robert R. McCrae',query:'meticolosamente pianificata'},r=>r.length===1&&r[0].id==='ocean-conscientiousness');
check({section:'Tratti di personalità (OCEAN)',animal:'Pangolino',query:'prudentemente preoccupata'},r=>r.length===1&&r[0].id==='ocean-neuroticism');
check({section:'Bias cognitivi',author:'Paul T. Costa Jr.'},r=>r.length===0);
check({query:'Psiche Thanatos'},r=>r.length===32&&r.every(p=>p.bookUrl==='https://www.amazon.it/dp/B0DVCC1HY6'));
const strategicIds=['strategic-double-bind',...Array.from({length:5},(_,i)=>'communication-axiom-'+(i+1)),'strategic-feedback'];
check({section:'Psicologia Strategica'},r=>r.length===7&&r.every((p,i)=>p.id===strategicIds[i]&&p.status==='definitive'&&p.order===118+i&&!p.bookTitle));
check({section:'Psicologia Strategica',author:'Janet Helmick Beavin'},r=>r.length===7);
check({section:'Psicologia Strategica',author:'Norbert Wiener'},r=>r.length===1&&r[0].id==='strategic-feedback');
check({section:'Psicologia Strategica',author:'Gregory Bateson'},r=>r.length===1&&r[0].id==='strategic-double-bind');
check({section:'Psicologia Strategica',animal:'Cucciolo'},r=>r.length===7);
check({section:'Psicologia Strategica',query:'terzo assioma scappo'},r=>r.length===1&&r[0].id==='communication-axiom-3');
check({section:'Psicologia Strategica',query:'spaventosamente discordante'},r=>r.length===1&&r[0].id==='communication-axiom-4');
check({section:'Psicologia Strategica',animal:'Lupo mannaro',query:'equilibrata'},r=>r.length===1&&r[0].id==='strategic-feedback');
check({section:'Psicologia Strategica',query:'Psiche Thanatos'},r=>r.length===0);
assert(posters.find(p=>p.id==='strategic-double-bind').description.includes('da solo non esaurisce'));count++;
assert(posters.find(p=>p.id==='communication-axiom-4').description.includes('non verbali'));count++;
assert(posters.find(p=>p.id==='strategic-feedback').description.includes('verso della correzione'));count++;
check({section:'Mente, esperienza e relazione',query:'continuing bonds',animal:'Cane',author:'Dennis Klass'},r=>r.length===1&&r[0].id==='continuing-bonds'&&r[0].status==='definitive'&&!r[0].bookTitle&&!r[0].bookUrl);
check({query:'affettuosamente ricordata'},r=>r.length===1&&r[0].id==='continuing-bonds');
check({section:'Bias cognitivi',query:'continuing bonds'},r=>r.length===0);
check({section:'Mente, esperienza e relazione',query:'resilience',animal:'Pettirosso',author:'Ann S. Masten'},r=>r.length===1&&r[0].id==='resilience'&&r[0].bookUrl==='https://www.amazon.it/dp/B0DVCC1HY6');
check({query:'nonostante tutto ancora in cammino'},r=>r.length===1&&r[0].id==='resilience');
check({section:'Gestione dello Stress',query:'resilience'},r=>r.length===0);
check({family:'Costruttivismo'},r=>r.length===0);
check({query:'costruttivismo radicale'},r=>r.length===0);
check({query:'costruttivismo critico'},r=>r.length===0);
assert(!posters.some(p=>['radical-constructivism','critical-constructivism'].includes(p.id)));count++;
console.log(`${count} controlli superati: ricerca, filtri combinati, stati, ordinamento, contenuti e risorse.`);
