/* شفرة — بيانات بوابة الفريق من السيرفر.
   PortalData.ready يجيب الموظفين والمهام والدخل مرة وحدة، وبعدها الصفحة ترسم.
   كل تعديل (مهمة، عمل، دفعة) يروح للسيرفر، والرد يحدّث القوائم هنا. */

const PortalData = {
  people: [],
  tasks: [],
  moneyEntries: [],

  catLabels: { site: 'مواقع', app: 'تطبيقات', dash: 'داشبورد', student: 'مشاريع طلاب' },
  // الشهور اللي تطلع في صفحة الحسابات: آخر 3 شهور + الشهر الجاي + أي شهر فيه دفعات
  get monthDefs() {
    const names = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'];
    const ar = (n) => String(n).replace(/\d/g, (d) => '٠١٢٣٤٥٦٧٨٩'[d]);
    const ids = new Set(this.moneyEntries.map((e) => e.month));
    const now = new Date();
    for (let i = -3; i <= 1; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() + i, 1);
      ids.add(d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0'));
    }
    return Array.from(ids).sort().map((id) => ({ id, label: names[Number(id.slice(5)) - 1] + ' ' + ar(id.slice(0, 4)) }));
  },
  get currentMonth() {
    const d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
  },
  statusLabel: { new: 'جديدة', doing: 'قيد التنفيذ', done: 'مكتملة' },
  statusColor: { new: '#9AA1AC', doing: '#5CE1E6', done: '#B8F34A' },
  prioColor: { 'عالية': '#FFB547', 'متوسطة': '#5CE1E6', 'منخفضة': '#9AA1AC' },
  dotColor: { 'متاح': '#B8F34A', 'مشغول': '#FFB547', 'إجازة': '#6E7681' },

  byId(id) { return this.people.find((p) => p.id === String(id)) || null; },

  statusOf(t) {
    const d = t.items.filter((i) => i.done).length;
    if (t.items.length && d === t.items.length) return 'done';
    if (d > 0) return 'doing';
    return 'new';
  },

  // ---------- تحويل بيانات السيرفر ----------
  _person(u) {
    const viewer = Auth.current();
    return {
      id: u.id, name: u.name, initial: (u.name || '؟').trim().charAt(0), email: u.email,
      phone: Auth.canSeePhone(viewer, u) ? (u.phone || '') : null,
      roleKey: u.role, title: Auth.roleLabel(u.role), role: (u.domains && u.domains[0]) || Auth.roleLabel(u.role),
      admin: u.role === 'owner' || u.role === 'admin', status: u.status || 'متاح',
      domains: u.domains || [], languages: u.languages || [], skills: u.languages || [],
      joined: u.createdAt, duties: [], meetings: u.meetings || { attended: 0, total: 0 },
      history: (u.history || []).filter((h) => h.due && h.done)
    };
  },
  _task(t) {
    return {
      id: String(t.id), title: t.title, project: t.project, due: t.due || '', priority: t.priority,
      assignee: t.assignee == null ? null : String(t.assignee),
      items: (t.items || []).map((i) => ({ text: i.text, done: !!i.done }))
    };
  },
  _money(e) { return { id: e.id, name: e.name, cat: e.cat, amount: Number(e.amount), month: e.month }; },
  _replaceTask(raw) {
    const t = this._task(raw);
    const i = this.tasks.findIndex((x) => x.id === t.id);
    if (i === -1) this.tasks.unshift(t); else this.tasks[i] = t;
    return t;
  },

  // ---------- التحميل ----------
  _ready: null,
  get ready() {
    if (this._ready) return this._ready;
    const self = this;
    this._ready = (async function () {
      const me = await Auth.ready();
      if (!me || !Auth.isStaff(me)) return;
      const jobs = [
        Auth.request('/api/people').then((list) => { self.people = list.map((u) => self._person(Auth.normalize(u))); }),
        Auth.request('/api/tasks').then((list) => { self.tasks = list.map((t) => self._task(t)); })
      ];
      if (Auth.can('viewAccounts', me)) {
        jobs.push(Auth.request('/api/income').then((list) => { self.moneyEntries = list.map((e) => self._money(e)); }));
      }
      const results = await Promise.allSettled(jobs);
      const failed = results.find((r) => r.status === 'rejected');
      if (failed) self.notify(failed.reason.message);
    })();
    return this._ready;
  },

  // رسالة صغيرة تحت الشاشة لأخطاء السيرفر
  notify(text) {
    let el = document.getElementById('portal-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'portal-toast';
      el.setAttribute('role', 'alert');
      el.style.cssText = 'position:fixed;bottom:88px;left:50%;transform:translateX(-50%);z-index:9999;max-width:min(92vw,440px);padding:12px 18px;border-radius:12px;background:#1E2228;border:1px solid #FFB547;color:#F2F3F5;font-size:14px;box-shadow:0 12px 30px -10px rgba(0,0,0,.7)';
      document.body.appendChild(el);
    }
    el.textContent = text;
    el.style.display = 'block';
    clearTimeout(this._toastT);
    this._toastT = setTimeout(() => { el.style.display = 'none'; }, 4500);
  },

  // ---------- التعديلات (ترسل للسيرفر) ----------
  async run(fn) {
    try { return await fn(); }
    catch (e) { this.notify(e.message); return null; }
  },
  createTask(data) {
    return this.run(async () => this._replaceTask(await Auth.request('/api/tasks', { method: 'POST', body: {
      title: data.title, project: data.project, due: data.due || null, priority: data.priority,
      assignee: data.assignee ? Number(data.assignee) : null, items: data.items.map((i) => i.text)
    } })));
  },
  setAssignee(taskId, assignee) {
    return this.run(async () => this._replaceTask(await Auth.request('/api/tasks/' + taskId, { method: 'PATCH', body: { assignee: assignee ? Number(assignee) : null } })));
  },
  claim(taskId) {
    return this.run(async () => this._replaceTask(await Auth.request('/api/tasks/' + taskId + '/claim', { method: 'POST' })));
  },
  addItem(taskId, text) {
    return this.run(async () => this._replaceTask(await Auth.request('/api/tasks/' + taskId + '/items', { method: 'POST', body: { text } })));
  },
  setItemDone(taskId, index, done) {
    return this.run(async () => this._replaceTask(await Auth.request('/api/tasks/' + taskId + '/items/' + index, { method: 'PATCH', body: { done } })));
  },
  addMoney(entry) {
    return this.run(async () => {
      const e = this._money(await Auth.request('/api/income', { method: 'POST', body: entry }));
      this.moneyEntries.push(e);
      return e;
    });
  },
  removeMoney(id) {
    return this.run(async () => {
      await Auth.request('/api/income/' + id, { method: 'DELETE' });
      this.moneyEntries = this.moneyEntries.filter((x) => x.id !== id);
      return true;
    });
  },

  // يعرض الموعد: لو تاريخ ISO يتحول لعربي، وإلا يرجع النص كما هو.
  formatDue(d) { return /^\d{4}-\d{2}-\d{2}$/.test(d || '') ? this.formatArabicDate(d) : (d || '—'); },
  isOverdue(t) { return /^\d{4}-\d{2}-\d{2}$/.test(t.due || '') && this.statusOf(t) !== 'done' && t.due < new Date().toISOString().slice(0, 10); },

  fmt(n) { return Number(n).toLocaleString('en-US'); },

  formatArabicDate(iso) {
    try { return new Date(iso + 'T12:00:00').toLocaleDateString('ar', { day: 'numeric', month: 'long', calendar: 'gregory' }); }
    catch (e) { return iso; }
  },

  daysLabel(n) { return n === 1 ? 'يوم' : n === 2 ? 'يومين' : n <= 10 ? n + ' أيام' : n + ' يوم'; },

  esc(v) { return String(v == null ? '' : v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
};
