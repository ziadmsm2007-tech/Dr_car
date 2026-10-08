"""أدوات المصادقة: decorators للتحقق من تسجيل الدخول والصلاحيات."""
from functools import wraps

from flask import session, redirect, url_for, flash

import models


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return models.get_user_by_id(user_id)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("flash_login_first")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    """يتحقق إن المستخدم مسجّل دخول وعنده واحد من الأدوار المطلوبة."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("flash_login_first")
                return redirect(url_for("login"))
            if session.get("role") not in roles:
                flash("flash_no_perm")
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return wrapped
    return decorator


def owner_required(view):
    """يسمح فقط لمالك التطبيق (OWNER_EMAIL) بالدخول — لوحة خاصة."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("flash_login_first")
            return redirect(url_for("login"))
        # lazy import لتجنب circular import
        from config import Config
        owner_email = (Config.OWNER_EMAIL or "").lower()
        cur = get_current_user()
        cur_email = (cur["email"].lower() if cur else "")
        # الصفحة خاصة بالمالك فقط — يطابق البريد مهما كان الدور
        if cur_email != owner_email:
            flash("flash_not_owner")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped
