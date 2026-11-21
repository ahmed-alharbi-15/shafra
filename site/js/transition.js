/* شفرة — انتقال الصفحات: شريط تقدم أعلى الشاشة عند الضغط على أي رابط داخلي،
   يكمل نفسه عند وصول الصفحة الجديدة. بدون مكتبات، يتوقف مع prefers-reduced-motion. */
(function () {
  var bar = document.getElementById('site-transition-bar');
  var dim = document.getElementById('site-transition-dim');
  var label = document.getElementById('site-transition-label');
  if (!bar || !dim) return;

  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}

  function setActive(on) {
    bar.classList.toggle('site-transition-active', on);
    dim.classList.toggle('site-transition-active', on);
    if (label) label.classList.toggle('site-transition-active', on);
  }

  // أكمل الشريط إذا كانت الصفحة السابقة بدأت انتقالاً قبل وصولنا هنا.
  if (sessionStorage.getItem('shafra_transitioning')) {
    sessionStorage.removeItem('shafra_transitioning');
    if (!reduce) {
      setActive(true);
      bar.style.transform = 'scaleX(1)';
      setTimeout(function () {
        setActive(false);
        setTimeout(function () { bar.style.transform = 'scaleX(0)'; }, 300);
      }, 150);
    }
  }

  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest('a[href]');
    if (!a) return;
    if (a.target && a.target !== '_self') return;
    if (a.hasAttribute('download')) return;
    var href = a.getAttribute('href') || '';
    if (!href || href.indexOf('#') === 0 || /^(mailto:|tel:|javascript:)/i.test(href)) return;

    var url;
    try { url = new URL(href, location.href); } catch (e2) { return; }
    if (url.origin !== location.origin) return;
    if (url.pathname === location.pathname && url.search === location.search) return;

    if (reduce) return;

    e.preventDefault();
    sessionStorage.setItem('shafra_transitioning', '1');
    bar.style.transform = 'scaleX(0)';
    setActive(true);
    requestAnimationFrame(function () { bar.style.transform = 'scaleX(.85)'; });
    setTimeout(function () { location.href = url.href; }, 320);
  });
})();
