const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../webfrontend/htmlauth/app.js'),'utf8').split('/* PLX_COPY_HELPERS_START */')[1].split('/* PLX_COPY_HELPERS_END */')[0];
const copy=new Function(source+'; return PLXCopy;')();
const rows=[{vehicle:'car_a',topic:'custom/car_a/left',label:'Reifendruck links',value:2.4,unit:'bar',recognition:'MQTT:\\icustom/car_a/left=\\i\\v'},
{vehicle:'car_a',topic:'custom/car_a/text',label:'Tür Zustand',value:'STANDBY',unit:'',recognition:null},
{vehicle:'car_b',topic:'custom/car_b/right',label:'Reifendruck rechts',value:null,unit:'bar',recognition:'MQTT:\\icustom/car_b/right=\\i\\v'}];
test('vehicle and full text filter supports translated labels, values and accents',()=>{
 assert.deepEqual(copy.filter(rows,'','car_b'),[rows[2]]);
 assert.deepEqual(copy.filter(rows,'pressure 2.4','',s=>s.replace('Reifendruck','pressure')),[rows[0]]);
 assert.deepEqual(copy.filter(rows,'tur','car_a'),[rows[1]]);
 assert.deepEqual(copy.filter(rows,'custom/car_a left',''),[rows[0]]);
});
test('bulk copy uses visible selected rows, literal recognitions and one entry per line',()=>{
 const selected=new Set(rows.map(r=>r.topic));const visible=copy.filter(rows,'','car_a');
 assert.equal(copy.lines(visible,selected,'topic').text,'custom/car_a/left\ncustom/car_a/text');
 assert.deepEqual(copy.lines(visible,selected,'recognition'),{text:rows[0].recognition,skipped:1});
 assert.equal(copy.lines(rows,new Set(),'topic').text,'');
});
test('clipboard success, rejection and missing API report whether manual fallback is needed',async()=>{
 let actual;assert.equal(await copy.write(rows[0].recognition,{writeText:async t=>actual=t}),true);assert.equal(actual,rows[0].recognition);
 assert.equal(await copy.write('topic',undefined),false);
 assert.equal(await copy.write('topic',{writeText:async()=>{throw Error('denied')}}),false);
});

test('mapping refresh clears old manual bulk copy before a failed reload',async()=>{
 const script=fs.readFileSync(path.join(__dirname,'../webfrontend/htmlauth/app.js'),'utf8');
 const refresh=script.slice(script.indexOf('  async function refreshCopyRows('),script.indexOf("  $('#copy-bulk-text').addEventListener"));
 const elements={
  '#loxone':{classList:{contains:()=>true}},
  '#copy-bulk-text':{value:'MQTT:\\iold/car/value=\\i\\v'},
  '#copy-bulk-plain':{open:true},
  '#copy-feedback':{textContent:'Kopiert'},
  '#copy-rows':{replaceChildren:()=>{}},
 };
 const state={config:{mqtt:{prefix:'new_prefix'},mqtt_format:'simple',vehicles:[{alias:'new_car'}],publish_fields:['soc'],publish_parameters:[]},snapshots:{}};
 let rejectReload,requested=false;
 const api=()=>{requested=true;return new Promise((_,reject)=>rejectReload=reject);};
 const run=new Function('state','$','api','node','copyCount',
  "let copyKey='old_mapping',copyGeneration=0,copyRows=['old'];"+refresh+';return refreshCopyRows;')
  (state,id=>elements[id],api,()=>({}),()=>{});
 const pending=run();
 assert.equal(requested,true);
 assert.equal(elements['#copy-bulk-text'].value,'');
 assert.equal(elements['#copy-bulk-plain'].open,false);
 assert.equal(elements['#copy-feedback'].textContent,'');
 rejectReload(new Error('Reload failed'));await pending;
 assert.equal(elements['#copy-bulk-text'].value,'');
 assert.equal(elements['#copy-bulk-plain'].open,false);
 assert.equal(elements['#copy-feedback'].textContent,'Reload failed');
});

test('diagnostic bulk selection respects vehicle and global heartbeat filters',()=>{
 const diagnostics=[{vehicle:'car_a',group:'diagnostic',topic:'plx/car_a/data_valid',label:'Datenfreigabe',value:0,recognition:'MQTT:\\iplx/car_a/data_valid=\\i\\v'},
 {vehicle:'',group:'diagnostic',topic:'plx/heartbeat',label:'PLX Heartbeat',value:null,recognition:'MQTT:\\iplx/heartbeat=\\i\\v'}];
 const all=[...rows,...diagnostics],selected=new Set(all.map(r=>r.topic));
 assert.deepEqual(copy.filter(all,'','__global__',x=>x,'diagnostic'),[diagnostics[1]]);
 assert.deepEqual(copy.filter(all,'','car_a',x=>x,'diagnostic'),[diagnostics[0]]);
 assert.equal(copy.lines(copy.filter(all,'','',x=>x,'diagnostic'),selected,'topic').text,'plx/car_a/data_valid\nplx/heartbeat');
 assert.equal(copy.lines(copy.filter(all,'','__global__',x=>x,'diagnostic'),selected,'recognition').text,diagnostics[1].recognition);
});

test('copy filters and language event are safe before initial status loads',()=>{
 const script=fs.readFileSync(path.join(__dirname,'../webfrontend/htmlauth/app.js'),'utf8');
 const render=script.slice(script.indexOf('  function renderCopyRows() {'),script.indexOf('  async function refreshCopyRows('));
 for(const state of [null,undefined]){
  const run=new Function('state','$',render+';return renderCopyRows;')(state,()=>{throw Error('DOM must not be accessed before status');});
  assert.doesNotThrow(()=>run());
 }
});
