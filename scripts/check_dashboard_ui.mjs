// Run only against the isolated .tmp/ui-review profile on loopback:8447.
// All devices are protocol fixtures. This never runs native Windows enforcement.
import assert from 'node:assert/strict';
import {readFileSync, mkdirSync, writeFileSync, readdirSync} from 'node:fs';
import {join} from 'node:path';
import {Browser, sleep} from '../.agents/skills/design-taste-frontend/scripts/lib/cdp.mjs';

const config=JSON.parse(readFileSync('.tmp/ui-review/runtime/lab.json','utf8'));
assert.ok(config.KIDSAFE_DATABASE_URL.endsWith('/.tmp/ui-review/runtime/kidsafe.db'));
const root='https://localhost:8447';
const out=process.env.KIDSAFE_UI_EVIDENCE||'docs/evidence/current-ui';
mkdirSync(out,{recursive:true});
const checks=[];
const browser=await Browser.launch({extraArgs:['--ignore-certificate-errors']});
const page=await browser.newPage();
async function wait(expression){for(let n=0;n<120;n++){if(await page.eval(expression))return;await sleep(80);}throw Error('Timeout: '+expression);}
async function api(path,body,method=body===undefined?'GET':'POST',extra={}){
  return page.eval(async({path,body,method,extra})=>{
    const r=await fetch('/api/'+path,{method,headers:{'Content-Type':'application/json','X-CSRF-Token':sessionStorage.getItem('ks-csrf')||'',...extra},...(body===undefined?{}:{body:JSON.stringify(body)})});
    const data=await r.json();if(!r.ok)throw Error(path+': '+r.status);return data;
  },{path,body,method,extra});
}
async function login(username=config.demo_username,password=config.demo_password){
  await page.goto(root+'/login',{settleMs:30});
  await page.eval(({username,password})=>{document.querySelector('[name=username]').value=username;document.querySelector('[name=password]').value=password;document.querySelector('#login-form').requestSubmit();},{username,password});
  await wait("location.pathname!=='/login'&&document.querySelector('#screen')?.getAttribute('aria-busy')!=='true'");
}
async function navigate(view,child){await page.goto(`${root}/app/${view}?child=${child}`,{settleMs:30});await wait("document.querySelector('#screen')?.getAttribute('aria-busy')!=='true'");}
async function click(selector){await page.eval(s=>{const e=document.querySelector(s);if(!e)throw Error('Missing '+s);e.click();},selector);}
async function gear(){await click('[data-action="account-menu"]');await wait("!document.querySelector('#account-menu').hidden");}
try{
  await login();
  checks.push('Parent login through the actual form');
  const original=(await api('children'))[0].id;
  await navigate('overview',original);
  assert.equal(await page.eval(()=>document.querySelector('.quick-actions')),null);
  assert.equal(await page.eval(()=>document.querySelector('[data-quick-command]')),null);
  assert.ok(await page.eval(()=>document.querySelector('#screen').textContent.includes('Công cụ & Kiểm soát')));
  checks.push('Overview contains tools summary and no embedded controls');
  await navigate('quick-control',original);
  const selectedDevice=await page.eval(()=>{const select=document.querySelector('#quick-device');select.selectedIndex=1;document.querySelector('.quick-action-card').dataset.beforeRefresh='true';return select.value;});
  await click('[data-action=refresh]');await wait("!document.querySelector('[data-before-refresh]')");
  assert.equal(await page.eval(()=>document.querySelector('#quick-device').value),selectedDevice);
  checks.push('Data refresh preserves the selected quick-action target');
  assert.equal(await page.eval(()=>document.querySelectorAll('nav a').length),8);
  assert.equal(await page.eval(()=>document.querySelectorAll('nav a svg').length),8);
  assert.equal(await page.eval(()=>document.querySelector('nav a[href*="privacy"]')),null);
  checks.push('Eight sidebar destinations have SVG icons; privacy moved to settings');
  await gear();
  assert.equal(await page.eval(()=>document.querySelectorAll('#account-menu [role=menuitem]').length),3);
  await page.send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowDown',code:'ArrowDown',windowsVirtualKeyCode:40});
  assert.equal(await page.eval(()=>document.activeElement.dataset.action),'delete-child');
  await page.send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});
  assert.equal(await page.eval(()=>document.activeElement.dataset.action),'account-menu');
  assert.equal(await page.eval(()=>document.querySelector('#account-menu').hidden),true);
  checks.push('Settings menu supports keyboard movement, Escape and focus restoration');
  await gear();await click('[data-action="show-audit"]');
  await wait("document.querySelector('#modal').open&&document.querySelector('#modal-title')?.textContent==='Những thay đổi liên quan đến con'&&!!document.querySelector('#modal .audit-item')");
  await page.screenshot({path:out+'/audit-dialog-1440.png',format:'png'});
  await click('#modal .dialog-close');
  checks.push('Audit opens in an accessible timeline with scoped descriptions');
  // Keep the original account intact; new forms operate on a disposable child.
  await click('[data-action="add-child"]');
  await page.eval(()=>{document.querySelector('#new-child input').value='Kiểm chứng giao diện · dữ liệu tổng hợp';document.querySelector('#new-child').requestSubmit();});
  await wait("location.pathname==='/app/devices'&&!!document.querySelector('[data-action=enroll]')");
  const child=await page.eval(()=>document.body.dataset.child);
  await click('[data-action=enroll]');
  await page.eval(()=>{
    const form=document.querySelector('#enroll-form');
    form.elements.consent.checked=true;
    form.requestSubmit();
  });
  await wait("!!document.querySelector('#pairing-code')");
  const pairingCode=await page.eval(()=>document.querySelector('#pairing-code').textContent);
  assert.ok(/^[A-Z2-9]{4}-[A-Z2-9]{4}$/.test(pairingCode));
  const firstCount=await page.eval(()=>document.querySelector('#pairing-countdown').textContent);
  assert.ok(/^Mã hết hạn sau \d{2}:\d{2} phút$/.test(firstCount));
  await wait(`document.querySelector('#pairing-countdown').textContent!==${JSON.stringify(firstCount)}`);
  await page.screenshot({path:'.tmp/ui-review/d038-pairing-1440.png',format:'png'});
  await click('#modal .dialog-close');
  checks.push('Pairing dialog shows an eight-character code and a live expiry countdown');
  await navigate('overview',child);
  await navigate('quick-control',child);
  assert.equal(await page.eval(()=>document.querySelectorAll('[data-quick-command]:disabled').length),3);
  assert.equal(await page.eval(()=>document.querySelector('.pairing-empty select:disabled option').textContent),'Chọn máy cần điều khiển...');
  assert.ok(await page.eval(()=>document.querySelector('.pairing-empty a').href.includes('/app/devices')));
  await page.screenshot({path:out+'/quick-control-empty-1440.png',format:'png',fullPage:true});
  await navigate('overview',child);
  assert.equal(await page.eval(()=>document.querySelector('.metric-value strong').textContent),'0p');
  checks.push('New child has honest zero values and disabled controls without devices');
  await navigate('time',child);
  await page.eval(()=>{for(const n of ['weekday','weekend','entertainment'])document.querySelector(`[name=${n}]`).value='0';document.querySelector('#quota-form').requestSubmit();});
  await wait("document.querySelector('#notice').textContent.includes('Đã lưu')");
  await navigate('overview',child);
  assert.equal(await page.eval(()=>document.querySelector('.metric progress').value),0);
  assert.equal(await page.eval(()=>document.querySelector('.metric-value span').textContent),'/ 0p');
  checks.push('Zero quota renders without division errors or an invented progress stub');
  await navigate('time',child);
  await page.eval(()=>{
    for (const [name,value] of Object.entries({weekday:120,weekend:90,entertainment:100})) {
      const input=document.querySelector(`#quota-form [name=${name}]`);
      input.value=String(value);
      input.dispatchEvent(new Event('input',{bubbles:true}));
    }
  });
  assert.ok(await page.eval(()=>document.querySelector('#quota-form button').disabled &&
    document.querySelector('#quota-error').textContent==='Thời gian giải trí không được vượt quá tổng hạn mức dùng máy trong ngày'));
  const invalidPolicy=(await api(`children/${child}/policy`)).policy;
  await assert.rejects(api(`children/${child}/policy`,{...invalidPolicy,weekday_quota_sec:7200,
    weekend_quota_sec:5400,entertainment_quota_sec:6000},'PUT'), /422/);
  checks.push('Live quota validation locks Save and the API rejects an excessive entertainment limit');
  await click('[data-action=schedule-none]');
  assert.ok(await page.eval(()=>document.querySelector('#schedule-warning').hidden));
  await click('[data-day="0"][data-slot="0"]');
  await click('[data-day="6"][data-slot="47"]');
  assert.ok(await page.eval(()=>{
    const message=document.querySelector('#schedule-warning').textContent;
    return message.includes('Thứ hai')&&message.includes('120 phút')&&message.includes('Chủ nhật')&&
      message.includes('90 phút')&&document.querySelector('[data-total-day="0"]').textContent==='0g 30p'&&
      document.querySelector('[data-day="0"][data-slot="0"]').title==='00:00 - 00:30'&&
      document.querySelector('[data-day="6"][data-slot="47"]').title==='23:30 - 23:59';
  }));
  assert.equal(await page.eval(()=>document.querySelector('#quota-form [name=entertainment]').value),'100');
  await page.screenshot({path:out+'/time-validation-1440.png',format:'png',fullPage:true});
  await click('[data-action=save-schedule]');
  await wait("document.querySelector('#notice').textContent.includes('Đã lưu')");
  const savedSchedule=(await api(`children/${child}/policy`)).policy;
  assert.equal(savedSchedule.weekday_quota_sec,0);
  assert.equal(savedSchedule.schedule.flat().filter(Boolean).length,2);
  await click('[data-action=schedule-all]');
  assert.ok(await page.eval(()=>document.querySelector('#schedule-warning').hidden&&
    [...document.querySelectorAll('[data-total-day]')].every(total=>total.textContent==='24g')));
  checks.push('Slot tooltips, live totals, distinct weekday/weekend warnings and independent schedule save');
  await page.eval(()=>{
    for (const [name,value] of Object.entries({weekday:120,weekend:120,entertainment:45})) {
      const input=document.querySelector(`#quota-form [name=${name}]`);
      input.value=String(value);
      input.dispatchEvent(new Event('input',{bubbles:true}));
    }
    document.querySelector('#quota-form').requestSubmit();
  });
  await wait("!document.querySelector('#quota-form button').disabled");
  assert.deepEqual((await api(`children/${child}/policy`)).policy.schedule,savedSchedule.schedule);
  await page.screenshot({path:out+'/configured-time-1440.png',format:'png',fullPage:true});
  await navigate('apps',child);
  assert.equal(await page.eval(()=>document.querySelectorAll('[data-app-group]').length),5);
  assert.ok(await page.eval(()=>document.querySelector('[data-app-group=blocked] [role=switch]').disabled));
  await click('[data-app-group=games] [data-group-action=config]');
  await page.eval(()=>{
    const input=document.querySelector('#group-form-games [name=exe_file]');
    const transfer=new DataTransfer();
    transfer.items.add(new File(['abc'],'game.exe'));
    input.files=transfer.files;
    input.dispatchEvent(new Event('change',{bubbles:true}));
  });
  await wait("document.querySelector('#group-form-games [name=app_hash]').value==='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'");
  await click('#group-form-games [data-group-action=add]');
  await page.eval(()=>{
    const form=document.querySelector('#group-form-games');
    form.elements.window.value='own';
    form.elements.window.dispatchEvent(new Event('change',{bubbles:true}));
    for (const field of form.querySelectorAll('[name=day]')) field.checked=field.value==='5'||field.value==='6';
    form.elements.message.value='Con có thể dùng ứng dụng học tập nhé.';
    form.requestSubmit();
  });
  await wait("document.querySelector('#notice').textContent.includes('Đã lưu')");
  const savedPolicy=(await api(`children/${child}/policy`)).policy;
  assert.equal(savedPolicy.entertainment_quota_sec,2700);
  assert.deepEqual(savedPolicy.app_groups.games.apps,[{name:'game.exe',sha256:'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'}]);
  assert.deepEqual(savedPolicy.app_groups.games.window,{days:[5,6],start_minute:1080,end_minute:1260});
  await navigate('apps',child);
  await wait("document.querySelector('[data-app-group=games] .group-preview')?.textContent==='game.exe'");
  await click('[data-app-group=games] [data-group-action=config]');
  assert.equal(await page.eval(()=>document.querySelector('#group-form-games [name=message]').value),'Con có thể dùng ứng dụng học tập nhé.');
  assert.ok(await page.eval(()=>{
    const form=document.querySelector('#group-form-games');
    const [mode,window]=['mode','window'].map(name=>form.elements[name].getBoundingClientRect());
    return Math.abs(mode.top-window.top)<1 && Math.abs(mode.height-window.height)<1;
  }));
  await page.screenshot({path:out+'/apps-config-1440.png',format:'png',fullPage:true});
  await page.setViewport({width:390,height:1000});
  await page.screenshot({path:out+'/apps-config-390.png',format:'png',fullPage:true});
  await page.setViewport({width:1440,height:1000});
  await click('[data-app-group=games] [role=switch]');
  await wait("document.querySelector('[data-app-group=games] [role=switch]').getAttribute('aria-checked')==='false'");
  assert.equal((await api(`children/${child}/policy`)).policy.app_groups.games.enabled,false);
  await click('[data-app-group=games] [role=switch]');
  await wait("document.querySelector('[data-app-group=games] [role=switch]').getAttribute('aria-checked')==='true'");
  checks.push('Five groups, Web Crypto file hash, custom window, message, reload and quick toggle');
  await click('#group-form-games [data-remove-app="0"]');
  assert.equal(await page.eval(()=>document.querySelectorAll('#group-form-games [data-remove-app]').length),0);
  await page.eval(app=>{
    const form=document.querySelector('#group-form-games');
    form.elements.app_name.value=app.name;
    form.elements.app_hash.value=app.sha256;
    form.querySelector('[data-group-action=add]').click();
    form.elements.mode.value='custom';
    form.elements.mode.dispatchEvent(new Event('change',{bubbles:true}));
    form.elements.quota.value='25';
    form.requestSubmit();
  },savedPolicy.app_groups.games.apps[0]);
  await wait("document.querySelector('[data-app-group=games] .group-badges').textContent.includes('25 phút')");
  assert.equal((await api(`children/${child}/policy`)).policy.app_groups.games.quota_sec,1500);
  await page.eval(()=>{
    const form=document.querySelector('#group-form-games');
    form.elements.mode.value='entertainment';
    form.elements.mode.dispatchEvent(new Event('change',{bubbles:true}));
    form.requestSubmit();
  });
  await wait("document.querySelector('[data-app-group=games] .group-badges').textContent.includes('Tự khóa khi hết giờ')");
  checks.push('Remove and re-add member, then save and clear a custom daily group limit');
  const device=await api('device/enroll',{code:pairingCode,fingerprint:crypto.randomUUID(),name:'Máy kiểm chứng giao thức'});
  const auth={Authorization:'Bearer '+device.access_token};
  const heartbeat=async (used,entertainment=700)=>api('device/heartbeat',{device_id:device.device_id,status:'active',quota_used_sec:used,entertainment_used_sec:entertainment,policy_version:device.policy.payload.version,usage_date:new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Ho_Chi_Minh',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())},'POST',auth);
  await navigate('overview',child);
  for(const [seconds,level] of [[3599,'green'],[3600,'yellow'],[5400,'orange'],[6480,'orange'],[6481,'red']]){
    await heartbeat(seconds);await click('[data-action=refresh]');
    await wait(`document.querySelector('.metric progress').dataset.level==='${level}'&&Math.abs(document.querySelector('.metric progress').value-${seconds/7200})<0.000001`);
  }
  checks.push('Real report values drive progress at <50%, 50%, 75%, 90% and >90%');
  assert.equal(await page.eval(()=>document.querySelectorAll('.metric-value strong')[1].textContent),'33p');
  assert.equal(await page.eval(()=>document.querySelectorAll('.metric-value span')[1].textContent),'/ 45p');
  assert.equal(await page.eval(()=>document.querySelector('.metrics').textContent.includes('Chưa có hạn mức giải trí riêng')),false);
  const quotaState=await api(`children/${child}/reports?days=1`);assert.equal(quotaState.entertainment_today.used_sec,700);
  assert.ok(Math.abs(await page.eval(()=>document.querySelectorAll('.metric progress')[1].value)-2000/2700)<.000001);
  checks.push('Entertainment remaining comes from independent reported usage, not ordinary screen time');
  const configuredStats=(await api(`children/${child}/policy`)).stats;
  const displayedStats=await page.eval(()=>[...document.querySelectorAll('.panel')].find(p=>p.querySelector('h2')?.textContent==='Công cụ & Kiểm soát').querySelector('.summary-stats').textContent);
  assert.ok(displayedStats.includes(String(configuredStats.controlled_app_count)));
  assert.ok(displayedStats.includes(String(configuredStats.blocked_domain_count)));
  checks.push('Overview tool counts use the effective app/domain policy');
  await page.screenshot({path:out+'/entertainment-usage-1440.png',format:'png',fullPage:true});
  await navigate('reports',child);
  assert.equal(await page.eval(()=>document.querySelectorAll('.chart-guides i').length),4);
  assert.ok(await page.eval(()=>Math.abs(document.querySelector('.chart-guides').getBoundingClientRect().bottom-
    document.querySelector('.report-chart .bar-track').getBoundingClientRect().bottom)<1));
  const downloadPath=join(browser.dir,'downloads');
  mkdirSync(downloadPath,{recursive:true});
  await browser.send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath});
  await click('.report-export');
  let csvName;
  for(let attempt=0;attempt<100&&!csvName;attempt++){
    csvName=readdirSync(downloadPath).find(name=>/^kidsafe-report-\d{4}-\d{2}-\d{2}\.csv$/.test(name));
    if(!csvName)await sleep(50);
  }
  assert.ok(csvName,'Chrome downloaded the weekly report');
  const csv=readFileSync(join(downloadPath,csvName),'utf8');
  assert.ok(csv.includes('6481')&&csv.includes('Giây giải trí'));
  await page.screenshot({path:out+'/reports-data-1440.png',format:'png',fullPage:true});
  checks.push('Weekly report has grid guides and a scoped UTF-8 CSV attachment with report data');
  await navigate('quick-control',child);
  await page.screenshot({path:out+'/quick-control-online-1440.png',format:'png',fullPage:true});
  for(const type of ['lock','unlock','add_time']){
    await click(`[data-quick-command=${type}]`);
    await wait(`fetch('/api/children/${child}/commands').then(r=>r.json()).then(cs=>cs.some(c=>c.type==='${type}'))`);
    await wait(`!document.querySelector('[data-quick-command=${type}]').disabled`);
    const command=(await api(`children/${child}/commands`)).find(c=>c.type===type);
    assert.equal(command.device_id,device.device_id);assert.equal(command.ack,false);
    if(type==='add_time')assert.equal((await api(`children/${child}/reports?days=1`)).extra_granted_seconds,0);
    await api(`device/commands/${command.id}/ack`,{},'POST',auth);
  }
  await navigate('overview',child);
  await wait("document.querySelector('.metric-value span').textContent==='/ 2g 15p'");
  assert.equal((await api(`children/${child}/reports?days=1`)).entertainment_today.quota_sec,2700);
  checks.push('All three quick commands target the selected device and stay pending until ACK');
  await navigate('devices',child);
  assert.ok(await page.eval(()=>document.querySelector('#screen').textContent.includes('App KidSafe của con')&&!document.querySelector('[data-action=child-account]')));
  const childUsername='ui-review-'+Date.now();
  // Retain regression coverage for legacy child-view accounts; native child use
  // no longer asks parents to create one through the product interface.
  await api(`children/${child}/account`,{username:childUsername,password:'Review-Child-2026'},'POST');
  await api(`children/${child}/account/password`,{password:'Renewed-Child-2026'},'PUT');
  await gear();await click('#account-menu [data-action=logout]');await wait("location.pathname==='/login'");
  checks.push('Settings logout invalidates the active session');
  await login(childUsername,'Renewed-Child-2026');
  assert.ok(await page.eval(()=>document.querySelector('.audit-timeline .audit-item time')&&
    !document.querySelector('.audit-timeline details,.audit-timeline pre')));
  checks.push('Legacy child-view account accepts its reset password; native app does not require this account');
  assert.ok(await page.eval(()=>!document.querySelector('.child-top,footer,[data-action=logout]')&&
    document.querySelector('.child-time-actions progress').dataset.childLevel==='orange'&&
    !document.querySelector('#screen').textContent.includes('Thời gian trên từng máy')));
  assert.ok(await page.eval(()=>{
    const bar=document.querySelector('.child-entertainment-progress');
    const hero=document.querySelector('.child-time').getBoundingClientRect();
    const button=document.querySelector('.child-time .child-request-button').getBoundingClientRect();
    const logs=[...document.querySelectorAll('.child-audit .audit-item')];
    return Math.abs(bar.value-2000/2700)<.000001&&bar.getAttribute('aria-valuetext')==='Còn 33 phút'&&
      button.width/hero.width>.5&&button.top>=bar.getBoundingClientRect().bottom&&
      document.querySelectorAll('.child-activities .child-empty svg').length===2&&
      logs.some(item=>item.textContent.includes('lệnh khóa máy')&&item.querySelector('.audit-icon-lock'))&&
      logs.some(item=>item.textContent.includes('lệnh mở khóa')&&item.querySelector('.audit-icon-unlock'));
  }));
  checks.push('Child sees the recorded entertainment balance, illustrated empty states and distinct audit icons');
  await page.screenshot({path:out+'/child-signed-in-1440.png',format:'png',fullPage:true});
  await click('[data-action=child-request]');
  assert.deepEqual(await page.eval(()=>[...document.querySelectorAll('#child-request-form [name=minutes]')].map(input=>input.value)),['5','10','15']);
  await click('#child-request-form [value="5"]');
  await page.setViewport({width:390,height:900});
  await page.screenshot({path:out+'/child-request-390.png',format:'png'});
  await click('#child-request-form button[type=submit]');
  await wait("document.querySelector('#notice').textContent.includes('Đã gửi lời xin thêm 5 phút')");
  await api('auth/logout',{});
  await page.setViewport({width:1440,height:1000});
  checks.push('Child layout is simplified and the real child submits the selected five minutes');
  await login();await navigate('overview',child);
  await wait("document.querySelectorAll('.metric-value strong').length===3");
  assert.equal(await page.eval(()=>document.querySelectorAll('.metric-value strong')[2].textContent),'1');
  await click('.metrics a[href*="requests"]');await wait("location.pathname==='/app/requests'&&!!document.querySelector('[data-request]')");
  assert.equal(await page.eval(()=>document.querySelector('[data-request]').textContent),'Đồng ý +5 phút');
  await click('[data-request]');await wait("document.querySelector('#screen').textContent.includes('Đã duyệt · Chờ máy xác nhận')");
  assert.equal((await api(`children/${child}/reports`)).pending_request_count,0);
  const approval=(await api(`children/${child}/commands`)).find(c=>!c.ack&&c.type==='add_time');
  assert.equal(approval.payload.seconds,300);
  await api(`device/commands/${approval.id}/ack`,{},'POST',auth);
  await click('[data-action=refresh]');await wait("!document.querySelector('[data-request]')&&document.querySelector('#screen').textContent.includes('Máy đã xác nhận')");
  checks.push('Child request, parent approval, pending count and agent ACK reconcile');
  await heartbeat(8400,2700);
  await page.goto(`${root}/child?child=${child}`,{settleMs:30});
  await wait("document.querySelector('.child-time-actions progress')?.dataset.childLevel==='red'");
  assert.equal(await page.eval(()=>document.querySelector('.child-entertainment-progress').value),0);
  await click('[data-action=child-request]');
  assert.ok(await page.eval(()=>document.querySelector('#child-request-form button[type=submit]').disabled));
  await click('#modal .dialog-close');
  checks.push('Exhausted progress is red and a parent preview cannot send a request');
  await navigate('apps',child);
  assert.ok(await page.eval(()=>['games','video'].every(key=>document.querySelector(`[data-app-group=${key}] .group-badges`).textContent.includes('Đã khóa do hết giờ giải trí'))));
  checks.push('Both entertainment groups show exhaustion from the synchronized usage');
  await navigate('web',child);
  assert.equal(await page.eval(()=>document.querySelectorAll('#web-categories [role=switch]').length),7);
  assert.equal(await page.eval(()=>document.querySelectorAll('.web-layout input[type=checkbox],.web-layout textarea').length),0);
  await page.eval(()=>{
    document.querySelector('[data-web-switch=games]').click();
    document.querySelector('[data-web-switch=safesearch]').click();
  });
  await wait("document.querySelector('[data-web-switch=games]').getAttribute('aria-checked')==='true'&&document.querySelector('[data-web-switch=safesearch]').getAttribute('aria-checked')==='false'");
  await navigate('web',child);
  assert.ok(await page.eval(()=>document.querySelector('[data-web-switch=games]').getAttribute('aria-checked')==='true'&&
    document.querySelector('[data-web-switch=safesearch]').getAttribute('aria-checked')==='false'));
  checks.push('Seven accessible switches auto-save category and SafeSearch updates without overwriting each other');
  await page.eval(()=>{
    const transfer=new DataTransfer();
    transfer.setData('text/plain','https://www.youtube.com/watch?v=123');
    document.querySelector('#web-domain').dispatchEvent(new ClipboardEvent('paste',{clipboardData:transfer,bubbles:true,cancelable:true}));
  });
  await wait("document.querySelector('#web-domain').value==='youtube.com'");
  await click('#web-domain-form button');
  await wait("!!document.querySelector('[data-web-remove=\"youtube.com\"]')");
  await page.eval(()=>{
    const input=document.querySelector('#web-domain');
    input.value='http://shop.example.co.uk/path?q=1#part';
    input.dispatchEvent(new Event('change',{bubbles:true}));
  });
  await wait("document.querySelector('#web-domain').value==='example.co.uk'");
  await click('#web-domain-form button');
  await wait("!!document.querySelector('[data-web-remove=\"example.co.uk\"]')");
  await page.eval(()=>{
    const input=document.querySelector('#web-domain');
    input.value='https://bad..example.com/path';
    input.dispatchEvent(new Event('change',{bubbles:true}));
  });
  assert.equal(await page.eval(()=>document.querySelector('#web-domain-error').textContent),'Chỉ nhập tên miền (ví dụ: facebook.com), không nhập đường dẫn.');
  assert.equal(await page.eval(()=>document.querySelector('#web-domain').getAttribute('aria-invalid')),'true');
  await page.screenshot({path:out+'/web-tags-error-1440.png',format:'png',fullPage:true});
  await page.setViewport({width:390,height:1000});
  await page.screenshot({path:out+'/web-tags-error-390.png',format:'png',fullPage:true});
  await page.setViewport({width:1440,height:1000});
  await click('[data-web-remove="youtube.com"]');
  await wait("!document.querySelector('[data-web-remove=\"youtube.com\"]')");
  assert.deepEqual((await api(`children/${child}/policy`)).policy.blocked_domains,['example.co.uk']);
  checks.push('URL paste and input change normalize to registrable domains, invalid input reports inline and chips remove exact entries');
  await navigate('overview',child);
  await gear();await click('[data-action=show-audit]');
  await wait("document.querySelectorAll('#modal .audit-item').length===10");
  assert.ok(await page.eval(()=>!document.querySelector('#modal details,#modal pre')&&
    !/Người thực hiện|Tối đa 50|blocked_categories/.test(document.querySelector('#modal-content').textContent)&&
    [...document.querySelectorAll('#modal .audit-item time')].every(e=>/^\d{2}:\d{2} \d{2}\/\d{2}$/.test(e.textContent))));
  await page.screenshot({path:out+'/audit-recent-1440.png',format:'png'});
  await page.setViewport({width:390,height:900});
  assert.ok(await page.eval(()=>{
    const list=document.querySelector('#audit-modal-list'), close=document.querySelector('#modal .dialog-close');
    const top=close.getBoundingClientRect().top;
    list.scrollTop=list.scrollHeight;
    const pinned=list.scrollTop>0&&close.getBoundingClientRect().top===top;
    list.scrollTop=0;
    return pinned;
  }));
  await page.screenshot({path:out+'/audit-recent-390.png',format:'png'});
  await click('#modal .dialog-close');
  checks.push('Audit shows ten newest items with timestamps and no raw audit fields');
  await page.setViewport({width:390,height:900});await click('[data-action=menu]');
  await gear();await page.screenshot({path:out+'/settings-menu-390.png',format:'png'});
  await click('#account-menu [data-action=delete-child]');
  await wait("document.querySelector('#delete-child-confirm')!==null");
  assert.equal(await page.eval(()=>document.activeElement.dataset.action),'cancel-delete');
  await page.screenshot({path:out+'/delete-dialog-390.png',format:'png'});
  await click('[data-action=cancel-delete]');
  assert.ok((await api('children')).some(c=>c.id===child));
  checks.push('Delete confirmation initially focuses Cancel; cancellation preserves data');
  await gear();await click('#account-menu [data-action=delete-child]');
  await click('#delete-child-confirm [type=submit]');
  await wait("document.querySelector('#screen').textContent.includes('Đã xóa dữ liệu trên server')");
  assert.equal(await page.eval(()=>document.body.dataset.child),'');
  assert.ok(!(await api('children')).some(c=>c.id===child));
  const cleanup=await heartbeat(6481);
  assert.ok(cleanup.commands.some(c=>c.payload.type==='delete_data'));
  assert.ok(await page.eval(()=>document.querySelector('#screen').textContent.includes('1 máy chờ xác nhận')));
  checks.push('Confirmed deletion erases server data and queues agent cleanup without claiming its ACK');
  await page.setViewport({width:1440,height:1000});await navigate('overview',original);
  await click('nav a[href*="/app/web"]');await wait("location.pathname==='/app/web'&&document.body.dataset.view==='web'&&!!document.querySelector('#web-domain-form')");
  await click('nav a[href*="/app/overview"]');await wait("location.pathname==='/app/overview'&&!!document.querySelector('.metrics')");
  await gear();await click('[data-action=show-audit]');await wait("!!document.querySelector('#modal .audit-item')");await click('#modal .dialog-close');
  checks.push('HTMX navigation keeps the correct scope and working settings handlers');
  assert.equal(page.consoleErrors.length,0);
  writeFileSync(out+'/functional-results.json',JSON.stringify({passed:true,checks,note:'Synthetic loopback/browser protocol evidence, not native Windows enforcement.'},null,2));
  console.log(`PASS: ${checks.length} browser interaction checks; no JavaScript exceptions.`);
}finally{await browser.close();}
