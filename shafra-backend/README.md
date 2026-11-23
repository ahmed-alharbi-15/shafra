# Shafra API — الباك اند لموقع شفرة (v2)

FastAPI + PostgreSQL على Render. مطابق لـ «عقد الـ API» في `CLAUDE.md` بريبو الموقع.

## الرتب
| الرتبة | يقدر |
|---|---|
| **Owner** (أحمد ونايف) | كل شي: يضيف المهام ويوزعها، يغيّر الرتب، يشوف الجوالات والحسابات |
| **أدمن** | بوابة الفريق + كل المهام + الحسابات والدخل |
| **مشرف** | بوابة الفريق + يشوف كل المهام |
| **موظف** | بوابة الفريق + مهامه والمفتوحة، ياخذ مهمة مفتوحة، يعلّم أعماله |
| **عميل** | أي أحد يسجل من الموقع. صفحة «حسابي» بس |

## متغيرات البيئة في Render
| المتغير | القيمة |
|---|---|
| `DATABASE_URL` | Internal Database URL من صفحة قاعدة البيانات |
| `SECRET_KEY` | نص عشوائي طويل |
| `CORS_ORIGINS` | `https://shafra-taupe.vercel.app` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` / `ADMIN_NAME` | حساب الـ Owner الأول |
| `OWNER2_EMAIL` / `OWNER2_PASSWORD` / `OWNER2_NAME` | حساب الـ Owner الثاني (اختياري) |
| `PYTHON_VERSION` | `3.12.7` |

حسابات الـ Owner تنشأ تلقائي أول ما يشتغل السيرفر. والجداول تنشأ تلقائي.
لو قاعدة البيانات فيها جداول من النسخة الأولى، السيرفر يمسحها وينشئها من جديد مرة وحدة.

## التشغيل على جهازك
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
وافتح http://127.0.0.1:8000/docs

## الـ Endpoints
| الطلب | الوصف | مين |
|---|---|---|
| `POST /api/auth/register` | `{name,email,phone?,password,remember}` ← عميل + توكن | الكل |
| `POST /api/auth/login` | `{email,password,remember}` ← توكن (30 يوم لو remember) | الكل |
| `GET` / `PATCH /api/me` | `{name,phone,domains[],languages[],status}` | صاحب الحساب |
| `POST /api/me/email` | `{newEmail,password}` | صاحب الحساب |
| `POST /api/me/password` | `{oldPassword,newPassword}` | صاحب الحساب |
| `DELETE /api/me` | `{password}` — يرفض لو Owner، ومهامه ترجع مفتوحة | صاحب الحساب |
| `GET /api/people` | الموظفين + سجل تسليماتهم. الجوال للـ Owner وصاحبه بس | موظف+ |
| `GET /api/users` | كل الحسابات حتى العملاء | Owner |
| `PATCH /api/users/:id/role` | `{role: admin\|moderator\|employee\|client}` | Owner |
| `PATCH /api/users/:id/meetings` | `{attended,total}` حضور الاجتماعات | Owner |
| `GET /api/tasks` | Owner/أدمن/مشرف: الكل. موظف: مهامه + المفتوحة | موظف+ |
| `POST /api/tasks` | `{title,project,due,priority,assignee?,items[]}` | Owner |
| `PATCH` / `DELETE /api/tasks/:id` | `{assignee}` وغيره | Owner |
| `POST /api/tasks/:id/claim` | ياخذ مهمة مفتوحة | موظف+ |
| `POST /api/tasks/:id/items` | `{text}` عمل جديد | المسؤول أو Owner |
| `PATCH /api/tasks/:id/items/:i` | `{done}` — `i` ترتيب العمل من 0 | المسؤول أو Owner |
| `GET` / `POST` / `DELETE /api/income` | `{name,cat,amount,month}` | Owner، أدمن |
| `GET /api/works` | الأعمال (اختياري، الموقع حاليًا يقرأ من projects-data.js) | الكل |
