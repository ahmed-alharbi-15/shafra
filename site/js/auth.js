/* شفرة — الحسابات والصلاحيات، مربوطة بسيرفر FastAPI على Render.
   - التوكن يتحفظ في المتصفح (localStorage مع «تذكرني»، وإلا sessionStorage).
   - بيانات الحساب الحالي تتخزن نسخة منها عشان الصفحات تعرف مين داخل بدون انتظار.
   - الصلاحيات هنا للعرض بس؛ السيرفر هو اللي يتحقق فعليًا في كل طلب.
   - العمليات اللي تكلّم السيرفر (login, register, ...) ترجع Promise → استخدم await. */

const API_BASE = 'https://shafra-hcjd.onrender.com';

const Auth = (function () {
  'use strict';

  const KEY_TOKEN = 'shafra_token';
  const KEY_ME = 'shafra_me';

  const ROLES = {
    owner: 'Owner',
    admin: 'أدمن',
    moderator: 'مشرف',
    employee: 'موظف',
    client: 'عميل'
  };
  const STAFF = ['owner', 'admin', 'moderator', 'employee'];

  // مين يقدر يسوي ايش (نفس الجدول اللي في السيرفر)
  const PERMS = {
    viewPortal:   ['owner', 'admin', 'moderator', 'employee'],
    viewAccounts: ['owner', 'admin'],
    viewAllTasks: ['owner', 'admin', 'moderator'],
    createTask:   ['owner', 'admin', 'moderator'], // يضيف مهمة جديدة
    assignTask:   ['owner', 'admin', 'moderator'], // يوزّع المهام ويتابع الموظفين
    deleteTask:   ['owner', 'admin', 'moderator'], // يحذف مهمة
    claimTask:    ['owner', 'admin', 'moderator', 'employee'],
    seePhones:    ['owner'],
    manageRoles:  ['owner']
  };

  const fail = (error) => ({ ok: false, error });
  let usersCache = [];   // كل الحسابات اللي يقدر يشوفها الشخص الداخل
  let readyPromise = null;

  /* ---------- التخزين ---------- */
  function store(remember) { return remember ? localStorage : sessionStorage; }
  function getToken() {
    try { return sessionStorage.getItem(KEY_TOKEN) || localStorage.getItem(KEY_TOKEN); } catch (e) { return null; }
  }
  function isRemembered() {
    try { return !!localStorage.getItem(KEY_TOKEN); } catch (e) { return false; }
  }
  function clearSession() {
    try {
      [localStorage, sessionStorage].forEach(function (s) { s.removeItem(KEY_TOKEN); s.removeItem(KEY_ME); });
      // بقايا النسخة القديمة اللي كانت تحفظ كل شي في المتصفح
      ['shafra_users_v1', 'shafra_session', 'shafra_portal_v1', 'token'].forEach(function (k) { localStorage.removeItem(k); sessionStorage.removeItem(k); });
    } catch (e) {}
  }
  function saveSession(token, user, remember) {
    clearSession();
    try { store(remember).setItem(KEY_TOKEN, token); } catch (e) {}
    cacheMe(user);
  }
  function cacheMe(raw) {
    try { store(isRemembered()).setItem(KEY_ME, JSON.stringify(raw)); } catch (e) {}
  }

  // يحوّل حساب السيرفر لشكل اللي تستخدمه الصفحات
  function normalize(u) {
    if (!u) return null;
    return {
      id: String(u.id), apiId: u.id, name: u.name, email: u.email, phone: u.phone || '',
      phoneHidden: u.phone === null, role: u.role, domains: u.domains || [], languages: u.languages || [],
      status: u.status || 'متاح', meetings: u.meetings || { attended: 0, total: 0 }, history: u.history || [],
      createdAt: String(u.created_at || '').slice(0, 10), lastLogin: u.last_login_at || null
    };
  }

  /* ---------- الطلبات ---------- */
  async function request(path, options) {
    const opts = options || {};
    const headers = { 'Content-Type': 'application/json' };
    const token = getToken();
    if (token) headers.Authorization = 'Bearer ' + token;
    let res;
    try {
      res = await fetch(API_BASE + path, { method: opts.method || 'GET', headers, body: opts.body ? JSON.stringify(opts.body) : undefined });
    } catch (e) {
      throw new Error('ما قدرنا نوصل للسيرفر. تأكد من النت وحاول مرة ثانية.');
    }
    let data = null;
    if (res.status !== 204) { try { data = await res.json(); } catch (e) {} }
    if (res.status === 401 && token && path.indexOf('/api/auth/') !== 0) {
      clearSession();
      const here = location.pathname.split('/').pop() || 'index.html';
      location.replace('login.html?next=' + encodeURIComponent(here + location.search));
      throw new Error('انتهت الجلسة، سجّل دخولك مرة ثانية.');
    }
    if (!res.ok) throw new Error((data && typeof data.detail === 'string') ? data.detail : 'صار خطأ، حاول مرة ثانية.');
    return data;
  }

  // يلف أي طلب ويرجع { ok, ... } بدل ما يرمي خطأ
  async function attempt(fn) {
    try { return Object.assign({ ok: true }, (await fn()) || {}); }
    catch (e) { return fail(e.message); }
  }

  /* ---------- الجلسة ---------- */
  function current() {
    if (!getToken()) return null;
    let raw = null;
    try { raw = JSON.parse(sessionStorage.getItem(KEY_ME) || localStorage.getItem(KEY_ME) || 'null'); } catch (e) {}
    return normalize(raw);
  }

  // يحدّث بيانات الشخص الداخل من السيرفر، ويجيب قائمة الحسابات لو هو موظف
  function ready() {
    if (readyPromise) return readyPromise;
    readyPromise = (async function () {
      if (!getToken()) return null;
      try {
        const me = await request('/api/me');
        cacheMe(me);
        const u = normalize(me);
        if (can('manageRoles', u)) usersCache = (await request('/api/users')).map(normalize);
        else if (isStaff(u)) usersCache = (await request('/api/people')).map(normalize);
        else usersCache = [u];
        return u;
      } catch (e) {
        return current();
      }
    })();
    return readyPromise;
  }

  /* ---------- الصلاحيات ---------- */
  function can(perm, user) {
    const u = user === undefined ? current() : user;
    return !!u && (PERMS[perm] || []).indexOf(u.role) !== -1;
  }
  const isStaff = (u) => !!u && STAFF.indexOf(u.role) !== -1;
  const homeFor = (u) => (isStaff(u) ? 'team.html' : 'account.html');
  // السيرفر أصلًا ما يرجع الجوال إلا للـ Owner ولصاحب الحساب
  const canSeePhone = (viewer, target) => !!viewer && !!target && !target.phoneHidden && (viewer.role === 'owner' || viewer.id === target.id);

  /* ---------- العمليات (كلها async) ---------- */
  function register(data) {
    return attempt(async function () {
      const r = await request('/api/auth/register', { method: 'POST', body: {
        name: String(data.name || '').trim(), email: String(data.email || '').trim(),
        phone: String(data.phone || '').trim() || null, password: data.password || '', remember: !!data.remember
      } });
      saveSession(r.access_token, r.user, !!data.remember);
      return { user: normalize(r.user) };
    });
  }

  function login(email, password, remember) {
    return attempt(async function () {
      const r = await request('/api/auth/login', { method: 'POST', body: { email: String(email || '').trim(), password, remember: !!remember } });
      saveSession(r.access_token, r.user, !!remember);
      return { user: normalize(r.user) };
    });
  }

  function logout(redirect) {
    clearSession();
    if (redirect !== false) location.href = typeof redirect === 'string' ? redirect : 'index.html';
  }

  function updateProfile(id, data) {
    return attempt(async function () {
      const body = {};
      ['name', 'phone', 'domains', 'languages', 'status'].forEach(function (k) { if (data[k] !== undefined) body[k] = data[k]; });
      if (body.name !== undefined) body.name = String(body.name).trim();
      if (body.phone !== undefined) body.phone = String(body.phone).trim();
      const me = await request('/api/me', { method: 'PATCH', body });
      cacheMe(me);
      return { user: normalize(me) };
    });
  }

  function changeEmail(id, newEmail, password) {
    return attempt(async function () {
      const me = await request('/api/me/email', { method: 'POST', body: { newEmail: String(newEmail || '').trim(), password } });
      cacheMe(me);
      return { user: normalize(me) };
    });
  }

  function changePassword(id, oldPw, newPw) {
    if (String(newPw || '').length < 8) return Promise.resolve(fail('كلمة المرور الجديدة لازم 8 خانات أو أكثر.'));
    return attempt(() => request('/api/me/password', { method: 'POST', body: { oldPassword: oldPw, newPassword: newPw } }));
  }

  function deleteAccount(id, password) {
    return attempt(async function () {
      await request('/api/me', { method: 'DELETE', body: { password } });
      logout(false);
    });
  }

  // بس الـ Owner يعيّن الأدمن والمشرفين والموظفين
  function setRole(actorId, userId, role) {
    return attempt(async function () {
      const u = normalize(await request('/api/users/' + encodeURIComponent(userId) + '/role', { method: 'PATCH', body: { role } }));
      usersCache = usersCache.map((x) => (x.id === u.id ? Object.assign({}, x, u) : x));
      return { user: u };
    });
  }

  // يحمي الصفحة: لازم يكون داخل. فحص الرتبة (staff/perm) يصير بعد ما يرد السيرفر،
  // عشان لو الـ Owner غيّر رتبة الشخص تنطبق على طول بدون ما يطلع ويدخل.
  function guard(opts) {
    const u = current();
    const here = location.pathname.split('/').pop() || 'index.html';
    if (!u) { location.replace('login.html?next=' + encodeURIComponent(here + location.search)); return null; }
    if (opts && (opts.staff || opts.perm)) {
      ready().then(function (fresh) {
        if (!fresh) return;
        if (opts.staff && !isStaff(fresh)) location.replace('account.html');
        else if (opts.perm && !can(opts.perm, fresh)) location.replace('team.html');
      });
    }
    return u;
  }

  return {
    ROLES, STAFF, PERMS,
    users: () => usersCache.slice(),
    byId: (id) => usersCache.find((u) => u.id === String(id)) || null,
    current, ready, can, isStaff, homeFor, canSeePhone, guard,
    register, login, logout, updateProfile, changeEmail, changePassword, deleteAccount, setRole,
    request, getToken, normalize,
    roleLabel: (r) => ROLES[r] || r
  };
})();
