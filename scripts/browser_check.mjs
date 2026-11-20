// Real Chromium verification, with an isolated temporary browser profile.
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {Browser,sleep} from '../.agents/skills/design-taste-frontend/scripts/lib/cdp.mjs';
import {probe,app as appProbe} from '../.agents/skills/design-taste-frontend/scripts/lib/probe.mjs';
import {judgeApp} from '../.agents/skills/design-taste-frontend/scripts/lib/rules.mjs';
const config=JSON.parse(readFileSync('.runtime/lab.json','utf8'));
const output='docs/evidence/ui';mkdirSync(output,{recursive:true});
const browser=await Browser.launch({extraArgs:['--ignore-certificate-errors']});
const page=await browser.newPage();
const results=[];
const findings=[];
async function wait(expression){for(let i=0;i<100;i++){if(await page.eval(expression))return;await sleep(100);}throw Error('Timeout: '+expression);}
async function login(username,password){await page.goto('https://localhost:8443/login',{settleMs:200});await page.eval(({username,password})=>{document.querySelector('[name=username]').value=username;document.querySelector('[name=password]').value=password;document.querySelector('#login-form').requestSubmit();},{username,password});await wait("location.pathname !== '/login' && document.querySelector('#screen')?.getAttribute('aria-busy') !== 'true'");}
try{
 await login(config.demo_username,config.demo_password);results.push('parent UI login');
 await page.eval(()=>document.querySelector('[data-action=add-child]').click());
 await page.eval(()=>{document.querySelector('#new-child input').value='An · hồ sơ demo';document.querySelector('#new-child').requestSubmit();});
 await wait("location.pathname === '/app/devices' && document.querySelector('#screen')?.getAttribute('aria-busy') !== 'true'");
 const child=await page.eval(()=>document.body.dataset.child);results.push('create child through form');
 const enrollment=await page.eval(async child=>{const csrf=sessionStorage.getItem('ks-csrf'),headers={'Content-Type':'application/json','X-CSRF-Token':csrf};const p=await fetch('/api/children/'+child+'/policy').then(r=>r.json());p.policy.weekday_quota_sec=180;p.policy.weekend_quota_sec=180;let r=await fetch('/api/children/'+child+'/policy',{method:'PUT',headers,body:JSON.stringify(p.policy)});if(!r.ok)throw Error('policy '+r.status);const code=await fetch('/api/children/'+child+'/enroll-codes',{method:'POST',headers,body:'{"consent":true}'}).then(r=>r.json());r=await fetch('/api/device/enroll',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:code.code,fingerprint:crypto.randomUUID(),name:'Máy demo giao thức'})});if(!r.ok)throw Error('enroll '+r.status);return r.json();},child);
 await page.eval(async e=>{const r=await fetch('/api/device/heartbeat',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+e.access_token},body:JSON.stringify({device_id:e.device_id,status:'active',quota_used_sec:120,policy_version:e.policy.payload.version,usage_date:new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Ho_Chi_Minh',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())})});if(!r.ok)throw Error('heartbeat '+r.status);},enrollment);
 for(const view of ['overview','time','apps','web','requests','reports','privacy']){
   await page.goto('https://localhost:8443/app/'+view+'?child='+child,{settleMs:200});await wait("document.querySelector('#screen')?.getAttribute('aria-busy') !== 'true'");
   if(await page.eval(()=>document.querySelector('#notice')?.classList.contains('error')))throw Error('View error '+view);
   results.push('render '+view);
 }
 await page.goto('https://localhost:8443/app/time?child='+child,{settleMs:100});await wait("!!document.querySelector('#schedule')");await page.eval(()=>{document.querySelector('[data-day="0"][data-slot="0"]').click();document.querySelector('[data-action="save-schedule"]').click();});await wait("document.querySelector('#notice')?.textContent.includes('Đã lưu')");results.push('edit and save 7x48 schedule');
 const executableHash=createHash('sha256').update(readFileSync('C:/Windows/System32/notepad.exe')).digest('hex');
 await page.goto('https://localhost:8443/app/apps?child='+child,{settleMs:100});await wait("!!document.querySelector('#apps-form')");await page.eval(hash=>{document.querySelector('[name=rules]').value='notepad.exe, '+hash;document.querySelector('#apps-form').requestSubmit();},executableHash);await wait("document.querySelector('#notice')?.textContent.includes('Đã lưu')");results.push('save app rule with actual executable SHA256');
 // Exercise a saved policy form, and HTMX navigation rather than only direct URLs.
 await page.goto('https://localhost:8443/app/web?child='+child,{settleMs:200});await wait("!!document.querySelector('#web-form')");await page.eval(()=>document.querySelector('#web-form').requestSubmit());await wait("document.querySelector('#notice')?.textContent.includes('Đã lưu')");results.push('save web policy form');
 await page.eval(()=>document.querySelector('nav a[href*="/app/overview"]').click());await wait("location.pathname==='/app/overview' && document.body.dataset.view==='overview' && !!document.querySelector('.metrics')");results.push('HTMX navigation and state reload');
 for(const width of [1440,768,390]){await page.setViewport({width,height:960});await sleep(150);const overflow=await page.eval(()=>document.documentElement.scrollWidth>innerWidth);if(overflow)throw Error('Parent overflow '+width);findings.push(...judgeApp(await page.eval(appProbe),await page.eval(probe),{width}));await page.screenshot({path:`${output}/parent-${width}.png`,format:'png',fullPage:true});}
 const childCredentials={username:'child-'+Date.now(),password:'Demo-'+crypto.randomUUID()};
 await page.eval(async ({child,credentials})=>{const r=await fetch('/api/children/'+child+'/account',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':sessionStorage.getItem('ks-csrf')},body:JSON.stringify(credentials)});if(!r.ok)throw Error('account '+r.status);}, {child,credentials:childCredentials});
 await page.eval(()=>document.querySelector('[data-action=logout]').click());await wait("location.pathname==='/login'");await login(childCredentials.username,childCredentials.password);results.push('child isolated account login');
 await page.eval(()=>document.querySelector('[data-action=child-request]').click());await wait("document.querySelector('#notice')?.textContent.includes('Đã gửi')");results.push('child request extra time');
 const denial=await page.eval(async()=>{const r=await fetch('/api/children',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':sessionStorage.getItem('ks-csrf')},body:'{"name":"Forbidden"}'});return r.status;});if(denial!==403)throw Error('Child mutated parent API');results.push('child cannot mutate parent API');
 await page.eval(()=>document.querySelector('[data-action=logout]').click());await wait("location.pathname==='/login'");await login(config.demo_username,config.demo_password);
 await page.goto('https://localhost:8443/app/requests?child='+child,{settleMs:100});await wait("!!document.querySelector('[data-request]')");await page.eval(()=>document.querySelector('[data-request]').click());await wait("document.querySelector('#notice')?.textContent.includes('Đã gửi')");results.push('parent approve +15 and show pending device ACK');
 await page.eval(async e=>{const headers={'Content-Type':'application/json',Authorization:'Bearer '+e.access_token};const hb=await fetch('/api/device/heartbeat',{method:'POST',headers,body:JSON.stringify({device_id:e.device_id,status:'active',quota_used_sec:120,policy_version:e.policy.payload.version,usage_date:new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Ho_Chi_Minh',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())})}).then(r=>r.json());for(const c of hb.commands){const r=await fetch('/api/device/commands/'+c.payload.id+'/ack',{method:'POST',headers,body:'{}'});if(!r.ok)throw Error('ACK '+r.status);}},enrollment);results.push('protocol ACK for parent approval');
 await page.eval(()=>document.querySelector('[data-action=logout]').click());await wait("location.pathname==='/login'");await login(childCredentials.username,childCredentials.password);await wait("document.querySelector('.time-number')?.textContent==='16 phút'");results.push('child remaining includes acknowledged grant only');
 for(const width of [1440,768,390]){await page.setViewport({width,height:960});await sleep(100);if(await page.eval(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Child overflow '+width);await page.screenshot({path:`${output}/child-${width}.png`,format:'png',fullPage:true});}
 if(page.consoleErrors.length)throw Error('Browser errors: '+page.consoleErrors.join('\n'));
 writeFileSync(output+'/browser-result.json',JSON.stringify({passed:true,checks:results,childId:child,note:'Synthetic demo data from browser protocol requests, not Windows enforcement evidence.'},null,2));
 writeFileSync(output+'/app-inspection.json',JSON.stringify(findings,null,2));
 console.log('PASS: '+results.length+' browser checks; screenshots at1440/768/390.');
}finally{await browser.close();}
