/* DrCar service worker — يسرّع التحميل المتكرر بتخزين الملفات الثابتة فقط.
   صفحات الحسابات والطلبات والـ OTP دايماً من الشبكة (مفيش كاش لها) عشان
   الجلسات والأكواد تفضل صح. */
const CACHE = "drcar-static-v1";
const PRECACHE = [
  "/static/css/style.css",
  "/static/js/dropdown.js",
  "/static/images/logo.svg",
  "/static/images/icon-192.png",
  "/static/images/icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== self.location.origin) return;
  // الملفات الثابتة فقط: كاش أولاً ثم الشبكة
  if (url.pathname.startsWith("/static/")) {
    e.respondWith(
      caches.match(e.request).then((hit) => {
        const net = fetch(e.request).then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(e.request, copy));
          }
          return res;
        }).catch(() => hit);
        return hit || net;
      })
    );
  }
});
