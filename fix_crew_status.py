import psycopg2
from urllib.parse import unquote

password = unquote("p%25%258N2n%5EdY6R%257rU")

conn = psycopg2.connect(
    host="public-primary-pg-inmumbaizone2-189645-1657841.db.onutho.com",
    port=5432,
    dbname="packers",
    user="dbadmin",
    password=password
)

cur = conn.cursor()

# Update crew status for those with active jobs
cur.execute("""
    UPDATE crew 
    SET status = 'assigned' 
    WHERE id IN (
        SELECT DISTINCT assigned_crew_id 
        FROM jobs 
        WHERE assigned_crew_id IS NOT NULL 
        AND status NOT IN ('job_completed', 'cancelled')
    )
""")

affected = cur.rowcount
conn.commit()

print(f"Updated {affected} crew members to 'assigned' status")

# Verify
cur.execute("SELECT full_name, status FROM crew")
crews = cur.fetchall()
print("\nCrew Status After Update:")
for crew in crews:
    print(f"  {crew[0]}: {crew[1]}")

cur.close()
conn.close()
