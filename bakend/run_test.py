import sys
import requests

sys.stdout.reconfigure(encoding='utf-8')
BASE_URL = 'http://127.0.0.1:5000'
passed = 0
failed = 0

def test(name, ok, info=''):
    global passed, failed
    if ok:
        passed += 1
        print(f"  [PASS] {name} ({info})")
    else:
        failed += 1
        print(f"  [FAIL] {name} ({info})")

print("--- RUNNING FULL PROJECT VALIDATION ---")

# 1. Health
try:
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    test("GET /api/health", r.status_code == 200, f"Status {r.status_code}")
except Exception as e:
    test("GET /api/health", False, str(e))

# 2. Chatbot Status
try:
    r = requests.get(f"{BASE_URL}/api/chatbot/status", timeout=5)
    d = r.json()
    test("GET /api/chatbot/status", r.status_code == 200 and d.get("success"), f"Model: {d.get('model')}")
except Exception as e:
    test("GET /api/chatbot/status", False, str(e))

# 3. Student Dashboard
try:
    r = requests.get(f"{BASE_URL}/api/student/dashboard?year=1st+Year&department=Computer+Science", timeout=10)
    d = r.json()
    subs = len(d.get("dashboard", {}).get("subjects", []))
    test("GET /api/student/dashboard", r.status_code == 200 and subs > 0, f"{subs} subjects")
except Exception as e:
    test("GET /api/student/dashboard", False, str(e))

# 4. Student Notices
try:
    r = requests.get(f"{BASE_URL}/api/student/notices", timeout=5)
    d = r.json()
    n = len(d.get("notices", []))
    test("GET /api/student/notices", r.status_code == 200 and d.get("success"), f"{n} notices")
except Exception as e:
    test("GET /api/student/notices", False, str(e))

# 5. Admin Documents
try:
    r = requests.get(f"{BASE_URL}/api/admin/documents", timeout=5)
    d = r.json()
    docs = len(d.get("documents", []))
    test("GET /api/admin/documents", r.status_code == 200 and d.get("success"), f"{docs} docs")
except Exception as e:
    test("GET /api/admin/documents", False, str(e))

# 6. Chatbot Questions
questions = [
    ("WHO IS BBA CA HOD", ["nilesh", "kaldate"]),
    ("who is BCS HOD", ["shaikh", "sarfaraz"]),
    ("who is principal of vpcsc indapur", ["lalasaheb", "kashid"]),
    ("Window 1 details", ["waghmare", "admission"]),
    ("Window 2 scholarship", ["pandit", "scholarship"]),
]

for q, kws in questions:
    try:
        r = requests.post(f"{BASE_URL}/api/chatbot/chat", json={"message": q}, timeout=35)
        if r.status_code == 200:
            reply = r.json().get("reply", "").lower()
            ok = any(k in reply for k in kws)
            test(f"Chat: {q}", ok, f"{r.elapsed.total_seconds():.1f}s")
        else:
            test(f"Chat: {q}", False, f"Status {r.status_code}")
    except Exception as e:
        test(f"Chat: {q}", False, str(e))

# 7. Multi-Turn alternating history test
try:
    h = [
        {"role": "user", "content": "Hello, what college is this?"},
        {"role": "assistant", "content": "Vidya Pratishthans Commerce and Science College, Indapur."}
    ]
    r = requests.post(f"{BASE_URL}/api/chatbot/chat", json={"message": "Where is it located?", "history": h}, timeout=35)
    test("Chat multi-turn history", r.status_code == 200, f"{r.elapsed.total_seconds():.1f}s")
except Exception as e:
    test("Chat multi-turn history", False, str(e))

# 8. Empty input validation
try:
    r = requests.post(f"{BASE_URL}/api/chatbot/chat", json={"message": "   "}, timeout=5)
    test("Input validation (empty)", r.status_code == 400, f"Status {r.status_code}")
except Exception as e:
    test("Input validation (empty)", False, str(e))

print(f"\n=== FINAL RESULT: {passed} PASSED, {failed} FAILED ===")
sys.exit(0 if failed == 0 else 1)
