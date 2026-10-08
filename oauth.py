"""تسجيل الدخول بجوجل وفيسبوك (OAuth) — نفس سلوك البرامج العالمية:
عند الضغط على الزر بيوديك فعلياً لصفحة جوجل/فيسبوك تختار حسابك منها،
وبعد الموافقة بيرجعك للموقع مسجّل دخول تلقائياً.

الملف مكتوب بحيث لو مكتبة Authlib مش مثبتة، أو لسه محطتش بيانات
GOOGLE_CLIENT_ID / FACEBOOK_CLIENT_ID، الموقع يفضل شغال عادي والأزرار
تدي رسالة واضحة بدل ما توقع السيرفر بالغلط.
"""
try:
    from authlib.integrations.flask_client import OAuth
    _AUTHLIB_AVAILABLE = True
except ImportError:
    OAuth = None
    _AUTHLIB_AVAILABLE = False

from config import Config

oauth = OAuth() if _AUTHLIB_AVAILABLE else None


def init_oauth(app):
    """يتسجل في create_app(). بيفعّل بس المزودين اللي بياناتهم موجودة."""
    if not _AUTHLIB_AVAILABLE:
        app.logger.warning(
            "Authlib غير مثبت — تسجيل الدخول بجوجل/فيسبوك متوقف. "
            "ثبّته بالأمر: pip install Authlib requests"
        )
        return

    oauth.init_app(app)

    if Config.GOOGLE_CLIENT_ID and Config.GOOGLE_CLIENT_SECRET:
        oauth.register(
            name="google",
            client_id=Config.GOOGLE_CLIENT_ID,
            client_secret=Config.GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )
    else:
        app.logger.info("تسجيل الدخول بجوجل غير مفعّل (GOOGLE_CLIENT_ID فاضي).")

    # فيسبوك متشال من المشروع كله — مفيش تسجيل له، ومفيش زرار ليه.
    # لو حد حط مفاتيحه في .env بالغلط، بنتجاهلها بصمت.


def enabled_providers():
    """أسماء مزودي OAuth المفعّلين فعلياً (المكتبة مثبتة + المفاتيح موجودة)."""
    if not _AUTHLIB_AVAILABLE or oauth is None:
        return set()
    return set(oauth._clients.keys())


def is_provider_enabled(provider):
    return provider in enabled_providers()
