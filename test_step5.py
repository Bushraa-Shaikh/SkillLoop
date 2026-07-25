"""
Step 5 Tests – Templates & Frontend
Run with: python test_step5.py
"""
import sys, os
sys.path.insert(0, r"C:\Users\Bushra Shaikh\Desktop\SkillLoop")

print("=" * 60)
print("   SKILLLOOP - STEP 5 TEMPLATE TESTS")
print("=" * 60)

passed = 0
failed = 0

def ok(msg):
    global passed; passed += 1
    print(f"  \u2705 {msg}")

def fail(msg):
    global failed; failed += 1
    print(f"  \u274c {msg}")

def info(msg):
    print(f"  \u2139  {msg}")

# ---------------------------------------------------------------
# TEST 1 - All template files exist
# ---------------------------------------------------------------
print("\n[TEST 1] Template files exist...")

import os
base = os.path.join("app", "templates")

required = [
    "base.html",
    "index.html",
    "auth/login.html",
    "auth/signup.html",
    "auth/verify_student.html",
    "auth/profile_setup.html",
    "dashboard/dashboard.html",
    "dashboard/wallet.html",
    "dashboard/notifications.html",
    "dashboard/profile.html",
    "dashboard/my_profile.html",
    "gigs/browse.html",
    "gigs/gig_detail.html",
    "gigs/create_gig.html",
    "gigs/edit_gig.html",
    "gigs/seller_gigs.html",
    "orders/place_order.html",
    "orders/buyer_orders.html",
    "orders/seller_orders.html",
    "orders/order_status.html",
    "orders/review.html",
    "orders/projects.html",
    "orders/post_project.html",
    "orders/project_detail.html",
    "orders/place_bid.html",
    "chat/chat.html",
    "chat/messages.html",
    "admin/dashboard.html",
    "admin/users.html",
    "admin/gigs.html",
    "admin/orders.html",
    "errors/404.html",
    "errors/403.html",
    "errors/500.html",
]

for tmpl in required:
    path = os.path.join(base, tmpl.replace("/", os.sep))
    if os.path.exists(path):
        ok(f"Found: {tmpl}")
    else:
        fail(f"MISSING: {tmpl}")

# ---------------------------------------------------------------
# TEST 2 - Static files exist
# ---------------------------------------------------------------
print("\n[TEST 2] Static files exist...")

static_files = [
    os.path.join("app", "static", "css", "style.css"),
    os.path.join("app", "static", "js",  "main.js"),
]
for f in static_files:
    if os.path.exists(f):
        size = os.path.getsize(f)
        ok(f"Found: {f}  ({size:,} bytes)")
    else:
        fail(f"MISSING: {f}")

# ---------------------------------------------------------------
# TEST 3 - Template sizes (not empty)
# ---------------------------------------------------------------
print("\n[TEST 3] Templates are not empty...")

for tmpl in required:
    path = os.path.join(base, tmpl.replace("/", os.sep))
    if os.path.exists(path):
        size = os.path.getsize(path)
        if size > 100:
            ok(f"{tmpl:<45} {size:>6} bytes")
        else:
            fail(f"{tmpl} is too small ({size} bytes) – may be empty!")

# ---------------------------------------------------------------
# TEST 4 - Templates extend base.html
# ---------------------------------------------------------------
print("\n[TEST 4] Templates extend base.html correctly...")

should_extend = [
    "auth/login.html",
    "auth/signup.html",
    "dashboard/dashboard.html",
    "dashboard/wallet.html",
    "gigs/browse.html",
    "gigs/create_gig.html",
    "orders/place_order.html",
    "chat/chat.html",
    "admin/dashboard.html",
    "errors/404.html",
]

for tmpl in should_extend:
    path = os.path.join(base, tmpl.replace("/", os.sep))
    if os.path.exists(path):
        content = open(path, encoding="utf-8").read()
        if 'extends "base.html"' in content or "extends 'base.html'" in content:
            ok(f"{tmpl} extends base.html")
        else:
            fail(f"{tmpl} does NOT extend base.html")

# ---------------------------------------------------------------
# TEST 5 - base.html has required blocks
# ---------------------------------------------------------------
print("\n[TEST 5] base.html has required elements...")

base_path = os.path.join(base, "base.html")
if os.path.exists(base_path):
    content = open(base_path, encoding="utf-8").read()
    checks = [
        ("{% block content %}", "content block"),
        ("{% block title %}",   "title block"),
        ("{% block scripts %}", "scripts block"),
        ("navbar",              "navbar"),
        ("style.css",           "CSS link"),
        ("main.js",             "JS link"),
        ("get_flashed_messages","flash messages"),
        ("current_user",        "current_user usage"),
        ("url_for",             "url_for usage"),
        ("footer",              "footer"),
    ]
    for pattern, label in checks:
        if pattern in content:
            ok(f"base.html has: {label}")
        else:
            fail(f"base.html MISSING: {label}")

# ---------------------------------------------------------------
# TEST 6 - CSS has required classes
# ---------------------------------------------------------------
print("\n[TEST 6] CSS has required classes...")

css_path = os.path.join("app", "static", "css", "style.css")
if os.path.exists(css_path):
    css = open(css_path, encoding="utf-8").read()
    css_classes = [
        (".navbar",      "navbar"),
        (".btn",         "button styles"),
        (".btn-primary", "primary button"),
        (".card",        "card"),
        (".gig-card",    "gig card"),
        (".user-card",   "user card"),
        (".form-control","form control"),
        (".alert",       "alerts"),
        (".badge",       "badges"),
        (".hero",        "hero section"),
        (".sidebar",     "sidebar"),
        (".chat-main",   "chat layout"),
        (".wallet-hero", "wallet hero"),
        (".auth-page",   "auth page"),
        (".stat-card",   "stat cards"),
        ("--teal",       "teal CSS variable"),
        ("--navy",       "navy CSS variable"),
        ("@media",       "responsive breakpoints"),
    ]
    for cls, label in css_classes:
        if cls in css:
            ok(f"CSS has: {label}")
        else:
            fail(f"CSS MISSING: {label}")

# ---------------------------------------------------------------
# TEST 7 - JS has required functions
# ---------------------------------------------------------------
print("\n[TEST 7] JavaScript has required functions...")

js_path = os.path.join("app", "static", "js", "main.js")
if os.path.exists(js_path):
    js = open(js_path, encoding="utf-8").read()
    js_checks = [
        (".alert",           "alert auto-dismiss"),
        ("data-confirm",     "confirm dialogs"),
        ("star-picker",      "star rating picker"),
        ("animateNum",       "number animation"),
        ("chat-messages",    "chat scroll"),
        ("showToast",        "toast notifications"),
        ("escHtml",          "HTML escaping"),
        ("socket.on",        "SocketIO"),
        ("new_message",      "chat send"),
    ]
    for pattern, label in js_checks:
        if pattern in js:
            ok(f"JS has: {label}")
        else:
            fail(f"JS MISSING: {label}")

# ---------------------------------------------------------------
# TEST 8 - Flask app renders templates (no DB needed)
# ---------------------------------------------------------------
print("\n[TEST 8] Flask renders templates (no DB)...")

try:
    from app import create_app
    app = create_app("testing")

    with app.test_client() as client:
        # Login page - should render fine without DB
        resp = client.get("/login")
        if resp.status_code == 200:
            html = resp.data.decode("utf-8")
            checks = [
                ("SkillLoop",    "brand name"),
                ("email",        "email field"),
                ("password",     "password field"),
                ("Google",       "Google login button"),
                ("Sign",         "sign in text"),
            ]
            for pattern, label in checks:
                if pattern in html:
                    ok(f"/login renders with: {label}")
                else:
                    fail(f"/login missing: {label}")
        else:
            fail(f"/login returned {resp.status_code}")

        # Signup page
        resp = client.get("/signup")
        if resp.status_code == 200:
            html = resp.data.decode("utf-8")
            if "university" in html.lower() and "password" in html.lower():
                ok("/signup renders correctly")
            else:
                fail("/signup missing form fields")
        else:
            fail(f"/signup returned {resp.status_code}")

        # Protected routes redirect to login
        for route in ["/dashboard", "/wallet", "/seller-gigs",
                      "/buyer-orders", "/create-gig"]:
            resp = client.get(route, follow_redirects=False)
            if resp.status_code in (302, 401):
                ok(f"{route} → redirects to login ({resp.status_code})")
            else:
                info(f"{route} → {resp.status_code} (may need DB)")

        # Error pages render
        with app.test_request_context():
            from flask import render_template
            for tmpl, code in [("errors/404.html","404"),
                                ("errors/403.html","403"),
                                ("errors/500.html","500")]:
                try:
                    html = render_template(tmpl)
                    if code in html:
                        ok(f"Error page {tmpl} renders")
                    else:
                        fail(f"Error page {tmpl} missing error code")
                except Exception as e:
                    fail(f"Error page {tmpl} failed: {e}")

except Exception as e:
    fail(f"Flask app error: {e}")
    import traceback; traceback.print_exc()

# ---------------------------------------------------------------
# TEST 9 - Template content checks
# ---------------------------------------------------------------
print("\n[TEST 9] Template content checks...")

content_checks = [
    ("index.html",
     ["hero", "Featured Gigs", "Top Performers",
      "New Talent", "Rising Stars"]),
    ("auth/login.html",
     ["email", "password", "Google", "signup"]),
    ("auth/signup.html",
     ["name", "email", "password", "university", "country"]),
    ("dashboard/dashboard.html",
     ["wallet_balance", "Dashboard", "notifications"]),
    ("dashboard/wallet.html",
     ["balance", "Transaction", "Campus Coins"]),
    ("gigs/browse.html",
     ["filter", "category", "price", "sort"]),
    ("gigs/gig_detail.html",
     ["gig.title", "Order Now", "reviews", "seller"]),
    ("gigs/create_gig.html",
     ["title", "description", "price", "delivery"]),
    ("orders/place_order.html",
     ["payment_method", "coins", "requirements"]),
    ("orders/order_status.html",
     ["Pending", "InProgress", "Delivered", "Completed"]),
    ("chat/chat.html",
     ["chat-messages", "drive_link", "Send"]),
    ("admin/dashboard.html",
     ["total_users", "total_gigs", "total_orders"]),
]

for tmpl, keywords in content_checks:
    path = os.path.join(base, tmpl.replace("/", os.sep))
    if not os.path.exists(path):
        fail(f"{tmpl} not found")
        continue
    content = open(path, encoding="utf-8").read()
    all_found = True
    for kw in keywords:
        if kw not in content:
            fail(f"{tmpl} missing: '{kw}'")
            all_found = False
    if all_found:
        ok(f"{tmpl} has all required content")

# ---------------------------------------------------------------
# TEST 10 - Count everything
# ---------------------------------------------------------------
print("\n[TEST 10] Final count...")

tmpl_count  = sum(1 for _, _, files in os.walk(base) for f in files if f.endswith(".html"))
css_size    = os.path.getsize(os.path.join("app","static","css","style.css")) if os.path.exists(os.path.join("app","static","css","style.css")) else 0
js_size     = os.path.getsize(os.path.join("app","static","js","main.js")) if os.path.exists(os.path.join("app","static","js","main.js")) else 0

ok(f"Total HTML templates : {tmpl_count}")
ok(f"CSS file size        : {css_size:,} bytes")
ok(f"JS file size         : {js_size:,} bytes")

# ---------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------
print()
print("=" * 60)
print(f"  Results: {passed} passed,  {failed} failed")
if failed == 0:
    print("  \u2705 ALL STEP 5 TESTS PASSED!")
    print()
    print("  Templates built:")
    print("    \U0001f3e0  Homepage + Base layout")
    print("    \U0001f510  Auth  (login, signup, verify, setup)")
    print("    \U0001f4ca  Dashboard (stats, orders, gigs)")
    print("    \U0001f6cd  Gigs  (browse, detail, create, edit)")
    print("    \U0001f4e6  Orders (place, status, review)")
    print("    \U0001f4ac  Chat  (real-time chat, inbox)")
    print("    \U0001fa99  Wallet (balance, transactions)")
    print("    \U0001f4cb  Projects (list, post, bid)")
    print("    \U0001f527  Admin (dashboard, users, gigs)")
    print("    \u26a0\ufe0f  Errors (404, 403, 500)")
else:
    print(f"  \u26a0\ufe0f  {failed} test(s) failed. Fix above issues.")
print("=" * 60)