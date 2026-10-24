/* UI-only demo and browser checks. No real Porsche account or session is used. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium} = require('/Users/dlanzenb/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const now = Math.floor(Date.now()/1000);
const demo = {
  config:{enabled:true,interval_s:900,max_age_s:3600,vehicles:[{vin:'WP0ZZZY1ZLSA12345',alias:'taycan'}],mqtt:{enabled:true,host:'127.0.0.1',port:1883,username:'loxberry',password_set:true,prefix:'porsche2lox',tls:false}},
  login:{state:'authenticated'},job:{state:'ok',message:'Vorschaudaten · Oberfläche mit einem simulierten Fahrzeug.'},busy:false,vehicles:[{vin:'WP0ZZZY1ZLSA12345',name:'Taycan'}],mqtt_ok:true,next_poll_epoch:now+600,auth_blocked:false,
  snapshots:{taycan:{soc:61,range_km:248,target_soc:80,direct_charge_enabled:0,data_valid:1,data_age_s:240,last_fetch_epoch:now-30}}
};
let lastRequest;
const server = http.createServer((req,res) => {
  if (req.url.includes('?api=')) {
    let body=''; req.on('data', chunk=>body+=chunk); req.on('end',()=>{
      lastRequest=JSON.parse(body);
      if(lastRequest.action==='save') {demo.config=lastRequest.params; demo.config.mqtt.password_set=true; delete demo.config.mqtt.password;}
      if(lastRequest.action==='login') demo.login={state:'captcha',image:'data:image/svg+xml;base64,'+Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="250" height="80"><rect width="250" height="80" fill="#eee"/><text x="30" y="52" font-size="32">TEST 42</text></svg>').toString('base64')};
      res.setHeader('Content-Type','application/json'); res.end(JSON.stringify({ok:true,data:demo}));
    });return;
  }
  if(req.url==='/app.css'||req.url==='/app.js') {res.setHeader('Content-Type',req.url.endsWith('css')?'text/css':'text/javascript');res.end(fs.readFileSync(path.join(root,'webfrontend/htmlauth',req.url.slice(1))));return;}
  res.setHeader('Content-Type','text/html; charset=utf-8');res.end('<!doctype html><html lang="de"><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>PLX Vorschau</title></head><body style="margin:0;background:#fff">'+fs.readFileSync(path.join(root,'templates/dashboard.html'),'utf8').replace('<?= $csrf ?>','demo-csrf')+'</body></html>');
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
  const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  try{
    await page.goto(`http://127.0.0.1:${server.address().port}/index.php`);
    await page.getByText('248 km',{exact:true}).waitFor();
    fs.mkdirSync(path.join(root,'docs/preview'),{recursive:true});
    await page.screenshot({path:path.join(root,'docs/preview/desktop.png'),fullPage:true});
    await page.getByRole('button',{name:'Einrichtung',exact:true}).click();
    await page.locator('[name="host"]').fill('test-broker');
    await page.waitForTimeout(3300);
    if(await page.locator('[name="host"]').inputValue()!=='test-broker')throw Error('Unsaved form overwritten by polling');
    await page.getByRole('button',{name:'Einstellungen speichern'}).click();
    await page.waitForTimeout(100);
    if(lastRequest.params?.mqtt?.host!=='test-broker')throw Error('Configuration not sent');
    await page.screenshot({path:path.join(root,'docs/preview/settings.png'),fullPage:true});
    await page.getByRole('button',{name:'Porsche-Konto',exact:true}).click();
    await page.locator('[name="email"]').fill('demo@example.com');
    await page.locator('[name="password"]').fill('demo-only');
    await page.getByRole('button',{name:'Bei Porsche anmelden',exact:true}).click();
    await page.locator('#captcha-form').waitFor({state:'visible'});
    if(await page.locator('[name="password"]').inputValue()!=='')throw Error('Password not cleared');
    await page.screenshot({path:path.join(root,'docs/preview/login.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    await page.getByRole('button',{name:'Übersicht',exact:true}).click();
    await page.screenshot({path:path.join(root,'docs/preview/mobile.png'),fullPage:true});
    if(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth))throw Error('Mobile horizontal overflow');
    if(errors.length)throw Error(errors.join('\n'));
    console.log('Browser checks passed: desktop/mobile, form preservation, save, CAPTCHA display, password clearing.');
  }finally{await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;server.close();});
