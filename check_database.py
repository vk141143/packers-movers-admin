import psycopg2
from urllib.parse import unquote

# Decode the password
password = unquote("p%25%258N2n%5EdY6R%257rU")
print(f"Decoded password: {password}")

# Connection string
conn_string = f"host=public-primary-pg-inmumbaizone2-189645-1657841.db.onutho.com port=5432 dbname=defaultdb user=dbadmin password={password}"

try:
    # Connect to database
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    print("\nDatabase connection successful!")
    
    # Check existing tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cur.fetchall()
    print(f"\nExisting tables in database ({len(tables)} total):")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check if required tables exist
    required_tables = ['jobs', 'clients', 'admins', 'crew', 'invoices', 'services', 'service_levels']
    print(f"\nChecking required tables:")
    
    existing_table_names = [t[0] for t in tables]
    for req_table in required_tables:
        if req_table in existing_table_names:
            print(f"  [OK] {req_table} - EXISTS")
        else:
            print(f"  [MISSING] {req_table}")
    
    # Check permissions
    print(f"\nChecking permissions for 'dbadmin' user:")
    cur.execute("""
        SELECT 
            has_schema_privilege('dbadmin', 'public', 'CREATE') as can_create,
            has_schema_privilege('dbadmin', 'public', 'USAGE') as can_use;
    """)
    perms = cur.fetchone()
    print(f"  - CREATE permission: {'YES' if perms[0] else 'NO'}")
    print(f"  - USAGE permission: {'YES' if perms[1] else 'NO'}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\nError: {e}")
