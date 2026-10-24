/* UI-only demo and browser checks. No real Porsche account or session is used. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium} = require('playwright');
const root = path.resolve(__dirname,'..');
const output=process.env.PLX_TEST_OUTPUT||require('node:os').tmpdir();
const now = Math.floor(Date.now()/1000);
const demo = {
  config:{enabled:true,interval_s:900,max_age_s:3600,vehicles:[{vin:'WP0ZZZY1ZLSA12345',alias:'taycan'}],mqtt:{enabled:true,host:'127.0.0.1',port:1883,username:'loxberry',password_set:true,prefix:'porsche2lox',tls:false}},
  login:{state:'authenticated'},job:{state:'ok',message:'Vorschaudaten · Oberfläche mit einem simulierten Fahrzeug.'},busy:false,vehicles:[{vin:'WP0ZZZY1ZLSA12345',name:'Taycan'}],mqtt_ok:true,next_poll_epoch:now+600,auth_blocked:false,
  snapshots:{taycan:{soc:61,range_km:248,target_soc:80,direct_charge_enabled:0,data_valid:1,data_age_s:240,last_fetch_epoch:now-30}}
};

const keys=['TIRE_PRESSURE_FRONT_LEFT','TIRE_PRESSURE_FRONT_RIGHT'];
Object.assign(demo.config,{mqtt_format:'simple',publish_fields:[],publish_parameters:keys});
demo.parameter_catalog=[...keys,'TRIP_STATISTICS_CYCLIC_HISTORY'].map(key=>({key,label:key===keys[0]?'Reifendruck vorne links':key===keys[1]?'Reifendruck vorne rechts':'Fahrthistorie',group:'Fahrzeug'}));
let lastRequest;
const server=http.createServer((req,res)=>{
 const name=req.url.split('?')[0];
 if(name==='/login'){const html=require('node:child_process').execFileSync(process.env.PYTHON||'python3',['-c',"from porsche2lox.standalone import Handler; from types import SimpleNamespace; Handler.login_page(SimpleNamespace(respond=lambda code,html,**kwargs: print(html)))"],{env:{...process.env,PYTHONPATH:path.join(root,'bin')}});res.setHeader('Content-Type','text/html;charset=utf-8');res.end(html);return;}
 if(req.url.includes('?api=')){let body='';req.on('data',c=>body+=c);req.on('end',()=>{lastRequest=JSON.parse(body);if(lastRequest.action==='save')demo.config={...lastRequest.params,mqtt:{...lastRequest.params.mqtt,password_set:true}};res.setHeader('Content-Type','application/json');res.end(JSON.stringify({ok:true,data:demo}));});return;}
 if(['/app.css','/app.js','/logo.svg'].includes(name)){res.setHeader('Content-Type',name.endsWith('css')?'text/css':name.endsWith('js')?'text/javascript':'image/svg+xml');res.end(fs.readFileSync(path.join(root,'webfrontend/htmlauth',name.slice(1))));return;}
 res.setHeader('Content-Type','text/html;charset=utf-8');res.end('<html><meta name="viewport" content="width=device-width,initial-scale=1"><body>'+fs.readFileSync(path.join(root,'templates/dashboard.html'),'utf8').replace('<?= $csrf ?>','demo-csrf')+'</body></html>');
});
demo.job.message='Fahrzeugliste aktualisiert.';
demo.snapshots.taycan.parameters=Object.fromEntries(keys.map((key,i)=>[key,{key,label:demo.parameter_catalog[i].label,group:'Fahrzeug & Sicherheit',available:1,data_valid:1,age_known:1,data_age_s:240,value:{actualPressureBar:2.4+i/10}}]));
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});try{
const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.route('https://plx.test/**',async route=>{const req=route.request(),u=new URL(req.url());const response=await fetch(`http://127.0.0.1:${server.address().port}${u.pathname}${u.search}`,{method:req.method(),body:req.method()==='POST'?req.postData():undefined,headers:req.headers()});await route.fulfill({status:response.status,headers:Object.fromEntries(response.headers),body:Buffer.from(await response.arrayBuffer())});});await page.goto('https://plx.test/');
await page.getByRole('button',{name:'EN',exact:true}).click();await page.getByRole('button',{name:'Setup',exact:true}).click();await page.locator('[name=host]').fill('draft-broker');
await page.getByRole('button',{name:'DE',exact:true}).click();if(await page.locator('[name=host]').inputValue()!=='draft-broker')throw Error('Draft lost');
await page.getByRole('button',{name:'EN',exact:true}).click();await page.getByRole('button',{name:'Vehicle data',exact:true}).click();await page.locator('#parameter-search').fill('tire pressure');await page.waitForTimeout(300);if(!await page.locator('#parameter-results').innerText().then(x=>x==='2 of 2 parameters'))throw Error('English search/count failed');
await page.screenshot({path:output+'/plx-english-desktop.png',fullPage:true});
await page.getByRole('button',{name:'Loxone',exact:true}).click();if(await page.locator('#publish-options input:checked').count()!==2)throw Error('Selection changed');
await page.reload();await page.getByRole('button',{name:'Overview',exact:true}).waitFor();await page.waitForTimeout(3300);if(!await page.locator('#connect-status').innerText().then(x=>x==='Porsche Connect connected'))throw Error('Polling not translated');
await page.setViewportSize({width:390,height:844});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');await page.screenshot({path:output+'/plx-english-mobile.png',fullPage:true});
await page.getByRole('button',{name:'DE',exact:true}).click();await page.getByRole('button',{name:'Übersicht',exact:true}).waitFor();if(await page.locator('#connect-status').innerText()!=='Porsche Connect verbunden')throw Error('German restore failed');
await page.goto(`http://127.0.0.1:${server.address().port}/login`);await page.getByRole('button',{name:'EN',exact:true}).click();await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();await page.reload();await page.getByRole('button',{name:'Sign in',exact:true}).waitFor();await page.getByRole('button',{name:'DE',exact:true}).click();await page.getByRole('button',{name:'Anmelden',exact:true}).waitFor();
await page.goto(`http://127.0.0.1:${server.address().port}/`);
await page.locator('.transport-warning').waitFor();
if(!await page.locator('#login-form [name=password]').isDisabled())throw Error('HTTP password field enabled');
const unsafe=[];page.on('request',r=>{if(r.method()==='POST'&&r.url().includes('?api=')){const a=JSON.parse(r.postData()).action;if(['login','captcha','save'].includes(a))unsafe.push(a);}});
for(const id of ['login-form','captcha-form','settings-form'])await page.locator('#'+id).evaluate(f=>f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));
await page.waitForTimeout(300);if(unsafe.length)throw Error('Secret-bearing HTTP request sent: '+unsafe.join(','));
if(errors.length)throw Error(errors.join(';'));console.log('PASS: DE/EN persistence, English search/status polling, two MQTT selections preserved, unsaved draft preserved, mobile no overflow, no JS errors');
}finally{await browser.close();server.close();}})().catch(e=>{console.error(e);process.exitCode=1;server.close();});
