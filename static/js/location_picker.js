/* =====================================================================
   Dr. Car — اختيار الموقع (زي أوبر / طلبات)
   - بحث بالعنوان مع اقتراحات
   - زر "موقعي الحالي" (GPS)
   - خريطة بدبوس تقدر تسحبه أو تضغط على الخريطة
   - بيملا العنوان + lat/lng + المحافظة والمدينة تلقائي
   بيطلق event اسمه "lp:change" على document كل ما الموقع يتغيّر.
   ===================================================================== */
(function () {
  'use strict';

  var DEFAULT_CENTER = [30.0444, 31.2357]; // القاهرة
  var DEFAULT_ZOOM = 11;

  function $(sel, root) { return (root || document).querySelector(sel); }
  function debounce(fn, ms) {
    var t;
    return function () {
      var a = arguments, c = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(c, a); }, ms);
    };
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function init(root) {
    if (!root || root.__lp) return;
    root.__lp = true;

    var input = $('#lpSearch', root);
    var results = $('#lpResults', root);
    var gpsBtn = $('#lpGps', root);
    var mapEl = $('#lpMap', root);
    var hint = $('#lpHint', root);
    var clearBtn = $('#lpClear', root);
    var latEl = $('#lpLat', root);
    var lngEl = $('#lpLng', root);
    var govHidden = $('#lpGov', root);
    var cityHidden = $('#lpCity', root);
    var govSel = root.dataset.govSelect ? $(root.dataset.govSelect) : null;
    var cityInput = root.dataset.cityInput ? $(root.dataset.cityInput) : null;
    var msg = {
      insecure: root.dataset.msgInsecure || '',
      denied: root.dataset.msgDenied || '',
      loading: root.dataset.msgLoading || '...',
      noResults: root.dataset.msgNoResults || '',
      fail: root.dataset.msgFail || '',
      hint: root.dataset.msgHint || '',
      picked: root.dataset.msgPicked || '',
      noMap: root.dataset.msgNoMap || '',
      gps: gpsBtn ? gpsBtn.innerHTML : ''
    };

    var map = null, marker = null, revToken = 0, searchCtl = null, activeIdx = -1, items = [];
    var cityAuto = !(cityInput && cityInput.value);

    /* ---------- رسائل صغيرة تحت الخريطة ---------- */
    function say(text, kind) {
      if (!hint) return;
      hint.textContent = text || msg.hint;
      hint.className = 'lp-hint' + (kind ? ' lp-' + kind : '');
    }

    /* ---------- ملء الحقول ---------- */
    function fill(info) {
      if (info.label != null && input) input.value = info.label;
      if (info.lat != null && latEl) latEl.value = (+info.lat).toFixed(6);
      if (info.lng != null && lngEl) lngEl.value = (+info.lng).toFixed(6);
      if (info.governorate) {
        if (govHidden) govHidden.value = info.governorate;
        if (govSel) {
          for (var i = 0; i < govSel.options.length; i++) {
            if (govSel.options[i].value === info.governorate) { govSel.selectedIndex = i; break; }
          }
        }
      }
      if (info.city) {
        if (cityHidden) cityHidden.value = info.city;
        if (cityInput && (cityAuto || !cityInput.value)) { cityInput.value = info.city; cityAuto = true; }
      }
      if (clearBtn) clearBtn.hidden = !(input && input.value);
      document.dispatchEvent(new CustomEvent('lp:change', { detail: info }));
    }

    /* ---------- الخريطة ---------- */
    function ensureMarker(lat, lng) {
      if (!map) return;
      if (!marker) {
        var icon = L.divIcon({
          className: 'lp-pin-wrap',
          html: '<div class="lp-pin"><span>📍</span></div>',
          iconSize: [36, 44], iconAnchor: [18, 42]
        });
        marker = L.marker([lat, lng], { draggable: true, icon: icon, autoPan: true }).addTo(map);
        marker.on('dragend', function () {
          var p = marker.getLatLng();
          reverse(p.lat, p.lng);
        });
      } else {
        marker.setLatLng([lat, lng]);
      }
    }

    function moveTo(lat, lng, zoom) {
      if (!map) return;
      ensureMarker(lat, lng);
      map.setView([lat, lng], zoom || Math.max(map.getZoom(), 16), { animate: true });
    }

    /* ---------- تحويل إحداثيات لعنوان ---------- */
    function reverse(lat, lng) {
      var my = ++revToken;
      if (latEl) latEl.value = (+lat).toFixed(6);
      if (lngEl) lngEl.value = (+lng).toFixed(6);
      say(msg.loading);
      fetch('/api/reverse?lat=' + lat + '&lng=' + lng, { headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (my !== revToken) return;
          if (d && d.ok && d.result) {
            fill({ label: d.result.label, lat: lat, lng: lng, governorate: d.result.governorate, city: d.result.city, area: d.result.area });
            say(msg.picked ? msg.picked : '', 'ok');
          } else { throw new Error('nf'); }
        })
        .catch(function () {
          if (my !== revToken) return;
          // السيرفر مش لاقي عنوان — نسيب الإحداثيات ونخلي المستخدم يكتب العنوان
          fill({ lat: lat, lng: lng });
          if (input && !input.value) input.value = (+lat).toFixed(5) + ', ' + (+lng).toFixed(5);
          say(msg.fail, 'warn');
        });
    }

    function setPoint(lat, lng, opts) {
      opts = opts || {};
      moveTo(lat, lng, opts.zoom);
      if (opts.label) {
        fill({ label: opts.label, lat: lat, lng: lng, governorate: opts.governorate, city: opts.city, area: opts.area });
        say(msg.picked ? msg.picked : '', 'ok');
      } else {
        reverse(lat, lng);
      }
    }

    function buildMap() {
      if (typeof L === 'undefined' || !mapEl) {
        if (mapEl) { mapEl.classList.add('lp-map-off'); mapEl.textContent = msg.noMap; }
        return;
      }
      var lat0 = parseFloat(latEl && latEl.value), lng0 = parseFloat(lngEl && lngEl.value);
      var has = isFinite(lat0) && isFinite(lng0);
      map = L.map(mapEl, { zoomControl: true, scrollWheelZoom: false, attributionControl: true })
        .setView(has ? [lat0, lng0] : DEFAULT_CENTER, has ? 16 : DEFAULT_ZOOM);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19, attribution: '&copy; OpenStreetMap'
      }).addTo(map);
      if (has) ensureMarker(lat0, lng0);
      root.lpMap = map; // متاح للصفحات/الاختبارات
      map.on('click', function (e) { setPoint(e.latlng.lat, e.latlng.lng, { zoom: map.getZoom() }); });
      // تفعيل الـ scroll zoom بعد أول ضغطة (عشان مانعطّلش سكرول الصفحة)
      map.once('focus', function () { map.scrollWheelZoom.enable(); });
      map.on('click', function () { map.scrollWheelZoom.enable(); });
      setTimeout(function () { map.invalidateSize(); }, 250);
      window.addEventListener('resize', debounce(function () { map.invalidateSize(); }, 200));
    }

    /* ---------- زر موقعي الحالي ---------- */
    function useGps() {
      if (!navigator.geolocation || !window.isSecureContext) {
        say(msg.insecure, 'warn');
        return;
      }
      gpsBtn.disabled = true;
      gpsBtn.textContent = '⏳ ' + msg.loading;
      navigator.geolocation.getCurrentPosition(function (pos) {
        gpsBtn.disabled = false; gpsBtn.innerHTML = msg.gps;
        setPoint(pos.coords.latitude, pos.coords.longitude, { zoom: 17 });
      }, function (err) {
        gpsBtn.disabled = false; gpsBtn.innerHTML = msg.gps;
        say(msg.denied, 'warn');
      }, { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 });
    }
    if (gpsBtn) gpsBtn.addEventListener('click', useGps);

    /* ---------- البحث والاقتراحات ---------- */
    function hideResults() { results.hidden = true; results.innerHTML = ''; activeIdx = -1; items = []; }

    function render(list, note) {
      items = list || [];
      activeIdx = -1;
      if (!items.length) {
        results.innerHTML = '<li class="lp-empty">' + esc(note || msg.noResults) + '</li>';
        results.hidden = false;
        return;
      }
      results.innerHTML = items.map(function (it, i) {
        var parts = String(it.label).split('،');
        var first = parts.shift();
        return '<li role="option" data-i="' + i + '"><span class="lp-r-ico">📍</span><span><b>' + esc(first) + '</b>' +
          (parts.length ? '<small>' + esc(parts.join('،').trim()) + '</small>' : '') + '</span></li>';
      }).join('');
      results.hidden = false;
    }

    function choose(i) {
      var it = items[i];
      if (!it) return;
      hideResults();
      setPoint(it.lat, it.lng, { zoom: 17, label: it.label, governorate: it.governorate, city: it.city, area: it.area });
    }

    var search = debounce(function () {
      var q = (input.value || '').trim();
      if (q.length < 3) { hideResults(); return; }
      if (searchCtl) searchCtl.abort();
      searchCtl = ('AbortController' in window) ? new AbortController() : null;
      render([], msg.loading);
      fetch('/api/geocode?q=' + encodeURIComponent(q), searchCtl ? { signal: searchCtl.signal } : {})
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && d.ok) render(d.results || []);
          else render([], msg.fail);
        })
        .catch(function (e) { if (e && e.name === 'AbortError') return; render([], msg.fail); });
    }, 450);

    if (input) {
      input.addEventListener('input', function () {
        if (clearBtn) clearBtn.hidden = !input.value;
        search();
      });
      input.addEventListener('keydown', function (e) {
        var lis = results.querySelectorAll('li[data-i]');
        if (e.key === 'ArrowDown' && lis.length) {
          e.preventDefault(); activeIdx = (activeIdx + 1) % lis.length;
        } else if (e.key === 'ArrowUp' && lis.length) {
          e.preventDefault(); activeIdx = (activeIdx - 1 + lis.length) % lis.length;
        } else if (e.key === 'Enter') {
          if (!results.hidden && lis.length) { e.preventDefault(); choose(activeIdx >= 0 ? activeIdx : 0); }
          return;
        } else if (e.key === 'Escape') { hideResults(); return; }
        else { return; }
        lis.forEach(function (li, i) { li.classList.toggle('active', i === activeIdx); });
      });
    }
    results.addEventListener('mousedown', function (e) {
      var li = e.target.closest('li[data-i]');
      if (li) { e.preventDefault(); choose(+li.dataset.i); }
    });
    document.addEventListener('click', function (e) { if (!root.contains(e.target)) hideResults(); });

    if (clearBtn) clearBtn.addEventListener('click', function () {
      input.value = ''; clearBtn.hidden = true; hideResults(); input.focus();
    });
    if (cityInput) cityInput.addEventListener('input', function () { cityAuto = false; });

    if (clearBtn) clearBtn.hidden = !(input && input.value);
    say(msg.hint);
    buildMap();
  }

  window.LocationPicker = { init: init };
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.lp').forEach(init);
  });
})();
