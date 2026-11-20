/* All displayed values come from scoped API responses. No fabricated activity. */
(() => {
  if (window.kidSafeLoaded) return;
  window.kidSafeLoaded = true;
  let state = {}, timer, loadSequence = 0, loading = false;
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const minutes = (n) => `${Math.floor(Number(n || 0)/60)} phút`;
  const shortTime = (seconds) => { const m=Math.floor(Math.max(0,Number(seconds)||0)/60);return m>=60?`${Math.floor(m/60)}g${m%60?' '+m%60+'p':''}`:`${m}p`; };
  const icons = {
    lock:'<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/>',
    unlock:'<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 7.5-2M12 14v3"/>',
    clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    gamepad:'<path d="M7 7h10c3 0 5 10 3 11s-4-3-5-3H9c-1 0-3 4-5 3S4 7 7 7Z"/><path d="M8 9v5m-2.5-2.5h5m5-1h.01m2 2h.01"/>',
    bell:'<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9m-11 12h4"/>',
    device:'<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8m-4-4v4"/>',
    study:'<path d="M12 6c-3-2-6-2-9-1v13c3-1 6-1 9 1 3-2 6-2 9-1V5c-3-1-6-1-9 1Zm0 0v13"/>',
    video:'<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m10 9 5 3-5 3Z"/>',
    social:'<path d="M5 4h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-5 4v-4a2 2 0 0 1-1-2V6a2 2 0 0 1 2-2Z"/><path d="M7 9h10m-10 4h6"/>',
    shield:'<path d="M12 3 4 6v6c0 5 4 8 8 10 4-2 8-5 8-10V6Z"/><path d="m9 9 6 6m0-6-6 6"/>',
    settings:'<path d="M4 6h16M4 12h16M4 18h16M8 4v4m8 2v4m-6 2v4"/>',
    folder:'<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/>',
    graduate:'<path d="m2 9 10-5 10 5-10 5-10-5Zm4 2v5c3 3 9 3 12 0v-5m4-2v6"/>',
    globe:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a16 16 0 0 0 0 18 16 16 0 0 0 0-18Z"/>',
    download:'<path d="M12 3v11m-4-4 4 4 4-4M4 15v5h16v-5"/>',
    search:'<circle cx="10.5" cy="10.5" r="5.5"/><path d="m15 15 5 5"/>'
  };
  const icon = (name) => `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name]||''}</svg>`;
  const progressLevel = (fraction) => fraction<.5?'green':fraction<.75?'yellow':fraction<=.9?'orange':'red';
  const pendingRequests = () => state.week.pending_requests || state.week.requests.filter(r=>!r.status||r.status==='pending');
  function quotaProgress(used,total) {
    const fraction=total>0?Math.min(1,Math.max(0,used/total)):(used>0?1:0);
    return `<progress max="1" value="${fraction}" data-level="${progressLevel(fraction)}" aria-label="Hạn mức dùng máy đã sử dụng" aria-valuetext="${esc(minutes(used)+' trên '+minutes(total))}"></progress>`;
  }
  function accountMenu(open, focus=false) {
    const menu=$('#account-menu'), toggle=$('[data-action="account-menu"]');
    if(!menu||!toggle)return;
    menu.hidden=!open;toggle.setAttribute('aria-expanded',String(open));
    if(open)menu.querySelector('button:not(:disabled)')?.focus();else if(focus)toggle.focus();
  }
  const mobileNavigation = matchMedia('(max-width: 1100px)');
  let sidebarReturnFocus = null, sidebarLastFocus = null, sidebarInert = [];
  function sidebarControls() {
    return [...($('#navigation')?.querySelectorAll('a[href],button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled),[tabindex]:not([tabindex="-1"])') || [])]
      .filter(element => element.getClientRects().length && !element.closest('[hidden]'));
  }
  function sidebarOpen(open, restoreFocus=true) {
    const navigation=$('#navigation'), toggle=$('[data-action="menu"]'), backdrop=$('#navigation-backdrop');
    if(!navigation||!toggle)return;
    open=Boolean(open&&mobileNavigation.matches);
    const wasOpen=navigation.classList.contains('open');
    if(open&&!wasOpen) {
      sidebarReturnFocus=document.activeElement;
      sidebarInert=[...document.querySelectorAll('.workspace,.skip')].map(element=>[element,element.inert]);
      sidebarInert.forEach(([element])=>element.inert=true);
    }
    navigation.classList.toggle('open',open);
    toggle.setAttribute('aria-expanded',String(open));
    document.body.classList.toggle('sidebar-open',open);
    if(backdrop)backdrop.hidden=!open;
    if(open) {
      navigation.setAttribute('role','dialog');
      navigation.setAttribute('aria-modal','true');
      (sidebarControls()[0]||navigation).focus();
    } else {
      navigation.removeAttribute('role');
      navigation.removeAttribute('aria-modal');
      sidebarInert.forEach(([element,previous])=>{if(element.isConnected)element.inert=previous;});
      sidebarInert=[];
      accountMenu(false);
      if(wasOpen&&restoreFocus) {
        const previous=sidebarReturnFocus?.isConnected&&sidebarReturnFocus.getClientRects().length?sidebarReturnFocus:toggle;
        previous.focus();
      }
      sidebarReturnFocus=null;
    }
  }
  mobileNavigation.addEventListener('change',()=>{
    const active=document.activeElement, navigation=$('#navigation');
    // A tap can open the drawer before the resize notification is dispatched.
    if(mobileNavigation.matches&&navigation?.classList.contains('open'))return;
    // CSS can hide the focused control before the media-query event runs.
    const focused=active===document.body&&sidebarLastFocus?.isConnected?sidebarLastFocus:active;
    const inside=navigation?.contains(focused);
    sidebarLastFocus=null;
    sidebarOpen(false,false);
    if(!inside)return;
    if(mobileNavigation.matches)$('[data-action="menu"]')?.focus();
    else if(!focused.getClientRects().length)
      (navigation.querySelector('nav a[aria-current]')||navigation.querySelector('nav a[href]')||navigation.querySelector('.brand'))?.focus();
  });
  document.addEventListener('pointerdown',event=>{
    if(!$('#navigation')?.contains(event.target))sidebarLastFocus=null;
  },{capture:true});
  document.addEventListener('keydown',event=>{
    const navigation=$('#navigation');
    if(!navigation?.classList.contains('open')||$('#modal')?.open)return;
    if(event.key==='Escape') {
      const account=$('#account-menu');
      if(account&&!account.hidden)return;
      event.preventDefault();sidebarOpen(false);return;
    }
    if(event.key!=='Tab')return;
    const controls=sidebarControls(), first=controls[0], last=controls.at(-1);
    if(!controls.length){event.preventDefault();navigation.focus();return;}
    if(event.shiftKey&&(document.activeElement===first||!navigation.contains(document.activeElement))){event.preventDefault();last.focus();}
    else if(!event.shiftKey&&(document.activeElement===last||!navigation.contains(document.activeElement))){event.preventDefault();first.focus();}
  },{capture:true});
  document.addEventListener('focusin',event=>{
    const navigation=$('#navigation');
    if(navigation?.contains(event.target))sidebarLastFocus=event.target;
    else if(event.target!==document.body)sidebarLastFocus=null;
    if(navigation?.classList.contains('open')&&!$('#modal')?.open&&!navigation.contains(event.target))
      (sidebarControls()[0]||navigation).focus();
  });
  function backgroundRefreshBlocked() {
    const focused=document.activeElement;
    return document.hidden||$('#modal')?.open||$('#navigation')?.classList.contains('open')||
      ($('#screen')?.contains(focused)&&focused.matches('a[href],button,input,select,textarea,[contenteditable="true"],[tabindex]'));
  }
  function scheduleRefresh() {
    clearTimeout(timer);
    timer=setTimeout(()=>{
      if(document.hidden||$('#modal')?.open) scheduleRefresh();
      else if(document.body.dataset.view==='apps') refreshGroupUsage();
      else load({background:true});
    },15000);
  }
  const stamp = (s) => s ? new Date(typeof s === 'number' ? s*1000 : s).toLocaleString('vi-VN') : 'Chưa kết nối';
  const categories = {education:'Giáo dục',entertainment:'Giải trí',social:'Mạng xã hội',games:'Trò chơi',age_inappropriate:'Không phù hợp lứa tuổi',unclassified:'Chưa phân loại'};
  const titles = {lock:'Khóa ngay',unlock:'Mở khóa tạm thời',add_time:'Cộng 15 phút',reduce_budget:'Đổi phần chia offline',delete_data:'Xóa dữ liệu'};
  function commandTitle(type, seconds=900) {
    return type==='add_time' ? 'Cộng '+minutes(seconds) : titles[type]||type;
  }
  function notice(text,error=false) { if($('#notice')) { $('#notice').textContent=text; $('#notice').className=error?'error':''; } }
  async function api(path, method='GET', body, headers={}) {
    const options={method,credentials:'same-origin',headers:{'Content-Type':'application/json',...(method!=='GET'?{'X-CSRF-Token':sessionStorage.getItem('ks-csrf')||''}:{}),...headers},...(body!==undefined?{body:JSON.stringify(body)}:{})};
    let response = await fetch('/api/'+path,options);
    if(response.status===403 && method!=='GET' && path!=='auth/login') {
      const fresh=await fetch('/api/auth/csrf',{credentials:'same-origin'});
      if(fresh.ok){const value=await fresh.json();sessionStorage.setItem('ks-csrf',value.csrf_token);options.headers['X-CSRF-Token']=value.csrf_token;response=await fetch('/api/'+path,options);}
    }
    if(response.status===401 && document.body.dataset.view!=='login'){location.href='/login';throw Error('Phiên đăng nhập đã hết hạn.');}
    let data; try{data=await response.json();}catch{data={detail:'Máy chủ chưa thể xử lý yêu cầu.'};}
    if(!response.ok)throw Error(response.status===403?'Phiên bảo mật cần đăng nhập lại, hoặc bạn không có quyền thực hiện.':response.status===409?(typeof data.detail==='string'?data.detail:'Đang chờ máy trả ngân sách. Hãy đồng bộ trước khi thử lại.'):(typeof data.detail==='string'?data.detail:`Dữ liệu chưa hợp lệ (${response.status}). Kiểm tra các trường đã nhập.`));
    return data;
  }
  const base = () => 'children/'+document.body.dataset.child;
  const row = (left,right,small='') => `<div class="row"><div class="row-name">${esc(left)}${small?`<small>${esc(small)}</small>`:''}</div><div class="num">${right}</div></div>`;
  const panel = (name,content,extra='')=>`<section class="panel"><div class="panel-heading"><h2>${esc(name)}</h2>${extra}</div>${content}</section>`;
  const empty = (text) => `<p class="empty">${esc(text)}</p>`;
  const list = (items,unit) => items.length?items.map(r=>row(r.subject,esc(unit(r.value)))).join(''):empty('Chưa có hoạt động được đồng bộ.');
  function dayKey() {return new Intl.DateTimeFormat('en-CA',{timeZone:state.policy?.timezone||'Asia/Ho_Chi_Minh',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());}
  function quota() {const date=new Date(),weekday=new Intl.DateTimeFormat('en-US',{timeZone:state.policy.timezone,weekday:'short'}).format(date);return state.policy[['Sat','Sun'].includes(weekday)?'weekend_quota_sec':'weekday_quota_sec'];}
  function online(device) {return device.last_seen && Date.now()/1000-device.last_seen<120;}
  function commandButtons(device) {return `<div class="actions"><button data-command="add_time" data-device="${esc(device.id)}">+ 15 phút</button><button data-command="unlock" data-device="${esc(device.id)}">Mở khóa</button><button data-command="lock" data-device="${esc(device.id)}">Khóa ngay</button></div>`;}
  function deviceRows(controls=true) {return state.devices.length?state.devices.map(d=>`<div class="row"><div class="row-name"><h3>${esc(d.name)}</h3><span class="state ${online(d)?'online':''}">${d.revoked?'Đã thu hồi':online(d)?'Đang kết nối':'Chưa kết nối'}</span><small>Lần cuối: ${esc(stamp(d.last_seen))} · Quy tắc ${d.reported_policy_version===state.version?'đã nhận':'đang chờ nhận'} · Phần giữ: ${minutes(d.allocation.weekday_sec)} ngày thường / ${minutes(d.allocation.weekend_sec)} cuối tuần</small></div>${controls&&!d.revoked?commandButtons(d):''}</div>`).join(''):empty('Chưa có máy của con. Tạo mã ghép đôi để thêm máy.');}
  function chart({guides=false}={}) {
    const lastDay = new Date((state.week.through_date||dayKey())+'T00:00:00Z');
    const days = Array.from({length:7},(_,index)=>{
      const date = new Date(lastDay);
      date.setUTCDate(date.getUTCDate()+index-6);
      const key = date.toISOString().slice(0,10);
      return {key,value:state.week.daily_seconds[key]||0};
    });
    const max = Math.max(60,...days.map(day=>day.value));
    const grid = guides ? '<div class="chart-guides" aria-hidden="true"><i></i><i></i><i></i><i></i></div>' : '';
    return `<div class="bar-chart${guides?' report-chart':''}" role="img" aria-label="Thời gian 7 ngày: ${esc(days.map(day=>day.key+' '+minutes(day.value)).join(', '))}">${grid}${days.map(day=>`<div class="day-bar">
      <span>${shortTime(day.value)}</span>
      <div class="bar-track"><svg class="bar-svg" viewBox="0 0 44 120" preserveAspectRatio="none" aria-hidden="true"><rect class="bar-fill" x="0" y="${120-day.value/max*120}" width="44" height="${day.value/max*120}"/></svg></div>
      <small>${day.key.slice(8)}/${day.key.slice(5,7)}</small></div>`).join('')}</div>`;
  }


  function quickTargetStatus() {
    const select=$('#quick-device'), target=$('#quick-target-status');
    if(!select||!target)return;
    const device=state.devices.find(d=>d.id===select.value&&!d.revoked);
    select.title=device?.name||'';
    target.innerHTML=device?`<span class="state ${online(device)?'online':''}">${online(device)?'Đang kết nối (Online)':'Chưa kết nối (Offline)'}</span><span class="caption">Lần cuối: ${esc(stamp(device.last_seen))}</span>`:'';
  }
  function quickControlView() {
    const devices=state.devices.filter(d=>!d.revoked), child=esc(document.body.dataset.child);
    const target=devices.length?`<div class="quick-target"><label for="quick-device">Thiết bị mục tiêu<select id="quick-device" aria-describedby="quick-target-status">${devices.map(d=>`<option value="${esc(d.id)}">${esc(d.name)} · ${online(d)?'Online':'Offline'}</option>`).join('')}</select></label><div id="quick-target-status" class="quick-target-status" aria-live="polite"></div></div>`:`<div class="pairing-empty"><p>Chưa có thiết bị của con. Tạo mã ghép đôi và kết nối máy trước khi gửi lệnh.</p><select disabled aria-label="Thiết bị mục tiêu"><option>Chọn máy cần điều khiển...</option></select><a class="soft-button" href="/app/devices?child=${child}">Đến trang ghép đôi →</a></div>`;
    const cards=[['lock','Khóa máy ngay','Yêu cầu máy nghỉ ngay.','Khóa máy ngay','danger'],['unlock','Mở khóa tạm thời','Mở khóa ngay lập tức, bỏ qua lịch','Mở khóa','primary'],['clock','Cộng thêm 15 phút','Cộng giờ, giữ lịch.','+15 phút','primary add-time']];
    return `<div class="stack">${panel('Chọn thiết bị điều khiển',target)}<div class="quick-control-grid">${cards.map(([symbol,title,description,label,style],i)=>`<section class="panel quick-action-card"><div class="quick-card-icon">${icon(symbol)}</div><h2>${title}</h2><p>${description}</p><button class="${style}" data-quick-command="${['lock','unlock','add_time'][i]}" ${devices.length?'':'disabled'}>${label}</button></section>`).join('')}</div><p class="caption quick-explanation">Lệnh được gửi đến máy đang chọn. Máy offline nhận lệnh còn hiệu lực khi kết nối lại. Mở khóa tạm thời kết thúc khi bấm Khóa máy ngay hoặc sang ngày mới. Quy tắc chặn ứng dụng và website vẫn áp dụng. Nếu Windows đang khóa, con cần tự đăng nhập lại.</p>${panel('Trạng thái lệnh gần đây',state.commands?.length?state.commands.slice(0,6).map(c=>row(commandTitle(c.type,c.payload?.seconds),`<span class="state ${c.ack?'online':''}">${c.ack?'Máy đã xác nhận':'Chờ máy xác nhận'}</span>`,`${state.devices.find(d=>d.id===c.device_id)?.name||'Thiết bị'} · ${stamp(c.created)}`)).join(''):empty('Chưa có lệnh được gửi.'))}</div>`;
  }
  function toolsSummary() {
    const stats=state.policyStats, child=esc(document.body.dataset.child);
    return `<div class="summary-stats">${row('Ứng dụng đang kiểm soát',String(stats.controlled_app_count))}${row('Tên miền đang chặn',String(stats.blocked_domain_count))}</div><div class="tools-links"><a class="soft-button" href="/app/time?child=${child}">Điều chỉnh lịch của con →</a><a class="soft-button" href="/app/quick-control?child=${child}">Điều khiển nhanh →</a></div>`;
  }
  function entertainmentProgress(data, approximate) {
    const fraction=data.quota_sec>0?Math.min(1,data.remaining_sec/data.quota_sec):0;
    const spent=data.quota_sec>0?data.used_sec/data.quota_sec:1;
    return `<progress max="1" value="${fraction}" data-level="${progressLevel(spent)}" aria-label="Thời gian giải trí còn lại" aria-valuetext="${approximate?'Tạm tính ':''}${esc(minutes(data.remaining_sec)+' trên '+minutes(data.quota_sec))}"></progress>`;
  }
  function overview() {
    const used=state.today.normal_seconds ?? state.today.total_seconds;
    const limit=quota()+(state.today.extra_granted_seconds||0);
    const pending=state.week.pending_request_count ?? pendingRequests().length;
    const devices=state.devices.filter(d=>!d.revoked);
    const child=esc(document.body.dataset.child);
    const extra=state.today.exception_seconds?.[dayKey()]||0;
    const entertainment=state.today.entertainment_today;
    const missingReports=entertainment.devices_count-entertainment.reporting_devices;
    const awaitingReports=missingReports>0&&entertainment.reporting_devices===0;
    return `<div class="metrics">
      <section class="metric"><div class="metric-title"><div class="metric-icon">${icon('clock')}</div><h2>Thời gian dùng máy hôm nay</h2></div><div class="metric-value"><strong>${shortTime(used)}</strong><span>/ ${shortTime(limit)}</span></div>${extra?`<p class="metric-note">Giờ ngoại lệ: ${shortTime(extra)}, ghi riêng.</p>`:''}${state.today.pending_extra_seconds?`<p class="metric-note">+${shortTime(state.today.pending_extra_seconds)} đang chờ máy nhận.</p>`:''}<div class="metric-bottom">${quotaProgress(used,limit)}</div></section>
      <section class="metric"><div class="metric-title"><div class="metric-icon">${icon('gamepad')}</div><h2>Giải trí còn lại hôm nay</h2></div><div class="metric-value"><strong>${awaitingReports?'—':Math.floor(entertainment.remaining_sec/60)+'p'}</strong><span>/ ${Math.floor(entertainment.quota_sec/60)}p</span></div>${missingReports>0?`<p class="metric-note">${awaitingReports?'':'Tạm tính. '}Chờ dữ liệu từ ${missingReports}/${entertainment.devices_count} máy.</p>`:''}<div class="metric-bottom">${awaitingReports?'':entertainmentProgress(entertainment,missingReports>0)}</div></section>
      <section class="metric"><div class="metric-title"><div class="metric-icon">${icon('bell')}</div><h2>Yêu cầu đang chờ duyệt</h2></div><div class="metric-value"><strong>${pending}</strong></div><div class="metric-bottom"><a class="soft-button" href="/app/requests?child=${child}">Xem yêu cầu →</a></div></section>
    </div><div class="two-col"><div class="stack">${panel('Một tuần sử dụng',chart())}${panel('Thiết bị của con',deviceRows(false))}</div><div class="stack">${panel('Công cụ & Kiểm soát',toolsSummary())}${panel('Hoạt động được ghi nhận',`<div class="summary-stats">${row('Lượt bị chặn tuần này',String(state.week.blocked_count))}${row('Xin thêm giờ',String(state.week.request_count ?? state.week.requests.length))}${row('Thiết bị đang kết nối',`${devices.filter(online).length} / ${devices.length}`)}</div>`)}${panel('Ứng dụng dùng nhiều',list(state.week.top_apps.slice(0,4),minutes))}</div></div>`;
  }
  const scheduleDays = ['Thứ hai','Thứ ba','Thứ tư','Thứ năm','Thứ sáu','Thứ bảy','Chủ nhật'];
  const shortDays = ['T2','T3','T4','T5','T6','T7','CN'];
  const quotaNames = {weekday:'weekday_quota_sec',weekend:'weekend_quota_sec',entertainment:'entertainment_quota_sec'};
  const quotaError = 'Thời gian giải trí không được vượt quá tổng hạn mức dùng máy trong ngày';
  const slotTime = slot => slot === 48 ? '23:59' : String(Math.floor(slot/2)).padStart(2,'0') + (slot%2 ? ':30' : ':00');
  const dayMinutes = slots => slots.filter(Boolean).length * 30;
  const dayTotal = value => value === 1440 ? '24g' : `${Math.floor(value/60)}g ${String(value%60).padStart(2,'0')}p`;

  function timeView() {
    state.scheduleDraft = state.policy.schedule.map(slots => [...slots]);
    const quotaForm = `<form id="quota-form"><div class="form-grid quota-grid">
      ${[['weekday','Ngày thường · phút'],['weekend','Cuối tuần · phút'],['entertainment','Giải trí mỗi ngày · phút']].map(([name,label]) => `<label><span>${label}</span><input name="${name}" type="number" min="0" max="1440" step="any" required value="${state.policy[quotaNames[name]]/60}" ${name==='entertainment'?'aria-describedby="quota-error"':''}></label>`).join('')}
    </div><p class="quota-note">Lưu ý: Hạn mức sử dụng trong ngày (Ngày thường / Cuối tuần) đã bao gồm cả thời gian Giải trí mỗi ngày ở trong đó. Khi dùng hết quỹ giải trí, các nhóm ứng dụng Trò chơi và Xem video sẽ tự động khóa, nhưng con vẫn có thể dùng máy cho mục đích Học tập trong thời gian còn lại.</p><p id="quota-error" class="quota-error" role="alert" hidden></p><div class="actions"><button class="primary">Lưu hạn mức</button></div></form>`;
    const weekActions = `<div class="actions schedule-actions"><button data-action="schedule-all">Cho phép cả tuần</button><button data-action="schedule-none">Tắt cả tuần</button></div>`;
    const hourLabels = [0,12,24,36,48].map(slot => `<span class="schedule-hour${slot===48?' schedule-end':''}" data-mark="${slot}">${slotTime(slot)}</span>`).join('');
    const rows = state.scheduleDraft.map((slots,day) => `<div class="schedule-line schedule-day"><span class="schedule-day-label">${shortDays[day]}</span>${slots.map((on,slot) => {
      const range = slotTime(slot)+' - '+slotTime(slot+1);
      return `<button type="button" data-day="${day}" data-slot="${slot}" aria-pressed="${on}" title="${range}" aria-label="${scheduleDays[day]}, ${range}"></button>`;
    }).join('')}<span class="schedule-total" data-total-day="${day}">${dayTotal(dayMinutes(slots))}</span></div>`).join('');
    const schedule = `<p class="schedule-note">Chọn khung giờ cho phép mở máy. Con có thể bật máy bất kỳ lúc nào trong khung giờ màu xanh, nhưng tổng thời gian dùng thực tế không vượt quá Hạn mức ngày ở trên.</p>
      <div class="schedule-scroll" tabindex="0" role="region" aria-label="Lịch sử dụng trong tuần"><div id="schedule" class="schedule-grid"><div class="schedule-line schedule-hours">${hourLabels}</div>${rows}</div></div>
      <div class="schedule-legend"><span><i class="swatch" aria-hidden="true"></i>Được phép sử dụng</span><span><i class="swatch swatch-locked" aria-hidden="true"></i>Khung giờ khóa máy</span></div>
      <div id="schedule-warning" class="schedule-warning" role="status" hidden></div>
      <button class="primary" data-action="save-schedule">Lưu lịch sử dụng</button>`;
    return `<div class="stack time-settings">${panel('Hạn mức dùng chung',quotaForm)}${panel('Lịch sử dụng trong tuần',schedule,weekActions)}</div>`;
  }

  function quotaDraft(form) {
    return Object.fromEntries(Object.entries(quotaNames).map(([name,key]) => [key,Math.round(form.elements[name].valueAsNumber*60)]));
  }

  function validateTimeSettings() {
    const form = $('#quota-form');
    if (!form) return false;
    const draft = quotaDraft(form);
    const excessive = draft.entertainment_quota_sec > Math.min(draft.weekday_quota_sec,draft.weekend_quota_sec);
    const input = form.elements.entertainment;
    input.setCustomValidity(excessive ? quotaError : '');
    input.setAttribute('aria-invalid',String(excessive));
    const error = $('#quota-error');
    error.hidden = !excessive;
    error.textContent = excessive ? quotaError : '';
    const valid = form.matches(':valid');
    form.querySelector('button').disabled = !valid || form.dataset.saving === 'true';

    const warnings = new Map();
    state.scheduleDraft.forEach((slots,day) => {
      const total = dayMinutes(slots);
      $(`[data-total-day="${day}"]`).textContent = dayTotal(total);
      const input = form.elements[day<5 ? 'weekday' : 'weekend'];
      const limit = Math.round(input.valueAsNumber*60);
      if (input.validity.valid && total>0 && total*60<limit) {
        if (!warnings.has(limit)) warnings.set(limit,[]);
        warnings.get(limit).push(scheduleDays[day]);
      }
    });
    const warning = $('#schedule-warning');
    const format = new Intl.NumberFormat('vi-VN',{maximumFractionDigits:2});
    const content = [...warnings].map(([limit,days]) => `<p><strong>Lưu ý:</strong> Tổng khung giờ mở máy của ${days.join(', ')} đang ít hơn Hạn mức ngày (${format.format(limit/60)} phút). Trong những ngày này, máy của con sẽ khóa sớm ngay khi hết khung giờ xanh.</p>`).join('');
    if (warning.innerHTML !== content) warning.innerHTML = content;
    warning.hidden = !content;
    return valid;
  }

  let timeSave = Promise.resolve();
  function saveTimeSettings(changes) {
    const scope = state;
    const endpoint = base()+'/policy';
    const save = timeSave.then(async () => {
      const result = await api(endpoint,'PUT',{...scope.policy,...changes});
      Object.assign(scope.policy,changes);
      scope.version = result.version;
      if (state === scope && $('#quota-form')) notice('Đã lưu quy tắc. Đang chờ máy của con nhận và áp dụng.');
    });
    timeSave = save.catch(()=>{});
    return save;
  }

  const groupLabels = {
    study:['Học tập','study'],
    games:['Trò chơi','gamepad'],
    video:['Xem video & Giải trí','video'],
    social:['Mạng xã hội & Trình duyệt','social'],
    blocked:['Ứng dụng chặn tuyệt đối','shield']
  };
  const groupModes = {
    daily:'Chỉ dùng hạn mức ngày',
    entertainment:'Trừ quỹ giải trí',
    custom:'Hạn mức riêng của nhóm'
  };
  const clockLabel = value => String(Math.floor(value/60)).padStart(2,'0')+':'+String(value%60).padStart(2,'0');
  const clockMinute = value => /^\d{2}:\d{2}$/.test(value) ? Number(value.slice(0,2))*60+Number(value.slice(3)) : NaN;

  function groupBadges(key, group) {
    if (key==='blocked') return '<span class="group-badge group-badge-danger">Luôn khóa</span>';
    const mode = group.mode==='custom' ? minutes(group.quota_sec)+' mỗi ngày cho nhóm' :
      group.mode==='entertainment' ? 'Trừ quỹ giải trí • Tự khóa khi hết giờ' : 'Không trừ quỹ giải trí';
    const window = group.window;
    const hours = window ? [window.days.length===7?'':window.days.map(day=>shortDays[day]).join(', '),
      clockLabel(window.start_minute)+' – '+clockLabel(window.end_minute)].filter(Boolean).join(' • ') : 'Theo lịch chung';
    const exhausted = group.enabled && group.mode==='entertainment' && state.today.entertainment_today?.remaining_sec===0;
    const groupExhausted = group.enabled && group.mode==='custom' && (state.today.app_group_today_seconds?.[key]||0)>=group.quota_sec;
    const locked = !group.enabled ? 'Đã khóa nhóm' : exhausted ? 'Đã khóa do hết giờ giải trí' :
      groupExhausted ? 'Đã khóa do hết giờ của nhóm' : '';
    return `<span class="group-badge">${mode}</span><span class="group-badge">${hours}</span>${locked?`<span class="group-badge group-badge-danger">${locked}</span>`:''}`;
  }

  function groupPreview(key, group) {
    const legacy = key==='games' ? state.policy.entertainment_apps : [];
    const names = [...new Set([...group.apps.map(app=>app.name),...legacy])];
    const identity = legacy.length ? 'Có ứng dụng cũ chỉ nhận diện theo tên' : 'Nhận diện SHA-256 ✓';
    const preview = names.length ? names.slice(0,3).join(', ')+(names.length>3?` +${names.length-3}`:'') : 'Chưa thêm ứng dụng';
    return `<p>${names.length} ứng dụng • ${identity}</p><p class="group-preview" title="${esc(preview)}">${esc(preview)}</p>`;
  }

  function groupMembers(group, legacy) {
    const entries = [...group.apps, ...legacy.map(name=>({name}))];
    if (!entries.length) return '<p class="muted">Chưa có ứng dụng trong nhóm.</p>';
    return entries.map((app,index)=>`<div class="group-member"><strong>${esc(app.name)}</strong>
      <code class="group-badge" title="${esc(app.sha256||'')}" >${app.sha256?'SHA-256 '+esc(app.sha256.slice(0,12))+'…':'Chỉ tên tệp'}</code>
      <button type="button" class="group-remove" data-remove-app="${index}" aria-label="Xóa ${esc(app.name)}">×</button></div>`).join('');
  }

  function groupEditor(key, group) {
    const window = group.window;
    const legacy = key==='games' ? state.policy.entertainment_apps : [];
    const restrictions = key==='blocked' ? '<p class="muted">Nhóm này luôn khóa, kể cả trong giờ sử dụng được phép.</p>' : `
      <div class="group-editor-grid">
        <fieldset><legend>A. Cách tính thời gian</legend>
          <label>Chế độ<select name="mode">${Object.entries(groupModes).map(([mode,label])=>`<option value="${mode}" ${group.mode===mode?'selected':''}>${label}</option>`).join('')}</select></label>
          <p class="muted" data-entertainment-help ${group.mode==='entertainment'?'':'hidden'}>Nhóm tự khóa khi hết quỹ giải trí trong ngày.</p>
          <label data-custom-limit ${group.mode==='custom'?'':'hidden'}>Hạn mức riêng · phút<input type="number" name="quota" min="0" max="1440" step="any" value="${(group.quota_sec??1800)/60}" ${group.mode==='custom'?'':'disabled'}></label>
        </fieldset>
        <fieldset><legend>B. Ngày và khung giờ</legend>
          <label>Lịch sử dụng<select name="window"><option value="shared">Dùng theo lịch tuần chung</option><option value="own" ${window?'selected':''}>Khung giờ riêng</option></select></label>
          <div class="group-window" ${window?'':'hidden'}>
            <div class="group-days" role="group" aria-label="Ngày được phép">${shortDays.map((day,i)=>`<label class="check"><input name="day" value="${i}" type="checkbox" ${!window||window.days.includes(i)?'checked':''}>${day}</label>`).join('')}</div>
            <div class="form-grid"><label>Bắt đầu<input name="start" type="time" value="${clockLabel(window?.start_minute??1080)}"></label><label>Kết thúc<input name="end" type="time" value="${clockLabel(window?.end_minute===1440?0:window?.end_minute??1260)}"></label></div>
            <p class="muted">Khung giờ riêng áp dụng trong lịch chung. Chọn kết thúc 00:00 để dùng đến hết ngày.</p>
          </div>
        </fieldset>
      </div>`;
    return `<form class="group-editor" id="group-form-${key}" data-group-form="${key}" hidden>${restrictions}
      <fieldset><legend>C. Ứng dụng và mã SHA-256</legend>
        <div class="group-members">${groupMembers(group,legacy)}</div>
        <div class="group-app-inputs"><label>Tên tệp .exe<input name="app_name" maxlength="100" placeholder="Ví dụ: game.exe" autocomplete="off"></label>
          <label>Mã SHA-256<input name="app_hash" maxlength="64" spellcheck="false" autocomplete="off" placeholder="64 ký tự hex"></label></div>
        <input name="exe_file" type="file" accept=".exe" hidden>
        <div class="actions group-app-actions"><button type="button" data-group-action="choose">${icon('folder')} Chọn tệp .exe</button>
          <button type="button" data-group-action="add">+ Thêm vào nhóm</button></div>
        <p class="muted">Mã băm được tính trong trình duyệt. Tệp ở lại trên máy này.</p>
        ${['social','video'].includes(key)?'<p class="muted">Nếu thêm trình duyệt, cả thời gian dùng trình duyệt sẽ thuộc nhóm này. Quy tắc từng tên miền nằm ở Lọc website.</p>':''}
      </fieldset>
      <fieldset><legend>D. Lời nhắn cho con khi ứng dụng bị khóa</legend>
        <label>Lời nhắn<textarea name="message" maxlength="280" rows="2" placeholder="Ví dụ: Con vẫn có thể dùng ứng dụng học tập nhé.">${esc(group.message)}</textarea></label>
      </fieldset>
      <p class="group-form-status" role="status" hidden></p><button type="submit" class="primary">Lưu cấu hình nhóm</button>
    </form>`;
  }

  function appView() {
    state.groupDrafts = {};
    const groups = Object.entries(groupLabels).map(([key,[name,symbol]])=>{
      const group = state.policy.app_groups[key];
      return `<section class="panel app-group" data-app-group="${key}">
        <div class="group-row">
          <div class="group-identity"><div class="group-icon">${icon(symbol)}</div><div>
            <h2>${name}</h2><div class="group-meta">${groupPreview(key,group)}</div>
          </div></div>
          <div class="group-badges">${groupBadges(key,group)}</div>
          <div class="group-actions">
            <button class="group-config" type="button" data-group-action="config" aria-expanded="false" aria-controls="group-form-${key}">${icon('settings')} Cấu hình</button>
            <button class="group-toggle" type="button" data-group-action="toggle" role="switch" aria-label="Cho phép nhóm ${name}" aria-checked="${group.enabled}" ${key==='blocked'?'disabled':''}>
              <span class="group-switch" aria-hidden="true"></span><span data-toggle-label>${group.enabled?'Bật':'Tắt'}</span>
            </button>
          </div>
        </div>${groupEditor(key,group)}
      </section>`;
    }).join('');
    const legacy = `<details class="panel legacy-app-rules"><summary>Quy tắc ứng dụng nâng cao</summary>
      <form id="apps-form"><p>Quy tắc ở đây áp dụng cùng với năm nhóm phía trên.</p>
        <label>Chế độ<select name="mode"><option value="blocklist" ${state.policy.app_mode==='blocklist'?'selected':''}>Chặn theo danh sách</option><option value="allowlist" ${state.policy.app_mode==='allowlist'?'selected':''}>Chỉ cho phép theo danh sách</option></select></label>
        <label>Danh sách · mỗi dòng: ten.exe, SHA256<textarea name="rules" spellcheck="false" rows="4">${esc(state.policy.apps.map(a=>a.name+', '+a.sha256).join('\n'))}</textarea></label>
        <div class="actions"><button class="primary">Lưu quy tắc ứng dụng</button></div>
      </form></details>`;
    return `<div class="stack app-groups">${groups}${legacy}</div>`;
  }

  function syncSwitch(toggle, enabled) {
    toggle.setAttribute('aria-checked',String(enabled));
    toggle.querySelector('[data-toggle-label]').textContent = enabled?'Bật':'Tắt';
  }

  function refreshGroupRow(card) {
    const key = card.dataset.appGroup;
    const group = state.policy.app_groups[key];
    card.querySelector('.group-badges').innerHTML = groupBadges(key,group);
    card.querySelector('.group-meta').innerHTML = groupPreview(key,group);
    syncSwitch(card.querySelector('.group-toggle'),group.enabled);
  }

  async function refreshGroupUsage() {
    const scope = state;
    try {
      const report = await api(base()+'/reports?days=1');
      if (scope===state && document.body.dataset.view==='apps') {
        state.today = report;
        document.querySelectorAll('[data-app-group]').forEach(refreshGroupRow);
        if ($('#freshness')) $('#freshness').textContent = 'Cập nhật '+new Date().toLocaleTimeString('vi-VN');
      }
    } catch {
      // Retain the last report until the next refresh.
    } finally {
      if (scope===state && document.body.dataset.view==='apps') scheduleRefresh();
    }
  }

  function groupStatus(form, message, error=false) {
    const status = form.querySelector('.group-form-status');
    status.textContent = message;
    status.hidden = !message;
    status.classList.toggle('error',error);
  }

  function groupDraft(key) {
    return state.groupDrafts[key] ??= {
      apps: state.policy.app_groups[key].apps.map(app=>({...app})),
      legacy: key==='games' ? [...state.policy.entertainment_apps] : []
    };
  }

  function addGroupApp(form, draft) {
    const name = form.elements.app_name.value.trim();
    const sha256 = form.elements.app_hash.value.trim().toLowerCase();
    if (!/^[\p{L}\p{M}\p{N}_. -]+\.exe$/iu.test(name)||!/^[\da-f]{64}$/.test(sha256)) {
      throw Error('Nhập tên .exe và mã SHA-256 gồm 64 ký tự hex.');
    }
    if (draft.apps.some(app=>app.name.toLowerCase()===name.toLowerCase()||app.sha256.toLowerCase()===sha256)) {
      throw Error('Tên tệp hoặc mã SHA-256 đã có trong nhóm.');
    }
    draft.apps.push({name,sha256});
    draft.legacy = draft.legacy.filter(app=>app.toLowerCase()!==name.toLowerCase());
    form.elements.app_name.value = form.elements.app_hash.value = '';
    form.querySelector('.group-members').innerHTML = groupMembers(draft,draft.legacy);
    groupStatus(form,'Đã thêm vào bản nháp. Bấm Lưu cấu hình nhóm để áp dụng.');
  }

  async function hashGroupApp(input) {
    const file = input.files[0], form = input.form;
    if (!file) return;
    const add = form.querySelector('[data-group-action="add"]');
    add.disabled = true;
    try {
      if (!/\.exe$/i.test(file.name)||file.name.length>100) throw Error('Chọn tệp .exe có tên tối đa 100 ký tự.');
      if (!globalThis.crypto?.subtle) throw Error('Cần mở trang HTTPS tin cậy để tính mã băm. Bạn có thể nhập mã thủ công.');
      if (file.size>256*1024*1024) throw Error('Tệp lớn hơn 256 MB. Hãy nhập mã SHA-256 thủ công.');
      groupStatus(form,'Đang tính SHA-256…');
      const digest = await crypto.subtle.digest('SHA-256',await file.arrayBuffer());
      if (input.files[0]!==file||!form.isConnected) return;
      form.elements.app_name.value = file.name;
      form.elements.app_hash.value = [...new Uint8Array(digest)].map(byte=>byte.toString(16).padStart(2,'0')).join('');
      groupStatus(form,'Đã tính mã băm. Bấm Thêm vào nhóm để tiếp tục.');
    } catch (error) {
      if(input.files[0]===file) groupStatus(form,error.message,true);
    } finally {
      if (input.files[0]===file) {
        input.value = '';
        add.disabled = false;
      }
    }
  }

  function readGroupSettings(form, key) {
    const fields = form.elements;
    const draft = groupDraft(key);
    const current = state.policy.app_groups[key];
    const updated = {...current, apps:[...draft.apps], message:fields.message.value.trim()};
    if (key==='blocked') return updated;
    updated.mode = fields.mode.value;
    updated.quota_sec = null;
    updated.window = null;
    if (updated.mode==='custom') {
      if (!fields.quota.validity.valid||!Number.isFinite(fields.quota.valueAsNumber)) throw Error('Nhập hạn mức nhóm từ 0 đến 1440 phút.');
      updated.quota_sec = Math.round(fields.quota.valueAsNumber*60);
    }
    if (fields.window.value==='own') {
      const days = new FormData(form).getAll('day').map(Number);
      const start = clockMinute(fields.start.value);
      const end = fields.end.value==='00:00' ? 1440 : clockMinute(fields.end.value);
      if (!days.length||!(end>start)) throw Error('Chọn ít nhất một ngày và giờ kết thúc sau giờ bắt đầu.');
      updated.window = {days,start_minute:start,end_minute:end};
    }
    return updated;
  }

  async function saveAppGroup(card, updated, legacy) {
    const scope = state, key = card.dataset.appGroup;
    if (scope.groupSaving) return;
    scope.groupSaving = true;
    const buttons = [...document.querySelectorAll('.group-toggle:not(:disabled),.group-editor button[type=submit]')];
    buttons.forEach(button=>button.disabled=true);
    try {
      const changes = {app_groups:{...scope.policy.app_groups,[key]:updated}};
      const assignedNames = new Set(Object.values(changes.app_groups).flatMap(group=>group.apps.map(app=>app.name.toLowerCase())));
      changes.entertainment_apps = (legacy??scope.policy.entertainment_apps).filter(name=>!assignedNames.has(name.toLowerCase()));
      const result = await api(base()+'/policy','PUT',{...scope.policy,...changes});
      Object.assign(scope.policy,changes);
      scope.version = result.version;
      if (scope===state && card.isConnected) {
        refreshGroupRow(card);
        if (key!=='games') {
          const games = document.querySelector('[data-app-group="games"]');
          refreshGroupRow(games);
          const draft = scope.groupDrafts.games;
          if (draft) {
            draft.legacy = draft.legacy.filter(name=>!assignedNames.has(name.toLowerCase()));
            games.querySelector('.group-members').innerHTML = groupMembers(draft,draft.legacy);
          } else {
            games.querySelector('.group-members').innerHTML = groupMembers(scope.policy.app_groups.games,scope.policy.entertainment_apps);
          }
        }
        notice('Đã lưu cấu hình nhóm. Đang chờ máy của con nhận quy tắc.');
      }
    } finally {
      scope.groupSaving = false;
      buttons.forEach(button=>button.disabled=false);
    }
  }

  async function groupAction(button) {
    const card = button.closest('[data-app-group]'), key = card.dataset.appGroup;
    const form = card.querySelector('form');
    try {
      if (button.dataset.removeApp!==undefined) {
        const draft = groupDraft(key), index = Number(button.dataset.removeApp);
        if (index<draft.apps.length) draft.apps.splice(index,1);
        else draft.legacy.splice(index-draft.apps.length,1);
        form.querySelector('.group-members').innerHTML = groupMembers(draft,draft.legacy);
        groupStatus(form,'Đã xóa khỏi bản nháp. Bấm Lưu cấu hình nhóm để áp dụng.');
        form.querySelector('[data-group-action="add"]').focus();
        return;
      }
      switch (button.dataset.groupAction) {
        case 'config':
          form.hidden = !form.hidden;
          button.setAttribute('aria-expanded',String(!form.hidden));
          break;
        case 'toggle': {
          const group = state.policy.app_groups[key];
          if (key!=='blocked') await saveAppGroup(card,{...group,enabled:!group.enabled});
          break;
        }
        case 'choose': form.elements.exe_file.click(); break;
        case 'add': addGroupApp(form,groupDraft(key)); break;
      }
    } catch (error) {
      if (form.hidden) notice(error.message,true);
      else groupStatus(form,error.message,true);
    }
  }
  const webSymbols = {education:'graduate',entertainment:'video',social:'social',games:'gamepad',
    age_inappropriate:'shield',unclassified:'globe',safesearch:'search'};
  const domainInputError = 'Chỉ nhập tên miền (ví dụ: facebook.com), không nhập đường dẫn.';

  function webSwitch(key, name, enabled) {
    const label = key==='safesearch' ? 'Bật SafeSearch' : 'Chặn danh mục '+name;
    return `<li class="web-category"><div class="web-category-name">
      <span class="group-icon web-icon web-icon-${key}">${icon(webSymbols[key])}</span><strong>${name}</strong>
      </div><button class="group-toggle" type="button" role="switch" data-web-switch="${key}"
        aria-label="${label}" aria-checked="${enabled}"><span class="group-switch" aria-hidden="true"></span>
        <span data-toggle-label>${enabled?'Bật':'Tắt'}</span></button></li>`;
  }

  function webDomainTags(domains) {
    const names = [...new Set(domains)];
    if (!names.length) return '<p class="web-empty">Chưa có tên miền chặn riêng.</p>';
    return `<ul class="web-tags" aria-label="Tên miền chặn riêng">${names.map(name=>
      `<li class="web-tag"><span>${esc(name)}</span><button type="button" data-web-remove="${esc(name)}"
      aria-label="Bỏ chặn riêng ${esc(name)}">×</button></li>`).join('')}</ul>`;
  }

  function webView() {
    const categoryRows = Object.entries(categories).map(([key,name]) =>
      webSwitch(key,name,state.policy.blocked_categories.includes(key)));
    categoryRows.push(webSwitch('safesearch','Bật SafeSearch',state.policy.safesearch));
    return `<div class="equal-col web-layout">
      ${panel('Lọc theo danh mục',`<ul id="web-categories" class="web-category-list">${categoryRows.join('')}</ul>`)}
      ${panel('Tên miền chặn riêng',`<form id="web-domain-form" novalidate>
        <label for="web-domain">Tên miền hoặc liên kết</label>
        <div class="web-add"><input id="web-domain" name="host" type="text" placeholder="facebook.com"
          autocomplete="off" spellcheck="false" inputmode="url" aria-describedby="web-domain-error">
          <button type="submit" class="primary">+ Thêm chặn</button></div>
        <p id="web-domain-error" role="alert" hidden></p>
        </form><div id="web-domain-tags" aria-live="polite">${webDomainTags(state.policy.blocked_domains)}</div>`)}
      </div>`;
  }

  function webHostname(value) {
    const text = value.trim();
    if (!text || /[\\\s\u0000-\u001f\u007f]/u.test(text)) throw Error(domainInputError);
    const address = text.startsWith('//') ? 'https:'+text :
      /^[a-z][a-z\d+.-]*:\/\//i.test(text) ? text : 'https://'+text;
    if (!/^https?:\/\/[^/?#]/i.test(address)) throw Error(domainInputError);
    let url;
    try { url = new URL(address); } catch { throw Error(domainInputError); }
    const host = url.hostname.replace(/\.$/,'');
    if (url.username || url.password || host.length>253 || !host.includes('.') ||
        /^\d+(\.\d+){3}$/.test(host) ||
        host.split('.').some(label=>!/^[a-z\d](?:[a-z\d-]{0,61}[a-z\d])?$/i.test(label))) {
      throw Error(domainInputError);
    }
    return host;
  }

  function domainError(input, message='') {
    const error = input.form.querySelector('#web-domain-error');
    error.hidden = !message;
    error.textContent = message;
    input.setAttribute('aria-invalid',String(!!message));
  }

  async function normalizeWebInput(input) {
    domainError(input);
    if (!input.value.trim()) return;
    let host;
    try { host = webHostname(input.value); } catch (error) {
      domainError(input,error.message);
      return;
    }
    input.value = host;
    try {
      const result = await api(base()+'/web/domain?host='+encodeURIComponent(host));
      if (input.isConnected && input.value===host) input.value = result.domain;
    } catch (error) {
      if (input.isConnected && input.value===host) {
        domainError(input,error.message===domainInputError ? domainInputError : 'Chưa chuẩn hóa được tên miền. Hãy thử lại.');
      }
    }
  }

  let webSave = Promise.resolve();
  function saveWebChange(change) {
    const scope = state;
    const endpoint = base()+'/web';
    const save = webSave.then(async ()=>{
      const response = await api(endpoint,'PATCH',change);
      const {version,...updated} = response;
      const domainsChanged = JSON.stringify(scope.policy.blocked_domains)!==JSON.stringify(updated.blocked_domains);
      Object.assign(scope.policy,updated);
      scope.version = version;
      if (scope!==state || !$('#web-categories')) return;
      document.querySelectorAll('[data-web-switch]').forEach(toggle=>{
        const key = toggle.dataset.webSwitch;
        syncSwitch(toggle,key==='safesearch' ? updated.safesearch : updated.blocked_categories.includes(key));
      });
      if (domainsChanged) $('#web-domain-tags').innerHTML = webDomainTags(updated.blocked_domains);
      notice(change.action==='add_domain' && !domainsChanged ? 'Tên miền đã có trong danh sách chặn riêng.' :
        'Đã lưu bộ lọc. Đang chờ máy của con nhận quy tắc.');
      $('#freshness').textContent = 'Cập nhật '+new Date().toLocaleTimeString('vi-VN');
    });
    webSave = save.catch(()=>{});
    return save;
  }

  async function submitWebDomain(form) {
    const input = form.elements.host;
    const button = form.querySelector('button');
    if (button.disabled) return;
    domainError(input);
    button.disabled = input.readOnly = true;
    try {
      const host = webHostname(input.value);
      input.value = host;
      await saveWebChange({action:'add_domain',host});
      if (input.isConnected) input.value = '';
    } catch (error) {
      if (input.isConnected) domainError(input,error.message);
    } finally {
      button.disabled = input.readOnly = false;
    }
  }

  async function webAction(button) {
    const key = button.dataset.webSwitch;
    const host = button.dataset.webRemove;
    const enabled = button.getAttribute('aria-checked')!=='true';
    const change = key==='safesearch' ? {action:key,enabled} :
      key ? {action:'category',category:key,enabled} : {action:'remove_domain',host};
    const restoreFocus = !key && document.activeElement===button;
    button.disabled = true;
    try {
      await saveWebChange(change);
      if (restoreFocus && document.activeElement===document.body) {
        ($('#web-domain-tags button')||$('#web-domain'))?.focus();
      }
    } catch (error) {
      if (document.body.dataset.view==='web') notice(error.message,true);
    } finally {
      button.disabled = false;
    }
  }
  function requestsView() {
    const all=new Map();
    for(const r of [...state.week.requests,...pendingRequests()])all.set(r.device_id+'-'+r.ts,r);
    const requests=[...all.values()].sort((a,b)=>b.ts.localeCompare(a.ts));
    const content=requests.length?requests.map(r=>`<div class="row"><div class="row-name"><h3>Con xin thêm ${r.requested_minutes??15} phút</h3><small>${esc(stamp(r.ts))} · ${esc(state.devices.find(d=>d.id===r.device_id)?.name||'Thiết bị')}</small></div>${r.status==='sent'?'<span class="state">Đã duyệt · Chờ máy xác nhận</span>':r.status==='acknowledged'?'<span class="state online">Máy đã xác nhận</span>':`<button data-command="add_time" data-device="${esc(r.device_id)}" data-request="${esc(r.ts)}">Đồng ý +${r.requested_minutes??15} phút</button>`}</div>`).join(''):empty('Chưa có yêu cầu xin thêm giờ.');
    return `<div class="stack">${panel('Lời nhắn xin thêm giờ',content)}${panel('Lệnh đã gửi',state.commands?.length?state.commands.map(c=>row(commandTitle(c.type,c.payload?.seconds),`<span class="state ${c.ack?'online':''}">${c.ack?'Máy đã xác nhận':'Chờ máy xác nhận'}</span>`,stamp(c.created))).join(''):empty('Chưa có lệnh được gửi.'))}</div>`;
  }
  function devicesView() {
    const childApp = '<p>Sau khi ghép đôi, con mở KidSafe trên máy Windows để xem thời gian, hoạt động trong ngày và xin thêm giờ.</p><p>Con không cần tài khoản web. Bấm biểu tượng KidSafe ở khay hệ thống để mở lại màn hình Hôm nay của em.</p>';
    const actions = `<div class="actions"><button class="primary" data-action="enroll">Tạo mã ghép đôi</button>
      <button type="button" data-action="pairing-profile">Tải tệp kết nối</button>
      <a class="soft-button" href="/download" hx-boost="false">Bộ cài Windows ↗</a>
      ${state.devices.some(d=>!d.revoked)?'<button data-action="allocation">Đổi phần chia offline</button>':''}</div>`;
    const revoke = state.devices.filter(d=>!d.revoked).map(d=>row(d.name,`<button class="danger" data-revoke="${esc(d.id)}">Thu hồi</button>`)).join('');
    return `<div class="stack">${panel('Máy của con',deviceRows()+actions)}${panel('App KidSafe của con',childApp)}${panel('Thu hồi thiết bị',revoke||empty('Chưa có thiết bị để thu hồi.'))}</div>`;
  }

  function reportsView() {
    const download = `<a class="soft-button report-export" href="/api/${esc(base())}/reports.csv" download hx-boost="false">${icon('download')} Xuất báo cáo (CSV)</a>`;
    const days = Object.entries(state.week.daily_seconds).sort().reverse().map(([day,value])=>row(day,minutes(value),`Trong đó giờ ngoại lệ: ${minutes(state.week.exception_seconds[day]||0)}`)).join('');
    return `<div class="stack report-layout">${panel('Thời lượng trong 7 ngày',chart({guides:true}),download)}
      <div class="equal-col reports-top">${panel('10 ứng dụng dùng nhiều nhất',list(state.week.top_apps,minutes))}
      ${panel('10 tên miền truy vấn nhiều nhất',list(state.week.top_domains,n=>n+' lượt'))}</div>
      ${panel('Theo từng ngày',days||empty('Chưa có thời lượng được đồng bộ.'))}</div>`;
  }
  const auditTitle = 'Những thay đổi liên quan đến con';
  function auditTimeline(entries, timezone) {
    if (!entries.length) return empty('Chưa có thay đổi được ghi nhận.');
    const clock = new Intl.DateTimeFormat('vi-VN',{timeZone:timezone,hour:'2-digit',minute:'2-digit',hourCycle:'h23'});
    const day = new Intl.DateTimeFormat('vi-VN',{timeZone:timezone,day:'2-digit',month:'2-digit'});
    return `<ol class="audit-timeline">${entries.slice(0,10).map(entry=>{
      const symbol = ['clock','lock','unlock','device','settings'].includes(entry.icon)?entry.icon:'settings';
      const timestamp = new Date(entry.ts);
      const dateParts = day.formatToParts(timestamp);
      const dateLabel = ['day','month'].map(part=>dateParts.find(value=>value.type===part).value).join('/');
      return `<li class="audit-item"><span class="audit-icon audit-icon-${symbol}">${icon(symbol)}</span>
        <span class="audit-message">${esc(entry.message)}</span>
        <time datetime="${esc(entry.ts)}">${esc(clock.format(timestamp)+' '+dateLabel)}</time></li>`;
    }).join('')}</ol>`;
  }

  function auditPanel() {
    return panel(auditTitle,auditTimeline(state.audit,state.policy.timezone));
  }
  function privacyView(){return `<div class="stack">${panel('Minh bạch với con',`<p>KidSafe chỉ ghi thời gian, ứng dụng và tên miền tối thiểu để thực hiện quy tắc. Không ghi nội dung chat, ảnh màn hình, phím bấm hoặc URL đầy đủ.</p><p>Dữ liệu hoạt động được giữ tối đa 90 ngày. Con có thể xem cùng dữ liệu hoạt động và các thay đổi liên quan đến mình.</p>`)}${auditPanel()}${panel('Xóa dữ liệu của con',`<p>Xóa dữ liệu trên server ngay và gửi lệnh xóa tới các máy. Máy đang offline cần kết nối lại và xác nhận. Việc xóa không thể hoàn tác.</p><button class="danger" data-action="delete-child">Xóa toàn bộ dữ liệu của con</button>`)}</div>`;}

  function childEmpty(kind) {
    const apps = kind==='apps';
    const art = apps ? `<ellipse cx="44" cy="37" rx="35" ry="21" fill="#f0ebfa"/>
      <path d="M23 44c0-13 8-19 18-19 11 0 20 7 20 17 0 6-8 11-19 11-10 0-19-4-19-9Z" fill="#baa6d7"/>
      <path d="m38 32 2-15 11 8 11-6 1 14c2 12-5 16-13 16-9 0-15-5-12-17Z" fill="#d6c7ec"/>
      <path d="M44 36q2 3 5 0m5 0q2 3 5 0m-9 5 2 1 2-1m6 7c8 1 13-2 13-8" fill="none" stroke="#75598f" stroke-width="2" stroke-linecap="round"/>
      <path d="M68 21h8l-8 8h8" fill="none" stroke="#9a82b5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`
      : `<ellipse cx="44" cy="38" rx="35" ry="20" fill="#e9f2f6"/>
      <path d="m21 36 8-14h30l8 14v14a4 4 0 0 1-4 4H25a4 4 0 0 1-4-4Z" fill="#bcd9e6" stroke="#6c97ab" stroke-width="2" stroke-linejoin="round"/>
      <path d="M22 37h13l3 6h12l3-6h13" fill="#e9f4f7" stroke="#6c97ab" stroke-width="2" stroke-linejoin="round"/>
      <path d="M44 9v7m-9-4 3 5m15-5-3 5" stroke="#d7a65e" stroke-width="2" stroke-linecap="round"/>`;
    const message = apps ? 'Chưa thấy ứng dụng nào được dùng hôm nay.' : 'Chưa thấy trang web nào được dùng hôm nay.';
    return `<div class="child-empty"><svg viewBox="0 0 88 64" aria-hidden="true">${art}</svg><p>${message}</p></div>`;
  }

  function childView() {
    const used = state.today.normal_seconds ?? state.today.total_seconds;
    const total = quota() + (state.today.extra_granted_seconds || 0);
    const remaining = Math.max(0,total-used);
    const ratio = total ? Math.min(1,remaining/total) : 0;
    const level = ratio<=.15 ? 'red' : ratio<=.35 ? 'orange' : 'green';
    const entertainment = state.today.entertainment_today;
    const missingReports = entertainment.devices_count>entertainment.reporting_devices;
    const awaitingReports = missingReports&&entertainment.reporting_devices===0;
    const entertainmentRatio = entertainment.quota_sec ? entertainment.remaining_sec/entertainment.quota_sec : 0;
    const entertainmentLabel = awaitingReports ? 'Đang chờ dữ liệu' :
      (missingReports ? 'Tạm tính còn ' : 'Còn ')+minutes(entertainment.remaining_sec);
    const bear = `<svg class="child-illustration" viewBox="0 0 160 150" aria-hidden="true">
      <circle cx="83" cy="73" r="58" fill="#fbe4a7"/>
      <path d="M25 110l-8 2m120-63 9-4M40 22l-4-8" stroke="#e1a647" stroke-width="3" stroke-linecap="round"/>
      <circle cx="48" cy="54" r="15" fill="#75a98e"/><circle cx="112" cy="54" r="15" fill="#75a98e"/>
      <circle cx="48" cy="54" r="7" fill="#b7d7ae"/><circle cx="112" cy="54" r="7" fill="#b7d7ae"/>
      <path d="M35 88c0-26 18-42 45-42s45 16 45 42c0 24-17 35-45 35S35 112 35 88Z" fill="#87b59b"/>
      <ellipse cx="80" cy="96" rx="21" ry="16" fill="#e6f0d9"/>
      <circle cx="64" cy="78" r="3.5" fill="#254840"/><circle cx="96" cy="78" r="3.5" fill="#254840"/>
      <path d="M75 91q5-4 10 0l-5 5Z" fill="#254840"/>
      <path d="M80 96q0 5-5 5m5-5q0 5 5 5" stroke="#254840" stroke-width="2" fill="none" stroke-linecap="round"/>
      <ellipse cx="53" cy="91" rx="6" ry="3" fill="#e9b8a1"/><ellipse cx="107" cy="91" rx="6" ry="3" fill="#e9b8a1"/>
    </svg>`;
    return `<div class="child-today">
      <section class="panel child-time">
        <div class="child-remaining"><h2>Thời gian hôm nay</h2>
          <div class="child-time-number"><span>Còn</span> <strong>${Math.floor(remaining/60)}</strong> <span>phút</span></div></div>
        <div class="child-time-actions">
          <progress max="1" value="${ratio}" data-child-level="${level}" aria-label="Thời gian còn lại" aria-valuetext="Còn ${minutes(remaining)}"></progress>
          <div class="child-entertainment">
            <div class="child-entertainment-label">${icon('gamepad')}<span>Giải trí (Trò chơi &amp; Video): <strong>${entertainmentLabel}</strong></span></div>
            ${awaitingReports?'':`<progress class="child-entertainment-progress" max="1" value="${entertainmentRatio}" aria-label="Thời gian giải trí còn lại" aria-valuetext="${entertainmentLabel}"></progress>`}
          </div>
        </div>
        ${bear}
        <button type="button" class="primary child-request-button" data-action="child-request"><span aria-hidden="true">✋</span> Xin thêm giờ</button>
      </section>
      <div class="equal-col child-activities">
        ${panel('Hôm nay em đã dùng gì?',state.today.top_apps.length?list(state.today.top_apps,minutes):childEmpty('apps'))}
        ${panel('Các trang em đã dùng',state.today.top_domains.length?list(state.today.top_domains,n=>n+' lượt'):childEmpty('web'))}
      </div>
      <div class="child-audit">${auditPanel()}</div>
    </div>`;
  }

  function showChildRequest() {
    const preview = document.body.dataset.preview==='true';
    const canSend = !preview && (state.today.entertainment_today?.devices_count||0)>0;
    const info = preview ? 'Con gửi yêu cầu ngay trong app KidSafe trên máy Windows nhé.' :
      !canSend ? 'Nhờ bố mẹ ghép máy để em có thể xin thêm giờ nhé.' : '';
    const choices = [5,10,15].map(value=>`<label class="child-minute-choice">
      <input type="radio" name="minutes" value="${value}" ${value===10?'checked':''}> <span>${value} phút</span></label>`).join('');
    modal('Xin thêm giờ',`<form id="child-request-form" data-request-key="${crypto.randomUUID()}">
      <fieldset><legend>Em muốn xin thêm bao nhiêu phút?</legend><div class="child-minute-choices">${choices}</div></fieldset>
      ${info?`<p>${info}</p>`:''}
      <button type="submit" class="primary child-request-button" ${canSend?'':'disabled'}>Gửi bố mẹ</button>
    </form>`);
  }
  async function load({background=false}={}) {
    if(background&&(loading||backgroundRefreshBlocked())){scheduleRefresh();return;}
    const selectedQuick=$('#quick-device')?.value;
    clearTimeout(timer);
    if(location.pathname.startsWith('/app/')) {
      document.body.dataset.view=location.pathname.split('/').pop();
      document.body.dataset.child=new URLSearchParams(location.search).get('child')||document.body.dataset.child;
    }
    const view=document.body.dataset.view, child=document.body.dataset.child, screen=$('#screen');
    if(!view||view==='login'||!screen)return;
    const sequence=++loadSequence;
    if(!child) {
      loading=false;
      screen.innerHTML=view==='child'?panel('Chưa có hồ sơ','<p>Nhờ bố mẹ tạo hồ sơ cho em nhé.</p>'):panel('Bắt đầu cùng con',`<p>Thêm hồ sơ, đặt lịch phù hợp rồi ghép máy của con. Mỗi con có hạn mức dùng chung cho các thiết bị.</p><button class="primary" data-action="add-child">Thêm hồ sơ đầu tiên</button>`);
      screen.removeAttribute('aria-busy');return;
    }
    loading=true;
    const scope='children/'+child;
    const current=()=>sequence===loadSequence&&screen===$('#screen')&&view===document.body.dataset.view&&child===document.body.dataset.child;
    try {
      const [p,devices,today,week,audit,childAccount]=await Promise.all([
        api(scope+'/policy'),view==='child'?[]:api(scope+'/devices'),api(scope+'/reports?days=1'),
        view==='child'?null:api(scope+'/reports?days=7'),['child','privacy'].includes(view)?api(scope+'/audit/recent'):[],
        view==='devices'?api(scope+'/account'):null
      ]);
      if(!current())return;
      const next={policy:p.policy,policyStats:p.stats,version:p.version,devices,today,week,audit,childAccount};
      if(['requests','quick-control'].includes(view)) {
        try{next.commands=await api(scope+'/commands');}catch{next.commands=[];}
      }
      if(!current())return;
      // A control can receive focus while the network request is in flight.
      if(background&&backgroundRefreshBlocked()){scheduleRefresh();return;}
      state=next;
      const renderers={overview,'quick-control':quickControlView,time:timeView,apps:appView,web:webView,requests:requestsView,devices:devicesView,reports:reportsView,privacy:privacyView,child:childView};
      screen.innerHTML=renderers[view]();
      if(selectedQuick&&[...($('#quick-device')?.options||[])].some(option=>option.value===selectedQuick))$('#quick-device').value=selectedQuick;
      quickTargetStatus();
      if(view==='time')validateTimeSettings();
      screen.removeAttribute('aria-busy');
      if(['overview','quick-control','requests','reports','child','apps'].includes(view))scheduleRefresh();
      if($('#freshness'))$('#freshness').textContent='Cập nhật '+new Date().toLocaleTimeString('vi-VN');
    } catch(error) {
      if(!current())return;
      if(background){notice('Chưa cập nhật được dữ liệu. Thông tin lần trước vẫn được giữ.',true);scheduleRefresh();return;}
      notice(error.message,true);
      screen.innerHTML=panel('Chưa tải được dữ liệu',`<p>Dữ liệu chưa được cập nhật. Kiểm tra kết nối rồi thử lại nhé.</p><button data-action="refresh">Thử lại</button>`);
      screen.removeAttribute('aria-busy');
    } finally {
      if(sequence===loadSequence)loading=false;
    }
  }
  async function savePolicy(changes){await api(base()+'/policy','PUT',{...state.policy,...changes});notice('Đã lưu quy tắc. Đang chờ máy của con nhận và áp dụng.');await load();}
  function modal(title,body,kind=''){sidebarOpen(false);const dialog=$('#modal');dialog.classList.toggle('audit-modal',kind==='audit');$('#modal-content').innerHTML=`<h2 id="modal-title">${esc(title)}</h2>${body}`;if(!dialog.open)dialog.showModal();$('#modal input')?.focus();}
  function childAccountDialog() {
    const username = state.childAccount?.username;
    const newPassword = '<label>Mật khẩu mới · ít nhất 10 ký tự<input name="password" type="password" required minlength="10" maxlength="1024" autocomplete="new-password"></label>';
    if (username) {
      modal('Làm mới mật khẩu của con',`<form id="child-password-form"><p>Tài khoản <strong>${esc(username)}</strong> sẽ cần đăng nhập lại sau khi đổi mật khẩu.</p>
        ${newPassword}<label>Nhập lại mật khẩu mới<input name="confirm_password" type="password" required minlength="10" maxlength="1024" autocomplete="new-password"></label>
        <button class="primary" type="submit">Lưu mật khẩu mới</button></form>`);
    } else {
      modal('Tạo tài khoản cho con',`<form id="account-form"><label>Tài khoản<input name="username" required maxlength="100" autocomplete="off"></label>${newPassword}<button class="primary" type="submit">Tạo tài khoản</button></form>`);
    }
  }

  async function downloadPairingProfile(button) {
    const message = button.closest('dialog')?.querySelector('#pairing-file-message');
    if (message) message.textContent = '';
    button.disabled = true;
    try {
      const response = await fetch('/app/pairing-profile');
      if (!response.ok) {
        const {detail} = await response.json().catch(() => ({}));
        throw Error(detail || 'Chưa tải được tệp kết nối.');
      }
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement('a');
      link.href = url;
      link.download = 'KidSafe-ket-noi.kidsafe';
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (error) {
      if (message?.isConnected) {
        message.textContent = error.message;
      } else {
        notice(error.message, true);
      }
    } finally {
      button.disabled = false;
    }
  }

  function showPairingCode(result, started) {
    const code = result.code.slice(0,4)+'-'+result.code.slice(4);
    $('#modal-content').innerHTML = `<h2 id="modal-title">Mã ghép đôi 8 ký tự</h2>
      <div class="pairing-code-box"><div class="enroll-code" id="pairing-code">${esc(code)}</div>
      <p id="pairing-countdown"></p><button type="button" data-action="enroll" hidden>Tạo mã mới</button></div>
      <p class="caption pairing-code-help">Chọn tệp kết nối và nhập mã này trong bộ cài trên máy của con.</p>
      <button type="button" data-action="pairing-profile">Tải tệp kết nối</button>
      <p id="pairing-file-message" role="alert"></p>`;
    const dialog = $('#modal'), timerLabel = $('#pairing-countdown'), codeLabel = $('#pairing-code');
    const deadline = started + result.expires_in*1000;
    const update = () => {
      if (!dialog.open||!timerLabel.isConnected) { clearInterval(interval); return; }
      const seconds = Math.max(0,Math.ceil((deadline-performance.now())/1000));
      const text = seconds ? 'Mã hết hạn sau '+String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0')+' phút' : 'Mã đã hết hạn';
      if (timerLabel.textContent!==text) timerLabel.textContent = text;
      if (seconds===0) {
        clearInterval(interval);
        codeLabel.textContent = '';
        codeLabel.hidden = true;
        timerLabel.nextElementSibling.hidden = false;
      }
    };
    const interval = setInterval(update,250);
    update();
    dialog.querySelector('.dialog-close')?.focus();
  }

  async function showAudit() {
    accountMenu(false,true);
    if (!document.body.dataset.child) {
      notice('Hãy chọn hồ sơ của con trước.');
      return;
    }
    const endpoint = base()+'/audit/recent', timezone = state.policy?.timezone||'Asia/Ho_Chi_Minh';
    modal(auditTitle,'<div id="audit-modal-list" tabindex="0" role="region" aria-label="Danh sách thay đổi"><p role="status">Đang tải những thay đổi liên quan đến con…</p></div>','audit');
    const content = $('#audit-modal-list'), dialog = $('#modal');
    try {
      const entries = await api(endpoint);
      if (dialog.open && content.isConnected) content.innerHTML = auditTimeline(entries,timezone);
    } catch (error) {
      if (dialog.open && content.isConnected) {
        content.innerHTML = `<p role="alert">${esc(error.message)}</p><button data-action="show-audit">Thử lại</button>`;
      }
    }
  }
  function confirmDeletion() {
    accountMenu(false,true);
    if(!document.body.dataset.child){notice('Hãy chọn hồ sơ của con trước.');return;}
    const name=$('#child-select option:checked')?.textContent||'hồ sơ đang chọn';
    modal('Xóa toàn bộ dữ liệu của con',`<form id="delete-child-confirm"><p>Bạn đang xóa dữ liệu của <strong>${esc(name)}</strong>.</p><p>Dữ liệu trên server sẽ bị xóa và lệnh xóa được gửi đến agent. Máy đang offline sẽ xử lý khi kết nối lại. Việc này không thể hoàn tác.</p><div class="dialog-actions"><button type="button" data-action="cancel-delete">Hủy</button><button type="submit" class="danger primary">Xóa toàn bộ dữ liệu của con</button></div></form>`);
    $('#modal [data-action="cancel-delete"]').focus();
  }
  async function deleteChild() {
    const id=document.body.dataset.child;
    if(!id)throw Error('Chưa chọn hồ sơ của con.');
    const result=await api(base(),'DELETE');
    clearTimeout(timer);
    $('#modal').close();
    document.body.dataset.child='';
    history.replaceState(null,'','/app/'+document.body.dataset.view);
    $('#child-select option[value="'+CSS.escape(id)+'"]')?.remove();
    if($('#child-select'))$('#child-select').value='';
    document.querySelectorAll('#account-menu [data-action="show-audit"],#account-menu [data-action="delete-child"]').forEach(b=>b.disabled=true);
    $('.child-preview')?.setAttribute('href','/child');
    $('#screen').innerHTML=panel('Đã xóa dữ liệu trên server',`<p>Còn ${result.pending_devices.length} máy chờ xác nhận xóa dữ liệu cục bộ.</p><a class="soft-button" href="/app/overview">Về danh sách hồ sơ →</a>`);
    notice('Đã gửi yêu cầu xóa đến các máy.');
    state={};
  }
  async function sendCommand(button) {
    const type=button.dataset.command||button.dataset.quickCommand;
    const deviceId=button.dataset.device||$('#quick-device')?.value;
    const device=state.devices.find(d=>d.id===deviceId&&!d.revoked);
    if(!device)throw Error('Hãy chọn một máy chưa bị thu hồi.');
    button.disabled=true;
    const key=button.dataset.request?'request-'+deviceId+'-'+button.dataset.request:crypto.randomUUID();
    const command=await api(base()+'/commands','POST',{device_id:deviceId,type},{'Idempotency-Key':key.slice(0,128)});
    notice('Đã gửi '+commandTitle(type,command.payload?.seconds).toLowerCase()+' đến '+device.name+'. Đang chờ thiết bị xác nhận.');
    await load();
    if($('#quick-device')){$('#quick-device').value=deviceId;quickTargetStatus();}
  }
  function deviceOptions(){return state.devices.filter(d=>!d.revoked).map(d=>`<option value="${esc(d.id)}">${esc(d.name)}</option>`).join('');}
  document.addEventListener('click',event=>{
    if(event.target.closest('#navigation a[href]'))sidebarOpen(false,false);
    if(!event.target.closest('.sidebar-foot'))accountMenu(false);
  });
  document.addEventListener('keydown',event=>{
    const toggle=$('[data-action="account-menu"]'), menu=$('#account-menu');
    if(!menu||!toggle)return;
    if(event.key==='Escape'&&!menu.hidden){event.preventDefault();accountMenu(false,true);return;}
    if(event.target===toggle&&event.key==='ArrowDown'){event.preventDefault();accountMenu(true);return;}
    if(menu.hidden||!menu.contains(event.target))return;
    const items=[...menu.querySelectorAll('button:not(:disabled)')],current=items.indexOf(event.target);
    if(['ArrowDown','ArrowUp','Home','End'].includes(event.key)){
      event.preventDefault();
      const next=event.key==='Home'?0:event.key==='End'?items.length-1:(current+(event.key==='ArrowDown'?1:-1)+items.length)%items.length;
      items[next]?.focus();
    }else if(event.key==='Tab')accountMenu(false,true);
  });
  document.addEventListener('submit',async event=>{const form=event.target;if(!form.id||form.method==='dialog')return;event.preventDefault();
    if(form.id==='web-domain-form'){await submitWebDomain(form);return;}
    if(form.dataset.groupForm){
      const key=form.dataset.groupForm;
      try {
        await saveAppGroup(form.closest('[data-app-group]'),readGroupSettings(form,key),key==='games'?groupDraft(key).legacy:undefined);
        groupStatus(form,'Đã lưu cấu hình nhóm.');
      } catch(error) { groupStatus(form,error.message,true); }
      return;
    }
    if(form.id==='quota-form'){if(!validateTimeSettings())return;form.dataset.saving='true';}const button=form.querySelector('button[type=submit],button:not([type])');if(button)button.disabled=true;const f=new FormData(form);try{switch(form.id){case 'login-form':{const result=await api('auth/login','POST',Object.fromEntries(f));sessionStorage.setItem('ks-csrf',result.csrf_token);location.href=result.role==='child-view'?'/child':'/app/overview';break;}case 'new-child':{const result=await api('children','POST',{name:f.get('name')});location.href='/app/devices?child='+result.id;break;}case 'quota-form':await saveTimeSettings(quotaDraft(form));break;case 'apps-form':{const apps=String(f.get('rules')).split('\n').filter(s=>s.trim()).map(line=>{const parts=line.split(',').map(x=>x.trim());if(parts.length!==2||!/^\w[\w. -]*\.exe$/i.test(parts[0])||!/^[a-f\d]{64}$/i.test(parts[1]))throw Error('Mỗi dòng cần tên .exe và mã SHA-256 gồm 64 ký tự, phân cách bằng dấu phẩy.');return {name:parts[0],sha256:parts[1].toLowerCase()};});await savePolicy({app_mode:f.get('mode'),apps});break;}case 'enroll-form':{
      if(!f.get('consent'))throw Error('Cần xác nhận sự đồng ý trước khi ghép máy.');
      const started=performance.now();
      const result=await api(base()+'/enroll-codes','POST',{consent:true});
      if(form.isConnected&&$('#modal').open)showPairingCode(result,started);
      break;
    }case 'account-form':{
      await api(base()+'/account','POST',Object.fromEntries(f));
      $('#modal').close();
      notice('Đã tạo tài khoản cho con.');
      await load();
      break;
    }case 'child-password-form':{
      if(f.get('password')!==f.get('confirm_password'))throw Error('Hai mật khẩu chưa khớp.');
      await api(base()+'/account/password','PUT',{password:f.get('password')});
      form.reset();
      $('#modal').close();
      notice('Đã làm mới mật khẩu. Con cần đăng nhập lại.');
      break;
    }case 'child-request-form':{
      if(document.body.dataset.preview==='true'||!(state.today.entertainment_today?.devices_count>0))return;
      const requested=Number(f.get('minutes'));
      await api(base()+'/requests','POST',{minutes:requested},{'Idempotency-Key':form.dataset.requestKey+'-'+requested});
      $('#modal').close();
      notice('Đã gửi lời xin thêm '+requested+' phút cho bố mẹ.');
      break;
    }case 'delete-child-confirm':await deleteChild();break;case 'allocation-form':await api(base()+'/allocation','PUT',{device_id:f.get('device'),weekday_sec:Number(f.get('weekday'))*60,weekend_sec:Number(f.get('weekend'))*60});$('#modal').close();notice('Đã gửi thay đổi phần chia. Phần giảm cần máy xác nhận; xem trạng thái lệnh trước khi cấp lại.');await load();break;}}catch(error){notice(error.message,true);if($('#modal')?.open){let note=$('#modal-content .form-error');if(!note){note=document.createElement('p');note.className='form-error';note.setAttribute('role','alert');$('#modal-content').append(note);}note.textContent=error.message;}}finally{if(form.id==='quota-form'){delete form.dataset.saving;if(form.isConnected)validateTimeSettings();}else if(button)button.disabled=false;}});
  document.addEventListener('click',async event=>{const button=event.target.closest('button');if(!button)return;if(button.dataset.webSwitch||button.dataset.webRemove){await webAction(button);return;}if(button.dataset.groupAction||button.dataset.removeApp!==undefined){await groupAction(button);return;}try{if(button.hasAttribute('data-day')){const day=Number(button.dataset.day),slot=Number(button.dataset.slot);const row=state.scheduleDraft[day];row[slot]=!row[slot];button.setAttribute('aria-pressed',String(row[slot]));validateTimeSettings();return;}if(button.dataset.command||button.dataset.quickCommand){await sendCommand(button);return;}if(button.dataset.revoke){if(!confirm('Thu hồi máy này và gửi lệnh xóa dữ liệu? Máy offline sẽ xử lý khi kết nối lại.'))return;await api(base()+'/devices/'+button.dataset.revoke,'DELETE');notice('Đã thu hồi quyền thu thập. Đang chờ máy xác nhận xóa.');await load();return;}switch(button.dataset.action){case 'account-menu':accountMenu($('#account-menu').hidden);break;case 'show-audit':await showAudit();break;case 'cancel-delete':$('#modal').close();break;case 'menu':sidebarOpen(!$('#navigation').classList.contains('open'));break;case 'close-menu':sidebarOpen(false);break;case 'logout':await api('auth/logout','POST',{});sessionStorage.removeItem('ks-csrf');location.href='/login';break;case 'refresh':await load();break;case 'add-child':modal('Thêm hồ sơ của con','<form id="new-child"><label>Tên gọi của con<input name="name" required maxlength="80" autocomplete="off"></label><button class="primary">Thêm hồ sơ</button></form>');break;case 'enroll':modal('Ghép máy của con','<form id="enroll-form"><p>Agent hiển thị biểu tượng và áp dụng lịch, hạn mức, danh sách chặn. Trẻ được biết và xem dữ liệu liên quan.</p><label class="check"><input type="checkbox" name="consent" required>Tôi là phụ huynh và đồng ý ghép thiết bị này.</label><button class="primary">Tạo mã 10 phút</button></form>');break;case 'pairing-profile':await downloadPairingProfile(button);break;case 'child-account':childAccountDialog();break;case 'allocation':modal('Đổi phần chia offline',`<form id="allocation-form"><label>Máy<select name="device">${deviceOptions()}</select></label><label>Ngày thường · phút<input name="weekday" type="number" min="0" max="1440" required></label><label>Cuối tuần · phút<input name="weekend" type="number" min="0" max="1440" required></label><p class="caption">Phần giảm cần xác nhận của máy và có hiệu lực từ ngày tiếp theo.</p><button class="primary">Gửi thay đổi</button></form>`);break;case 'schedule-all':case 'schedule-none':{
        const allowed=button.dataset.action==='schedule-all';
        state.scheduleDraft.forEach(row=>row.fill(allowed));
        document.querySelectorAll('#schedule button').forEach(slot=>slot.setAttribute('aria-pressed',String(allowed)));
        validateTimeSettings();
        break;
      }case 'save-schedule':{
        button.disabled=true;
        await saveTimeSettings({schedule:state.scheduleDraft.map(row=>[...row])});
        break;
      }case 'delete-child':confirmDeletion();break;case 'child-request':showChildRequest();break;}}catch(error){notice(error.message,true);}finally{button.disabled=false;}});
  document.addEventListener('paste',event=>{
    const input=event.target;
    if(input.id!=='web-domain'||input.readOnly||!event.clipboardData)return;
    event.preventDefault();
    input.value=event.clipboardData.getData('text/plain');
    normalizeWebInput(input);
  });
  document.addEventListener('input',event=>{
    if(event.target.form?.id==='quota-form')validateTimeSettings();
    if(event.target.id==='web-domain')domainError(event.target);
  });
  document.addEventListener('change',event=>{
    const input=event.target, form=input.form;
    if(input.id==='web-domain'&&!input.readOnly)normalizeWebInput(input);
    if(form?.dataset.groupForm){
      if(input.name==='mode'){
        form.elements.quota.disabled=input.value!=='custom';
        form.querySelector('[data-custom-limit]').hidden=form.elements.quota.disabled;
        form.querySelector('[data-entertainment-help]').hidden=input.value!=='entertainment';
      }
      if(input.name==='window')form.querySelector('.group-window').hidden=input.value!=='own';
      if(input.name==='exe_file')hashGroupApp(input);
    }
    if(event.target.id==='quick-device')quickTargetStatus();if(event.target.id==='child-select'&&event.target.value)location.href='/app/'+document.body.dataset.view+'?child='+encodeURIComponent(event.target.value);});
  document.addEventListener('DOMContentLoaded',load);
  document.addEventListener('htmx:beforeSwap',event=>{if(event.detail?.target===document.body)sidebarOpen(false,false);});
  document.addEventListener('htmx:afterSettle',event=>{if(event.target===document.body)load();});
})();
