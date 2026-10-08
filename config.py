import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_dotenv():
    """يقرأ ملف .env ويحوّله لمتغيرات بيئة — من غير أي مكتبة زيادة.

    القواعد: السطر اللي فيه = بيفصل key عن value، والـ # في أوله تعليقات،
    والقيمة اللي فيها # أو مسافات تكتبها بين علامتي تنصيص.
    اللي في البيئة الحقيقية له الأولوية على الملف.
    """
    path = os.path.join(BASE_DIR, ".env")
    if not os.path.isfile(path):
        return
    try:
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                # شيل علامات التنصيص لو موجودة
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        # ملف .env مش موجود أو مش مقروء — هنكمل بمتغيرات البيئة بس
        pass


_load_dotenv()


class Config:
    """إعدادات التطبيق العامة، تُقرأ من متغيرات البيئة عند توفرها."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me-in-production")

    DATABASE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "app.db"))

    # إعدادات البريد - كلها تُقرأ من البيئة، لا توجد بيانات حقيقية في الكود
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")  # App Password من Gmail
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")

    OTP_EXPIRY_SECONDS = 10 * 60  # صلاحية كود التحقق: 10 دقائق
    OTP_RESEND_COOLDOWN_SECONDS = 45  # لازم يستنى قد كده قبل ما يطلب كود جديد

    # حسابات افتراضية تُنشأ أول مرة فقط (غيّرها في البيئة قبل النشر الحقيقي)
    DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "ChangeMe123!")

    # البريد الوحيد المسموح له بدخول لوحة المالك الخاصة — غيّره لبريدك
    OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "ziadmsm2007@gmail.com")

    # ---------------------------------------------------------------
    # تسجيل الدخول بجوجل وفيسبوك (OAuth)
    # حط بياناتك بين علامتي التنصيص هنا، أو استخدم متغيرات البيئة.
    # طريقة الحصول عليها موضحة بالتفصيل في README.md تحت "تفعيل تسجيل
    # الدخول بجوجل وفيسبوك". من غيرهم، الأزرار هتظهر لكن هتديك رسالة
    # إن الخاصية لسه مش مفعّلة بدل ما توقع البرنامج.
    # ---------------------------------------------------------------
    # تسجيل الدخول بجوجل (OAuth)
    #
    # ازاي تفعّلها (مرة واحدة بس):
    #   1) افتح https://console.cloud.google.com/apis/credentials
    #   2) اعمل Project (لو أول مرة)، بعدين Enable الـ Google Identity
    #      Platform API من صفحة APIs & Services.
    #   3) OAuth consent screen → External → حدّد الإيميل واسم التطبيق،
    #      وحط رابط الموقع في Application home page.
    #   4) Credentials → Create Credentials → OAuth client ID →
    #      Application type: Web application.
    #   5) Authorized redirect URIs حط السطر ده بالظبط:
    #        http://127.0.0.1:5000/auth/google/callback
    #   6) انسخ الـ Client ID و Client Secret والصقهم تحت، أو خزّنهم في
    #      متغيرات البيئة-named بالاسم ده.
    #
    # ملحوظة مهمة: لازم callback الموديل بالظبط على العنوان اللي شغّال
    # عليه السيرفر (لو فتحت من جهازك بـ localhost اكتب localhost مش
    # 127.0.0.1 والعكس).
    # ---------------------------------------------------------------
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    # فيسبوك وتيلجرام متشالين من المشروع — مفيش تسجيل لهم ولا أزرار.
    # (تيلجرام كان محتاج دومين حقيقي وده مش متاح على localhost)

    # نظام الإسكرو — عمولة المنصة 20%، والباقي للفني
    COMMISSION_RATE = float(os.environ.get("COMMISSION_RATE", 0.20))
    # حساباتك اللي العميل هيدفع عليها (غيّرها لرقمك الحقيقي)
    OWNER_VODAFONE_CASH = os.environ.get("OWNER_VODAFONE_CASH", "01000000000")
    OWNER_INSTAPAY = os.environ.get("OWNER_INSTAPAY", "ziadmsm2007@instapay")
    OWNER_BANK_ACCOUNT = os.environ.get("OWNER_BANK_ACCOUNT", "")

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "photos")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
