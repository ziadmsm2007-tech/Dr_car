"""الدفع أونلاين بالكارت عبر Paymob (مصر).

التدفق:
1) auth token بالمفتاح العام.
2) تسجيل طلب بالمبلغ (بالقروش) + merchant_order_id = رقم طلبنا.
3) payment key ببيانات العميل + integration ID.
4) تحويل العميل لصفحة الـ iFrame للدفع.
5) Paymob يرجّع العميل على /paymob/callback ونتحقق من HMAC قبل
   ما نعتبر الطلب مدفوع (مهم: أي callback من غير توقيع سليم مرفوض).

لو المكتبة/المفاتيح ناقصة، الدوال بترفع PaymobError برسالة واضحة،
والـ routes بتحوّلها لرسالة للمستخدم بدل ما توقع السيرفر.
"""
import hashlib
import hmac

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:  # pragma: no cover
    requests = None
    _REQUESTS_AVAILABLE = False

from config import Config

BASE = "https://accept.paymob.com/api"
IFRAME_URL = BASE + "/acceptance/iframes/{iframe_id}?payment_token={token}"

# ترتيب الحقول المعتمد من Paymob لحساب HMAC بتاع الـ callback
HMAC_FIELDS = (
    "amount_cents", "created_at", "currency", "error_occured",
    "has_parent_transaction", "id", "integration_id", "is_3d_secure",
    "is_auth", "is_capture", "is_refunded", "is_standalone_payment",
    "is_voided", "order", "owner", "pending", "source_data_pan",
    "source_data_sub_type", "source_data_type", "success",
)


class PaymobError(Exception):
    pass


def is_configured():
    """Paymob جاهز فعلياً (المكتبة + كل المفاتيح موجودة)."""
    return bool(
        _REQUESTS_AVAILABLE
        and Config.PAYMOB_API_KEY
        and Config.PAYMOB_INTEGRATION_ID
        and Config.PAYMOB_IFRAME_ID
        and Config.PAYMOB_HMAC_SECRET
    )


def _post(path, payload, auth_token=None):
    """POST واحد لكل نداءات Paymob — timeout قصير وخطأ موحّد."""
    try:
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = auth_token
        resp = requests.post(BASE + path, json=payload, headers=headers, timeout=20)
    except Exception as e:
        raise PaymobError("تعذّر الاتصال ببوابة الدفع، حاول تاني.") from e
    if resp.status_code >= 400:
        raise PaymobError("بوابة الدفع رفضت الطلب (راجع مفاتيح Paymob).")
    try:
        return resp.json()
    except ValueError as e:
        raise PaymobError("رد غير متوقع من بوابة الدفع.") from e


def _billing_data(order, user):
    """Paymob بيطلب بيانات عنوان كاملة — اللي ناقص بنحط له NA (مقبول)."""
    name = (user.get("name") or order.get("name") or "Customer").strip()
    parts = name.split(None, 1)
    first = parts[0][:30]
    last = (parts[1] if len(parts) > 1 else "NA")[:30]
    email = (user.get("email") or "customer@example.com").strip()
    phone = "".join(ch for ch in str(order.get("phone") or "") if ch.isdigit())
    if len(phone) < 8:
        phone = "01000000000"
    return {
        "apartment": "NA", "floor": "NA", "street": "NA", "building": "NA",
        "city": (user.get("city") or user.get("governorate") or "Cairo")[:30],
        "country": "EG",
        "email": email,
        "first_name": first, "last_name": last,
        "phone_number": phone,
        "postal_code": "NA", "shipping_method": "NA",
        "state": (user.get("governorate") or "Cairo")[:30],
    }


def create_payment_link(order, user):
    """يبني عملية دفع كاملة ويرجّع (رابط الـ iFrame, رقم طلب Paymob).

    order: صف الطلب من قاعدة البيانات (لازم سعره النهائي بعد الخصم).
    user: صاحب الطلب (للاسم والإيميل).
    """
    if not is_configured():
        raise PaymobError("الدفع الأونلاين لسه مش مفعّل من صاحب الموقع.")

    try:
        amount_cents = int(round(float(order["service_price"]) * 100))
    except (TypeError, ValueError):
        raise PaymobError("سعر الطلب غير صالح للدفع الأونلاين.")
    if amount_cents <= 0:
        raise PaymobError("سعر الطلب غير صالح للدفع الأونلاين.")

    auth = _post("/auth/tokens", {"api_key": Config.PAYMOB_API_KEY})
    auth_token = auth.get("token")
    if not auth_token:
        raise PaymobError("بوابة الدفع رفضت المفتاح (راجع PAYMOB_API_KEY).")

    service_name = str(order.get("service_name") or "Car service")[:50]
    reg = _post("/ecommerce/orders", {
        "auth_token": auth_token,
        "delivery_needed": "false",
        "amount_cents": amount_cents,
        "currency": "EGP",
        "merchant_order_id": str(order["id"]),
        "items": [{
            "name": service_name,
            "amount_cents": amount_cents,
            "description": service_name,
            "quantity": "1",
        }],
    }, auth_token=auth_token)
    paymob_order_id = reg.get("id")
    if not paymob_order_id:
        raise PaymobError("تعذّر إنشاء طلب الدفع، حاول تاني.")

    key = _post("/acceptance/payment_keys", {
        "auth_token": auth_token,
        "amount_cents": amount_cents,
        "expiration": 3600,
        "order_id": paymob_order_id,
        "billing_data": _billing_data(order, user),
        "currency": "EGP",
        "integration_id": int(Config.PAYMOB_INTEGRATION_ID),
    }, auth_token=auth_token)
    payment_token = key.get("token")
    if not payment_token:
        raise PaymobError("تعذّر بدء الدفع، حاول تاني.")

    url = IFRAME_URL.format(iframe_id=Config.PAYMOB_IFRAME_ID, token=payment_token)
    return url, paymob_order_id


def calc_hmac(params):
    """يحسب توقيع Paymob المتوقع من باراميترات الـ callback."""
    blob = "".join(str(params.get(field, "")) for field in HMAC_FIELDS)
    return hmac.new(
        Config.PAYMOB_HMAC_SECRET.encode("utf-8"),
        blob.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()


def verify_callback(params):
    """يتحقق من الـ callback: توقيع سليم + دفع ناجح فعلاً.

    يرجّع dict فيه (order_id المحلي, paymob_order_id, txn_id, amount_cents)
    أو يرفع PaymobError لو أي حاجة مش سليمة.
    """
    if not Config.PAYMOB_HMAC_SECRET:
        raise PaymobError("الدفع الأونلاين لسه مش مفعّل من صاحب الموقع.")

    received = str(params.get("hmac", ""))
    if not received or not hmac.compare_digest(calc_hmac(params), received):
        raise PaymobError("توقيع الدفع غير سليم — تم رفض العملية.")

    if str(params.get("success", "")).lower() != "true":
        raise PaymobError("عملية الدفع لم تتم بنجاح.")
    for field in ("pending", "is_voided", "is_refunded", "error_occured"):
        if str(params.get(field, "")).lower() == "true":
            raise PaymobError("عملية الدفع غير مكتملة.")

    try:
        amount_cents = int(float(str(params.get("amount_cents", "0"))))
    except (TypeError, ValueError):
        raise PaymobError("بيانات الدفع غير مكتملة.")

    local_id = None
    merchant = str(params.get("merchant_order_id") or "").strip()
    if merchant.isdigit():
        local_id = int(merchant)

    try:
        paymob_order_id = int(str(params.get("order", "0")))
    except (TypeError, ValueError):
        paymob_order_id = 0

    txn_id = str(params.get("id", ""))
    if not txn_id:
        raise PaymobError("بيانات الدفع غير مكتملة.")

    return {
        "local_id": local_id,
        "paymob_order_id": paymob_order_id,
        "txn_id": txn_id,
        "amount_cents": amount_cents,
    }
