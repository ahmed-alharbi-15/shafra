"""ينشئ حسابات Owner (من owners.json) أو يغيّر كلمة مرورها في قاعدة البيانات.

التشغيل (من مجلد shafra-backend):
    DATABASE_URL="<رابط قاعدة البيانات>" python3 -m app.set_owner_password

يسألك كلمة المرور لكل Owner (مخفية، وما تنحفظ في أي ملف). اتركها فاضية لتخطي الحساب.
"""
import getpass

from sqlalchemy import select

from .config import get_settings
from .database import SessionLocal
from .main import migrate_schema
from .models import User
from .security import hash_password


def main() -> None:
    owners = get_settings().owner_profiles
    if not owners:
        print("ما لقيت owners.json")
        return
    migrate_schema()
    with SessionLocal() as db:
        for email, o in owners.items():
            user = db.scalar(select(User).where(User.email == email))
            state = "موجود" if user else "جديد"
            pw = getpass.getpass(f"كلمة مرور {o.get('name', email)} <{email}> ({state}) — فاضي للتخطي: ")
            if not pw:
                continue
            if len(pw) < 8:
                print("  أقل من 8 خانات، تخطيته.")
                continue
            if user:
                user.hashed_password = hash_password(pw)
                user.role = "owner"
            else:
                db.add(User(name=o.get("name") or email.split("@")[0], email=email, hashed_password=hash_password(pw), role="owner"))
            db.commit()
            print("  تم.")


if __name__ == "__main__":
    main()
