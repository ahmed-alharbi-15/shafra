/* شفرة — الحسابات والصلاحيات (نسخة المتصفح).
   كل شي هنا محفوظ في localStorage لين يجهز باكند نايف.
   TODO(backend): استبدل كل دالة تحت بطلب API حقيقي (تسجيل، دخول، تعديل، حذف)،
   وخلّ السيرفر هو اللي يتحقق من الدور في كل طلب. الواجهة ما تعتمد عليها للأمان.
   تفاصيل الـ API في CLAUDE.md تحت «عقد الـ API». */

const Auth = (function () {
  'use strict';

  const KEY_USERS = 'shafra_users_v1';
  const KEY_SESSION = 'shafra_session';

  const ROLES = {
    owner: 'Owner',
    admin: 'أدمن',
    moderator: 'مشرف',
    employee: 'موظف',
    client: 'عميل'
  };
  const STAFF = ['owner', 'admin', 'moderator', 'employee'];

  // مين يقدر يسوي ايش
  const PERMS = {
    viewPortal:   ['owner', 'admin', 'moderator', 'employee'],
    viewAccounts: ['owner', 'admin'],
    viewAllTasks: ['owner', 'admin', 'moderator'],
    createTask:   ['owner'],              // تحديد المهام ولمين
    assignTask:   ['owner'],
    claimTask:    ['owner', 'admin', 'moderator', 'employee'], // ياخذ مهمة مفتوحة
    seePhones:    ['owner'],
    manageRoles:  ['owner']
  };

  /* ---------- SHA-256 (متزامن، بدون مكتبات) ---------- */
  function sha256(str) {
    const K = [
      0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
      0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
      0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
      0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
      0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
      0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ];
    const bytes = [];
    const utf8 = unescape(encodeURIComponent(str));
    for (let i = 0; i < utf8.length; i++) bytes.push(utf8.charCodeAt(i));
    const bitLen = bytes.length * 8;
    bytes.push(0x80);
    while (bytes.length % 64 !== 56) bytes.push(0);
    for (let i = 7; i >= 0; i--) bytes.push(i >= 4 ? 0 : (bitLen >>> (i * 8)) & 0xff);
    let h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    const rotr = (x, n) => (x >>> n) | (x << (32 - n));
    for (let o = 0; o < bytes.length; o += 64) {
      const w = new Array(64);
      for (let i = 0; i < 16; i++) w[i] = (bytes[o + 4 * i] << 24) | (bytes[o + 4 * i + 1] << 16) | (bytes[o + 4 * i + 2] << 8) | bytes[o + 4 * i + 3];
      for (let i = 16; i < 64; i++) {
        const s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >>> 3);
        const s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >>> 10);
        w[i] = (w[i - 16] + s0 + w[i - 7] + s1) | 0;
      }
      let [a, b, c, d, e, f, g, hh] = h;
      for (let i = 0; i < 64; i++) {
        const S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
        const ch = (e & f) ^ (~e & g);
        const t1 = (hh + S1 + ch + K[i] + w[i]) | 0;
        const S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
        const maj = (a & b) ^ (a & c) ^ (b & c);
        const t2 = (S0 + maj) | 0;
        hh = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0;
      }
      h = [(h[0] + a) | 0, (h[1] + b) | 0, (h[2] + c) | 0, (h[3] + d) | 0, (h[4] + e) | 0, (h[5] + f) | 0, (h[6] + g) | 0, (h[7] + hh) | 0];
    }
    return h.map((x) => ('00000000' + (x >>> 0).toString(16)).slice(-8)).join('');
  }
  const hashPw = (pw, salt) => sha256(salt + ':' + pw);
  const newSalt = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36);

  /* ---------- حسابات الـ Owner الثابتة ---------- */
  // اثنينهم Owner دائم. غيّروا الإيميل والباسورد من «حسابي» أول ما تدخلون.
  const SEED_OWNERS = [
    { id: 'ahmed', name: 'أحمد الحربي', email: 'ahmed@shafra.local', role: 'owner', salt: 'k3j9x2ma1p', passHash: '91f771c62e2c7e77c3e202020c6bd5f4061fe9a4f1a9a043813522627111efff',
      domains: ['تطوير الواجهات (Frontend)', 'تطبيقات متعددة المنصات (Flutter / React Native)'], languages: ['HTML', 'CSS', 'JavaScript', 'Dart'] },
    { id: 'partner', name: 'نايف الحربي', email: 'naif@shafra.local', role: 'owner', salt: 'q8w4z7nb5r', passHash: 'aef1b92e38a6ebda931fad94611f663fbf2afb235adaabe8df50c7eb9e00a6e6',
      domains: ['تطوير الخوادم (Backend)', 'قواعد البيانات'], languages: ['Python', 'SQL'] }
  ];

  /* ---------- التخزين ---------- */
  function readUsers() {
    let list = [];
    try { list = JSON.parse(localStorage.getItem(KEY_USERS) || '[]'); } catch (e) { list = []; }
    if (!Array.isArray(list)) list = [];
    let changed = false;
    const hasApi = list.some((u) => u.source === 'api');
    SEED_OWNERS.forEach(function (seed) {
      if (!hasApi && !list.some((u) => u.id === seed.id)) {
        list.unshift(Object.assign({ phone: '', createdAt: '2026-11-01' }, seed));
        changed = true;
      }
    });
    if (changed) writeUsers(list);
    return list;
  }
  function writeUsers(list) {
    try { localStorage.setItem(KEY_USERS, JSON.stringify(list)); } catch (e) {}
  }

  const emailOk = (e) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);
  const phoneOk = (p) => !p || /^\+?[0-9\s-]{8,16}$/.test(p);
  const norm = (e) => String(e || '').trim().toLowerCase();
  const fail = (error) => ({ ok: false, error });

  /* ---------- الجلسة ---------- */
  function setSession(id, remember) {
    try { sessionStorage.removeItem(KEY_SESSION); localStorage.removeItem(KEY_SESSION); } catch (e) {}
    try { (remember ? localStorage : sessionStorage).setItem(KEY_SESSION, id); } catch (e) {}
  }
  function current() {
    let id = null;
    try { id = sessionStorage.getItem(KEY_SESSION) || localStorage.getItem(KEY_SESSION); } catch (e) {}
    if (!id) return null;
    return readUsers().find((u) => u.id === id) || null;
  }

  /* ---------- الصلاحيات ---------- */
  function can(perm, user) {
    const u = user === undefined ? current() : user;
    return !!u && (PERMS[perm] || []).indexOf(u.role) !== -1;
  }
  const isStaff = (u) => !!u && STAFF.indexOf(u.role) !== -1;
  const homeFor = (u) => (isStaff(u) ? 'team.html' : 'account.html');
  // الرقم ما يشوفه إلا الـ Owner وصاحب الحساب
  const canSeePhone = (viewer, target) => !!viewer && !!target && (viewer.role === 'owner' || viewer.id === target.id);

  /* ---------- العمليات ---------- */
  function register(data) {
    const name = String(data.name || '').trim();
    const email = norm(data.email);
    const phone = String(data.phone || '').trim();
    if (name.length < 2) return fail('اكتب اسمك.');
    if (!emailOk(email)) return fail('الإيميل مو صحيح.');
    if (!phoneOk(phone)) return fail('رقم الجوال مو صحيح.');
    if (String(data.password || '').length < 8) return fail('كلمة المرور لازم 8 خانات أو أكثر.');
    const users = readUsers();
    if (users.some((u) => norm(u.email) === email)) return fail('هذا الإيميل مسجّل من قبل.');
    const salt = newSalt();
    const user = {
      id: 'u' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5),
      name, email, phone, role: 'client', domains: [], languages: [],
      salt, passHash: hashPw(data.password, salt), createdAt: new Date().toISOString().slice(0, 10)
    };
    users.push(user); writeUsers(users);
    setSession(user.id, !!data.remember);
    return { ok: true, user };
  }

  function login(email, password, remember) {
    const u = readUsers().find((x) => norm(x.email) === norm(email));
    if (!u || hashPw(password, u.salt) !== u.passHash) return fail('الإيميل أو كلمة المرور غلط.');
    setSession(u.id, !!remember);
    return { ok: true, user: u };
  }

  // يحوّل مستخدم الباكند (نايف) لحساب محلي للجلسة. التوكن الحقيقي يحفظه api.js.
  // TODO(backend): الباكند يرجع is_admin بس. لما يضيف حقل role (owner/admin/moderator/employee/client) استخدمه هنا.
  function adoptApi(u, remember) {
    const id = 'b' + u.id;
    const rec = {
      id, apiId: u.id, source: 'api', name: u.name, email: String(u.email || '').toLowerCase(), phone: u.phone || '',
      role: u.role_key || (u.is_admin ? 'owner' : 'employee'), domains: u.domains || [], languages: u.skills || [],
      createdAt: u.joined || new Date().toISOString().slice(0, 10)
    };
    const list = readUsers().filter((x) => x.id !== id && !(x.id === 'ahmed' && !x.source) && !(x.id === 'partner' && !x.source));
    list.push(rec); writeUsers(list);
    setSession(id, !!remember);
    return rec;
  }

  function logout(redirect) {
    try { sessionStorage.removeItem(KEY_SESSION); localStorage.removeItem(KEY_SESSION); localStorage.removeItem('token'); } catch (e) {}
    if (redirect !== false) location.href = typeof redirect === 'string' ? redirect : 'index.html';
  }

  function patchUser(id, fn) {
    const users = readUsers();
    const u = users.find((x) => x.id === id);
    if (!u) return fail('الحساب غير موجود.');
    const r = fn(u, users);
    if (r && r.ok === false) return r;
    writeUsers(users);
    return { ok: true, user: u };
  }

  function updateProfile(id, data) {
    if (data.name !== undefined && String(data.name).trim().length < 2) return fail('اكتب اسمك.');
    if (data.phone !== undefined && !phoneOk(String(data.phone).trim())) return fail('رقم الجوال مو صحيح.');
    return patchUser(id, function (u) {
      if (data.name !== undefined) u.name = String(data.name).trim();
      if (data.phone !== undefined) u.phone = String(data.phone).trim();
      if (Array.isArray(data.domains)) u.domains = data.domains;
      if (Array.isArray(data.languages)) u.languages = data.languages;
    });
  }

  function changeEmail(id, newEmail, password) {
    const email = norm(newEmail);
    if (!emailOk(email)) return fail('الإيميل مو صحيح.');
    return patchUser(id, function (u, users) {
      if (hashPw(password, u.salt) !== u.passHash) return fail('كلمة المرور الحالية غلط.');
      if (users.some((x) => x.id !== id && norm(x.email) === email)) return fail('هذا الإيميل مستخدم.');
      u.email = email;
    });
  }

  function changePassword(id, oldPw, newPw) {
    if (String(newPw || '').length < 8) return fail('كلمة المرور الجديدة لازم 8 خانات أو أكثر.');
    return patchUser(id, function (u) {
      if (hashPw(oldPw, u.salt) !== u.passHash) return fail('كلمة المرور الحالية غلط.');
      u.salt = newSalt(); u.passHash = hashPw(newPw, u.salt);
    });
  }

  function deleteAccount(id, password) {
    const users = readUsers();
    const u = users.find((x) => x.id === id);
    if (!u) return fail('الحساب غير موجود.');
    if (u.role === 'owner') return fail('حساب Owner ما ينحذف من الموقع.');
    if (hashPw(password, u.salt) !== u.passHash) return fail('كلمة المرور غلط.');
    writeUsers(users.filter((x) => x.id !== id));
    // المهام اللي كانت عليه ترجع مفتوحة
    try {
      const raw = JSON.parse(localStorage.getItem('shafra_portal_v1') || 'null');
      if (raw && Array.isArray(raw.tasks)) {
        raw.tasks.forEach((t) => { if (t.assignee === id) t.assignee = null; });
        localStorage.setItem('shafra_portal_v1', JSON.stringify(raw));
      }
    } catch (e) {}
    logout(false);
    return { ok: true };
  }

  // بس الـ Owner يعيّن الأدمن والمشرفين والموظفين
  function setRole(actorId, userId, role) {
    const actor = readUsers().find((x) => x.id === actorId);
    if (!actor || !can('manageRoles', actor)) return fail('هذي الخاصية للـ Owner بس.');
    if (['admin', 'moderator', 'employee', 'client'].indexOf(role) === -1) return fail('رتبة غير صحيحة.');
    return patchUser(userId, function (u) {
      if (u.role === 'owner') return fail('رتبة Owner ثابتة.');
      u.role = role;
    });
  }

  // يحمي الصفحة: staff = بوابة الفريق، غير كذا أي حساب داخل
  function guard(opts) {
    const u = current();
    const here = location.pathname.split('/').pop() || 'index.html';
    if (!u) { location.replace('login.html?next=' + encodeURIComponent(here + location.search)); return null; }
    if (opts && opts.staff && !isStaff(u)) { location.replace('account.html'); return null; }
    if (opts && opts.perm && !can(opts.perm, u)) { location.replace('team.html'); return null; }
    return u;
  }

  return {
    ROLES, STAFF, PERMS,
    users: readUsers, byId: (id) => readUsers().find((u) => u.id === id) || null,
    current, can, isStaff, homeFor, canSeePhone, guard,
    adoptApi, register, login, logout, updateProfile, changeEmail, changePassword, deleteAccount, setRole,
    roleLabel: (r) => ROLES[r] || r
  };
})();
