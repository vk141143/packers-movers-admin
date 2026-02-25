import psycopg2
from urllib.parse import unquote

# Decode the password
password = unquote("p%25%258N2n%5EdY6R%257rU")

# Connection string for packers database
conn_string = f"host=public-primary-pg-inmumbaizone2-189645-1657841.db.onutho.com port=5432 dbname=packers user=dbadmin password={password}"

try:
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    print("Deleting all crew data...")
    
    # Delete all crew records
    cur.execute("DELETE FROM crew;")
    
    rows_deleted = cur.rowcount
    print(f"Deleted {rows_deleted} crew records")
    
    conn.commit()
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")