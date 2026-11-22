/* شفرة — قائمة الموقع العام حسب الحساب:
   موظف/أدمن/Owner → «بوابة الفريق»، عميل → «حسابي»، غير داخل → «تسجيل الدخول». */
(function () {
  if (typeof Auth === 'undefined') return;
  const me = Auth.current();
  if (!me) return;
  const staff = Auth.isStaff(me);
  document.querySelectorAll('header a[href$="login.html"]').forEach(function (a) {
    a.setAttribute('href', a.getAttribute('href').replace('login.html', staff ? 'team.html' : 'account.html'));
    a.textContent = staff ? 'بوابة الفريق' : 'حسابي';
  });
})();
