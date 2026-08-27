# نظام إدارة مكتب النائب وخدمة المواطنين

نظام ويب فعلي (وليس Prototype) لإدارة مكتب نائب: بوابة مواطنين، شكاوى
وطلبات واستعلامات، مواعيد، تحويل الطلبات لنواب آخرين عبر البريد
الإلكتروني، أرشيف رسمي، لوحة تحكم، صلاحيات وأمان، وسجلات تدقيق كاملة.

**راجع أيضًا** `01-architecture-plan.md` للاطلاع على التصميم المعماري
الكامل (Database Schema، Roles & Permissions، Workflow، إلخ) قبل هذا
الملف — README هنا يركّز على التشغيل الفعلي فقط.

هذه النسخة الحالية هي **مرحلة "الأساس" (Step 1)** من خطة التنفيذ:
هيكل المشروع، الإعدادات، الاتصال بقاعدة البيانات وRedis، تصميم القالب
الأساسي RTL. الموديلات والمنطق التجاري الفعلي لكل تطبيق (accounts,
requests_app, deputies...) ستُضاف تباعًا في الخطوات القادمة.

---

## المتطلبات قبل البدء (Windows)

- Windows 10/11
- Python 3.12 (أو أحدث من 3.11)
- PostgreSQL 15+ (أو 16)
- Redis (لتشغيل Celery — انظر الملاحظة أدناه)
- Git

### ملاحظة: Redis على Windows

Redis لا يُدعم رسميًا على Windows مباشرة. الخيارات المقترحة:

1. **الأسهل للتطوير المحلي**: تثبيت [Memurai](https://www.memurai.com/) —
   بديل متوافق مع Redis يعمل كخدمة Windows أصلية (له نسخة مجانية
   للتطوير).
2. **بديل**: تشغيل Redis عبر Docker Desktop على Windows (إن كان
   متاحًا على جهاز المكتب):
   `docker run -d -p 6379:6379 redis:7`
3. **لاحقًا في Production**: يعمل Redis بشكل طبيعي مباشرة على سيرفر
   Linux (VPS)، ولا حاجة لهذه البدائل هناك.

---

## 1) تثبيت Python

نزّل Python من https://www.python.org/downloads/ وتأكد من تفعيل خيار
"Add Python to PATH" أثناء التثبيت. تحقق من التثبيت:

```powershell
python --version
```

## 2) تثبيت PostgreSQL

نزّل من https://www.postgresql.org/download/windows/ وثبّته مع
pgAdmin. بعد التثبيت، أنشئ قاعدة البيانات والمستخدم عبر psql (أو
pgAdmin):

```powershell
psql -U postgres
```

داخل psql:

```sql
CREATE DATABASE naib_office_db;
CREATE USER naib_app_user WITH PASSWORD 'ضع_كلمة_مرور_قوية_هنا';
-- صلاحيات دنيا فقط، وليس صلاحيات superuser (Database least privilege)
GRANT ALL PRIVILEGES ON DATABASE naib_office_db TO naib_app_user;
\q
```

## 3) استنساخ المشروع وإعداد Virtual Environment

```powershell
git clone <رابط المستودع> naib-office-system
cd naib-office-system

python -m venv .venv
.venv\Scripts\Activate.ps1
```

> إن ظهرت رسالة منع تنفيذ السكربتات في PowerShell، شغّل مرة واحدة (كمسؤول):
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## 4) تثبيت المتطلبات

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## 5) إعداد ملف البيئة (.env)

```powershell
copy .env.example .env
notepad .env
```

عدّل القيم التالية على الأقل:

- `DJANGO_SECRET_KEY` — قيمة عشوائية طويلة (يمكن توليدها عبر
  `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- `DATABASE_URL` — بيانات قاعدة البيانات التي أنشأتها في الخطوة 2
- `REDIS_URL` — عادة `redis://127.0.0.1:6379/0` إن كنت تستخدم Memurai
  محليًا بنفس المنفذ الافتراضي

## 6) تشغيل Migrations

```powershell
python manage.py migrate
```

## 7) إنشاء مستخدم Super Admin

```powershell
python manage.py createsuperuser
```

## 8) تشغيل الخادم محليًا

```powershell
python manage.py runserver
```

افتح المتصفح على http://127.0.0.1:8000

## 9) تشغيل Celery (في نافذة PowerShell منفصلة، بعد تفعيل venv فيها أيضًا)

```powershell
celery -A config worker --loglevel=info --pool=solo
```

> `--pool=solo` ضروري على Windows لأن أنماط التوازي الافتراضية في
> Celery (prefork) غير مدعومة على Windows.

ولتشغيل المهام الدورية (Celery Beat — لاحقًا عند تفعيل Reply Inbox)،
في نافذة ثالثة:

```powershell
celery -A config beat --loglevel=info
```

## 10) تشغيل الاختبارات

```powershell
pytest
```

---

## هيكل المشروع

راجع قسم "Folder Structure" في `01-architecture-plan.md` للشرح الكامل.

---

## SMTP (البريد الصادر)

أثناء التطوير، البريد يُطبع في الطرفية بدل الإرسال الفعلي افتراضيًا
(`USE_CONSOLE_EMAIL_BACKEND=True` في `.env`). لاختبار إرسال حقيقي عبر
Microsoft 365 أو Google Workspace، عدّل `.env`:

```
USE_CONSOLE_EMAIL_BACKEND=False
EMAIL_HOST=smtp.office365.com   # أو smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...          # استخدم App Password وليس كلمة المرور الفعلية
```

---

## Deployment (Cloud/VPS) — نظرة عامة

سيُستكمل بالتفصيل الكامل عند الوصول لخطوة Production في خطة التنفيذ.
باختصار:

1. `DJANGO_SETTINGS_MODULE=config.settings.production`
2. جميع القيم الحساسة من متغيرات بيئة النظام على السيرفر (وليس ملف
   `.env` بالضرورة).
3. Gunicorn خلف Nginx (reverse proxy) + شهادة HTTPS (مثلًا عبر
   Let's Encrypt).
4. `python manage.py collectstatic` لتجميع الملفات الثابتة، وتُخدَّم
   عبر Nginx أو whitenoise.
5. Redis + Celery worker + Celery beat كخدمات systemd منفصلة.
6. PostgreSQL بمستخدم بصلاحيات دنيا (كما في التطوير)، ونسخ احتياطي
   يومي مشفّر خارج السيرفر (راجع قسم Disaster Recovery في وثيقة
   التخطيط).
7. Firewall يسمح فقط بالمنافذ الضرورية (80/443، وSSH محدود بـ IP إن
   أمكن).

---

## Security Checklist سريع قبل أي نشر فعلي

- [ ] `DEBUG=False` في Production
- [ ] `DJANGO_SECRET_KEY` مختلف تمامًا عن أي قيمة استُخدمت في التطوير
- [ ] `.env` غير موجود في Git (تحقق: `git status`)
- [ ] HTTPS مفعّل وإجباري
- [ ] 2FA مفعّل لكل حسابات الموظفين
- [ ] نسخة احتياطية حقيقية مُختبرة (Restore Drill ناجح موثّق)
- [ ] صلاحيات قاعدة البيانات دنيا وليست superuser
- [ ] مراجعة Security Checklist الكامل في `01-architecture-plan.md` §7

---

## بيانات تجريبية

لا تُستخدم أي بيانات حقيقية في هذا المستودع. عند إضافة أمر
`seed_demo_data` (في خطوة لاحقة من خطة التنفيذ) ستكون كل الأسماء
والبريد الإلكتروني (`@example.com`) وهمية بشكل واضح.
