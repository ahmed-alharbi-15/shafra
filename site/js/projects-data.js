/* شفرة — مصفوفة المشاريع الموحّدة. يقرأها projects/project.html عبر ?id=
   أي قيمة بين أقواس مربعة [...] محتوى حقيقي ما وصل بعد — لا تُستبدل باختراع، فقط تُحدَّث هنا. */

const ProjectsData = [
  {
    id: 'sofrah',
    personal: false,
    filterCats: 'site',
    kind: 'sofrah',
    tags: ['موقع', 'منصة محتوى'],
    title: 'سفرة',
    summary: 'منصة عربية لاكتشاف السفر والأكل — تتصفح الدول والمدن، تعرف وش تاكل فيها، وتطبخ وصفاتها في بيتك.',
    metaDescription: 'سفرة: منصة عربية لاكتشاف السفر والأكل — تتصفح الدول والمدن، تعرف وش تاكل فيها، وتطبخ وصفاتها في بيتك.',
    meta: { type: 'موقع + سيرفر', audience: 'السعودية والعالم العربي', year: '[السنة]', url: '[رابط الموقع]' },
    heroNote: '[ضع هنا لقطة شاشة حقيقية من الصفحة الرئيسية]',
    challenge: { title: 'محتوى سفر وأكل عربي، مرتب وسهل', body: 'أغلب محتوى السفر والطبخ بالإنجليزي أو مبعثر بين حسابات. احتجنا منصة عربية واحدة تجمع الدول والمدن والأكلات، وتبقى سريعة رغم مئات الصور.' },
    solution: { title: 'واجهة خفيفة + سيرفر مستقل', body: 'واجهة بـ HTML و CSS و JavaScript بدون أي مكتبات، وسيرفر FastAPI مع قاعدة PostgreSQL، والصور كلها على Cloudinary بدل التخزين المحلي — أكثر من ٣٠٠ صورة بدون ما يثقل الموقع.' },
    features: [
      { icon: 'globe', title: 'صفحات الدول والمدن', body: 'لكل دولة ومدينة صفحة فيها الوجهات والأكلات المشهورة.' },
      { icon: 'filter', title: 'فلتر الوصفات', body: 'تصفية حسب النوع: أطباق رئيسية، حلويات، وسناكات.' },
      { icon: 'image', title: 'صور على Cloudinary', body: 'تحميل كسول للصور وتخزين سحابي يكبر مع المحتوى.' },
      { icon: 'lock', title: 'حسابات وتسجيل دخول', body: 'سيرفر بـ JWT وصلاحيات لإدارة المحتوى.' }
    ],
    stack: {
      frontend: { owner: 'أحمد الحربي', items: ['HTML', 'CSS', 'JavaScript', 'Vercel', 'Cloudinary'] },
      backend: { owner: 'نايف الحربي', items: ['Python', 'FastAPI', 'PostgreSQL', 'Render'] }
    },
    gallery: ['[لقطة: صفحة دولة]', '[لقطة: صفحة وصفة]', '[لقطة: نسخة الجوال]']
  },
  {
    id: 'city-challenge',
    personal: false,
    filterCats: 'site app',
    kind: 'phones',
    tags: ['موقع', 'تطبيق'],
    title: 'تحدي المدن',
    summary: '[وصف قصير لفكرة تحدي المدن وش يقدم للمستخدم]',
    metaDescription: '[وصف قصير لفكرة تحدي المدن وش يقدم للمستخدم]',
    meta: { type: 'موقع + تطبيق', audience: '[الجمهور المستهدف]', year: '[السنة]', url: '[رابط الموقع]' },
    heroNote: '[ضع هنا لقطة شاشة حقيقية من المشروع]',
    challenge: { title: '[عنوان التحدي]', body: '[صف المشكلة اللي كان يواجهها المستخدم قبل تحدي المدن]' },
    solution: { title: '[عنوان الحل]', body: '[صف كيف حل تحدي المدن هذي المشكلة]' },
    features: [
      { icon: 'spark', title: '[ميزة 1]', body: '[وصف مختصر للميزة]' },
      { icon: 'bolt', title: '[ميزة 2]', body: '[وصف مختصر للميزة]' }
    ],
    stack: {
      frontend: { owner: 'أحمد الحربي', items: ['Flutter'] },
      backend: { owner: 'نايف الحربي', items: ['[TECH STACK]'] }
    },
    gallery: ['[لقطة: الشاشة الرئيسية]', '[لقطة: نسخة الجوال]']
  },
  {
    id: 'dash-1',
    personal: false,
    filterCats: 'dash',
    kind: 'dash',
    tags: ['داشبورد'],
    title: '[اسم مشروع لوحة التحكم]',
    summary: '[وش تدير اللوحة ولمين — مثلاً طلبات مطعم أو مخزون محل]',
    metaDescription: '[وش تدير اللوحة ولمين — مثلاً طلبات مطعم أو مخزون محل]',
    meta: { type: 'داشبورد', audience: '[الجمهور المستهدف]', year: '[السنة]', url: '[رابط اللوحة]' },
    heroNote: '[ضع هنا لقطة شاشة حقيقية من اللوحة]',
    challenge: { title: '[عنوان التحدي]', body: '[صف المشكلة اللي كانت تواجه العميل قبل اللوحة]' },
    solution: { title: '[عنوان الحل]', body: '[صف كيف حلّت اللوحة هذي المشكلة]' },
    features: [
      { icon: 'shield', title: '[ميزة 1]', body: '[وصف مختصر للميزة]' },
      { icon: 'cube', title: '[ميزة 2]', body: '[وصف مختصر للميزة]' }
    ],
    stack: {
      frontend: { owner: 'أحمد الحربي', items: ['[TECH STACK]'] },
      backend: { owner: 'نايف الحربي', items: ['[TECH STACK]'] }
    },
    gallery: ['[لقطة: الشاشة الرئيسية]', '[لقطة: تقرير أو جدول]']
  },
  {
    id: 'site-2',
    personal: false,
    filterCats: 'site',
    kind: 'site',
    tags: ['موقع'],
    title: '[اسم موقع شركة]',
    summary: '[نوع النشاط + وش كان المطلوب من الموقع]',
    metaDescription: '[نوع النشاط + وش كان المطلوب من الموقع]',
    meta: { type: 'موقع', audience: '[الجمهور المستهدف]', year: '[السنة]', url: '[رابط الموقع]' },
    heroNote: '[ضع هنا لقطة شاشة حقيقية من الصفحة الرئيسية]',
    challenge: { title: '[عنوان التحدي]', body: '[صف المشكلة اللي كان يواجهها العميل قبل الموقع]' },
    solution: { title: '[عنوان الحل]', body: '[صف كيف حل الموقع هذي المشكلة]' },
    features: [
      { icon: 'globe', title: '[ميزة 1]', body: '[وصف مختصر للميزة]' },
      { icon: 'spark', title: '[ميزة 2]', body: '[وصف مختصر للميزة]' }
    ],
    stack: {
      frontend: { owner: 'أحمد الحربي', items: ['[TECH STACK]'] },
      backend: { owner: 'نايف الحربي', items: ['[TECH STACK]'] }
    },
    gallery: ['[لقطة: الصفحة الرئيسية]', '[لقطة: نسخة الجوال]']
  },
  {
    id: 'app-2',
    personal: false,
    filterCats: 'app',
    kind: 'phones',
    tags: ['تطبيق'],
    title: '[اسم التطبيق]',
    summary: '[وصف التطبيق بسطر واحد]',
    metaDescription: '[وصف التطبيق بسطر واحد]',
    meta: { type: 'تطبيق جوال', audience: '[الجمهور المستهدف]', year: '[السنة]', url: '[رابط المتجر]' },
    heroNote: '[ضع هنا لقطة شاشة حقيقية من التطبيق]',
    challenge: { title: '[عنوان التحدي]', body: '[صف المشكلة اللي كان يواجهها المستخدم قبل التطبيق]' },
    solution: { title: '[عنوان الحل]', body: '[صف كيف حل التطبيق هذي المشكلة]' },
    features: [
      { icon: 'bolt', title: '[ميزة 1]', body: '[وصف مختصر للميزة]' },
      { icon: 'lock', title: '[ميزة 2]', body: '[وصف مختصر للميزة]' }
    ],
    stack: {
      frontend: { owner: 'أحمد الحربي', items: ['Flutter'] },
      backend: { owner: 'نايف الحربي', items: ['[TECH STACK]'] }
    },
    gallery: ['[لقطة: الشاشة الرئيسية]', '[لقطة: شاشة ثانية]']
  },
  {
    id: 'dash-2',
    personal: false,
    filterCats: 'dash',
    kind: 'dash',
    tags: ['داشبورد'],
    title: '[اسم نظام الإدارة]',
    summary: '[وصف النظام بسطر واحد]',
    metaDescription: '[وصف النظام بسطر واحد]',
    meta: { type: 'داشبورد', audience: '[الجمهور المستهدف]', year: '[السنة]', url: '[رابط اللوحة]' },
    heroNote: '[ضع هنا لقطة شاشة حقيقية من اللوحة]',
    challenge: { title: '[عنوان التحدي]', body: '[صف المشكلة اللي كانت تواجه العميل قبل النظام]' },
    solution: { title: '[عنوان الحل]', body: '[صف كيف حلّ النظام هذي المشكلة]' },
    features: [
      { icon: 'cube', title: '[ميزة 1]', body: '[وصف مختصر للميزة]' },
      { icon: 'shield', title: '[ميزة 2]', body: '[وصف مختصر للميزة]' }
    ],
    stack: {
      frontend: { owner: 'أحمد الحربي', items: ['[TECH STACK]'] },
      backend: { owner: 'نايف الحربي', items: ['[TECH STACK]'] }
    },
    gallery: ['[لقطة: الشاشة الرئيسية]', '[لقطة: تقرير أو جدول]']
  },
  {
    id: 'student-1',
    personal: false,
    filterCats: 'student',
    kind: 'code',
    tags: ['مشروع طلاب'],
    title: '[اسم مشروع التخرج]',
    summary: '[الجامعة والتخصص + وش سوى المشروع]',
    metaDescription: '[الجامعة والتخصص + وش سوى المشروع]',
    meta: { type: 'مشروع تخرج', audience: '[الجهة المستفيدة]', year: '[السنة]', url: '[رابط المشروع]' },
    heroNote: '[ضع هنا لقطة شاشة حقيقية من المشروع]',
    challenge: { title: '[عنوان التحدي]', body: '[صف متطلب مشروع التخرج اللي احتجتوا تحلونه]' },
    solution: { title: '[عنوان الحل]', body: '[صف الحل اللي بنيتوه للطالب]' },
    features: [
      { icon: 'spark', title: '[ميزة 1]', body: '[وصف مختصر للميزة]' }
    ],
    stack: {
      frontend: { owner: 'أحمد الحربي', items: ['[TECH STACK]'] },
      backend: { owner: 'نايف الحربي', items: ['[TECH STACK]'] }
    },
    gallery: ['[لقطة: الشاشة الرئيسية]']
  },
  {
    id: 'student-2',
    personal: false,
    filterCats: 'student',
    kind: 'code',
    tags: ['مشروع طلاب'],
    title: '[اسم مشروع مقرر جامعي]',
    summary: '[المقرر + فكرة المشروع]',
    metaDescription: '[المقرر + فكرة المشروع]',
    meta: { type: 'مشروع مقرر', audience: '[الجهة المستفيدة]', year: '[السنة]', url: '[رابط المشروع]' },
    heroNote: '[ضع هنا لقطة شاشة حقيقية من المشروع]',
    challenge: { title: '[عنوان التحدي]', body: '[صف متطلب المقرر اللي احتجتوا تحلونه]' },
    solution: { title: '[عنوان الحل]', body: '[صف الحل اللي بنيتوه للطالب]' },
    features: [
      { icon: 'bolt', title: '[ميزة 1]', body: '[وصف مختصر للميزة]' }
    ],
    stack: {
      frontend: { owner: 'أحمد الحربي', items: ['[TECH STACK]'] },
      backend: { owner: 'نايف الحربي', items: ['[TECH STACK]'] }
    },
    gallery: ['[لقطة: الشاشة الرئيسية]']
  }
];
