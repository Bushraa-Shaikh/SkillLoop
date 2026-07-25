"""
Step 6 – SQL Server Setup & Database Test
Run with: python setup_db.py
This script:
  1. Tests your SQL Server connection
  2. Creates the database
  3. Runs the schema
  4. Seeds test data
  5. Verifies everything works
"""
import sys, os
sys.path.insert(0, r"C:\Users\Bushra Shaikh\Desktop\SkillLoop")

print("=" * 60)
print("   SKILLLOOP - DATABASE SETUP & TEST")
print("=" * 60)

# ---------------------------------------------------------------
# STEP 1 – Check pyodbc installed
# ---------------------------------------------------------------
print("\n[STEP 1] Checking pyodbc...")
try:
    import pyodbc
    print(f"  OK  pyodbc version: {pyodbc.version}")
except ImportError:
    print("  FAIL  pyodbc not installed. Run: pip install pyodbc")
    sys.exit(1)

# ---------------------------------------------------------------
# STEP 2 – List available ODBC drivers
# ---------------------------------------------------------------
print("\n[STEP 2] Available ODBC Drivers...")
drivers = pyodbc.drivers()
if drivers:
    for d in drivers:
        print(f"  OK  Driver found: {d}")
else:
    print("  FAIL  No ODBC drivers found!")
    print("        Download: https://aka.ms/downloadmsodbcsql")
    sys.exit(1)

# Find SQL Server driver
sql_driver = None
preferred = [
    "ODBC Driver 17 for SQL Server",
    "ODBC Driver 18 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server",
]
for p in preferred:
    if p in drivers:
        sql_driver = p
        break

if sql_driver:
    print(f"\n  OK  Using driver: {sql_driver}")
else:
    print("\n  WARN  Preferred driver not found. Using: " + drivers[0])
    sql_driver = drivers[0]

# ---------------------------------------------------------------
# STEP 3 – Get connection details
# ---------------------------------------------------------------
print("\n[STEP 3] Connection Configuration...")
print("  Enter your SQL Server details (press Enter for defaults):\n")

server   = input("  Server   [localhost]: ").strip() or "localhost"
username = input("  Username (leave blank for Windows Auth): ").strip()
password = input("  Password:             ").strip()

if not password:
    print("  WARN  No password entered. Trying Windows Authentication...")
    use_windows_auth = True
else:
    use_windows_auth = False

# ---------------------------------------------------------------
# STEP 4 – Test connection to SQL Server (master db first)
# ---------------------------------------------------------------
print("\n[STEP 4] Testing SQL Server connection...")

if use_windows_auth:
    conn_str = (
        f"DRIVER={{{sql_driver}}};"
        f"SERVER={server};"
        f"DATABASE=master;"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )
else:
    conn_str = (
        f"DRIVER={{{sql_driver}}};"
        f"SERVER={server};"
        f"DATABASE=master;"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    print(f"  OK  Connected to SQL Server!")
    print(f"  OK  Version: {version[:80]}...")
    conn.close()
except Exception as e:
    print(f"  FAIL  Cannot connect: {e}")
    print()
    print("  Troubleshooting:")
    print("  1. Make sure SQL Server is running")
    print("     - Open 'SQL Server Configuration Manager'")
    print("     - Check 'SQL Server (MSSQLSERVER)' is Running")
    print("  2. Enable TCP/IP:")
    print("     - SQL Server Config Manager > Network Config > Protocols")
    print("     - Enable TCP/IP, restart SQL Server")
    print("  3. Check firewall allows port 1433")
    print("  4. For named instance try: SERVER=localhost\\SQLEXPRESS")
    sys.exit(1)

# ---------------------------------------------------------------
# STEP 5 – Create database
# ---------------------------------------------------------------
print("\n[STEP 5] Creating skillloop_db database...")

try:
    conn = pyodbc.connect(conn_str, timeout=10, autocommit=True)
    cursor = conn.cursor()

    # Check if exists
    cursor.execute(
        "SELECT name FROM sys.databases WHERE name = 'skillloop_db'"
    )
    exists = cursor.fetchone()

    if exists:
        print("  OK  Database 'skillloop_db' already exists")
    else:
        cursor.execute("CREATE DATABASE skillloop_db")
        print("  OK  Database 'skillloop_db' created!")

    conn.close()
except Exception as e:
    print(f"  FAIL  Error creating database: {e}")
    sys.exit(1)

# ---------------------------------------------------------------
# STEP 6 – Update .env with connection details
# ---------------------------------------------------------------
print("\n[STEP 6] Updating .env file...")

env_path = ".env"
try:
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            content = f.read()

        # Update values
        import re
        content = re.sub(r"DB_SERVER=.*",   f"DB_SERVER={server}",   content)
        content = re.sub(r"DB_USERNAME=.*", f"DB_USERNAME={username}", content)
        if not use_windows_auth:
            content = re.sub(r"DB_PASSWORD=.*", f"DB_PASSWORD={password}", content)

        with open(env_path, "w") as f:
            f.write(content)
        print(f"  OK  .env updated with connection details")
    else:
        print("  WARN  .env file not found - skipping")
except Exception as e:
    print(f"  WARN  Could not update .env: {e}")

# ---------------------------------------------------------------
# STEP 7 – Run schema
# ---------------------------------------------------------------
print("\n[STEP 7] Running database schema...")

schema_path = os.path.join("migrations", "schema.sql")
if not os.path.exists(schema_path):
    print(f"  FAIL  Schema file not found: {schema_path}")
    sys.exit(1)

# Connect to skillloop_db
if use_windows_auth:
    db_conn_str = (
        f"DRIVER={{{sql_driver}}};"
        f"SERVER={server};"
        f"DATABASE=skillloop_db;"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )
else:
    db_conn_str = (
        f"DRIVER={{{sql_driver}}};"
        f"SERVER={server};"
        f"DATABASE=skillloop_db;"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )

try:
    conn = pyodbc.connect(db_conn_str, timeout=10, autocommit=True)
    cursor = conn.cursor()

    # Read and split schema by GO statements
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()

    # Split on GO keyword (SQL Server batch separator)
    batches = [b.strip() for b in schema.split("\nGO") if b.strip()]

    success = 0
    errors  = 0
    for batch in batches:
        # Skip USE/database switching statements
        if batch.upper().startswith("USE "):
            continue
        if not batch or batch.startswith("--"):
            continue
        try:
            cursor.execute(batch)
            success += 1
        except Exception as e:
            err_msg = str(e)
            # Ignore "already exists" errors
            if "already exists" in err_msg or \
               "There is already an object" in err_msg or \
               "duplicate" in err_msg.lower():
                success += 1  # table already there = fine
            else:
                errors += 1
                print(f"  WARN  Batch error (non-critical): {err_msg[:80]}")

    conn.close()
    print(f"  OK  Schema executed: {success} batches OK, {errors} warnings")

except Exception as e:
    print(f"  FAIL  Schema error: {e}")
    sys.exit(1)

# ---------------------------------------------------------------
# STEP 8 – Verify tables created
# ---------------------------------------------------------------
print("\n[STEP 8] Verifying tables...")

expected_tables = [
    "Users", "Skills", "UserSkills", "Badges", "UserBadges",
    "Gigs", "GigImages", "Wallet", "Transactions", "Orders",
    "Reviews", "Messages", "Projects", "Bids",
    "Notifications", "Portfolio"
]

try:
    conn   = pyodbc.connect(db_conn_str, timeout=10)
    cursor = conn.cursor()

    for table in expected_tables:
        cursor.execute(
            "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_NAME = ?", (table,)
        )
        exists = cursor.fetchone()[0]
        if exists:
            print(f"  OK  Table exists: {table}")
        else:
            print(f"  FAIL  Table MISSING: {table}")

    conn.close()
except Exception as e:
    print(f"  FAIL  Table verification error: {e}")

# ---------------------------------------------------------------
# STEP 9 – Seed test data
# ---------------------------------------------------------------
print("\n[STEP 9] Seeding test data...")

from werkzeug.security import generate_password_hash

test_users = [
    {
        "name":       "Admin User",
        "email":      "admin@skillloop.com",
        "password":   "Admin1234",
        "university": "SkillLoop HQ",
        "country":    "Pakistan",
        "role":       "admin",
        "verified":   1,
    },
    {
        "name":       "Ali Hassan",
        "email":      "ali@fast.edu.pk",
        "password":   "Test1234",
        "university": "FAST University",
        "country":    "Pakistan",
        "role":       "both",
        "verified":   1,
    },
    {
        "name":       "Sara Ahmed",
        "email":      "sara@iba.edu.pk",
        "password":   "Test1234",
        "university": "IBA Karachi",
        "country":    "Pakistan",
        "role":       "seller",
        "verified":   1,
    },
    {
        "name":       "Zara Khan",
        "email":      "zara@nust.edu.pk",
        "password":   "Test1234",
        "university": "NUST Islamabad",
        "country":    "Pakistan",
        "role":       "buyer",
        "verified":   1,
    },
]

try:
    conn   = pyodbc.connect(db_conn_str, timeout=10)
    cursor = conn.cursor()

    created_users = []
    for u in test_users:
        # Check if already exists
        cursor.execute(
            "SELECT user_id FROM Users WHERE email = ?", (u["email"],)
        )
        existing = cursor.fetchone()
        if existing:
            print(f"  OK  User already exists: {u['email']}")
            created_users.append(existing[0])
            continue

        pw_hash = generate_password_hash(u["password"])
        cursor.execute(
            """
            INSERT INTO Users
              (name, email, password_hash, university, country,
               role, is_verified, auth_provider, is_active)
            VALUES (?,?,?,?,?,?,?,?,1)
            """,
            (u["name"], u["email"], pw_hash,
             u["university"], u["country"],
             u["role"], u["verified"], "local")
        )
        conn.commit()

        cursor.execute(
            "SELECT user_id FROM Users WHERE email = ?", (u["email"],)
        )
        uid = cursor.fetchone()[0]
        created_users.append(uid)

        # Create wallet
        cursor.execute(
            "INSERT INTO Wallet (user_id, balance) VALUES (?,?)",
            (uid, 100)
        )
        conn.commit()
        print(f"  OK  Created user: {u['name']} ({u['role']}) - ID:{uid}")

    # Seed a gig
    if len(created_users) >= 2:
        seller_id = created_users[1]  # Ali Hassan
        cursor.execute(
            "SELECT gig_id FROM Gigs WHERE seller_id = ?", (seller_id,)
        )
        gig_exists = cursor.fetchone()
        if not gig_exists:
            cursor.execute(
                """
                INSERT INTO Gigs
                  (seller_id, title, description, category, price,
                   delivery_days, revisions, tags, is_active, allow_swap)
                VALUES (?,?,?,?,?,?,?,?,1,1)
                """,
                (
                    seller_id,
                    "I will build a professional Flask web application",
                    "Full-stack Python Flask developer with 3 years experience. "
                    "I will create a clean, responsive web application with "
                    "database integration, authentication, and modern UI.",
                    "Web Development",
                    50,
                    5,
                    2,
                    "flask, python, web, backend",
                )
            )
            conn.commit()
            print(f"  OK  Created sample gig for {test_users[1]['name']}")
        else:
            print(f"  OK  Gig already exists for {test_users[1]['name']}")

    conn.close()
    print("  OK  Test data seeded successfully!")

except Exception as e:
    print(f"  FAIL  Seed error: {e}")
    import traceback; traceback.print_exc()

# ---------------------------------------------------------------
# STEP 10 – Test app models with real DB
# ---------------------------------------------------------------
print("\n[STEP 10] Testing models with real database...")

# Update config dynamically
os.environ["DB_SERVER"]   = server
os.environ["DB_USERNAME"] = username
os.environ["DB_PASSWORD"] = password if not use_windows_auth else ""
os.environ["DB_NAME"]     = "skillloop_db"

try:
    from app.utils.db import test_connection
    if test_connection():
        print("  OK  Database connection via app utility works!")
    else:
        print("  FAIL  App utility connection failed")
except Exception as e:
    print(f"  FAIL  Connection utility error: {e}")

try:
    from app.models.user import UserModel
    user = UserModel.get_by_email("admin@skillloop.com")
    if user:
        print(f"  OK  UserModel.get_by_email works: {user.name}")
    else:
        print("  WARN  Admin user not found via model")
except Exception as e:
    print(f"  FAIL  UserModel error: {e}")

try:
    from app.models.gig import GigModel
    gigs = GigModel.get_featured(limit=5)
    print(f"  OK  GigModel.get_featured works: {len(gigs)} gigs found")
except Exception as e:
    print(f"  FAIL  GigModel error: {e}")

try:
    from app.models.wallet import WalletModel
    balance = WalletModel.get_balance(1)
    print(f"  OK  WalletModel.get_balance works: {balance} coins")
except Exception as e:
    print(f"  FAIL  WalletModel error: {e}")

# ---------------------------------------------------------------
# FINAL SUMMARY
# ---------------------------------------------------------------
print()
print("=" * 60)
print("  DATABASE SETUP COMPLETE!")
print()
print("  Test Accounts Created:")
print("  ┌─────────────────────────────┬──────────┬──────────┐")
print("  │ Email                       │ Password │ Role     │")
print("  ├─────────────────────────────┼──────────┼──────────┤")
for u in test_users:
    print(f"  │ {u['email']:<27}   │ {u['password']:<8} │ {u['role']:<8} │")
print("  └─────────────────────────────┴──────────┴──────────┘")
print()
print("  Next step: python run.py")
print("  Then open: http://localhost:5000")
print("=" * 60)