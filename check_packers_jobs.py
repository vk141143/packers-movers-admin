import psycopg2
from urllib.parse import unquote

# Decode the password
password = unquote("p%25%258N2n%5EdY6R%257rU")

# Connection string for packers database
conn_string = f"host=public-primary-pg-inmumbaizone2-189645-1657841.db.onutho.com port=5432 dbname=packers user=dbadmin password={password}"

try:
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    print("Checking jobs table structure in packers database...")
    
    # Check if jobs table exists and get its columns
    cur.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'jobs' 
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    
    if columns:
        print(f"\nJobs table exists with {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) - {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        # Check if client fields exist
        client_id_exists = any(col[0] == 'client_id' for col in columns)
        client_name_exists = any(col[0] == 'client_name' for col in columns)
        client_email_exists = any(col[0] == 'client_email' for col in columns)
        client_phone_exists = any(col[0] == 'client_phone' for col in columns)
        
        print(f"\nColumn check:")
        print(f"  - client_id exists: {client_id_exists}")
        print(f"  - client_name exists: {client_name_exists}")
        print(f"  - client_email exists: {client_email_exists}")
        print(f"  - client_phone exists: {client_phone_exists}")
        
    else:
        print("Jobs table does not exist")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")