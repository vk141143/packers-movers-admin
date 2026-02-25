import psycopg2
from urllib.parse import unquote

# Decode the password
password = unquote("p%25%258N2n%5EdY6R%257rU")

# Connection string
conn_string = f"host=public-primary-pg-inmumbaizone2-189645-1657841.db.onutho.com port=5432 dbname=defaultdb user=dbadmin password={password}"

try:
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    print("Adding client_name column to jobs table...")
    
    # Add client_name column
    cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS client_name VARCHAR(255);")
    
    # Update existing jobs with default client name
    cur.execute("UPDATE jobs SET client_name = 'Client' WHERE client_name IS NULL;")
    
    conn.commit()
    print("Migration completed successfully!")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")