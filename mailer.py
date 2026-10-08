"""إرسال بريد OTP، مع رجوع آمن لو مكتبة flask_mail مش متثبتة أو الإعدادات ناقصة."""
try:
    from flask_mail import Mail, Message
    mail = Mail()
    _MAIL_AVAILABLE = True
except ImportError:
    mail = None
    _MAIL_AVAILABLE = False


def init_mail(app):
    if _MAIL_AVAILABLE:
        mail.init_app(app)


def send_otp_email(app, email, otp):
    if not _MAIL_AVAILABLE:
        app.logger.warning("flask-mail not installed - OTP for %s is %s (dev mode)", email, otp)
        return False
    if not app.config.get("MAIL_USERNAME") or not app.config.get("MAIL_PASSWORD"):
        app.logger.warning("Mail not configured - OTP for %s is %s (dev mode)", email, otp)
        return False
    try:
        msg = Message("Your OTP Code", recipients=[email])
        msg.body = f"Your OTP code is: {otp}\nIt expires in 10 minutes."
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error("Error sending OTP email: %s", e)
        return False
