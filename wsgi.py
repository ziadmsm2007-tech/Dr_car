"""نقطة دخول السيرفر الإنتاجي (Gunicorn / Render / Railway / أي استضافة).

تشغيل محلي:
    python wsgi.py

تشغيل على سيرفر (الاستضافة بتشغّل الأمر ده لوحدها من Procfile):
    gunicorn wsgi:app
"""
from app import app  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
