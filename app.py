import hashlib
import os
import random
import re
import time

from werkzeug.utils import secure_filename
import uuid

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
    send_from_directory,
)

from config import Config
from database import init_db
import models
import cart
import geo
import math

EGYPT_GOVERNORATES = [
    "القاهرة", "الجيزة", "الإسكندرية", "الدقهلية", "البحر الأحمر", "البحيرة", "الفيوم", "الغربية",
    "الإسماعيلية", "المنوفية", "المنيا", "القليوبية", "الوادي الجديد", "السويس", "أسوان", "أسيوط",
    "بني سويف", "بورسعيد", "دمياط", "الشرقية", "جنوب سيناء", "كفر الشيخ", "مطروح", "الأقصر", "قنا", "شمال سيناء", "سوهاج"
]

def haversine(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

_PHONE_RE = re.compile(r"^\+?[0-9][0-9\s\-]{7,16}$")
_IPV4_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def _clean_phone(raw):
    """رقم التليفون: يرجّع النص منظّف، أو None لو فيه حاجة غلط، أو '' لو فاضي."""
    raw = (raw or "").strip()
    if not raw:
        return ""
    return raw if _PHONE_RE.match(raw) else None


def _parse_coords(lat, lng):
    try:
        lat = float(lat) if str(lat or "").strip() else None
        lng = float(lng) if str(lng or "").strip() else None
    except (TypeError, ValueError):
        return None, None
    if lat is not None and lng is not None and not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None, None
    return lat, lng


def _eff_region(cust, gov_form=None, city_form=None):
    """المحافظة/المدينة اللي بنحسب بيها السعر: اللي اختارها العميل على الخريطة
    لو موجودة، وإلا اللي اتسجّل بيها في بروفايله."""
    cust = cust or {}
    gov = (gov_form or "").strip() or cust.get("governorate")
    city = (city_form or "").strip() or cust.get("city")
    if gov and gov not in EGYPT_GOVERNORATES:
        gov = cust.get("governorate")
    return gov, city
from mailer import init_mail, send_otp_email
from oauth import init_oauth, oauth, enabled_providers, is_provider_enabled
from auth import login_required, role_required, owner_required, get_current_user
from services_data import (
    categories,
    get_service_by_id,
    get_all_services,
    localize_service,
    localize_category,
    localize_categories,
    get_localized_service_by_id,
    get_localized_services,
    get_services_by_category,
    get_category_key,
    get_category_for_service,
    get_visual_for_service,
    get_image_for_service,
    get_adjusted_price,
    get_zone,
    get_car_image,
    get_car_multiplier,
    CAR_MAKES,
    get_car_makes,
)
from i18n import LANGUAGES, LANG_DIR, get_lang, make_t


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    init_mail(app)
    init_oauth(app)
    register_routes(app)
    init_db()
    return app


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_photo(file):
    if not file or file.filename == "":
        return None
    if not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit(".", 1)[1].lower()
    fname = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(Config.UPLOAD_FOLDER, fname)
    file.save(path)
    return f"uploads/photos/{fname}"


def _hash_otp(otp):
    return hashlib.sha256(otp.encode()).hexdigest()


PAYMENT_METHODS = [
    {"value": "Cash", "label_key": "pay_cash", "icon": "💵"},
    {"value": "Card", "label_key": "pay_card", "icon": "💳"},
    {"value": "InstaPay", "label_key": "pay_instapay", "icon": "🏦"},
    {"value": "Vodafone Cash", "label_key": "pay_vodafone", "icon": "📱"},
    {"value": "Orange Money", "label_key": "pay_orange", "icon": "📱"},
    {"value": "Etisalat Cash", "label_key": "pay_etisalat", "icon": "📱"},
    {"value": "we Pay", "label_key": "pay_we", "icon": "📱"},
    {"value": "Meeza", "label_key": "pay_meeza", "icon": "💳"},
    {"value": "PayPal", "label_key": "pay_paypal", "icon": "🌐"},
    {"value": "Google Pay", "label_key": "pay_google", "icon": "📲"},
    {"value": "Apple Pay", "label_key": "pay_apple", "icon": "🍎"},
    {"value": "Bank Transfer", "label_key": "pay_bank", "icon": "🏛️"},
]


def register_routes(app):

    @app.context_processor
    def inject_globals():
        lang = get_lang()
        cur = get_current_user()
        unread = 0
        try:
            if cur:
                unread = models.get_unread_count(cur["id"])
        except:
            unread = 0
        return {
            "current_user": cur,
            "lang": lang,
            "lang_dir": LANG_DIR.get(lang, "ltr"),
            "t": make_t(lang),
            "LANGUAGES": LANGUAGES,
            "localize_service": localize_service,
            "localize_category": localize_category,
            "payment_methods": PAYMENT_METHODS,
            "owner_email": (Config.OWNER_EMAIL or "").lower(),
            "commission_rate": Config.COMMISSION_RATE,
            "owner_vodafone": Config.OWNER_VODAFONE_CASH,
            "owner_instapay": Config.OWNER_INSTAPAY,
            "unread_notifications": unread,
            "cart_count": cart.count(),
            # القالب بيستخدم enabled_providers() مباشرة، وبنمررها كمان هنا
            # عشان متحتاجش import جوّا كل قالب
            "enabled_providers": enabled_providers,
            "oauth_providers": enabled_providers(),
        }

    # -----------------------------------------------------------------
    # Language switcher
    # -----------------------------------------------------------------
    @app.route("/lang/<code>")
    def set_lang(code):
        if code in LANGUAGES:
            session["lang"] = code
            resp = redirect(request.referrer or url_for("landing"))
            resp.set_cookie("lang", code, max_age=365 * 24 * 3600)
            return resp
        return redirect(url_for("landing"))

    # -----------------------------------------------------------------
    # Public pages
    # -----------------------------------------------------------------
    @app.route("/")
    def index():
        return redirect(url_for("landing"))

    @app.route("/landing")
    def landing():
        lang = get_lang()
        cats = localize_categories(categories, lang)
        return render_template("landing.html", landing_categories=cats)

    @app.route("/overview")
    def overview():
        return render_template("overview.html")

    @app.route("/contact_us", methods=["GET", "POST"])
    def contact_us():
        if request.method == "POST":
            flash("flash_contact_thanks")
            return redirect(url_for("contact_us"))
        return render_template("contact_us.html")

    # -----------------------------------------------------------------
    # Auth
    # -----------------------------------------------------------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            role = request.form.get("role", "client").strip().lower()
            governorate = request.form.get("governorate", "").strip()
            city = request.form.get("city", "").strip()
            address = request.form.get("address", "").strip()
            lat, lng = _parse_coords(request.form.get("lat"), request.form.get("lng"))
            phone = _clean_phone(request.form.get("phone"))

            photo = None
            if role == "technician" and "photo" in request.files:
                photo = save_photo(request.files["photo"])

            if role not in ("client", "technician"):
                role = "client"  # الأدمن لا يُنشأ من صفحة التسجيل العامة

            if not name or not email or not password or not governorate:
                flash("flash_fill_fields")
                return redirect(url_for("register"))
            if len(password) < 6:
                flash("flash_pass_short")
                return redirect(url_for("register"))
            if confirm_password and confirm_password != password:
                flash("flash_pass_mismatch")
                return redirect(url_for("register"))
            if phone is None:
                flash("flash_phone_invalid")
                return redirect(url_for("register"))
            if governorate not in EGYPT_GOVERNORATES:
                flash("flash_fill_fields")
                return redirect(url_for("register"))

            existing = models.get_user_by_email(email)
            if existing:
                if not existing.get("has_password", 1) and existing.get("oauth_provider"):
                    # الإيميل ده اتسجل قبل كده بجوجل/فيسبوك بس
                    flash("flash_email_exists_oauth")
                else:
                    flash("flash_email_exists")
                return redirect(url_for("login"))

            models.create_user(name, email, password, role, governorate, city, address, lat, lng, photo, phone or None)
            flash("flash_reg_ok")
            return redirect(url_for("login"))

        return render_template("register.html", governorates=EGYPT_GOVERNORATES)

    def _login_user_and_redirect(user, new_account=False):
        """يفتح جلسة اليوزر ويوديه للوحته المناسبة — مستخدمة من تسجيل
        الدخول العادي وتسجيل الدخول بجوجل/فيسبوك معاً."""
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        session["name"] = user["name"]

        # حساب جوجل جديد: لسه مفيهوش محافظة/عنوان/تليفون — نوديه يكمّل بياناته
        # الأول (المحافظة مطلوبة عشان تحديد السعر والفنيين القريبين)
        if new_account or (user["role"] in ("client", "technician") and not user.get("governorate") and user.get("oauth_provider")):
            flash("flash_complete_profile")
            return redirect(url_for("profile", welcome=1))

        if user["role"] == "client":
            return redirect(url_for("customer_dashboard"))
        elif user["role"] == "technician":
            return redirect(url_for("technical_dashboard"))
        elif user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))
        flash("flash_role_unknown")
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = models.verify_user(email, password)
            if user:
                # الفني لازم موافقة الإدارة
                if user["role"] == "technician" and not user.get("is_approved"):
                    flash("flash_tech_pending")
                    return redirect(url_for("login"))
                return _login_user_and_redirect(user)

            # الإيميل موجود بس بحساب جوجل/فيسبوك بلا باسورد — نوجّهه صح
            existing = models.get_user_by_email(email)
            if existing and not existing.get("has_password", 1) and existing.get("oauth_provider"):
                flash("flash_use_oauth_instead")
                return redirect(url_for("login"))

            flash("flash_invalid_creds")
            return redirect(url_for("login"))

        return render_template("login.html")

    # -----------------------------------------------------------------
    # تسجيل الدخول بجوجل — بيوديك لصفحة جوجل تختار حسابك، وبيرجعك مسجّل.
    # فيسبوك متشال، فهو المزوّد الوحيد دلوقتي.
    # -----------------------------------------------------------------
    OAUTH_PROVIDERS = ("google",)

    @app.route("/auth/<provider>")
    def oauth_login(provider):
        if provider not in OAUTH_PROVIDERS or not is_provider_enabled(provider):
            flash("flash_oauth_not_configured")
            return redirect(url_for("login"))
        client = oauth.create_client(provider)

        # جوجل بيقبل بس localhost / 127.0.0.1 (http) أو دومين حقيقي (https).
        # جوجل بيرفض عناوين الـ IP الخام (زي 192.168.x.x) وبيطلع Error 400.
        # الحل: وحّد كل الدخول المحلي على 127.0.0.1 (هو اللي متسجل في Google Console).
        host_only = request.host.split(":")[0]
        port = request.host.partition(":")[2]
        port_suffix = (":" + port) if port else ""
        if not PUBLIC_BASE_URL:
            # localhost -> وحّده على 127.0.0.1 عشان الـ redirect_uri يطابق المسجل
            if host_only == "localhost":
                target = "http://127.0.0.1" + port_suffix + url_for("oauth_login", provider=provider)
                return redirect(target)
            # IP خام (LAN) — لو من نفس الجهاز حوّله لـ 127.0.0.1، لو من موبايل
            # ارفض برسالة واضحة (جوجل مستحيل يقبل IP).
            if _IPV4_RE.match(host_only) and host_only != "127.0.0.1":
                if request.remote_addr in ("127.0.0.1", "::1", host_only):
                    target = "http://127.0.0.1" + port_suffix + url_for("oauth_login", provider=provider)
                    return redirect(target)
                flash("flash_oauth_ip_blocked")
                return redirect(url_for("login"))

        if PUBLIC_BASE_URL:
            redirect_uri = PUBLIC_BASE_URL + url_for("oauth_callback", provider=provider)
        else:
            redirect_uri = url_for("oauth_callback", provider=provider, _external=True)
        app.logger.info("OAuth redirect_uri = %s  (لازم يكون مضاف بالظبط في Google Console)", redirect_uri)
        try:
            # prompt=select_account يخلي جوجل يعرض شاشة "اختر حسابك" كل مرة
            return client.authorize_redirect(redirect_uri, prompt="select_account")
        except Exception as e:
            app.logger.warning("OAuth (%s) redirect failed: %s", provider, e)
            flash("flash_oauth_failed")
            return redirect(url_for("login"))

    @app.route("/auth/<provider>/callback")
    def oauth_callback(provider):
        if provider not in OAUTH_PROVIDERS or not is_provider_enabled(provider):
            flash("flash_oauth_not_configured")
            return redirect(url_for("login"))

        client = oauth.create_client(provider)
        try:
            token = client.authorize_access_token()
        except Exception as e:
            app.logger.warning("OAuth (%s) failed: %s", provider, e)
            flash("flash_oauth_failed")
            return redirect(url_for("login"))

        oauth_id = None
        email = ""
        name = ""
        avatar = None
        try:
            userinfo = token.get("userinfo") or client.userinfo(token=token)
            oauth_id = userinfo.get("sub")
            email = (userinfo.get("email") or "").strip().lower()
            name = userinfo.get("name") or (email.split("@")[0] if email else "")
            avatar = userinfo.get("picture")
        except Exception as e:
            app.logger.warning("OAuth (%s) profile fetch failed: %s", provider, e)

        if not oauth_id:
            flash("flash_oauth_failed")
            return redirect(url_for("login"))

        user = models.get_user_by_oauth(provider, oauth_id)
        new_account = False

        if not user:
            if not email:
                # فيسبوك أحياناً ميرجعش إيميل لو المستخدم رفض صلاحية الإيميل
                flash("flash_oauth_no_email")
                return redirect(url_for("login"))

            existing = models.get_user_by_email(email)
            if existing:
                # نفس الإيميل مسجّل قبل كده (بباسورد عادي مثلاً) — نربط الحسابين
                # بدل ما نعمل حساب مكرر
                models.link_oauth_to_user(existing["id"], provider, oauth_id, avatar)
                user = models.get_user_by_id(existing["id"])
            else:
                # حساب جديد بالكامل — تسجيل الدخول الاجتماعي بيفتح حساب "عميل"
                # (مالك سيارة)، أما الفنيين فلازم يسجلوا بالنموذج العادي عشان
                # لازم يرفعوا صورتهم وتتراجع موافقتهم من الإدارة أولاً
                models.create_oauth_user(name or email.split("@")[0], email, provider, oauth_id, avatar)
                user = models.get_user_by_email(email)
                new_account = True

        if not user:
            flash("flash_oauth_failed")
            return redirect(url_for("login"))

        if user["role"] == "technician" and not user.get("is_approved"):
            flash("flash_tech_pending")
            return redirect(url_for("login"))

        return _login_user_and_redirect(user, new_account=new_account)

    @app.route("/notifications")
    @login_required
    def notifications_page():
        notes = models.get_notifications(session["user_id"], limit=20)
        # mark as read when viewed
        try:
            models.mark_notifications_read(session["user_id"])
        except:
            pass
        return render_template("notifications.html", notifications=notes)

    # -----------------------------------------------------------------
    # البروفايل — كل بيانات المستخدم اللي سجّلها + تعديلها
    # -----------------------------------------------------------------
    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        uid = session["user_id"]
        user = models.get_user_by_id(uid)
        if not user:
            session.clear()
            return redirect(url_for("login"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            phone = _clean_phone(request.form.get("phone"))
            governorate = request.form.get("governorate", "").strip()
            city = request.form.get("city", "").strip()
            address = request.form.get("address", "").strip()
            lat, lng = _parse_coords(request.form.get("lat"), request.form.get("lng"))

            if not name:
                flash("flash_fill_fields")
                return redirect(url_for("profile"))
            if phone is None:
                flash("flash_phone_invalid")
                return redirect(url_for("profile"))
            if user["role"] in ("client", "technician") and governorate not in EGYPT_GOVERNORATES:
                flash("flash_fill_fields")
                return redirect(url_for("profile"))
            if governorate and governorate not in EGYPT_GOVERNORATES:
                governorate = ""

            models.update_user_profile(uid, name, phone or None, governorate or None, city or None,
                                       address or None, lat, lng)
            session["name"] = name
            flash("flash_profile_saved")
            return redirect(url_for("profile"))

        if user["role"] == "client":
            orders_count = models.count_orders_by_customer(uid)
        elif user["role"] == "technician":
            orders_count = models.count_orders_by_technician(uid)
        else:
            orders_count = 0
        try:
            member_since = time.strftime("%Y-%m-%d", time.localtime(float(user.get("created_at") or 0)))
        except (TypeError, ValueError, OSError):
            member_since = ""
        return render_template(
            "profile.html",
            u=user,
            governorates=EGYPT_GOVERNORATES,
            orders_count=orders_count,
            member_since=member_since,
            welcome=request.args.get("welcome") == "1",
        )

    # -----------------------------------------------------------------
    # APIs بتخدم اختيار الموقع (بحث + عنوان من إحداثيات) وعرض السعر
    # -----------------------------------------------------------------
    @app.route("/api/geocode")
    def api_geocode():
        q = request.args.get("q", "").strip()
        if len(q) < 3:
            return jsonify({"ok": True, "results": []})
        try:
            return jsonify({"ok": True, "results": geo.search(q[:120])})
        except Exception as e:
            app.logger.warning("geocode failed: %s", e)
            return jsonify({"ok": False, "error": "geocode_failed"}), 502

    @app.route("/api/reverse")
    def api_reverse():
        lat, lng = _parse_coords(request.args.get("lat"), request.args.get("lng"))
        if lat is None or lng is None:
            return jsonify({"ok": False, "error": "bad_coords"}), 400
        try:
            res = geo.reverse(lat, lng)
        except Exception as e:
            app.logger.warning("reverse geocode failed: %s", e)
            return jsonify({"ok": False, "error": "geocode_failed"}), 502
        if not res:
            return jsonify({"ok": False, "error": "not_found"}), 404
        return jsonify({"ok": True, "result": res})

    @app.route("/api/quote", methods=["POST"])
    @role_required("client")
    def api_quote():
        """السعر بيظهر بس لما العميل يختار نوع وموديل عربيته."""
        data = request.get_json(silent=True) or {}
        car_make = (data.get("car_make") or "").strip()
        car_model = (data.get("car_model") or "").strip()
        if not car_make or not car_model:
            return jsonify({"ok": False, "reason": "no_car"})
        cust = get_current_user() or {}
        gov, city = _eff_region(cust, data.get("governorate"), data.get("city"))
        location = (data.get("location") or "").strip()
        if data.get("service_id"):
            try:
                wanted = [(int(data["service_id"]), 1)]
            except (TypeError, ValueError):
                wanted = []
        else:
            wanted = [(i["service_id"], i["qty"]) for i in cart.items()]
        lines, total = [], 0
        for sid, qty in wanted:
            svc = get_service_by_id(sid)
            if not svc:
                continue
            unit = get_adjusted_price(svc["base_price"], gov, city, location, car_make)
            lines.append({"service_id": sid, "unit": unit, "qty": qty, "line_total": unit * qty})
            total += unit * qty
        return jsonify({"ok": True, "lines": lines, "total": total})

    @app.route("/logout")
    def logout():
        session.clear()
        flash("flash_logout")
        return redirect(url_for("landing"))

    def _send_reset_otp(email):
        """يبعت كود تحقق جديد لإيميل واحد ويسجّل وقت الإرسال (لعداد إعادة الإرسال)."""
        user = models.get_user_by_email(email)
        # نفس الرسالة سواء الإيميل موجود أو لا، لمنع كشف وجود الحساب من عدمه
        if user:
            otp = f"{random.randint(100000, 999999)}"
            session["otp_hash"] = _hash_otp(otp)
            session["otp_expires"] = time.time() + Config.OTP_EXPIRY_SECONDS
            session["otp_last_sent"] = time.time()
            session["reset_email"] = email
            send_otp_email(app, email, otp)
        else:
            # نحافظ على نفس التوقيت حتى لو الإيميل مش موجود، عشان محدش يعرف
            # يفرّق بين الحالتين من سرعة الرد
            session["reset_email"] = email
            session["otp_last_sent"] = time.time()
            session["otp_expires"] = time.time() + Config.OTP_EXPIRY_SECONDS
            session["otp_hash"] = _hash_otp(f"{random.randint(100000, 999999)}")

    @app.route("/forgot_password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            _send_reset_otp(email)
            flash("flash_otp_sent")
            return redirect(url_for("verify_otp"))
        return render_template("forgot_password.html")

    @app.route("/resend_otp", methods=["GET", "POST"])
    def resend_otp():
        email = session.get("reset_email")
        if not email:
            flash("flash_verify_first")
            return redirect(url_for("forgot_password"))

        last_sent = session.get("otp_last_sent", 0)
        remaining = Config.OTP_RESEND_COOLDOWN_SECONDS - (time.time() - last_sent)
        if remaining > 0:
            flash("flash_otp_wait")
            return redirect(url_for("verify_otp"))

        _send_reset_otp(email)
        flash("flash_otp_resent")
        return redirect(url_for("verify_otp"))

    @app.route("/verify_otp", methods=["GET", "POST"])
    def verify_otp():
        if request.method == "POST":
            entered = request.form.get("otp", "").strip()
            stored_hash = session.get("otp_hash")
            expires = session.get("otp_expires", 0)

            if not stored_hash or time.time() > expires:
                flash("flash_otp_expired")
                return redirect(url_for("forgot_password"))

            if _hash_otp(entered) != stored_hash:
                flash("flash_otp_invalid")
                return redirect(url_for("verify_otp"))

            session.pop("otp_hash", None)
            session.pop("otp_expires", None)
            session["otp_verified"] = True
            return redirect(url_for("reset_password"))

        expires = session.get("otp_expires", 0)
        last_sent = session.get("otp_last_sent", 0)
        expires_in = max(0, int(expires - time.time()))
        resend_wait = max(0, int(Config.OTP_RESEND_COOLDOWN_SECONDS - (time.time() - last_sent)))
        return render_template("verify_otp.html", expires_in=expires_in, resend_wait=resend_wait)

    @app.route("/reset_password", methods=["GET", "POST"])
    def reset_password():
        if not session.get("otp_verified") or not session.get("reset_email"):
            flash("flash_verify_first")
            return redirect(url_for("forgot_password"))

        if request.method == "POST":
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            if len(new_password) < 6:
                flash("flash_pass_short")
                return redirect(url_for("reset_password"))
            if new_password != confirm_password:
                flash("flash_pass_mismatch")
                return redirect(url_for("reset_password"))

            models.update_user_password(session["reset_email"], new_password)
            flash("flash_pass_reset")

            session.pop("otp_verified", None)
            session.pop("reset_email", None)
            session.pop("otp_last_sent", None)
            return redirect(url_for("login"))

        return render_template("reset_password.html")

    # -----------------------------------------------------------------
    # Client area
    # -----------------------------------------------------------------
    @app.route("/customer_dashboard")
    @role_required("client")
    def customer_dashboard():
        """الصفحة الرئيسية الموحّدة: المكان + البحث + التصنيفات + كل الخدمات
        + الطلبات الأخيرة. (صفحة الخدمات اتدمجت هنا)."""
        lang = get_lang()
        my_recent_orders = models.get_orders_by_customer(session["user_id"], limit=5)
        cats = localize_categories(categories, lang)
        cats_meta = {localize_category(k, lang): k for k in categories}
        cur = get_current_user() or {}
        gov = cur.get("governorate")
        city = cur.get("city")
        addr = cur.get("address")

        cat_key = get_category_key(request.args.get("cat", "").strip())
        if cat_key:
            raw_list = get_services_by_category(cat_key, lang)
            active_cat = localize_category(cat_key, lang)
        else:
            raw_list = get_localized_services(lang)
            active_cat = None

        services = []
        for s in raw_list:
            ck = get_category_for_service(s["id"])
            services.append({
                **s,
                "base_price": get_adjusted_price(s["base_price"], gov, city, addr),
                "visual": get_visual_for_service(s["id"]),
                "image": get_image_for_service(s["id"]),
                "cat": ck,
                "cat_label": localize_category(ck, lang),
            })
        return render_template(
            "customer_dashboard.html",
            categories=cats,
            cats_meta=cats_meta,
            all_categories=categories,
            services=services,
            active_cat=active_cat,
            orders=my_recent_orders,
            gov=gov,
            city=city,
        )

    @app.route("/customer_services")
    @login_required
    def customer_services():
        """صفحة الخدمات اتدمجت مع الصفحة الرئيسية — بنوجّه عشان كل اللينكات القديمة
        تفضل شغالة (مع الحفاظ على فلتر التصنيف لو موجود)."""
        cat = request.args.get("cat", "").strip()
        target = url_for("customer_dashboard", cat=cat) if cat else url_for("customer_dashboard")
        return redirect(target)

    @app.route("/service/<int:service_id>")
    @login_required
    def service_details(service_id):
        lang = get_lang()
        service = get_localized_service_by_id(service_id, lang)
        if not service:
            return render_template("404.html"), 404
        cat_key = get_category_for_service(service_id)
        visual = get_visual_for_service(service_id)
        image_url = get_image_for_service(service_id)
        cat_name = localize_category(cat_key, lang) if cat_key else ""
        # سعر حسب منطقته (التجمع/زايد أغلى)
        cur = get_current_user()
        gov = cur.get("governorate") if cur else None
        city = cur.get("city") if cur else None
        addr = cur.get("address") if cur else None
        adj_price = get_adjusted_price(service["base_price"], gov, city, addr)
        zone = get_zone(gov, city, addr)
        related = [s for s in get_services_by_category(cat_key, lang) if s["id"] != service_id][:4] if cat_key else []
        # عدّل السعر المعروض
        service = {**service, "base_price": adj_price, "zone": zone}
        return render_template("service_details.html", service=service, cat_key=cat_key, cat_name=cat_name, visual=visual, image_url=image_url, related=related, zone=zone)

    @app.route("/order_service/<int:service_id>", methods=["GET", "POST"])
    @role_required("client")
    def order_service(service_id):
        lang = get_lang()
        service = get_localized_service_by_id(service_id, lang)
        if not service:
            return render_template("404.html"), 404
        # سعر حسب منطقته للعرض
        cur = get_current_user()
        gov0 = cur.get("governorate") if cur else None
        city0 = cur.get("city") if cur else None
        addr0 = cur.get("address") if cur else None
        raw = get_service_by_id(service_id)
        adj_for_display = get_adjusted_price(service["base_price"], gov0, city0, addr0)
        service_display = {**service, "base_price": adj_for_display}
        visual = get_visual_for_service(service_id)
        image_url = get_image_for_service(service_id)

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            location = request.form.get("location", "").strip()
            lat, lng = _parse_coords(request.form.get("lat"), request.form.get("lng"))
            car_make = request.form.get("car_make", "").strip()
            car_model = request.form.get("car_model", "").strip()
            car_year = request.form.get("car_year", "").strip()
            # فوري — لو مفيش ميعاد نعتبره الآن
            scheduled_at = request.form.get("scheduled_at", "").strip() or time.strftime("%Y-%m-%d %H:%M")

            if not all([name, phone, location, car_make, car_model]):
                flash("flash_fill_fields")
                return redirect(url_for("order_service", service_id=service_id))

            # السعر النهائي حسب المنطقة + نوع العربية
            raw = get_service_by_id(service_id)
            cust0 = models.get_user_by_id(session["user_id"])
            gov_for_price, city_for_price = _eff_region(cust0, request.form.get("governorate"), request.form.get("city"))
            final_price = get_adjusted_price(raw["base_price"], gov_for_price, city_for_price, location, car_make)
            car_label = f"{car_make} {car_model}" + (f" {car_year}" if car_year else "")
            models.create_order(
                service_id=service_id,
                customer_id=session["user_id"],
                name=name,
                phone=phone,
                location=location,
                payment_method="Pending",
                service_name=raw["name"],
                service_price=final_price,
                lat=lat,
                lng=lng,
                scheduled_at=scheduled_at,
                car_make=car_make,
                car_model=car_model,
                car_year=car_year or None,
            )
            # إشعار للفنيين القريبين فقط — نفس المحافظة
            gov = gov_for_price or ""
            for tech in [u for u in models.get_all_users() if u["role"]=="technician" and (not gov or u.get("governorate")==gov)]:
                models.add_notification(tech["id"], f"طلب جديد: {raw['name']}", f"من {name} في {gov or location} — 🚗 {car_label} — ميعاد: {scheduled_at} — السعر: {final_price} ج.م")

            flash("flash_order_placed")
            return redirect(url_for("my_orders"))

        return render_template("order_form.html", service=service_display, car_makes=CAR_MAKES, car_makes_list=get_car_makes(), base_price=raw["base_price"], gov=gov0, city=city0, address=addr0, saved_lat=(cur or {}).get("lat"), saved_lng=(cur or {}).get("lng"), saved_phone=(cur or {}).get("phone") or "", visual=visual, image_url=image_url)

    # -----------------------------------------------------------------
    # السلة والدفع — إحساس تطبيق طلبات (كل حاجة في مكان واحد)
    # -----------------------------------------------------------------
    def _cart_line_items(lang, car_make=None):
        """يبني أصناف السلة مع السعر المظبوط حسب منطقة العميل (ونوع العربية لو اتحدد)."""
        cur = get_current_user() or {}
        gov = cur.get("governorate")
        city = cur.get("city")
        addr = cur.get("address")
        line_items = []
        for it in cart.items():
            svc = get_service_by_id(it["service_id"])
            if not svc:
                continue
            loc = localize_service(svc, lang)
            unit = get_adjusted_price(svc["base_price"], gov, city, addr, car_make)
            line_items.append({
                "service_id": svc["id"],
                "name": loc["name"],
                "description": loc["description"],
                "qty": it["qty"],
                "unit_price": unit,
                "line_total": unit * it["qty"],
                "visual": get_visual_for_service(svc["id"]),
                "image": get_image_for_service(svc["id"]),
            })
        return line_items

    @app.route("/cart")
    @role_required("client")
    def cart_view():
        lang = get_lang()
        items = _cart_line_items(lang)
        subtotal = sum(i["line_total"] for i in items)
        return render_template("cart.html", items=items, subtotal=subtotal)

    @app.route("/cart/add/<int:service_id>", methods=["POST", "GET"])
    @role_required("client")
    def cart_add(service_id):
        if not get_service_by_id(service_id):
            return render_template("404.html"), 404
        try:
            qty = int(request.values.get("qty", 1))
        except (TypeError, ValueError):
            qty = 1
        cart.add_item(service_id, qty)
        flash("flash_cart_added")
        nxt = request.values.get("next") or request.referrer
        return redirect(nxt or url_for("cart_view"))

    @app.route("/cart/update/<int:service_id>", methods=["POST"])
    @role_required("client")
    def cart_update(service_id):
        try:
            qty = int(request.form.get("qty", 1))
        except (TypeError, ValueError):
            qty = 1
        cart.set_qty(service_id, qty)
        return redirect(url_for("cart_view"))

    @app.route("/cart/remove/<int:service_id>", methods=["POST"])
    @role_required("client")
    def cart_remove(service_id):
        cart.remove_item(service_id)
        return redirect(url_for("cart_view"))

    @app.route("/cart/clear", methods=["POST"])
    @role_required("client")
    def cart_clear():
        cart.clear()
        return redirect(url_for("cart_view"))

    @app.route("/checkout", methods=["GET", "POST"])
    @role_required("client")
    def checkout():
        lang = get_lang()
        if cart.is_empty():
            flash("flash_cart_empty")
            return redirect(url_for("customer_services"))

        cur = get_current_user() or {}
        gov0 = cur.get("governorate")
        city0 = cur.get("city")
        addr0 = cur.get("address")

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            location = request.form.get("location", "").strip()
            lat, lng = _parse_coords(request.form.get("lat"), request.form.get("lng"))
            car_make = request.form.get("car_make", "").strip()
            car_model = request.form.get("car_model", "").strip()
            car_year = request.form.get("car_year", "").strip()
            scheduled_at = request.form.get("scheduled_at", "").strip() or time.strftime("%Y-%m-%d %H:%M")
            gov_eff, city_eff = _eff_region(cur, request.form.get("governorate"), request.form.get("city"))

            if not all([name, phone, location, car_make, car_model]):
                flash("flash_fill_fields")
                return redirect(url_for("checkout"))

            line_items = _cart_line_items(lang, car_make)
            car_label = f"{car_make} {car_model}" + (f" {car_year}" if car_year else "")
            for li in line_items:
                raw = get_service_by_id(li["service_id"])
                final_price = get_adjusted_price(raw["base_price"], gov_eff, city_eff, location, car_make)
                models.create_order(
                    service_id=li["service_id"],
                    customer_id=session["user_id"],
                    name=name,
                    phone=phone,
                    location=location,
                    payment_method="Pending",
                    service_name=raw["name"],
                    service_price=final_price,
                    lat=lat,
                    lng=lng,
                    scheduled_at=scheduled_at,
                    car_make=car_make,
                    car_model=car_model,
                    car_year=car_year or None,
                )
            # نفس منطق الطلب الفردي: إشعار الفنيين في نفس المحافظة
            for tech in [u for u in models.get_all_users() if u["role"] == "technician" and (not gov_eff or u.get("governorate") == gov_eff)]:
                models.add_notification(
                    tech["id"],
                    f"طلبات جديدة ({len(line_items)})",
                    f"من {name} في {gov_eff or location} — 🚗 {car_label} — ميعاد: {scheduled_at}",
                )
            cart.clear()
            flash("flash_order_placed")
            return redirect(url_for("my_orders"))

        items = _cart_line_items(lang)
        subtotal = sum(i["line_total"] for i in items)
        return render_template(
            "checkout.html",
            items=items,
            subtotal=subtotal,
            car_makes=CAR_MAKES,
            car_makes_list=get_car_makes(),
            gov=gov0,
            city=city0,
            address=addr0,
            saved_lat=cur.get("lat"),
            saved_lng=cur.get("lng"),
            saved_phone=cur.get("phone") or "",
        )

    @app.route("/my_orders")
    @role_required("client")
    def my_orders():
        orders = models.get_orders_by_customer(session["user_id"])
        return render_template("my_orders.html", orders=orders)

    @app.route("/track_order/<int:order_id>")
    @role_required("client")
    def track_order(order_id):
        lang = get_lang()
        order = models.get_order_by_id(order_id)
        if not order:
            return render_template("404.html"), 404
        if order["customer_id"] != session["user_id"]:
            flash("flash_no_access")
            return redirect(url_for("my_orders"))

        step_order = ["Pending", "In Progress", "Awaiting Payment", "Completed"]
        # Completed يظهر فقط بعد الدفع
        display_completed = order["status"] == "Completed" and order.get("payment_status") == "Paid"
        current_index = step_order.index(order["status"]) if order["status"] in step_order else -1
        if display_completed:
            current_index = 3
        steps = [
            {"key": "step_1", "done": True},
            {"key": "step_2", "done": current_index >= 1},
            {"key": "step_3", "done": current_index >= 2},
            {"key": "step_4", "done": display_completed},
        ]
        # خط سير الفني ووقت الوصول — لما الفني يقبل
        technician = models.get_user_by_id(order["technician_id"]) if order.get("technician_id") else None
        tech_lat = technician.get("lat") if technician else None
        tech_lng = technician.get("lng") if technician else None
        client_lat = order.get("lat")
        client_lng = order.get("lng")
        # fallback لموقع العميل المسجل لو الطلب بدون إحداثيات
        if client_lat is None or client_lng is None:
            cust = models.get_user_by_id(order["customer_id"])
            client_lat = cust.get("lat") if cust else None
            client_lng = cust.get("lng") if cust else None
        distance = haversine(tech_lat, tech_lng, client_lat, client_lng)
        eta_min = int(distance / 0.67) + 5 if distance is not None else None
        route = None
        if technician and client_lat and client_lng and tech_lat and tech_lng:
            route = {"tech": {"lat": tech_lat, "lng": tech_lng, "name": technician["name"], "gov": technician.get("governorate")}, "client": {"lat": client_lat, "lng": client_lng}, "distance": distance, "eta": eta_min}
        return render_template("track_order.html", order=order, steps=steps, payment_methods=PAYMENT_METHODS, route=route, technician=technician)

    @app.route("/cancel_order/<int:order_id>")
    @role_required("client")
    def cancel_order(order_id):
        order = models.get_order_by_id(order_id)
        if not order or order["customer_id"] != session["user_id"]:
            flash("flash_no_access")
            return redirect(url_for("my_orders"))
        # منع الإلغاء بعد ما الفني يستلم الطلب — ده بيمنع احتيال "لغى بعد ما الفني وصل"
        if order["technician_id"] is not None or order["status"] != "Pending":
            flash("flash_cancel_fail_assigned")
            return redirect(url_for("my_orders"))
        # بدل الحذف — نحفظه كـ Rejected عشان يظهر في سجل المالك المالي
        models.update_order_status(order_id, "Rejected")
        flash("flash_order_cancelled")
        return redirect(url_for("my_orders"))

    @app.route("/client_complete_order/<int:order_id>")
    @role_required("client")
    def client_complete_order(order_id):
        # لم يعد يُستخدم — الدفع هو الذي يُكمل الطلب
        flash("flash_pay_first")
        return redirect(url_for("track_order", order_id=order_id))

    @app.route("/pay_order/<int:order_id>", methods=["POST"])
    @role_required("client")
    def pay_order(order_id):
        order = models.get_order_by_id(order_id)
        if not order or order["customer_id"] != session["user_id"]:
            flash("flash_no_access")
            return redirect(url_for("my_orders"))
        if order["status"] not in ("Awaiting Payment", "Completed"):
            flash("flash_not_ready_to_pay")
            return redirect(url_for("track_order", order_id=order_id))
        if order.get("payment_status") == "Paid":
            flash("flash_already_paid")
            return redirect(url_for("track_order", order_id=order_id))
        payment_method = request.form.get("payment_method", "").strip()
        coupon_code = request.form.get("coupon_code", "").strip().upper()
        allowed = {p["value"] for p in PAYMENT_METHODS}
        if payment_method not in allowed:
            flash("flash_fill_fields")
            return redirect(url_for("track_order", order_id=order_id))
        # كوبون
        discount = 0
        if coupon_code:
            coupon, err = models.validate_coupon(coupon_code, order.get("location"))
            if err:
                flash("flash_coupon_bad")
                return redirect(url_for("track_order", order_id=order_id))
            discount = int(order["service_price"] * coupon["discount_percent"] / 100)
            # حدّث السعر
            with models.get_db() as conn:
                conn.execute("UPDATE orders SET coupon_code=?, discount=?, service_price = service_price - ? WHERE id=?", (coupon_code, discount, discount, order_id))
            models.use_coupon(coupon_code)
            models.add_points(order["customer_id"], 10)
            flash("flash_coupon_ok")
        models.mark_order_paid(order_id, payment_method)
        # إشعار للفني إن العميل دفع + نقاط ولاء
        if order.get("technician_id"):
            models.add_notification(order["technician_id"], "تم الدفع ✅", f"العميل دفع {order['service_price'] - discount} ج.م لطلب #{order_id}")
        models.add_points(order["customer_id"], 20)
        flash("flash_paid_completed")
        return redirect(url_for("track_order", order_id=order_id))

    @app.route("/rate_order/<int:order_id>", methods=["POST"])
    @role_required("client")
    def rate_order(order_id):
        order = models.get_order_by_id(order_id)
        if not order or order["customer_id"] != session["user_id"]:
            flash("flash_no_access")
            return redirect(url_for("my_orders"))
        if order.get("payment_status") != "Paid" or order["status"] != "Completed":
            flash("flash_not_ready_to_pay")
            return redirect(url_for("track_order", order_id=order_id))
        if order.get("rating") is not None:
            flash("flash_already_paid")
            return redirect(url_for("track_order", order_id=order_id))
        try:
            rating = int(request.form.get("rating", 0))
            review = request.form.get("review", "").strip()[:300]
            if rating < 1 or rating > 5:
                raise ValueError
        except:
            flash("flash_fill_fields")
            return redirect(url_for("track_order", order_id=order_id))
        models.add_rating(order_id, rating, review)
        if order.get("technician_id"):
            models.add_notification(order["technician_id"], f"تقييم جديد ⭐ {rating}", f"من العميل: {review or 'بدون تعليق'}")
        flash("flash_rated")
        return redirect(url_for("track_order", order_id=order_id))

    @app.route("/order_chat/<int:order_id>", methods=["GET", "POST"])
    @login_required
    def order_chat(order_id):
        order = models.get_order_by_id(order_id)
        if not order:
            return render_template("404.html"), 404
        uid = session["user_id"]
        if uid not in (order["customer_id"], order.get("technician_id")):
            # العميل أو الفني المخصص فقط
            if session.get("role") == "technician" and order["status"] == "Pending":
                pass  # الفني يقدر يشوف قبل القبول للسؤال
            else:
                flash("flash_no_access")
                return redirect(url_for("landing"))
        if request.method == "POST":
            msg = request.form.get("message", "").strip()
            if msg:
                models.add_message(order_id, uid, msg)
                # إشعار للطرف الآخر
                other = order["customer_id"] if uid != order["customer_id"] else order.get("technician_id")
                if other:
                    sender = models.get_user_by_id(uid)
                    models.add_notification(other, f"رسالة جديدة 💬", f"من {sender['name']}: {msg[:40]}")
        # إذا طلب JSON
        if request.args.get("format") == "json":
            from flask import jsonify
            return jsonify(models.get_messages(order_id))
        messages = models.get_messages(order_id)
        return render_template("chat.html", order=order, messages=messages)

    @app.route("/approve_technician/<int:user_id>", methods=["POST"])
    @owner_required
    def approve_technician(user_id):
        models.approve_technician(user_id)
        u = models.get_user_by_id(user_id)
        if u:
            models.add_notification(user_id, "تمت الموافقة ✅", "يمكنك الآن استقبال الطلبات")
        flash("flash_tech_approved")
        return redirect(url_for("admin_dashboard"))

    @app.route("/invoice/<int:order_id>")
    @login_required
    def invoice(order_id):
        order = models.get_order_by_id(order_id)
        if not order or (session["user_id"] not in (order["customer_id"], order.get("technician_id")) and session.get("role") != "admin" and models.get_user_by_id(session["user_id"])["email"].lower() != Config.OWNER_EMAIL.lower()):
            flash("flash_no_access")
            return redirect(url_for("landing"))
        customer = models.get_user_by_id(order["customer_id"])
        technician = models.get_user_by_id(order["technician_id"]) if order.get("technician_id") else None
        return render_template("invoice.html", order=order, customer=customer, technician=technician)

    @app.route("/update_location", methods=["POST"])
    @role_required("technician")
    def update_location():
        lat = request.form.get("lat") or request.json.get("lat") if request.is_json else None
        lng = request.form.get("lng") or request.json.get("lng") if request.is_json else None
        try:
            lat = float(lat); lng = float(lng)
        except:
            return "bad", 400
        # حدّث موقع الفني نفسه
        with models.get_db() as conn:
            conn.execute("UPDATE users SET lat=?, lng=? WHERE id=?", (lat, lng, session["user_id"]))
        # حدّث كل طلباته النشطة In Progress
        with models.get_db() as conn:
            conn.execute("UPDATE orders SET tech_lat=?, tech_lng=? WHERE technician_id=? AND status='In Progress'", (lat, lng, session["user_id"]))
        return "ok"

    # -----------------------------------------------------------------
    # Technician area
    # -----------------------------------------------------------------
    @app.route("/technical_dashboard")
    @role_required("technician")
    def technical_dashboard():
        raw_pending = models.get_orders_by_status("Pending")
        tech = models.get_user_by_id(session["user_id"])
        pending_orders = []
        for o in raw_pending:
            cust = models.get_user_by_id(o["customer_id"])
            o_lat = o.get("lat") or (cust.get("lat") if cust else None)
            o_lng = o.get("lng") or (cust.get("lng") if cust else None)
            t_lat = tech.get("lat") if tech else None
            t_lng = tech.get("lng") if tech else None
            dist = haversine(t_lat, t_lng, o_lat, o_lng)
            eta = f"{int(dist / 0.67) + 5} د" if dist is not None else None
            same_gov = cust and tech and cust.get("governorate") and cust.get("governorate") == tech.get("governorate")
            # حصر القريب فقط: نفس المحافظة أو أقل من 30 كم، غير كده من آخر الدنيا ما يظهرش
            if tech.get("governorate"):
                if not same_gov and (dist is None or dist > 30):
                    continue
            pending_orders.append({**o, "distance": dist, "eta": eta, "same_gov": same_gov, "customer_gov": cust.get("governorate") if cust else ""})
        pending_orders.sort(key=lambda x: (x["distance"] if x["distance"] is not None else 9999))
        my_active_orders = [
            o for o in models.get_orders_by_technician(session["user_id"])
            if o["status"] == "In Progress"
        ]
        earnings = models.get_technician_earnings(session["user_id"], Config.COMMISSION_RATE)
        wallet = models.get_wallet(session["user_id"])
        return render_template(
            "technical_dashboard.html",
            pending_orders=pending_orders,
            my_active_orders=my_active_orders,
            earnings=earnings,
            wallet=wallet,
        )

    @app.route("/technician_tasks")
    @role_required("technician")
    def technician_tasks():
        tasks = models.get_orders_by_technician(session["user_id"])
        return render_template("technician_tasks.html", tasks=tasks)

    @app.route("/accept_order/<int:order_id>")
    @role_required("technician")
    def accept_order(order_id):
        order = models.get_order_by_id(order_id)
        if order and order["status"] == "Pending":
            otp = str(random.randint(1000, 9999))
            with models.get_db() as conn:
                conn.execute("UPDATE orders SET status='In Progress', technician_id=?, otp_code=? WHERE id=?", (session["user_id"], otp, order_id))
            tech = models.get_user_by_id(session["user_id"])
            models.add_notification(order["customer_id"], "الفني قبل طلبك ✅", f"{tech['name']} قبل طلب #{order_id} — كود التسليم: {otp} — شوف خط السير")
            flash("flash_order_accepted")
        return redirect(url_for("technical_dashboard"))

    @app.route("/reject_order/<int:order_id>")
    @role_required("technician")
    def reject_order(order_id):
        models.update_order_status(order_id, "Rejected")
        return redirect(url_for("technical_dashboard"))

    @app.route("/technician_complete_order/<int:order_id>", methods=["GET", "POST"])
    @role_required("technician")
    def technician_complete_order(order_id):
        order = models.get_order_by_id(order_id)
        if not order or order["technician_id"] != session["user_id"]:
            return redirect(url_for("technician_tasks"))
        if request.method == "POST":
            otp = request.form.get("otp", "").strip()
            if otp and otp == order.get("otp_code"):
                models.update_order_status(order_id, "Awaiting Payment")
                models.add_notification(order["customer_id"], "الفني أنهى الشغل ⏳", f"طلب #{order_id} جاهز للدفع — ادفع عشان يظهر مكتمل")
                flash("flash_waiting_payment")
            else:
                flash("flash_otp_wrong")
            return redirect(url_for("technician_tasks"))
        # GET — اعرض صفحة إدخال OTP
        return render_template("verify_otp_tech.html", order=order)

    @app.route("/reverse_order/<int:order_id>")
    @role_required("technician")
    def reverse_order(order_id):
        order = models.get_order_by_id(order_id)
        if not order:
            return render_template("404.html"), 404
        status_label = (
            "tech_status_arrived" if order["status"] == "Completed"
            else "tech_status_not_arrived"
        )
        return render_template("reverse_order.html", order=order, technician_status=status_label)

    # -----------------------------------------------------------------
    # Admin area
    # -----------------------------------------------------------------
    @app.route("/admin_dashboard")
    @owner_required
    def admin_dashboard():
        stats = {
            "total_orders": models.count_orders(),
            "pending_orders": models.count_orders("Pending"),
            "completed_orders": models.count_orders("Completed"),
            "total_clients": models.count_users_by_role("client"),
            "total_technicians": models.count_users_by_role("technician"),
        }
        stats["total_users"] = stats["total_clients"] + stats["total_technicians"] + models.count_users_by_role("admin")
        stats["revenue_paid"] = models.get_total_revenue()
        stats["revenue_pending"] = models.get_pending_revenue()
        stats["rejected_orders"] = models.count_orders("Rejected")
        # إسكرو 20%: عمولة المنصة والمستحق للفنيين
        stats["commission_total"] = stats["revenue_paid"] * Config.COMMISSION_RATE
        stats["payout_pending_total"] = stats["revenue_paid"] * (1 - Config.COMMISSION_RATE) - sum(
            1 for o in models.get_all_orders() if o.get("payment_status") == "Paid" and o.get("payout_status") == "Paid" for _ in [1]
        ) * 0  # placeholder
        # نحسب المعلق للفنيين فعلياً
        all_paid = [o for o in models.get_all_orders() if o.get("payment_status") == "Paid"]
        stats["payout_pending_total"] = sum(o["service_price"] for o in all_paid if o.get("payout_status") != "Paid") * (1 - Config.COMMISSION_RATE)
        recent_orders = models.get_recent_orders(limit=10)

        # كشف احتيال: طلب ملغي لكن كان فيه فني مستلم — ده اللي تقصده "لغى وخد الفلوس"
        all_orders = models.get_all_orders(limit=50)
        suspicious = [o for o in all_orders if o["status"] == "Rejected" and o["technician_id"] is not None]
        # مستحقات الفنيين المعلقة
        pending_payouts = models.get_pending_payouts()

        # بيانات كل المستخدمين مع عدد طلباتهم/مهامهم — للمالك فقط
        raw_users = models.get_all_users()
        users_data = []
        for u in raw_users:
            if u["role"] == "client":
                cnt = models.count_orders_by_customer(u["id"])
            elif u["role"] == "technician":
                cnt = models.count_orders_by_technician(u["id"])
            else:
                cnt = 0
            users_data.append({**u, "orders_count": cnt})

        # موافقة الفنيين
        pending_techs = models.get_pending_technicians()
        # أرباح كل فني + محفظته المباشرة زي أوبر
        tech_earnings = {}
        wallets = {}
        for u in raw_users:
            if u["role"] == "technician":
                tech_earnings[u["id"]] = models.get_technician_earnings(u["id"], Config.COMMISSION_RATE)
                wallets[u["id"]] = models.get_wallet(u["id"])

        return render_template("admin_dashboard.html", stats=stats, recent_orders=recent_orders, users_data=users_data, suspicious=suspicious, pending_payouts=pending_payouts, tech_earnings=tech_earnings, wallets=wallets, pending_techs=pending_techs)

    @app.route("/mark_payout/<int:order_id>", methods=["POST"])
    @owner_required
    def mark_payout(order_id):
        order = models.get_order_by_id(order_id)
        if order and order.get("payment_status") == "Paid" and order.get("payout_status") == "Pending":
            models.mark_payout_done(order_id)
            flash("flash_payout_done")
        return redirect(url_for("admin_dashboard"))

    # -----------------------------------------------------------------
    # Error handlers
    # -----------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500


app = create_app()

# -------------------------------------------------------------------
# وراء بروكسي (Render / Railway / Hugging Face...): بدون السطور دي
# كل الطلبات هتظهر http والـ redirect URLs هتبقى غلط (فشل OAuth).
# -------------------------------------------------------------------
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_for=1)

# رابط الموقع الحقيقي — بيستخدم في redirect URLs بتاعة جوجل
PUBLIC_BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")

if __name__ == "__main__":
    is_local = not PUBLIC_BASE_URL  # محلي = مفيش BASE_URL متحدد
    # اعرف عنوان الجهاز على الشبكة المحلية عشان تفتح الموقع من الموبايل
    lan_ip = None
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # مفيش داتا بتتبعت فعلياً — بس ده أسرع way لمعرفة الـ IP المستخدم للتوجيه
            s.connect(("10.255.255.255", 1))
            lan_ip = s.getsockname()[0]
        finally:
            s.close()
    except Exception:
        try:
            lan_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            lan_ip = None

    # HTTPS محلي (شهادة مؤقتة): ده اللي بيخلّي المتصفح يسمح بـ GPS (تحديد الموقع)
    # على الموبايل أو من عنوان الـ IP. شغّله بـ: set USE_HTTPS=1  (أو run_https.bat)
    use_https = os.environ.get("USE_HTTPS", "0") == "1"
    ssl_ctx = None
    if use_https:
        try:
            import cryptography  # noqa: F401
            ssl_ctx = "adhoc"
        except ImportError:
            print("⚠️ HTTPS محتاج مكتبة cryptography:  pip install cryptography")
            use_https = False
    scheme = "https" if use_https else "http"

    print("=" * 56)
    if is_local:
        print("  DrCar جاهز!")
        print(f"  على الجهاز ده:      {scheme}://localhost:5000")
        if lan_ip:
            print(f"  من الموبايل:        {scheme}://{lan_ip}:5000")
            print("  (لازم الموبايل والكمبيوتر على نفس شبكة الواي فاي)")
            if not use_https:
                print("  ⚠️ GPS على الموبايل محتاج https — شغّل run_https.bat")
        else:
            print("  من الموبايل:        شغّل ipconfig وهات عنوان IPv4 وحطه بدل 127.0.0.1")
        print()
        print("  ℹ️ للنشر على سيرفر وكل الناس تفتحه، شوف DEPLOY.md")
    else:
        print(f"  🌐 DrCar شغال على: {PUBLIC_BASE_URL}")
    print("=" * 56)

    # debug مفتوح محلياً بس — على السيرفر دايماً مقفول
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=is_local and os.environ.get("FLASK_DEBUG", "0") == "1",
        ssl_context=ssl_ctx,
    )