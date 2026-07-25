"""
fix_db.py - Fixes all database issues
Run with: python fix_db.py
"""
import sys, os, re
sys.path.insert(0, r"C:\Users\Bushra Shaikh\Desktop\SkillLoop")

import pyodbc
from werkzeug.security import generate_password_hash

# ── Your connection details ─────────────────────────────────────
SERVER   = r"DESKTOP-O2BN9FQ\Bushra Shaikh"  # raw string fixes backslash
USERNAME = ""   # leave empty for Windows Auth
PASSWORD = ""   # leave empty for Windows Auth

DRIVER   = "ODBC Driver 18 for SQL Server"

def conn_str(db="skillloop_db"):
    return (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={db};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )

print("=" * 55)
print("  SKILLLOOP - DATABASE FIX")
print("=" * 55)

# ── STEP 1: Test connection ─────────────────────────────────────
print("\n[1] Testing connection...")
try:
    conn = pyodbc.connect(conn_str("master"), timeout=10)
    ver  = conn.cursor().execute("SELECT @@VERSION").fetchone()[0]
    conn.close()
    print(f"  OK  Connected: {ver[:60]}...")
except Exception as e:
    print(f"  FAIL  {e}")
    sys.exit(1)

# ── STEP 2: Create database ─────────────────────────────────────
print("\n[2] Creating database...")
try:
    conn   = pyodbc.connect(conn_str("master"), autocommit=True)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sys.databases WHERE name='skillloop_db'"
    )
    if cursor.fetchone():
        print("  OK  Already exists")
    else:
        cursor.execute("CREATE DATABASE skillloop_db")
        print("  OK  Created skillloop_db!")
    conn.close()
except Exception as e:
    print(f"  FAIL  {e}"); sys.exit(1)

# ── STEP 3: Run schema batch by batch ──────────────────────────
print("\n[3] Running schema...")

schema_path = os.path.join("migrations", "schema.sql")
schema = open(schema_path, "r", encoding="utf-8").read()

try:
    conn   = pyodbc.connect(conn_str("skillloop_db"), autocommit=True)
    cursor = conn.cursor()

    ok_n = err_n = 0

    # Split correctly on GO (on its own line)
    batches = re.split(r'^\s*GO\s*$', schema, flags=re.MULTILINE)

    for batch in batches:
        batch = batch.strip()
        if not batch:
            continue
        # Skip USE statements
        if re.match(r'^\s*USE\s+', batch, re.IGNORECASE):
            continue
        # Skip pure comment blocks
        if all(line.strip().startswith('--') or not line.strip()
               for line in batch.splitlines()):
            continue
        try:
            cursor.execute(batch)
            ok_n += 1
        except Exception as e:
            msg = str(e)
            safe = ["already exists", "There is already an object",
                    "duplicate key", "Cannot add", "Violation of PRIMARY"]
            if any(s in msg for s in safe):
                ok_n += 1
            else:
                err_n += 1
                print(f"  WARN  {msg[:90]}")

    conn.close()
    print(f"  OK  {ok_n} batches OK, {err_n} warnings")

except Exception as e:
    print(f"  FAIL  {e}"); sys.exit(1)

# ── STEP 4: Verify tables ───────────────────────────────────────
print("\n[4] Verifying tables...")
tables = ["Users","Skills","Gigs","Orders","Wallet","Transactions",
          "Messages","Reviews","Projects","Bids","Notifications",
          "Badges","UserSkills","GigImages","Portfolio","UserBadges"]
try:
    conn   = pyodbc.connect(conn_str("skillloop_db"))
    cursor = conn.cursor()
    all_ok = True
    for t in tables:
        cursor.execute(
            "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_NAME=?", (t,)
        )
        if cursor.fetchone()[0]:
            print(f"  OK  {t}")
        else:
            print(f"  FAIL  MISSING: {t}")
            all_ok = False
    conn.close()
    if not all_ok:
        print("\n  Some tables missing!")
        print("  Please open SSMS and run migrations\\schema.sql manually")
        sys.exit(1)
except Exception as e:
    print(f"  FAIL  {e}"); sys.exit(1)

# ── STEP 5: Seed users ──────────────────────────────────────────
print("\n[5] Seeding test users...")
users = [
    ("Admin User",  "admin@skillloop.com", "Admin1234",
     "SkillLoop HQ",    "Pakistan", "admin",  1),
    ("Ali Hassan",  "ali@fast.edu.pk",     "Test1234",
     "FAST University", "Pakistan", "both",   1),
    ("Sara Ahmed",  "sara@iba.edu.pk",     "Test1234",
     "IBA Karachi",     "Pakistan", "seller", 1),
    ("Zara Khan",   "zara@nust.edu.pk",    "Test1234",
     "NUST Islamabad",  "Pakistan", "buyer",  1),
    ("Omar Sheikh", "omar@lums.edu.pk",    "Test1234",
     "LUMS Lahore",     "Pakistan", "both",   1),
]

try:
    conn   = pyodbc.connect(conn_str("skillloop_db"))
    cursor = conn.cursor()
    uids   = []

    for name, email, pw, uni, country, role, verified in users:
        cursor.execute(
            "SELECT user_id FROM Users WHERE email=?", (email,)
        )
        row = cursor.fetchone()
        if row:
            uids.append(row[0])
            print(f"  OK  Exists : {email}")
            continue

        cursor.execute(
            """INSERT INTO Users
               (name,email,password_hash,university,country,
                role,is_verified,auth_provider,is_active)
               VALUES (?,?,?,?,?,?,?,'local',1)""",
            (name, email, generate_password_hash(pw),
             uni, country, role, verified)
        )
        conn.commit()
        cursor.execute(
            "SELECT user_id FROM Users WHERE email=?", (email,)
        )
        uid = cursor.fetchone()[0]
        uids.append(uid)

        cursor.execute(
            "SELECT wallet_id FROM Wallet WHERE user_id=?", (uid,)
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO Wallet (user_id,balance) VALUES (?,100)",
                (uid,)
            )
        conn.commit()
        print(f"  OK  Created: {name} [{role}] id={uid}")

    # ── Seed gigs ───────────────────────────────────────────────
    print("\n  Seeding gigs...")
    gigs = [
        (uids[1],
         "I will build a professional Flask web application",
         "Full-stack Python Flask developer. Clean responsive apps.",
         "Web Development", 50, 5, 2, "flask,python,web"),
        (uids[2],
         "I will design a stunning UI/UX for your app",
         "Professional UI/UX designer using Figma.",
         "UI/UX Design", 40, 3, 3, "design,ui,ux,figma"),
        (uids[4],
         "I will write SEO-optimized content for your website",
         "Content writer specializing in tech blogging.",
         "Content Writing", 25, 2, 2, "writing,seo,content"),
        (uids[1],
         "I will build a machine learning model for your data",
         "Data scientist with Python, sklearn, TensorFlow.",
         "Data Analysis", 80, 7, 1, "ml,python,data,ai"),
    ]

    for sid, title, desc, cat, price, days, revs, tags in gigs:
        cursor.execute(
            "SELECT gig_id FROM Gigs WHERE seller_id=? AND title=?",
            (sid, title)
        )
        if cursor.fetchone():
            print(f"  OK  Exists : {title[:45]}")
            continue
        cursor.execute(
            """INSERT INTO Gigs
               (seller_id,title,description,category,price,
                delivery_days,revisions,tags,is_active,allow_swap)
               VALUES (?,?,?,?,?,?,?,?,1,1)""",
            (sid, title, desc, cat, price, days, revs, tags)
        )
        conn.commit()
        print(f"  OK  Created: {title[:45]}")

    conn.close()

except Exception as e:
    print(f"  FAIL  {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# ── STEP 6: Fix .env ────────────────────────────────────────────
print("\n[6] Fixing .env file...")
env_path = ".env"

# Use raw string for server path in .env
new_env = f"""FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=skillloop-secret-key-change-in-production

DB_SERVER={SERVER}
DB_NAME=skillloop_db
DB_USERNAME=
DB_PASSWORD=

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

APP_URL=http://localhost:5000
INITIAL_COINS=100
"""

with open(env_path, "w", encoding="utf-8") as f:
    f.write(new_env)
print("  OK  .env written!")

# ── STEP 7: Fix config.py for Windows Auth ──────────────────────
print("\n[7] Testing app connection...")
os.environ["DB_SERVER"]   = SERVER
os.environ["DB_NAME"]     = "skillloop_db"
os.environ["DB_USERNAME"] = ""
os.environ["DB_PASSWORD"] = ""

# Patch config to use Windows Auth
from config.config import Config

def patched_conn_str():
    return (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE=skillloop_db;"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )

Config.get_connection_string = staticmethod(patched_conn_str)

try:
    from app.utils.db import test_connection
    if test_connection():
        print("  OK  App DB connection works!")
    else:
        print("  FAIL  App DB connection failed")
except Exception as e:
    print(f"  FAIL  {e}")

try:
    from app.models.user import UserModel
    u = UserModel.get_by_email("admin@skillloop.com")
    print(f"  OK  UserModel works: {u.name if u else 'not found'}")
except Exception as e:
    print(f"  FAIL  UserModel: {e}")

try:
    from app.models.gig import GigModel
    gigs = GigModel.get_featured(5)
    print(f"  OK  GigModel works: {len(gigs)} gigs")
    for g in gigs:
        print(f"       [{g['gig_id']}] {g['title'][:40]}")
except Exception as e:
    print(f"  FAIL  GigModel: {e}")

# ── SUMMARY ─────────────────────────────────────────────────────
print()
print("=" * 55)
print("  ALL FIXED!")
print()
print("  Test Accounts:")
print(f"  {'Email':<28} Password   Role")
print("  " + "-" * 50)
for name, email, pw, *_ in users:
    role = [u[5] for u in users if u[1]==email][0]
    print(f"  {email:<28} {pw:<10} {role}")
print()
print("  Run: python run.py")
print("  Open: http://localhost:5000")
print("=" * 55)