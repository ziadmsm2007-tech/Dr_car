"""خدمة اللوكيشن: بحث عناوين + تحويل إحداثيات لعنوان (زي أوبر/طلبات).

بنستخدم OpenStreetMap Nominatim (مجاني، من غير مفتاح). الطلبات بتعدّي من
السيرفر بتاعنا (مش من المتصفح) عشان:
  1) نبعت User-Agent صح (شرط عند Nominatim) ونلتزم بحد 1 طلب/ثانية.
  2) نرجّع للمتصفح بيانات جاهزة: عنوان مختصر + المحافظة + المدينة.
  3) نعمل كاش للنتايج المتكررة فتبقى أسرع.
"""
import threading
import time

try:
    import requests
except ImportError:  # الموقع يفضل شغال حتى لو المكتبة مش مثبتة
    requests = None

NOMINATIM = "https://nominatim.openstreetmap.org"
USER_AGENT = "DrCar/1.0 (car-service app; contact: support@autocare.app)"

EG_GOVERNORATES = [
    "القاهرة", "الجيزة", "الإسكندرية", "الدقهلية", "البحر الأحمر", "البحيرة", "الفيوم", "الغربية",
    "الإسماعيلية", "المنوفية", "المنيا", "القليوبية", "الوادي الجديد", "السويس", "أسوان", "أسيوط",
    "بني سويف", "بورسعيد", "دمياط", "الشرقية", "جنوب سيناء", "كفر الشيخ", "مطروح", "الأقصر", "قنا",
    "شمال سيناء", "سوهاج",
]

_EN_TO_AR = {
    "cairo": "القاهرة", "giza": "الجيزة", "alexandria": "الإسكندرية", "dakahlia": "الدقهلية",
    "red sea": "البحر الأحمر", "beheira": "البحيرة", "faiyum": "الفيوم", "fayoum": "الفيوم",
    "gharbia": "الغربية", "ismailia": "الإسماعيلية", "monufia": "المنوفية", "minya": "المنيا",
    "qalyubia": "القليوبية", "qalyubiyya": "القليوبية", "new valley": "الوادي الجديد", "suez": "السويس",
    "aswan": "أسوان", "asyut": "أسيوط", "assiut": "أسيوط", "beni suef": "بني سويف",
    "port said": "بورسعيد", "damietta": "دمياط", "sharqia": "الشرقية", "south sinai": "جنوب سيناء",
    "kafr el sheikh": "كفر الشيخ", "kafr el-sheikh": "كفر الشيخ", "matrouh": "مطروح", "matruh": "مطروح",
    "luxor": "الأقصر", "qena": "قنا", "north sinai": "شمال سيناء", "sohag": "سوهاج",
}

_lock = threading.Lock()
_last_call = [0.0]
_cache = {}
_CACHE_MAX = 500
_CACHE_TTL = 6 * 3600


def match_governorate(*texts):
    """يرجّع اسم المحافظة بالعربي (من القائمة المعتمدة) أو '' لو مش لاقيها."""
    blob = " ".join(t for t in texts if t)
    if not blob:
        return ""
    for g in EG_GOVERNORATES:
        if g in blob:
            return g
    low = blob.lower()
    # الأطول أولاً عشان "north sinai" يتغلب على "sinai"
    for en in sorted(_EN_TO_AR, key=len, reverse=True):
        if en in low:
            return _EN_TO_AR[en]
    return ""


def _get(path, params):
    if requests is None:
        raise RuntimeError("requests not installed")
    key = (path, tuple(sorted(params.items())))
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit[0] < _CACHE_TTL:
        return hit[1]
    with _lock:
        # احترام حد Nominatim: طلب واحد كل ثانية
        wait = 1.05 - (time.time() - _last_call[0])
        if wait > 0:
            time.sleep(wait)
        resp = requests.get(
            NOMINATIM + path,
            params=params,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "ar,en;q=0.6"},
            timeout=8,
        )
        _last_call[0] = time.time()
    resp.raise_for_status()
    data = resp.json()
    if len(_cache) >= _CACHE_MAX:
        _cache.clear()
    _cache[key] = (now, data)
    return data


def _short_label(item):
    """عنوان مختصر ومفهوم: شارع، حي، مدينة، محافظة — من غير الرمز البريدي والدولة."""
    a = item.get("address") or {}
    street = a.get("road") or a.get("pedestrian") or a.get("residential") or ""
    if a.get("house_number") and street:
        street = f"{a['house_number']} {street}"
    poi = item.get("name") or ""
    area = a.get("neighbourhood") or a.get("suburb") or a.get("quarter") or a.get("city_district") or ""
    city = a.get("city") or a.get("town") or a.get("village") or a.get("municipality") or ""
    state = (a.get("state") or "").replace("محافظة ", "").replace(" Governorate", "")
    parts = []
    for p in (poi if poi and poi != street else "", street, area, city, state):
        if p and p not in parts:
            parts.append(p)
    if parts:
        return "، ".join(parts)
    # fallback: display_name بس من غير آخر جزئين (الرمز البريدي + الدولة)
    dn = (item.get("display_name") or "").split("،")
    return "،".join(dn[:4]).strip() or (item.get("display_name") or "")


def _normalize(item):
    a = item.get("address") or {}
    state = a.get("state") or a.get("governorate") or a.get("region") or ""
    gov = match_governorate(state, a.get("county") or "", a.get("city") or "", item.get("display_name") or "")
    city = (a.get("city") or a.get("town") or a.get("village") or a.get("municipality")
            or a.get("suburb") or a.get("county") or "")
    area = a.get("neighbourhood") or a.get("suburb") or a.get("quarter") or a.get("city_district") or ""
    try:
        lat = float(item.get("lat"))
        lng = float(item.get("lon"))
    except (TypeError, ValueError):
        return None
    return {
        "label": _short_label(item),
        "full": item.get("display_name") or "",
        "lat": lat,
        "lng": lng,
        "governorate": gov,
        "city": city,
        "area": area,
    }


def search(q, limit=6):
    data = _get("/search", {
        "format": "jsonv2", "addressdetails": 1, "limit": limit,
        "countrycodes": "eg", "accept-language": "ar", "q": q,
    })
    out = []
    for it in data or []:
        n = _normalize(it)
        if n:
            out.append(n)
    return out


def reverse(lat, lng):
    data = _get("/reverse", {
        "format": "jsonv2", "addressdetails": 1, "zoom": 18,
        "accept-language": "ar", "lat": f"{lat:.6f}", "lon": f"{lng:.6f}",
    })
    if not data or data.get("error"):
        return None
    n = _normalize(data)
    if n:
        # الإحداثيات الأصلية للدبوس أدق من اللي بيرجّعه الـ geocoder
        n["lat"], n["lng"] = float(lat), float(lng)
    return n
