import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse, unquote

def try_connect(hostname, port, username, password, database, ssl_mode=None):
    """Attempt a psycopg2 connection with optional SSL."""
    kwargs = dict(host=hostname, port=port, user=username, password=password, dbname=database, connect_timeout=15)
    if ssl_mode:
        kwargs["sslmode"] = ssl_mode
    return psycopg2.connect(**kwargs)

def sync_db():
    print("\n[*] OrgoLife - Automated Database Schema Sync")
    print("-------------------------------------------------")

    # 1. Load configuration
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")

    if not db_url or "[YOUR_PASSWORD]" in db_url:
        print("[ERROR] DATABASE_URL is not set correctly in your .env file.")
        return

    # Parse URL
    try:
        db_url = db_url.strip().replace("[", "").replace("]", "")
        result   = urlparse(db_url)
        base_user = result.username.strip() if result.username else "postgres"
        password  = unquote(result.password.strip()) if result.password else None
        database  = result.path.lstrip('/').strip() or "postgres"
        hostname  = result.hostname.strip() if result.hostname else None
        port      = result.port or 5432
    except Exception as e:
        print(f"[ERROR] Could not parse DATABASE_URL: {e}")
        return

    print(f"[*] Password decoded length: {len(password) if password else 0} chars")

    # 2. Find schema file
    schema_path = Path(__file__).parent.parent / "supabase_schema.sql"
    if not schema_path.exists():
        print(f"[ERROR] Schema file not found at {schema_path}")
        return

    print(f"[*] Reading schema from: {schema_path.name}")
    with open(schema_path, "r", encoding="utf-8") as f:
        full_sql = f.read()

    # 3. Try multiple connection strategies
    project_ref = "htcooghlfkazzszfnurw"
    pooler_host = "aws-0-ap-south-1.pooler.supabase.com"
    direct_host = f"db.{project_ref}.supabase.co"

    strategies = [
        # (label, host, port, user, ssl)
        ("Direct connection (SSL required)", direct_host,  5432, "postgres",                      "require"),
        ("Transaction Pooler",               pooler_host,  6543, f"postgres.{project_ref}",       "require"),
        ("Session Pooler",                   pooler_host,  5432, f"postgres.{project_ref}",       "require"),
        ("Direct connection (prefer SSL)",   direct_host,  5432, "postgres",                      "prefer"),
    ]

    conn = None
    for label, host, p, user, ssl in strategies:
        print(f"\n[*] Trying: {label}")
        print(f"    Host={host}  Port={p}  User={user}")
        try:
            conn = try_connect(host, p, user, password, database, ssl)
            print(f"[OK] Connected via: {label}")
            break
        except Exception as e:
            print(f"    Failed: {e}")

    if conn is None:
        print("\n" + "="*55)
        print("[FAILED] Could not connect to Supabase automatically.")
        print("="*55)
        print("\n>> MANUAL FIX (30 seconds):")
        print("   1. Open https://supabase.com/dashboard")
        print("   2. Select your project -> SQL Editor (left sidebar)")
        print("   3. Click 'New query'")
        print(f"   4. Open and copy ALL contents of: supabase_schema.sql")
        print("   5. Paste and click RUN")
        print("\nThen run: python main.py  (to start the server)")
        return

    # 4. Apply schema
    try:
        conn.autocommit = True
        cur = conn.cursor()
        print("[*] Applying schema...")
        cur.execute(full_sql)
        print("[SUCCESS] Database schema synchronized successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to apply schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    sync_db()
