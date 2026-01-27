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

# Check crew status
cur.execute("SELECT id, full_name, status FROM crew")
crews = cur.fetchall()

print("Crew Status:")
for crew in crews:
    print(f"  {crew[1]}: {crew[2]}")

# Check if crew has active jobs
cur.execute("""
    SELECT c.full_name, j.id, j.status 
    FROM crew c 
    LEFT JOIN jobs j ON j.assigned_crew_id = c.id 
    WHERE j.status NOT IN ('job_completed', 'cancelled') OR j.status IS NULL
""")
active_jobs = cur.fetchall()

print("\nActive Jobs:")
for job in active_jobs:
    print(f"  {job[0]}: Job {job[1]} - {job[2]}")

cur.close()
conn.close()
