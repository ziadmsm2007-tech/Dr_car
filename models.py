"""طبقة الوصول للبيانات: كل دوال قراءة/كتابة المستخدمين والطلبات."""
import secrets

from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db


# ---------- المستخدمون ----------
def get_user_by_email(email):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def verify_user(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def create_user(name, email, password, role, governorate=None, city=None, address=None, lat=None, lng=None, photo=None, phone=None):
    with get_db() as conn:
        try:
            is_approved = 0 if role == "technician" else 1
            conn.execute(
                "INSERT INTO users (name, email, password_hash, role, phone, governorate, city, address, lat, lng, photo, is_approved) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (name, email, generate_password_hash(password), role, phone, governorate, city, address, lat, lng, photo, is_approved),
            )
            return True
        except Exception as e:
            print("create_user error", e)
            return False


def update_user_profile(user_id, name, phone, governorate, city, address, lat, lng):
    """يحدّث بيانات البروفايل (الاسم/التليفون/العنوان/الموقع). الإيميل والدور مش بيتغيروا."""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET name = ?, phone = ?, governorate = ?, city = ?, address = ?, lat = ?, lng = ? WHERE id = ?",
            (name, phone, governorate, city, address, lat, lng, user_id),
        )


def update_user_password(email, new_password):
    with get_db() as conn:
        # has_password=1 عشان لو الحساب كان اتعمل بجوجل/فيسبوك، دلوقتي بقى
        # ليه باسورد حقيقي كمان ويقدر يدخل بيه عادي زي أي حساب تاني
        conn.execute(
            "UPDATE users SET password_hash = ?, has_password = 1 WHERE email = ?",
            (generate_password_hash(new_password), email),
        )


# ---------- تسجيل الدخول بجوجل / فيسبوك (OAuth) ----------
def get_user_by_oauth(provider, oauth_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE oauth_provider = ? AND oauth_id = ?",
            (provider, str(oauth_id)),
        ).fetchone()
        return dict(row) if row else None


def create_oauth_user(name, email, provider, oauth_id, avatar_url=None, role="client",
                       governorate=None, city=None, address=None):
    """يعمل حساب جديد بمعلومات جوجل/فيسبوك. الحساب بياخد باسورد عشوائي غير
    قابل للاستخدام لحد ما اليوزر يعمل "نسيت كلمة المرور" ويحط واحد بنفسه."""
    with get_db() as conn:
        try:
            random_password_hash = generate_password_hash(secrets.token_hex(32))
            is_approved = 0 if role == "technician" else 1
            conn.execute(
                """INSERT INTO users
                   (name, email, password_hash, role, governorate, city, address,
                    photo, is_approved, oauth_provider, oauth_id, avatar_url, has_password)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                (name, email, random_password_hash, role, governorate, city, address,
                 None, is_approved, provider, str(oauth_id), avatar_url),
            )
            return True
        except Exception as e:
            print("create_oauth_user error", e)
            return False


def link_oauth_to_user(user_id, provider, oauth_id, avatar_url=None):
    """يربط حساب جوجل/فيسبوك بحساب موجود مسبقاً بنفس الإيميل، بدل ما يعمل
    حساب مكرر — نفس اللي بتعمله البرامج الاحترافية."""
    with get_db() as conn:
        if avatar_url:
            conn.execute(
                "UPDATE users SET oauth_provider = ?, oauth_id = ?, avatar_url = ? WHERE id = ?",
                (provider, str(oauth_id), avatar_url, user_id),
            )
        else:
            conn.execute(
                "UPDATE users SET oauth_provider = ?, oauth_id = ? WHERE id = ?",
                (provider, str(oauth_id), user_id),
            )


def count_users_by_role(role):
    with get_db() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM users WHERE role = ?", (role,)
        ).fetchone()[0]


def get_all_users():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def count_orders_by_customer(customer_id):
    with get_db() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM orders WHERE customer_id = ?", (customer_id,)
        ).fetchone()[0]


def count_orders_by_technician(technician_id):
    with get_db() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM orders WHERE technician_id = ?", (technician_id,)
        ).fetchone()[0]


def get_all_orders(limit=None):
    query = "SELECT * FROM orders ORDER BY created_at DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
    with get_db() as conn:
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]


# ---------- الطلبات ----------
def create_order(service_id, customer_id, name, phone, location, payment_method,
                  service_name, service_price, lat=None, lng=None, scheduled_at=None, car_make=None, car_model=None, car_year=None):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO orders
               (service_id, customer_id, name, phone, location, lat, lng, car_make, car_model, car_year, payment_method,
                service_name, service_price, status, payment_status, scheduled_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 'Unpaid', ?)""",
            (service_id, customer_id, name, phone, location, lat, lng, car_make, car_model, car_year, payment_method,
             service_name, service_price, scheduled_at),
        )


def mark_order_paid(order_id, payment_method):
    from config import Config
    with get_db() as conn:
        row = conn.execute("SELECT technician_id, service_price FROM orders WHERE id=?", (order_id,)).fetchone()
        if not row:
            return
        tech_id, price = row[0], row[1] or 0
        conn.execute(
            "UPDATE orders SET payment_status = 'Paid', payment_method = ?, status = 'Completed', payout_status = 'Pending' WHERE id = ?",
            (payment_method, order_id),
        )
        # خصم مباشر زي أوبر — 20% للمنصة
        if tech_id:
            commission = price * Config.COMMISSION_RATE
            net = price - commission
            conn.execute("INSERT OR IGNORE INTO wallets (user_id, balance) VALUES (?, 0)", (tech_id,))
            if payment_method == "Cash":
                # كاش: الفني خد الفلوس كاش → مديون للمنصة بالعمولة
                conn.execute("UPDATE wallets SET balance = balance - ? WHERE user_id=?", (commission, tech_id))
            else:
                # أونلاين: الفلوس عند المنصة → الفني ليه 80%
                conn.execute("UPDATE wallets SET balance = balance + ? WHERE user_id=?", (net, tech_id))


def mark_payout_done(order_id):
    with get_db() as conn:
        conn.execute("UPDATE orders SET payout_status = 'Paid' WHERE id = ?", (order_id,))


def get_pending_payouts(technician_id=None):
    with get_db() as conn:
        if technician_id:
            rows = conn.execute(
                "SELECT * FROM orders WHERE payment_status='Paid' AND payout_status='Pending' AND technician_id=?",
                (technician_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM orders WHERE payment_status='Paid' AND payout_status='Pending' ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def get_technician_earnings(technician_id, commission_rate=0.20):
    with get_db() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(service_price),0), COUNT(*) FROM orders WHERE technician_id=? AND payment_status='Paid'",
            (technician_id,),
        ).fetchone()
        total = row[0] or 0
        count = row[1] or 0
        commission = total * commission_rate
        net = total * (1 - commission_rate)
        # pending payout (owner hasn't sent yet)
        row2 = conn.execute(
            "SELECT COALESCE(SUM(service_price),0) FROM orders WHERE technician_id=? AND payment_status='Paid' AND payout_status='Pending'",
            (technician_id,),
        ).fetchone()
        pending = (row2[0] or 0) * (1 - commission_rate)
        return {"total": total, "count": count, "commission": commission, "net": net, "pending_payout": pending}


def get_wallet(user_id):
    with get_db() as conn:
        row = conn.execute("SELECT balance FROM wallets WHERE user_id=?", (user_id,)).fetchone()
        if row:
            return row[0]
        # إنشاء محفظة صفرية لو مش موجودة
        conn.execute("INSERT OR IGNORE INTO wallets (user_id, balance) VALUES (?, 0)", (user_id,))
        return 0


def update_wallet(user_id, delta):
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO wallets (user_id, balance) VALUES (?, 0)", (user_id,))
        conn.execute("UPDATE wallets SET balance = balance + ? WHERE user_id=?", (delta, user_id))


def get_all_wallets():
    with get_db() as conn:
        rows = conn.execute("SELECT user_id, balance FROM wallets").fetchall()
        return {r[0]: r[1] for r in rows}


def get_pending_technicians():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM users WHERE role='technician' AND is_approved=0").fetchall()
        return [dict(r) for r in rows]


def approve_technician(user_id):
    with get_db() as conn:
        conn.execute("UPDATE users SET is_approved=1 WHERE id=?", (user_id,))


def get_coupon(code):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM coupons WHERE code=?", (code,)).fetchone()
        return dict(row) if row else None


def validate_coupon(code, governorate=None):
    c = get_coupon(code)
    if not c:
        return None, "كود غير صحيح"
    if c["used_count"] >= c["max_uses"]:
        return None, "الكوبون انتهى"
    if c["governorate"] and governorate and c["governorate"] not in governorate:
        return None, f"الكوبون لمنطقة {c['governorate']} فقط"
    return c, None


def use_coupon(code):
    with get_db() as conn:
        conn.execute("UPDATE coupons SET used_count = used_count + 1 WHERE code=?", (code,))


def add_points(user_id, pts):
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO wallets (user_id, balance) VALUES (?, 0)", (user_id,))
        conn.execute("UPDATE users SET points = COALESCE(points,0) + ? WHERE id=?", (pts, user_id))


def update_user_photo(user_id, photo_path):
    with get_db() as conn:
        conn.execute("UPDATE users SET photo=? WHERE id=?", (photo_path, user_id))


def add_rating(order_id, rating, review=""):
    with get_db() as conn:
        conn.execute("UPDATE orders SET rating=?, review=? WHERE id=?", (rating, review, order_id))
        # تحديث متوسط تقييم الفني
        row = conn.execute("SELECT technician_id FROM orders WHERE id=?", (order_id,)).fetchone()
        if row and row[0]:
            tech_id = row[0]
            avg = conn.execute("SELECT AVG(rating), COUNT(*) FROM orders WHERE technician_id=? AND rating IS NOT NULL", (tech_id,)).fetchone()
            conn.execute("UPDATE users SET rating_avg=?, rating_count=? WHERE id=?", (avg[0] or 0, avg[1] or 0, tech_id))


def get_messages(order_id):
    with get_db() as conn:
        rows = conn.execute("SELECT m.*, u.name as sender_name FROM messages m JOIN users u ON u.id=m.sender_id WHERE order_id=? ORDER BY created_at ASC", (order_id,)).fetchall()
        return [dict(r) for r in rows]


def add_message(order_id, sender_id, message):
    with get_db() as conn:
        conn.execute("INSERT INTO messages (order_id, sender_id, message) VALUES (?, ?, ?)", (order_id, sender_id, message))


def add_notification(user_id, title, body=""):
    with get_db() as conn:
        conn.execute("INSERT INTO notifications (user_id, title, body) VALUES (?, ?, ?)", (user_id, title, body))


def get_notifications(user_id, limit=10):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT ?", (user_id, limit)).fetchall()
        return [dict(r) for r in rows]


def get_unread_count(user_id):
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) FROM notifications WHERE user_id=? AND is_read=0", (user_id,)).fetchone()
        return row[0] or 0


def mark_notifications_read(user_id):
    with get_db() as conn:
        conn.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (user_id,))


def get_order_by_id(order_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        return dict(row) if row else None


def get_orders_by_customer(customer_id, limit=None):
    query = "SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
    with get_db() as conn:
        rows = conn.execute(query, (customer_id,)).fetchall()
        return [dict(r) for r in rows]


def get_orders_by_technician(technician_id):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE technician_id = ? ORDER BY created_at DESC",
            (technician_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_orders_by_status(status):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC", (status,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_recent_orders(limit=10):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def count_orders(status=None):
    with get_db() as conn:
        if status:
            return conn.execute(
                "SELECT COUNT(*) FROM orders WHERE status = ?", (status,)
            ).fetchone()[0]
        return conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]


def get_total_revenue():
    with get_db() as conn:
        row = conn.execute("SELECT COALESCE(SUM(service_price),0) FROM orders WHERE payment_status='Paid'").fetchone()
        return row[0] or 0


def get_pending_revenue():
    with get_db() as conn:
        row = conn.execute("SELECT COALESCE(SUM(service_price),0) FROM orders WHERE payment_status='Unpaid' AND status IN ('Awaiting Payment','In Progress','Pending')").fetchone()
        return row[0] or 0


def get_revenue_by_status():
    with get_db() as conn:
        rows = conn.execute("SELECT status, COUNT(*), COALESCE(SUM(service_price),0) FROM orders GROUP BY status").fetchall()
        return [dict(zip(["status","count","total"], r)) for r in rows]


def update_order_status(order_id, status, technician_id=None):
    with get_db() as conn:
        if technician_id is not None:
            conn.execute(
                "UPDATE orders SET status = ?, technician_id = ? WHERE id = ?",
                (status, technician_id, order_id),
            )
        else:
            conn.execute(
                "UPDATE orders SET status = ? WHERE id = ?", (status, order_id)
            )


def delete_order(order_id):
    with get_db() as conn:
        conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
