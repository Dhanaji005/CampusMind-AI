# =====================================================
# CAMPUSMIND AI - SUPABASE USERS SYNC SCRIPT
# =====================================================

import sqlite3
import os
import sys

# Ensure backend root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_supabase

def sync_users_to_supabase():
    supabase = get_supabase()
    if not supabase:
        print("[-] Supabase client could not be initialized.")
        return False

    db_path = os.path.join(os.path.dirname(__file__), "campusmind.db")
    if not os.path.exists(db_path):
        print("[-] campusmind.db not found.")
        return False

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    print(f"[*] Found {len(rows)} users in local SQLite database.")

    success_count = 0
    for r in rows:
        user_record = {
            "name": r["name"],
            "email": r["email"],
            "password_hash": r["password_hash"],
            "role": r["role"],
            "department": r["department"] or "BBA(CA)",
            "year_of_study": r["year_of_study"] or "3rd Year",
            "semester": r["semester"] or 5,
            "student_id": r["student_id"] or "",
            "avatar_url": r["avatar_url"] or ""
        }
        try:
            # Check if user already exists in Supabase
            existing = supabase.table("users").select("id").eq("email", r["email"]).execute()
            if existing.data and len(existing.data) > 0:
                # Update
                supabase.table("users").update(user_record).eq("email", r["email"]).execute()
                print(f"[+] Updated user in Supabase: {r['email']}")
            else:
                # Insert
                supabase.table("users").insert(user_record).execute()
                print(f"[+] Inserted user in Supabase: {r['email']}")
            success_count += 1
        except Exception as e:
            print(f"[-] Error syncing {r['email']}: {e}")

    conn.close()
    print(f"\n[+] Total {success_count}/{len(rows)} users synchronized with Supabase!")
    return True

if __name__ == "__main__":
    sync_users_to_supabase()
