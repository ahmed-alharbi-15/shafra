# Shafra API — الباك اند لموقع شفرة

FastAPI + PostgreSQL، جاهز للرفع على Render. مبني على تصاميم `design/` في ريبو الموقع:
بوابة الفريق (Login, Team, Accounts, Profile) وصفحة الأعمال.

## التشغيل على جهازك
```bash
python -m venv .venv
source .venv/bin/activate        # ويندوز: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # وعدّل القيم
uvicorn app.main:app --reload
```
افتح http://127.0.0.1:8000/docs وجرّب كل شي من هناك. اضغط **Authorize** وحط التوكن اللي يرجع من `/api/auth/login`.

على جهازك يستخدم SQLite تلقائيًا (ملف `shafra.db`)، وعلى Render يستخدم PostgreSQL.

## الرفع على GitHub
سوّ له ريبو **منفصل** عن الموقع، مثلًا `shafra-backend`:
```bash
git init
git add .
git commit -m "Shafra backend"
git branch -M main
git remote add origin https://github.com/ahmed-alharbi-15/shafra-backend.git
git push -u origin main
```

## الرفع على Render (Blueprint)
1. في Render: **New → Blueprint** واختر الريبو.
2. Render يقرأ `render.yaml` وينشئ السيرفر وقاعدة البيانات ويربطهم، ويولّد `SECRET_KEY` تلقائيًا.
3. بيطلب منك ثلاث قيم:
   - `CORS_ORIGINS`: رابط الموقع على Vercel، مثل `https://shafra.vercel.app` (أكثر من رابط افصلهم بفاصلة)
   - `ADMIN_EMAIL` و `ADMIN_PASSWORD`: حسابك. ينشأ تلقائيًا كأدمن أول ما يشتغل السيرفر.
4. بعد ما يخلص: `https://shafra-api.onrender.com/docs`

> - السيرفر المجاني ينام بعد فترة بدون استخدام، وأول طلب بعدها ياخذ تقريبًا دقيقة.
> - قاعدة البيانات المجانية في Render لها مدة وتنتهي. شيك على صفحتها وحدّث الخطة قبل ما تنتهي عشان ما تضيع البيانات.

## حسابات Owner (أحمد ونايف)
الاثنين Owner: أدمن كامل، ومحميين: ما ينوقفون ولا يعدّلهم إلا Owner. تنشأ تلقائيًا أول ما يشتغل السيرفر من متغير `OWNERS`.

في Render: **Environment** ثم أضف `OWNERS` (سطر واحد):
```json
[{"name":"أحمد الحربي","email":"EMAIL1","password":"PASSWORD1"},{"name":"نايف الحربي","email":"EMAIL2","password":"PASSWORD2"}]
```
بدّل `EMAIL` و`PASSWORD` بالقيم الحقيقية، وبعدها **Manual Deploy**.

- كلمات المرور تنكتب في Render فقط، لا تحطها في الكود ولا في GitHub.
- لو الحساب موجود من قبل ما تتغير كلمة مروره، يتأكد بس إنه أدمن وفعّال. تغيير الكلمة من `/api/auth/change-password` أو `reset-password`.
- الرد على تسجيل الدخول فيه `is_owner` عشان الواجهة تعرض رتبة Owner.

## الصلاحيات
- **ما فيه تسجيل عام.** البوابة للأدمن والموظفين فقط، والأدمن يضيف الحسابات.
- **الأدمن:** يضيف المهام ويوزعها، ويدير الموظفين، ويشوف الحسابات والدخل، وينشر الأعمال في الموقع.
- **الموظف:**
  - يشوف المهام والفريق والملفات الشخصية.
  - يضيف أعمال لمهامه ويعلّمها كمنجزة.
  - يعدل حالته ومهاراته في ملفه.
- **«نسيت كلمة المرور؟»:** الأدمن يحط له كلمة جديدة من `POST /api/team/{id}/reset-password`.

## الـ Endpoints

### تسجيل الدخول
| Method | Path | الوصف |
|---|---|---|
| POST | /api/auth/login | `{email, password, remember}` و`remember` = «تذكرني» (30 يوم) |
| GET | /api/auth/me | ملفي الشخصي كامل مع الإحصائيات |
| PATCH | /api/auth/me | تعديل `status` / `skills` / `avatar_url` |
| POST | /api/auth/change-password | تغيير كلمة المرور |

### الفريق
| Method | Path | الوصف | |
|---|---|---|---|
| GET | /api/team | الموظفين + عدد مهامهم المفتوحة | موظف |
| GET | /api/team/{id} | الملف: الالتزام %، التقييم، حضور الاجتماعات، متوسط التأخير، المهام الحالية، سجل التسليمات | موظف |
| POST | /api/team | إضافة موظف | أدمن |
| PATCH | /api/team/{id} | تعديل بياناته، وعدد الاجتماعات `meetings_attended/total` | أدمن |
| POST | /api/team/{id}/reset-password | كلمة مرور جديدة | أدمن |
| DELETE | /api/team/{id} | إيقاف الحساب (يبقى سجله) | أدمن |

### المهام
| Method | Path | الوصف | |
|---|---|---|---|
| GET | /api/tasks?assignee_id=&status=new\|doing\|done | المهام مع الفلاتر | موظف |
| GET | /api/tasks/stats?assignee_id= | المفتوحة، الأعمال المنجزة/الكل، المكتملة، الموظفين | موظف |
| POST | /api/tasks | `{title, project, priority, due, assignee_id, items: [...]}` | أدمن |
| PATCH / DELETE | /api/tasks/{id} | تعديل / حذف | أدمن |
| POST | /api/tasks/{id}/items | «عمل جديد تحت المهمة» | صاحب المهمة أو أدمن |
| PATCH | /api/tasks/{id}/items/{item_id} | `{done: true}` تعليم كمنجز | صاحب المهمة أو أدمن |
| DELETE | /api/tasks/{id}/items/{item_id} | حذف عمل | صاحب المهمة أو أدمن |

- **حالة المهمة تنحسب تلقائيًا من الأعمال:**
  - `new`: ما فيه شي منجز.
  - `doing`: بعضها منجز.
  - `done`: كلها منجزة.
- **تاريخ التسليم `completed_at`:** ينسجل أول ما تكتمل المهمة، ومنه ينحسب الالتزام بالمواعيد.
- **الأولوية:** `عالية` | `متوسطة` | `منخفضة`
- **حالة الموظف:** `متاح` | `مشغول` | `إجازة`

### الحسابات (أدمن فقط)
| Method | Path | الوصف |
|---|---|---|
| GET | /api/payments?month=2026-11 | دفعات الشهر + إجمالي الشهر + إجمالي كل الشهور + المجموع لكل قسم |
| POST | /api/payments | `{name, category, amount, month}` |
| DELETE | /api/payments/{id} | حذف دفعة |

### الأعمال
| Method | Path | الوصف | |
|---|---|---|---|
| GET | /api/works?cat=site\|app\|dash\|student | الأعمال المنشورة + عدد كل فلتر | عام |
| GET | /api/works/{slug} | عمل واحد | عام |
| GET | /api/works/admin/all | كل الأعمال حتى غير المنشورة | أدمن |
| POST / PATCH / DELETE | /api/works, /api/works/{id} | إضافة / تعديل / حذف | أدمن |

`is_personal: true` يعرض شارة «مشروع شخصي». الصور ارفعها على Cloudinary وحط الرابط في `image_url`.

## ربطه بالفرونت اند
```js
const API = "https://shafra-api.onrender.com";
const token = () => localStorage.getItem("token");

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
      ...options.headers,
    },
  });
  if (res.status === 401) { localStorage.removeItem("token"); location.href = "login.html"; return; }
  const data = res.status === 204 ? null : await res.json();
  if (!res.ok) throw new Error(data?.detail || "صار خطأ");
  return data;
}

// تسجيل دخول
const { access_token, user } = await api("/api/auth/login", {
  method: "POST",
  body: JSON.stringify({ email, password, remember }),
});
localStorage.setItem("token", access_token);

// المهام والإحصائيات
const tasks = await api("/api/tasks?status=doing");
const stats = await api("/api/tasks/stats");

// تعليم عمل كمنجز
await api(`/api/tasks/${taskId}/items/${itemId}`, { method: "PATCH", body: JSON.stringify({ done: true }) });

// صفحة الأعمال العامة
const { items, counts } = await api("/api/works?cat=app");
```
