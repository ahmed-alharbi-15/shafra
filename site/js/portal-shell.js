/* شفرة — يضبط شريط البوابة حسب الشخص الداخل: اسمه، رتبته، وإخفاء اللي ما له صلاحية فيه، وزر الخروج. */
(function () {
  const me = Auth.current();
  if (!me) return;

  const prof = document.querySelector('a[aria-label="ملفي الشخصي"]');
  if (prof) {
    prof.href = 'profile.html?id=' + me.id;
    const first = prof.querySelector('span');
    if (first) first.textContent = (me.name || '؟').trim().charAt(0);
    const inner = prof.querySelectorAll('span > span');
    if (inner[0]) inner[0].textContent = me.name;
    if (inner[1]) inner[1].textContent = Auth.roleLabel(me.role) + ' · ملفي الشخصي';
  }
  document.querySelectorAll('a[href^="profile.html?id="]').forEach(function (a) {
    if (a !== prof && /id=ahmed$/.test(a.getAttribute('href')) && a.closest('.portal-bottomnav')) a.href = 'profile.html?id=' + me.id;
  });

  if (!Auth.can('viewAccounts', me)) {
    document.querySelectorAll('a[href="accounts.html"]').forEach(function (a) { a.style.display = 'none'; });
  }

  const side = document.querySelector('[data-portal-sidebar]');
  if (side) {
    const row = document.createElement('div');
    row.style.cssText = 'display:flex;gap:8px';
    const link = 'flex:1;display:inline-flex;align-items:center;justify-content:center;min-height:42px;border-radius:10px;border:1px solid #333943;background:transparent;color:#D7DBE1;font-family:inherit;font-size:14px;text-decoration:none;cursor:pointer';
    row.innerHTML = '<a href="account.html" style="' + link + '">حسابي</a><button type="button" id="logout-btn" style="' + link + '">تسجيل الخروج</button>';
    side.appendChild(row);
  }
  const top = document.querySelector('.portal-topbar-mobile');
  if (top) {
    const b = document.createElement('button');
    b.type = 'button'; b.id = 'logout-btn-m';
    b.textContent = 'خروج';
    b.style.cssText = 'font-size:13px;color:#D7DBE1;padding:4px 12px;border-radius:99px;border:1px solid #333943;background:transparent;font-family:inherit;cursor:pointer';
    top.appendChild(b);
  }
  document.addEventListener('click', function (e) {
    if (e.target.closest('#logout-btn, #logout-btn-m')) Auth.logout('login.html');
  });
})();
