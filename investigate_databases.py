import psycopg2
from urllib.parse import unquote

password = unquote("p%25%258N2n%5EdY6R%257rU")
host = "public-primary-pg-inmumbaizone2-189645-1657841.db.onutho.com"

print("Checking databases...\n")

# Try to connect to postgres database first to list all databases
try:
    conn = psycopg2.connect(
        host=host,
        port=5432,
        dbname="postgres",
        user="dbadmin",
        password=password
    )
    cur = conn.cursor()
    
    # List all databases
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
    databases = cur.fetchall()
    
    print(f"Available databases ({len(databases)}):")
    for db in databases:
        print(f"  - {db[0]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Could not list databases: {e}")
    print("\nTrying known databases...\n")

# Check each database for tables
for db_name in ["defaultdb", "packers", "postgres"]:
    print(f"\n{'='*60}")
    print(f"Checking database: {db_name}")
    print('='*60)
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=5432,
            dbname=db_name,
            user="dbadmin",
            password=password
        )
        cur = conn.cursor()
        
        print(f"[OK] Connected to '{db_name}'")
        
        # Check tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        print(f"\nTables found: {len(tables)}")
        
        if tables:
            for table in tables:
                # Count rows in each table
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table[0]};")
                    count = cur.fetchone()[0]
                    print(f"  - {table[0]} ({count} rows)")
                except:
                    print(f"  - {table[0]} (cannot count)")
        else:
            print("  (no tables)")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Cannot connect to '{db_name}': {e}")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
