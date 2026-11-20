(() => {
  const form = document.querySelector('[data-auth]');
  const notice = document.querySelector('#notice');
  const registering = form.dataset.auth === 'register';
  const confirm = form.elements.confirm_password;
  let saving = false;
  if (confirm) {
    const validate = () => confirm.setCustomValidity(confirm.value && confirm.value !== form.elements.password.value ? 'Hai mật khẩu chưa khớp.' : '');
    confirm.addEventListener('input', validate);
    form.elements.password.addEventListener('input', validate);
  }
  if (!registering && sessionStorage.getItem('ks-signup-complete')) {
    document.querySelector('#auth-success').hidden = false;
    form.elements.username.value = sessionStorage.getItem('ks-signup-username') || '';
    sessionStorage.removeItem('ks-signup-complete');
    sessionStorage.removeItem('ks-signup-username');
  }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (saving) return;
    saving = true;
    const button = form.querySelector('[type=submit]');
    button.disabled = true;
    notice.textContent = '';
    try {
      const body = Object.fromEntries(new FormData(form));
      body.username = body.username.trim();
      if (registering) body.name = body.name.trim();
      const headers = {'Content-Type': 'application/json'};
      if (registering) headers['X-CSRF-Token'] = document.querySelector('meta[name=signup-csrf]').content;
      const response = await fetch(`/api/auth/${form.dataset.auth}`, {method: 'POST', credentials: 'same-origin', headers, body: JSON.stringify(body)});
      let result = {};
      try { result = await response.json(); } catch { /* A rate-limit response may be plain text. */ }
      if (!response.ok) {
        const translated = {'Invalid credentials': 'Tên tài khoản hoặc mật khẩu chưa đúng.', 'Account temporarily locked': 'Tài khoản tạm khóa. Vui lòng thử lại sau 15 phút.'};
        throw Error(response.status === 429 ? 'Bạn thử quá nhiều lần. Vui lòng đợi một phút rồi thử lại.' : translated[result.detail] || (typeof result.detail === 'string' ? result.detail : 'Thông tin chưa hợp lệ. Vui lòng kiểm tra lại.'));
      }
      if (registering) {
        sessionStorage.setItem('ks-signup-complete', '1');
        sessionStorage.setItem('ks-signup-username', body.username);
        location.assign('/login');
      } else {
        sessionStorage.setItem('ks-csrf', result.csrf_token);
        location.assign(result.role === 'child-view' ? '/child' : '/app/overview');
      }
    } catch (error) {
      notice.textContent = error instanceof TypeError ? 'Chưa kết nối được với KidSafe. Vui lòng thử lại.' : error.message;
      notice.className = 'error';
    } finally {
      saving = false;
      button.disabled = false;
    }
  });
})();
