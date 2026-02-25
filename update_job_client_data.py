import psycopg2
from urllib.parse import unquote

# Decode the password
password = unquote("p%25%258N2n%5EdY6R%257rU")

# Connection string for packers database
conn_string = f"host=public-primary-pg-inmumbaizone2-189645-1657841.db.onutho.com port=5432 dbname=packers user=dbadmin password={password}"

try:
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    print("Checking existing jobs...")
    
    # Check current job data
    cur.execute("SELECT id, client_id, client_name, client_email, client_phone FROM jobs LIMIT 5;")
    jobs = cur.fetchall()
    
    print(f"Found {len(jobs)} jobs:")
    for job in jobs:
        print(f"  Job {job[0]}: client_id={job[1]}, name={job[2]}, email={job[3]}, phone={job[4]}")
    
    # Update existing jobs with sample client data
    print("\nUpdating jobs with sample client data...")
    cur.execute("""
        UPDATE jobs 
        SET 
            client_name = 'John Smith',
            client_email = 'john.smith@example.com',
            client_phone = '+44 7700 900123'
        WHERE client_name IS NULL;
    """)
    
    rows_updated = cur.rowcount
    print(f"Updated {rows_updated} jobs with client data")
    
    conn.commit()
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")