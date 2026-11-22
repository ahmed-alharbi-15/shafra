/* شفرة — يغيّر «تسجيل الدخول» في القائمة إلى «بوابة الفريق» إذا المستخدم داخل.
   TODO(backend): لما يجهز الدخول الحقيقي يكفي وجود "token" (api.js). علامة shafra_demo_login مؤقتة للدخول الشكلي. */
(function () {
  var on = false;
  try { on = !!(localStorage.getItem('token') || localStorage.getItem('shafra_demo_login')); } catch (e) {}
  if (!on) return;
  document.querySelectorAll('header a[href$="login.html"]').forEach(function (a) {
    a.setAttribute('href', a.getAttribute('href').replace('login.html', 'team.html'));
    a.textContent = 'بوابة الفريق';
  });
})();
