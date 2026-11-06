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
