/* شفرة — بيانات تجريبية لبوابة الفريق (بدون باكند).
   نايف: استبدل محتوى PortalData.people / PortalData.tasks / PortalData.moneyEntries
   بطلبات API حقيقية من سيرفر FastAPI لاحقًا. كل */ // TODO(backend) تحت يشير لمكان يحتاج ربط حقيقي.

const PortalData = {
  // TODO(backend): اجلب الموظفين من /api/people بدل هذي المصفوفة.
  people: [
    {
      id: 'ahmed', name: 'أحمد الحربي', initial: 'أ', role: 'Frontend Developer', status: 'متاح',
      skills: ['HTML', 'CSS', 'JavaScript', 'Flutter'], admin: true,
      title: 'شريك مؤسس — مطوّر واجهات', joined: '[تاريخ الانضمام]',
      duties: ['تصميم وبرمجة واجهات المواقع والتطبيقات', 'تطبيقات الجوال بـ Flutter', 'رفع المشاريع على Vercel ومتابعة الأداء', 'التواصل مع العملاء على التصميم'],
      meetings: { attended: 11, total: 12 },
      history: [
        { title: 'صفحات الدول في سفرة', project: 'سفرة', due: '2026-10-05', done: '2026-10-04' },
        { title: 'فلتر الوصفات', project: 'سفرة', due: '2026-10-14', done: '2026-10-14' },
        { title: 'تصميم موقع شفرة', project: 'موقع شفرة', due: '2026-11-10', done: '2026-11-12' },
        { title: 'واجهة الحجز — مشروع تخرج', project: 'مشاريع طلاب', due: '2026-11-15', done: '2026-11-15' }
      ]
    },
    {
      id: 'partner', name: 'نايف الحربي', initial: 'ن', role: 'Backend Developer', status: 'مشغول',
      skills: ['Python', 'FastAPI', 'PostgreSQL'], admin: true,
      title: 'شريك مؤسس — مطوّر خوادم', joined: '[تاريخ الانضمام]',
      duties: ['بناء الـ API وقواعد البيانات', 'تسجيل الدخول والصلاحيات', 'رفع السيرفرات على Render', 'حماية البيانات والنسخ الاحتياطي'],
      meetings: { attended: 12, total: 12 },
      history: [
        { title: 'API الوصفات', project: 'سفرة', due: '2026-10-08', done: '2026-10-07' },
        { title: 'نقل الصور لـ Cloudinary', project: 'سفرة', due: '2026-10-20', done: '2026-10-23' },
        { title: 'قاعدة بيانات تحدي المدن', project: 'تحدي المدن', due: '2026-11-08', done: '2026-11-08' }
      ]
    },
    {
      id: 'designer', name: '[اسم المصمم]', initial: 'م', role: 'UI/UX Designer', status: 'متاح',
      skills: ['Figma', 'Branding'], admin: false,
      title: 'مصمم واجهات', joined: '[تاريخ الانضمام]',
      duties: ['تصميم الشاشات والهوية', 'تجهيز ملفات التسليم للمطورين'],
      meetings: { attended: 7, total: 9 },
      history: [{ title: 'هوية تحدي المدن', project: 'تحدي المدن', due: '2026-11-01', done: '2026-11-05' }]
    },
    {
      id: 'motion', name: '[اسم مصمم الأنيميشن]', initial: 'ح', role: 'Motion Designer', status: 'إجازة',
      skills: ['After Effects', 'Lottie'], admin: false,
      title: 'مصمم موشن', joined: '[تاريخ الانضمام]',
      duties: ['أنيميشن المواقع والتطبيقات', 'فيديوهات تعريفية'],
      meetings: { attended: 5, total: 6 },
      history: [{ title: 'أنيميشن الرئيسية', project: 'موقع شفرة', due: '2026-11-18', done: '2026-11-17' }]
    }
  ],

  // TODO(backend): اجلب المهام من /api/tasks، وخلّ toggle/addItem يرسلوا PATCH/POST حقيقي.
  tasks: [
    { id: 't1', title: 'إضافة صفحات دول جديدة', project: 'سفرة', assignee: 'ahmed', due: '٢٠ نوفمبر', priority: 'عالية',
      items: [
        { text: 'تجميع صور المدن ورفعها على Cloudinary', done: true },
        { text: 'كتابة محتوى الأكلات المشهورة', done: true },
        { text: 'بناء كروت المدن', done: false },
        { text: 'مراجعة الصفحات على الجوال', done: false }
      ] },
    { id: 't2', title: 'API للوصفات والفلترة', project: 'سفرة', assignee: 'partner', due: '٢٢ نوفمبر', priority: 'عالية',
      items: [
        { text: 'جدول الوصفات في PostgreSQL', done: true },
        { text: 'Endpoint للفلترة حسب النوع', done: false },
        { text: 'فهرسة قاعدة البيانات', done: false },
        { text: 'توثيق الـ API', done: false }
      ] },
    { id: 't3', title: 'هوية وشاشات تحدي المدن', project: 'تحدي المدن', assignee: 'designer', due: '٢٨ نوفمبر', priority: 'متوسطة',
      items: [
        { text: 'لوحة الألوان والخطوط', done: false },
        { text: 'تصميم الشعار', done: false },
        { text: 'شاشات التطبيق الأساسية', done: false }
      ] },
    { id: 't4', title: 'أنيميشن الصفحة الرئيسية', project: 'موقع شفرة', assignee: 'motion', due: '١٨ نوفمبر', priority: 'منخفضة',
      items: [
        { text: 'حركة نافذة الكود', done: true },
        { text: 'انتقالات الكروت عند التمرير', done: true }
      ] },
    { id: 't5', title: 'مشروع تخرج: نظام حجز مواعيد', project: 'مشاريع طلاب', assignee: 'ahmed', due: '٣ ديسمبر', priority: 'متوسطة',
      items: [
        { text: 'تحليل المتطلبات مع الطالب', done: true },
        { text: 'واجهة الحجز', done: false },
        { text: 'لوحة الإدارة', done: false },
        { text: 'جلسة شرح الكود للطالب', done: false }
      ] }
  ],

  // TODO(backend): اجلب الدفعات من /api/income، وخلّ الإضافة والحذف يرسلوا POST/DELETE حقيقي.
  moneyEntries: [
    { id: 1, name: '[مثال] موقع مطعم', cat: 'site', amount: 3500, month: '2026-11' },
    { id: 2, name: '[مثال] تطبيق حجوزات', cat: 'app', amount: 6000, month: '2026-11' },
    { id: 3, name: '[مثال] مشروع تخرج', cat: 'student', amount: 1200, month: '2026-11' },
    { id: 4, name: '[مثال] لوحة تحكم متجر', cat: 'dash', amount: 4000, month: '2026-10' }
  ],

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

  fmt(n) { return Number(n).toLocaleString('en-US'); },

  formatArabicDate(iso) {
    try { return new Date(iso + 'T12:00:00').toLocaleDateString('ar', { day: 'numeric', month: 'long', calendar: 'gregory' }); }
    catch (e) { return iso; }
  },

  daysLabel(n) { return n === 1 ? 'يوم' : n === 2 ? 'يومين' : n <= 10 ? n + ' أيام' : n + ' يوم'; }
};
