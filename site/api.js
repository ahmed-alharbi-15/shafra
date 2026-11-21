// api.js — الملف الوحيد اللي فيه رابط السيرفر
// حطه داخل مجلد site/ واستدعه في أي صفحة تحتاج السيرفر:
// <script src="api.js"></script>

const API = "https://shafra-hcjd.onrender.com";

function getToken() {
  return localStorage.getItem("token");
}

// دالة وحدة لكل الطلبات: ترسل التوكن تلقائي وترجع البيانات
async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json" };
  if (getToken()) headers.Authorization = "Bearer " + getToken();

  const res = await fetch(API + path, { ...options, headers });

  // إذا انتهى الدخول، يرجعه لصفحة تسجيل الدخول
  if (res.status === 401 && !path.startsWith("/api/auth/login")) {
    localStorage.removeItem("token");
    location.href = "/login.html";
    return;
  }

  const data = res.status === 204 ? null : await res.json();
  if (!res.ok) {
    const msg = typeof data?.detail === "string" ? data.detail : "صار خطأ، حاول مرة ثانية";
    throw new Error(msg);
  }
  return data;
}

// تسجيل الدخول
async function login(email, password, remember) {
  const data = await api("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password, remember }),
  });
  localStorage.setItem("token", data.access_token);
  return data.user;
}

// تسجيل الخروج
function logout() {
  localStorage.removeItem("token");
  location.href = "/login.html";
}

// حطها أول الصفحات اللي لازم لها دخول (بوابة الفريق)
function requireLogin() {
  if (!getToken()) location.href = "/login.html";
}
