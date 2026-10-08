/* ============================================================
   تشغيل القوائم المخصصة — بيتقرأ مرة واحدة لكل .dd في الصفحة
   ============================================================ */
(function(){
    'use strict';

    function closeAll(except){
        document.querySelectorAll('.dd.is-open').forEach(function(dd){
            if(dd === except) return;
            dd.classList.remove('is-open');
            var menu = dd.querySelector('.dd-menu');
            if(menu) menu.hidden = true;
            var btn = dd.querySelector('.dd-trigger');
            if(btn) btn.setAttribute('aria-expanded','false');
        });
    }

    function openDD(dd){
        closeAll(dd);
        dd.classList.add('is-open');
        var menu = dd.querySelector('.dd-menu');
        var btn  = dd.querySelector('.dd-trigger');
        var search = dd.querySelector('.dd-search');
        if(menu) menu.hidden = false;
        if(btn) btn.setAttribute('aria-expanded','true');
        // لو مفيش عناصر، متورّيش خانة البحث
        if(dd.querySelectorAll('.dd-item').length === 0) dd.classList.add('no-items');
        if(search && !dd.classList.contains('no-items')) setTimeout(function(){ search.focus(); }, 30);
        flipIfNeeded(dd);
        keepInView(dd);
    }

    // لو المساحة تحت صغيرة، نفتح القائمة لفوق
    function flipIfNeeded(dd){
        dd.classList.remove('drop-up');
        var menu = dd.querySelector('.dd-menu');
        if(!menu) return;
        var h = menu.offsetHeight;
        var trigger = dd.querySelector('.dd-trigger');
        if(!trigger) return;
        var rect = trigger.getBoundingClientRect();
        var spaceBelow = window.innerHeight - rect.bottom;
        var spaceAbove = rect.top;
        if(spaceBelow < h + 16 && spaceAbove > spaceBelow){
            dd.classList.add('drop-up');
        }
        // لو القائمة أطول من المساحة المتاحة في أي اتجاه، نقصّل ارتفاعها
        var avail = dd.classList.contains('drop-up') ? spaceAbove : spaceBelow;
        if(avail < 160 && avail > 80){
            menu.style.maxHeight = Math.max(140, avail - 20) + 'px';
        }
    }

    // على الموبايل: نخلي القائمة جوه الشاشة حتى لو الصفحة طويلة
    function keepInView(dd){
        if(window.innerWidth > 576) return;
        var menu = dd.querySelector('.dd-menu');
        if(!menu) return;
        var trigger = dd.querySelector('.dd-trigger');
        if(!trigger) return;
        var r = trigger.getBoundingClientRect();
        var mh = menu.offsetHeight;
        var margin = 10;
        // نحسب空间 المتاح فوق وتحت
        var above = r.top - margin;
        var below = window.innerHeight - r.bottom - margin;
        if(below >= mh || below >= above) return;
        // القائمة أطول من أي مكان — نثبتها وتعمل scroll
        menu.style.position = 'fixed';
        menu.style.left = margin + 'px';
        menu.style.right = margin + 'px';
        menu.style.width = 'auto';
        menu.style.maxHeight = Math.max(160, Math.min(mh, window.innerHeight - 2 * margin)) + 'px';
        if(above < below){
            menu.style.top = Math.max(margin, window.innerHeight - r.bottom - mh) + 'px';
            menu.style.bottom = 'auto';
            dd.classList.add('drop-up');
        } else {
            menu.style.top = r.bottom + margin + 'px';
            menu.style.bottom = 'auto';
            dd.classList.remove('drop-up');
        }
    }

    function closeDD(dd){
        dd.classList.remove('is-open');
        var menu = dd.querySelector('.dd-menu');
        var btn  = dd.querySelector('.dd-trigger');
        if(menu){
            menu.hidden = true;
            // نرجّع أي inline styles للوضع العادي
            menu.style.position = '';
            menu.style.left = '';
            menu.style.right = '';
            menu.style.width = '';
            menu.style.top = '';
            menu.style.bottom = '';
            menu.style.maxHeight = '';
        }
        dd.classList.remove('drop-up');
        if(btn) btn.setAttribute('aria-expanded','false');
    }

    // بِنتحكم في كل .dd موجود، ون-export دوال مساعدة عشان order_form
    function setupDD(dd){
        if(dd.dataset.ddReady === '1') return;
        dd.dataset.ddReady = '1';

        var btn   = dd.querySelector('.dd-trigger');
        var menu  = dd.querySelector('.dd-menu');
        var list  = dd.querySelector('.dd-list');
        var search= dd.querySelector('.dd-search');
        var empty = dd.querySelector('.dd-empty');
        var input = dd.querySelector('input[type=hidden]');
        var valueEl= dd.querySelector('.dd-value');
        var placeholder = valueEl ? valueEl.textContent.trim() : '';
        if(valueEl && !valueEl.dataset.ph) valueEl.dataset.ph = placeholder;

        btn.addEventListener('click', function(e){
            e.stopPropagation();
            if(dd.classList.contains('is-open')) closeDD(dd); else openDD(dd);
        });

        menu.addEventListener('click', function(e){ e.stopPropagation(); });

        list.addEventListener('click', function(e){
            var item = e.target.closest('.dd-item');
            if(!item) return;
            list.querySelectorAll('.dd-item').forEach(function(x){
                x.setAttribute('aria-selected','false');
            });
            item.setAttribute('aria-selected','true');
            var v = item.getAttribute('data-value') || '';
            if(input) input.value = v;
            if(valueEl){
                valueEl.textContent = v;
                valueEl.classList.remove('is-placeholder');
            }
            closeDD(dd);
            dd.dispatchEvent(new CustomEvent('dd:change', { detail: { value: v }, bubbles: true }));
        });

        if(search){
            search.addEventListener('input', function(){
                var q = search.value.trim().toLowerCase();
                var shown = 0;
                list.querySelectorAll('.dd-item').forEach(function(it){
                    var txt = (it.getAttribute('data-value') || '').toLowerCase();
                    var hit = !q || txt.indexOf(q) !== -1;
                    it.style.display = hit ? '' : 'none';
                    if(hit) shown++;
                });
                if(empty) empty.hidden = shown !== 0;
            });
            // Enter في خانة البحث = اختار أول نتيجة
            search.addEventListener('keydown', function(e){
                if(e.key !== 'Enter') return;
                e.preventDefault();
                var first = list.querySelector('.dd-item:not([style*="display: none"])');
                if(first) first.click();
            });
            // على الموبايل: لو المستخدم فتح لوحة المفاتيح، خليها فوقها
            search.addEventListener('focus', function(){ setTimeout(function(){ keepInView(dd); }, 260); });
        }

        // لوحة المفاتيح: سهم لفوق/تحت + Enter + Esc
        dd.addEventListener('keydown', function(e){
            if(e.key === 'Escape'){ closeDD(dd); btn.focus(); return; }
            if(!dd.classList.contains('is-open')) return;
            if(e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
            e.preventDefault();
            var items = Array.prototype.filter.call(
                list.querySelectorAll('.dd-item'), function(x){ return x.style.display !== 'none'; }
            );
            if(!items.length) return;
            var cur = items.indexOf(document.activeElement);
            var next = e.key === 'ArrowDown'
                ? (cur + 1) % items.length
                : (cur - 1 + items.length) % items.length;
            items[next].focus();
        });
    }

    function initAll(scope){
        (scope || document).querySelectorAll('.dd').forEach(setupDD);
    }

    document.addEventListener('click', function(){ closeAll(null); });
    document.addEventListener('keydown', function(e){
        if(e.key === 'Escape') closeAll(null);
    });

    // على الموبايل: لو المستخدم سكر-list من برّه، نرجّعها لوضعها الطبيعي
    window.addEventListener('resize', function(){
        document.querySelectorAll('.dd.is-open').forEach(function(dd){
            flipIfNeeded(dd); keepInView(dd);
        });
    });
    // مسح البحث لما يقفل
    document.addEventListener('click', function(e){
        // نقفل أي قائمة مفتوحة غير اللي اتضغط عليها
        document.querySelectorAll('.dd.is-open').forEach(function(dd){
            if(dd.contains(e.target)) return;
            closeDD(dd);
        });
    }, true);

    // API بسيط للاستخدام من صفحات تانية
    window.DD = {
        open: openDD,
        close: closeDD,
        setValue: function(dd, v){
            var input = dd.querySelector('input[type=hidden]');
            var valueEl = dd.querySelector('.dd-value');
            if(input) input.value = v;
            if(valueEl){
                valueEl.textContent = v || valueEl.dataset.ph || '';
                valueEl.classList.toggle('is-placeholder', !v);
            }
            dd.querySelectorAll('.dd-item').forEach(function(it){
                it.setAttribute('aria-selected', it.getAttribute('data-value') === v ? 'true' : 'false');
            });
        },
        setOptions: function(dd, arr, placeholder){
            var list = dd.querySelector('.dd-list');
            list.innerHTML = '';
            (arr || []).forEach(function(o){
                var b = document.createElement('button');
                b.type = 'button';
                b.className = 'dd-item';
                b.setAttribute('data-value', o);
                b.setAttribute('role','option');
                b.setAttribute('aria-selected','false');
                b.innerHTML = '<span class="dd-item-text"></span>' +
                    '<svg class="dd-tick" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">' +
                    '<path d="m5 13 4.5 4.5L19 7"/></svg>';
                b.querySelector('.dd-item-text').textContent = o;
                list.appendChild(b);
            });
            var empty = dd.querySelector('.dd-empty');
            if(empty) empty.hidden = (arr || []).length !== 0;
            if(placeholder !== undefined){
                var valueEl = dd.querySelector('.dd-value');
                if(valueEl){ valueEl.textContent = placeholder; valueEl.dataset.ph = placeholder; }
            }
        },
        get: function(dd){
            var i = dd.querySelector('input[type=hidden]');
            return i ? i.value : '';
        },
        init: initAll
    };

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', function(){ initAll(); });
    } else {
        initAll();
    }
})();

