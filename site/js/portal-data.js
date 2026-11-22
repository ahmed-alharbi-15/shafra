/* شفرة — بيانات تجريبية لبوابة الفريق (بدون باكند).
   نايف: استبدل محتوى PortalData.people / PortalData.tasks / PortalData.moneyEntries
   بطلبات API حقيقية من سيرفر FastAPI لاحقًا. كل */ // TODO(backend) تحت يشير لمكان يحتاج ربط حقيقي.

const PortalData = {
  // الموظفين = كل حساب رتبته مو «عميل». يجي من Auth (حاليًا من المتصفح).
  // TODO(backend): اجلبهم من GET /api/people (الرقم يرجع للـ Owner وصاحب الحساب بس).
  get people() {
    const viewer = Auth.current();
    return Auth.users().filter(Auth.isStaff).map(function (u) {
      return {
        id: u.id, name: u.name, initial: (u.name || '؟').trim().charAt(0), email: u.email,
        phone: Auth.canSeePhone(viewer, u) ? (u.phone || '') : null,
        roleKey: u.role, title: Auth.roleLabel(u.role), role: (u.domains && u.domains[0]) || Auth.roleLabel(u.role),
        admin: u.role === 'owner' || u.role === 'admin', status: 'متاح',
        domains: u.domains || [], languages: u.languages || [], skills: u.languages || [],
        joined: u.createdAt, duties: [], meetings: { attended: 0, total: 0 }, history: []
      };
    });
  },

  // TODO(backend): اجلب المهام من /api/tasks، وخلّ toggle/addItem يرسلوا PATCH/POST حقيقي.
  tasks: [],

  // TODO(backend): اجلب الدفعات من /api/income، وخلّ الإضافة والحذف يرسلوا POST/DELETE حقيقي.
  moneyEntries: [],

  catLabels: { site: 'مواقع', app: 'تطبيقات', dash: 'داشبورد', student: 'مشاريع طلاب' },
  monthDefs: [
    { id: '2026-09', label: 'سبتمبر ٢٠٢٦' },
    { id: '2026-10', label: 'أكتوبر ٢٠٢٦' },
    { id: '2026-11', label: 'نوفمبر ٢٠٢٦' },
    { id: '2026-12', label: 'ديسمبر ٢٠٢٦' }
  ],
  statusLabel: { new: 'جديدة', doing: 'قيد التنفيذ', done: 'مكتملة' },
  statusColor: { new: '#9AA1AC', doing: '#5CE1E6', done: '#B8F34A' },
  prioColor: { 'عالية': '#FFB547', 'متوسطة': '#5CE1E6', 'منخفضة': '#9AA1AC' },
  dotColor: { 'متاح': '#B8F34A', 'مشغول': '#FFB547', 'إجازة': '#6E7681' },

  byId(id) { return this.people.find((p) => p.id === id) || null; },

  statusOf(t) {
    const d = t.items.filter((i) => i.done).length;
    if (t.items.length && d === t.items.length) return 'done';
    if (d > 0) return 'doing';
    return 'new';
  },

  // التخزين المؤقت في المتصفح لين يجهز الباكند.
  // TODO(backend): احذف save() وخلّ كل تعديل يروح لـ API.
  save() {
    try { localStorage.setItem('shafra_portal_v1', JSON.stringify({ tasks: this.tasks, moneyEntries: this.moneyEntries })); } catch (e) {}
  },

  // يعرض الموعد: لو تاريخ ISO يتحول لعربي، وإلا يرجع النص كما هو.
  formatDue(d) { return /^\d{4}-\d{2}-\d{2}$/.test(d || '') ? this.formatArabicDate(d) : (d || '—'); },
  isOverdue(t) { return /^\d{4}-\d{2}-\d{2}$/.test(t.due || '') && this.statusOf(t) !== 'done' && t.due < new Date().toISOString().slice(0, 10); },

  fmt(n) { return Number(n).toLocaleString('en-US'); },

  formatArabicDate(iso) {
    try { return new Date(iso + 'T12:00:00').toLocaleDateString('ar', { day: 'numeric', month: 'long', calendar: 'gregory' }); }
    catch (e) { return iso; }
  },

  daysLabel(n) { return n === 1 ? 'يوم' : n === 2 ? 'يومين' : n <= 10 ? n + ' أيام' : n + ' يوم'; }
};

(function () {
  try {
    const saved = JSON.parse(localStorage.getItem('shafra_portal_v1') || 'null');
    if (saved) {
      if (Array.isArray(saved.tasks)) PortalData.tasks = saved.tasks;
      if (Array.isArray(saved.moneyEntries)) PortalData.moneyEntries = saved.moneyEntries;
    }
  } catch (e) {}
})();
