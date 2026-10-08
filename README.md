# AutoCare - Car Service Booking Platform (نسخة احترافية)

## الفرق عن الكود الأصلي

### مشاكل أمنية اتصلحت
- **الباسوردات كانت بتتخزن كنص عادي** (`password = db.Column(db.String)` وبتتقارن مباشرة) — دلوقتي كل باسورد بيتخزن مُشفّر (`werkzeug.security`).
- **`secret_key` و بيانات إيميل Gmail الحقيقية** كانوا مكتوبين صريح في الكود — دلوقتي كلهم بيتقروا من متغيرات البيئة.
- **كل صفحات الداشبورد كانت مفتوحة بدون أي حماية** (`customer_dashboard`, `technical_dashboard`, `admin_dashboard` ملهاش أي تحقق تسجيل دخول) — دلوقتي فيه `@role_required("client"/"technician"/"admin")` على كل صفحة، فمينفعش حد يدخل داشبورد مش بتاعته.
- **مفيش أي تحقق إن الطلب فعلاً بتاع اليوزر اللي بيحاول يشوفه** (`track_order`, `cancel_order`) — دلوقتي بيتحقق إن `customer_id` بتاع الطلب هو نفسه اليوزر الحالي.
- **الـ OTP كان بيتبعت لكن مفيش صفحة تتحقق منه** — يعني أي حد يقدر يوصل مباشرة لـ `reset_password` بدون ما يعرف الكود خالص. دلوقتي فيه صفحة `/verify_otp` كاملة، والكود بيتخزن مُشفّر (hash) في الـ session مش نص عادي، وله صلاحية 10 دقايق بس.

### مشاكل هيكلية
- **بيانات الخدمات (`categories`) كانت متكررة 3 مرات** في نفس الملف (مرة import من `services_data` مش موجود أصلاً، ومرة inline، ومرة تالتة جوه `customer_dashboard`) — دلوقتي فيها نسخة واحدة بس في `services_data.py`.
- **`my_orders` كانت بترجع بيانات وهمية ثابتة** (`orders = [{"id": 1, ...}]`) بدل ما تجيب طلبات اليوزر الحقيقية من قاعدة البيانات.
- **متغير `orders = []` و `tasks = orders` عالميين ملهومش استخدام حقيقي** جنب وجود موديل `Order` كامل في قاعدة البيانات — كود ميت اتشال.
- **فصل الكود لطبقات واضحة**:
  - `config.py` - الإعدادات
  - `database.py` - الاتصال بقاعدة البيانات وإنشاء الجداول
  - `models.py` - كل عمليات القراءة/الكتابة
  - `services_data.py` - كتالوج الخدمات (مصدر واحد)
  - `auth.py` - decorators الحماية (`login_required`, `role_required`)
  - `mailer.py` - إرسال OTP (بيرجع تلقائياً لوضع "طباعة في الـ console" لو مفيش إعدادات بريد)
  - `app.py` - الـ routes فقط

### تحسينات وظيفية
- الطلب بيتحفظ بربط حقيقي بين العميل (`customer_id`) والفني (`technician_id`) وسعر واسم الخدمة وقت الطلب (عشان لو السعر اتغيّر بعدين، الطلب القديم يفضل زي ما كان).
- فني بيقدر يقبل/يرفض/ينهي طلب، والطلب بيتربط بيه تلقائياً.
- تتبع الطلب (`track_order`) بيوضح خطوات حقيقية بناءً على حالة الطلب الفعلية.
- الأدمن بيشوف إحصائيات حقيقية (عدد الطلبات/العملاء/الفنيين) بدل بيانات وهمية.

### تسجيل الدخول والتسجيل (تحديث جديد)
- **تسجيل الدخول بجوجل وفيسبوك (OAuth حقيقي)**: زرار "المتابعة عبر جوجل/فيسبوك" في صفحتي الدخول والتسجيل بيوديك فعلاً لصفحة جوجل/فيسبوك تختار حسابك منها، وبيرجعك مسجّل دخول تلقائياً — نفس تجربة البرامج الكبيرة. تفاصيل التفعيل تحت "تفعيل تسجيل الدخول بجوجل وفيسبوك".
- لو نفس الإيميل مسجّل قبل كده بباسورد عادي، وبعدين اتسجل بيه بجوجل/فيسبوك، بيتربط بنفس الحساب مش بيتعمل حساب مكرر.
- **نسيت كلمة المرور**: كود التحقق بقى بخانات منفصلة (زي واتساب) مع عدّاد لصلاحية الكود، وزرار "إعادة إرسال" بعدّاد تهدئة 45 ثانية (من غير ما تضطر تكتب إيميلك تاني)، وتأكيد كلمة المرور الجديدة قبل الحفظ.
- إصلاح كلاسات CSS كانت مستخدمة في صفحات الدخول بس مش متعرّفة أصلاً (`auth-wrap`, `auth-icon`, `auth-body`, `input-icon-wrap`...) وده كان بيخلي تصميم الصفحات ناقص — دلوقتي متظبطة بالكامل.
- زرار إظهار/إخفاء كلمة المرور (👁️) في كل خانات الباسورد.

## طريقة التشغيل

```bash
pip install -r requirements.txt
python app.py
```

هيتعمل تلقائياً 3 حسابات تجريبية أول مرة:

| الدور | الإيميل | الباسورد |
|---|---|---|
| Admin | admin@example.com | ChangeMe123! |
| Client | client@example.com | ChangeMe123! |
| Technician | tech@example.com | ChangeMe123! |

**غيّر البيانات دي قبل أي نشر حقيقي** عن طريق متغيرات البيئة:

```bash
export SECRET_KEY="مفتاح-عشوائي-طويل"
export DEFAULT_ADMIN_EMAIL="admin@yourcompany.com"
export DEFAULT_ADMIN_PASSWORD="كلمة-مرور-قوية"
python app.py
```

## تفعيل إرسال OTP بالإيميل فعلياً (اختياري)

لو عايز الـ OTP يتبعت بإيميل حقيقي بدل ما يتطبع في الـ terminal بس:

```bash
pip install Flask-Mail
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="app-password-from-gmail"   # مش الباسورد العادي، لازم App Password
python app.py
```

من غير الإعدادات دي، الكود هيشتغل عادي بس هيطبع الـ OTP في التيرمنال (وضع تطوير آمن).

## تفعيل تسجيل الدخول بجوجل وفيسبوك (Google / Facebook Login)

الأزرار موجودة دايماً في صفحتي الدخول والتسجيل. من غير ما تحط المفاتيح بتاعتك، الضغط
عليها هيدّيك رسالة "الخاصية لسه مش مفعّلة" بدل ما يبوّظ الموقع. علشان تشغّلها فعلياً:

### جوجل
1. ادخل [Google Cloud Console](https://console.cloud.google.com/) → أنشئ مشروع جديد (أو استخدم موجود).
2. من القائمة: **APIs & Services → OAuth consent screen** → اعمل الإعداد الأساسي (اسم التطبيق، إيميلك).
3. بعدين **APIs & Services → Credentials → Create Credentials → OAuth client ID** → اختار **Web application**.
4. تحت **Authorized redirect URIs** ضيف بالظبط:
   - `http://127.0.0.1:5000/auth/google/callback` (للتجربة على جهازك)
   - ولو هترفعه على دومين حقيقي، ضيف كمان `https://your-domain.com/auth/google/callback`
5. هيديك **Client ID** و **Client Secret** — انسخهم.

### فيسبوك
1. ادخل [Meta for Developers](https://developers.facebook.com/) → **My Apps → Create App** → اختار نوع "Consumer" أو "Business".
2. من لوحة التطبيق، ضيف منتج **Facebook Login** → **Settings**.
3. تحت **Valid OAuth Redirect URIs** ضيف بالظبط:
   - `http://127.0.0.1:5000/auth/facebook/callback`
   - وبعد النشر: `https://your-domain.com/auth/facebook/callback`
4. من **App Settings → Basic** هتلاقي **App ID** و **App Secret**.

### حط المفاتيح في المشروع
افتح `config.py` وحط القيم بين علامتي التنصيص في السطور دي (أو استخدم environment
variables بنفس الاسم لو مرتاح لها أكتر):

```python
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "الصق_Client_ID_هنا")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "الصق_Client_Secret_هنا")
FACEBOOK_CLIENT_ID = os.environ.get("FACEBOOK_CLIENT_ID", "الصق_App_ID_هنا")
FACEBOOK_CLIENT_SECRET = os.environ.get("FACEBOOK_CLIENT_SECRET", "الصق_App_Secret_هنا")
```

ثبّت المكتبة المطلوبة (موجودة أصلاً في requirements.txt):
```bash
pip install Authlib requests
```

شغّل الموقع عادي (`python app.py` أو دبل-كليك على `شغل DrCar.bat`)، وجرّب تضغط
"المتابعة عبر جوجل" في صفحة الدخول — هيوديك فعلاً لصفحة جوجل تختار حسابك منها.

**ملاحظات مهمة:**
- التسجيل بجوجل/فيسبوك بيفتح دايماً **حساب عميل (مالك سيارة)**. الفنيين لازم
  يسجّلوا بالنموذج العادي لأنهم لازم يرفعوا صورة وتتراجع موافقتهم من الإدارة.
- لو حد سجّل قبل كده بإيميله وباسورد عادي، وبعدين دخل بجوجل/فيسبوك بنفس الإيميل،
  النظام بيربط الحسابين مع بعض تلقائي بدل ما يعمل حساب مكرر.
- في الإنتاج (مش على جهازك) جوجل وفيسبوك بيطلبوا الموقع يكون شغال بـ **HTTPS**
  (بيسمحوا بـ HTTP بس لـ localhost/127.0.0.1 وقت التجربة).

## نقاط تحتاج انتباه قبل النشر الفعلي

1. **لا تشغّل بـ `debug=True` في الإنتاج**.
2. **SQLite مناسب للتطوير فقط** - للمواقع الحقيقية استخدم PostgreSQL.
3. أضف **CSRF protection** (`Flask-WTF`) لكل النماذج.
4. أضف **rate limiting** على `/login` و `/forgot_password` لمنع محاولات التخمين.
5. فعّل **HTTPS** وخلي الكوكيز `Secure`.
