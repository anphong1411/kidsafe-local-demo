// Isolated synthetic profile only; never use this fixture setup on user data.
import assert from 'node:assert/strict';
import {readFileSync, mkdirSync, writeFileSync} from 'node:fs';
import {Browser, sleep} from '../.agents/skills/design-taste-frontend/scripts/lib/cdp.mjs';

const phase = process.argv[2] || 'after';
assert.ok(['before','after'].includes(phase));
const out = `${process.env.KIDSAFE_UI_EVIDENCE || "docs/evidence/current-ui"}/${phase}`;
mkdirSync(out, {recursive:true});
const config = JSON.parse(readFileSync('.tmp/ui-review/runtime/lab.json','utf8'));
assert.ok(config.KIDSAFE_DATABASE_URL.endsWith('/.tmp/ui-review/runtime/kidsafe.db'));
const browser = await Browser.launch({extraArgs:['--ignore-certificate-errors']});
const page = await browser.newPage();
const root = 'https://localhost:8447';
async function wait(expression) {
  for (let n=0;n<120;n++) {if(await page.eval(expression))return; await sleep(100);}
  throw Error(`Timeout: ${expression}`);
}
try {
  await page.goto(root+'/login',{settleMs:50});
  await page.eval(async c=>{
    const login=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:c.demo_username,password:c.demo_password})});
    if(!login.ok)throw Error('login '+login.status);
    const {csrf_token}=await login.json();sessionStorage.setItem('ks-csrf',csrf_token);
    const headers={'Content-Type':'application/json','X-CSRF-Token':csrf_token};
    const api=async(path,body,extra={})=>{const r=await fetch('/api/'+path,{method:body===undefined?'GET':'POST',headers:{...headers,...extra},...(body===undefined?{}:{body:JSON.stringify(body)})});if(!r.ok)throw Error(path+' '+r.status);return r.json();};
    let children=await api('children');
    if(children.length)return;
    const child=await api('children',{name:'An Phong · hồ sơ kiểm thử'});
    for(let i=0;i<2;i++){
      const code=await api(`children/${child.id}/enroll-codes`,{consent:true});
      const d=await api('device/enroll',{code:code.code,fingerprint:crypto.randomUUID(),name:i?'Laptop học tập của An Phong':'Máy tính để bàn của An Phong'});
      const auth={Authorization:'Bearer '+d.access_token};
      if(!i)await api('device/heartbeat',{device_id:d.device_id,status:'active',quota_used_sec:2700,policy_version:1,usage_date:new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Ho_Chi_Minh',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())},auth);
      const ts=new Date().toISOString();
      const event=type=>({ts,device_id:d.device_id,child_id:child.id,type,subject:type==='app_stop'?'notepad.exe':type==='unlock_request'?'more_time':'example.org',duration_sec:type==='app_stop'?1200:0,policy_id:d.policy.payload.policy_id});
      await api('device/events',{events:[event('app_stop'),event('unlock_request'),event('blocked_domain')]},{...auth,'Idempotency-Key':crypto.randomUUID()});
    }
    await api(`children/${child.id}/account`,{username:'child-review',password:'ChildReview-2026'});
  }, config);
  const children=await page.eval(async()=>fetch('/api/children').then(r=>r.json()));
  const child=children[0].id;
  const measurements=[];
  const typographyFailures=[];
  for(const view of ['overview','time','apps','web','requests','devices','quick-control','reports','privacy','child','login']) {
    await page.setViewport({width:1440,height:1000});
    await page.goto(root+(view==='child'?'/child?child='+child:view==='login'?'/login':`/app/${view}?child=${child}`),{settleMs:60});
    if(view!=='login') {
      await wait("!!document.querySelector('#screen')&&document.querySelector('#screen').getAttribute('aria-busy')!=='true'");
      assert.ok(await page.eval(()=>!document.querySelector('#screen [data-action=refresh]')), `${view} loaded without an API error`);
    }
    for(const width of [1440,1280,1024,768,390,360]) {
      await page.setViewport({width,height:1000});await sleep(45);
      const m=await page.eval(()=>{
        const visible=e=>!!e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';
        const small=[...document.querySelectorAll('body *')].filter(e=>visible(e)&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&parseFloat(getComputedStyle(e).fontSize)<14).map(e=>({tag:e.tagName,text:e.textContent.trim().slice(0,80),size:getComputedStyle(e).fontSize}));
        const headings=[...document.querySelectorAll('h1,h2,h3')].filter(visible).map(e=>({text:e.textContent,size:getComputedStyle(e).fontSize,lines:Math.round(e.getBoundingClientRect().height/parseFloat(getComputedStyle(e).lineHeight))}));
        const account=document.querySelector('.account-name')||document.querySelector('.sidebar-foot>span');
        const kpiFooters=[...document.querySelectorAll('.metrics .metric-bottom')].map(e=>{const r=e.getBoundingClientRect();return r.top+r.height/2;});
        const controls=[...document.querySelectorAll('.quick-action-card')].map(e=>e.getBoundingClientRect().height);
        const inputs=[...document.querySelectorAll('.quota-grid input')].map(e=>e.getBoundingClientRect().top);
        const scope=document.querySelector('.scope-label');
        const scopeLines=scope?scope.getBoundingClientRect().height/parseFloat(getComputedStyle(scope).lineHeight):0;
        const kpiHeights=[...document.querySelectorAll('.metrics .metric')].map(e=>e.getBoundingClientRect().height);
        const marks=[...document.querySelectorAll('.schedule-hour')];
        const scheduleAlignment=marks.map(mark=>{
          const slot=Number(mark.dataset.mark);
          const markRect=mark.getBoundingClientRect();
          return Math.max(...Array.from({length:7},(_,day)=>{
            const cell=document.querySelector(`[data-day="${day}"][data-slot="${Math.min(slot,47)}"]`).getBoundingClientRect();
            return Math.abs(slot===48 ? cell.right-markRect.right : cell.left-markRect.left);
          }));
        });
        const scheduleHeight=document.querySelector('#schedule button')?.getBoundingClientRect().height;
        const webPanels=[...document.querySelectorAll('.web-layout>.panel')].map(e=>e.getBoundingClientRect().height);
        const preview=document.querySelector('.child-preview');
        const reportHeader=document.querySelector('.report-layout .panel-heading');
        const reportAction=reportHeader?.querySelector('.report-export');
        const reportTitle=reportHeader?.querySelector('h2');
        const reportAligned=reportAction&&reportTitle ? reportAction.getBoundingClientRect().top<reportTitle.getBoundingClientRect().bottom : false;
        return {overflow:document.documentElement.scrollWidth>innerWidth,small,headings,kpiHeights,kpiFooters,controls,inputs,scopeLines,scheduleAlignment,scheduleHeight,webPanels,previewNoWrap:preview?getComputedStyle(preview).whiteSpace==='nowrap':true,reportAligned,account:account?{height:account.getBoundingClientRect().height,width:account.getBoundingClientRect().width,text:account.textContent,font:getComputedStyle(account).fontSize,whiteSpace:getComputedStyle(account).whiteSpace}:null};
      });
      measurements.push({view,width,...m});
      if(m.overflow)typographyFailures.push(view+' '+width+': page overflow');
      if(m.small.length)typographyFailures.push(view+' '+width+': text below 14px');
      if(m.headings.some(h=>h.lines>2&&!(view==='child'&&h.text.startsWith('Hôm nay của ')))&&view!=='login')typographyFailures.push(view+' '+width+': heading exceeds two lines');
      if(m.scopeLines>1.1)typographyFailures.push(view+' '+width+': scope label wrapped');
      if(view==='time'&&(m.scheduleAlignment.length!==5||m.scheduleAlignment.some(offset=>offset>1)||m.scheduleHeight!==30))typographyFailures.push(view+' '+width+': schedule ruler misaligned or wrong slot height');
      if(view==='web'&&width>700&&(m.webPanels.length!==2||Math.abs(m.webPanels[0]-m.webPanels[1])>1))typographyFailures.push(view+' '+width+': unequal filter panels');
      if(!m.previewNoWrap)typographyFailures.push(view+' '+width+': child preview can wrap');
      if(view==='reports'&&width>=768&&!m.reportAligned)typographyFailures.push(view+' '+width+': report export misaligned');
      if(width>=768&&m.inputs.length&&Math.max(...m.inputs)-Math.min(...m.inputs)>1)typographyFailures.push(view+' '+width+': inputs misaligned');
      if(width>=768&&m.controls.length&&Math.max(...m.controls)-Math.min(...m.controls)>1)typographyFailures.push(view+' '+width+': controls unequal');
      if(width>700&&m.kpiFooters.length&&Math.max(...m.kpiFooters)-Math.min(...m.kpiFooters)>1)typographyFailures.push(view+' '+width+': KPI footers misaligned');
      if(m.kpiHeights.length&&Math.max(...m.kpiHeights)-Math.min(...m.kpiHeights)>1)typographyFailures.push(view+' '+width+': unequal KPI heights');
      if([1440,768,390].includes(width))await page.screenshot({path:`${out}/${view}-${width}.png`,format:'png',fullPage:true});
    }
  }
  writeFileSync(`${out}/measurements.json`,JSON.stringify({note:'Isolated synthetic protocol data; no Windows enforcement or user data changed.',measurements,consoleErrors:page.consoleErrors,typographyFailures},null,2));
  console.log(JSON.stringify({phase,pages:11,viewports:6,overflows:measurements.filter(m=>m.overflow).map(m=>[m.view,m.width]),smallTextInstances:measurements.reduce((n,m)=>n+m.small.length,0),consoleErrors:page.consoleErrors,typographyFailures}));
  if(phase==='after')assert.deepEqual(typographyFailures,[]);
  assert.deepEqual(page.consoleErrors,[]);
}finally{await browser.close();}
