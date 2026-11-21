/* شفرة — شاشة التحميل: تظهر مرة وحدة لكل جلسة (sessionStorage)، وتختفي بسلاسة. */
(function () {
  var el = document.getElementById('site-loading');
  if (!el) return;

  if (sessionStorage.getItem('shafra_loaded')) {
    el.remove();
    return;
  }

  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}

  var pctEl = el.querySelector('.pct');
  var msgEl = el.querySelector('.msg');
  var DURATION = reduce ? 1 : 3200;

  function messageFor(p) {
    if (p < 30) return 'نجهّز الكود';
    if (p < 60) return 'نصب القهوة';
    if (p < 90) return 'نشغّل اللوحة';
    if (p < 100) return 'آخر لمسات';
    return 'جاهز!';
  }

  function finish() {
    sessionStorage.setItem('shafra_loaded', '1');
    el.classList.add('hide');
    setTimeout(function () { el.remove(); }, 550);
  }

  if (reduce) {
    if (pctEl) pctEl.textContent = '100';
    if (msgEl) msgEl.textContent = 'جاهز!';
    finish();
    return;
  }

  var start = null;
  function tick(ts) {
    if (start === null) start = ts;
    var k = Math.min(1, (ts - start) / DURATION);
    var eased = 1 - Math.pow(1 - k, 2.2);
    var p = Math.round(eased * 100);
    if (pctEl) pctEl.textContent = String(p);
    if (msgEl) msgEl.textContent = messageFor(p);
    if (k < 1) requestAnimationFrame(tick);
    else finish();
  }
  requestAnimationFrame(tick);
})();
