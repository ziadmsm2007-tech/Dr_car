"""سلة الطلبات (زي طلبات) — بتتخزّن في الجلسة، مفيش أي حاجة في قاعدة البيانات.

السلة عبارة عن dict: {service_id (نص) : الكمية (int)}.
عشان السلة تفضل مع اليوزر حتى لو قفل الصفحة وفتحها تاني في نفس الجلسة،
وبتتفرّغ لوحده لما الطلب يتأكّد.
"""
from flask import session

CART_KEY = "cart"


def _raw():
    """السلة الخام كـ dict {str(service_id): int(qty)}."""
    data = session.get(CART_KEY)
    if not isinstance(data, dict):
        return {}
    clean = {}
    for k, v in data.items():
        try:
            sid = int(k)
            qty = int(v)
        except (TypeError, ValueError):
            continue
        if qty > 0:
            clean[str(sid)] = qty
    return clean


def _save(data):
    session[CART_KEY] = data
    session.modified = True


def add_item(service_id, qty=1):
    """يضيف خدمة للسلة (أو يزوّد كميتها لو موجودة)."""
    try:
        sid = int(service_id)
        qty = int(qty)
    except (TypeError, ValueError):
        return
    if qty < 1:
        qty = 1
    data = _raw()
    key = str(sid)
    data[key] = data.get(key, 0) + qty
    _save(data)


def set_qty(service_id, qty):
    """يحدّد كمية خدمة. الكمية صفر أو أقل = حذف."""
    data = _raw()
    key = str(service_id)
    try:
        qty = int(qty)
    except (TypeError, ValueError):
        qty = 0
    if qty <= 0:
        data.pop(key, None)
    else:
        data[key] = qty
    _save(data)


def remove_item(service_id):
    data = _raw()
    data.pop(str(service_id), None)
    _save(data)


def clear():
    session.pop(CART_KEY, None)
    session.modified = True


def items():
    """قائمة [{service_id:int, qty:int}] بترتيب الإضافة."""
    return [{"service_id": int(k), "qty": int(v)} for k, v in _raw().items()]


def count():
    """إجمالي عدد الأصناف (مجموع الكميات) — للـ badge."""
    return sum(_raw().values())


def is_empty():
    return count() == 0
