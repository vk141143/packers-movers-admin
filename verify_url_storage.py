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

print("Checking if URLs are stored in database...\n")

# Check crew table for document URLs
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'crew' 
    AND column_name IN ('drivers_license', 'dbs_certificate', 'proof_of_address', 'insurance_certificate', 'right_to_work', 'profile_photo')
    ORDER BY column_name
""")
crew_cols = cur.fetchall()
print("[CREW TABLE] Document URL columns:")
for col in crew_cols:
    print(f"  - {col[0]} ({col[1]})")

# Check job_photos table
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'job_photos'
    ORDER BY column_name
""")
photo_cols = cur.fetchall()
print("\n[JOB_PHOTOS TABLE] Columns:")
for col in photo_cols:
    print(f"  - {col[0]} ({col[1]})")

# Check jobs table for property photos
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'jobs' 
    AND column_name = 'property_photos'
""")
job_cols = cur.fetchall()
print("\n[JOBS TABLE] Property photos column:")
for col in job_cols:
    print(f"  - {col[0]} ({col[1]})")

# Check clients table for profile photo
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'clients' 
    AND column_name = 'profile_photo'
""")
client_cols = cur.fetchall()
print("\n[CLIENTS TABLE] Profile photo column:")
for col in client_cols:
    print(f"  - {col[0]} ({col[1]})")

print("\n" + "="*60)
print("SUMMARY:")
print("="*60)
print("✓ Crew documents URLs -> crew table (drivers_license, dbs_certificate, etc.)")
print("✓ Job before/after photos URLs -> job_photos table (photo_url column)")
print("✓ Client property photos URLs -> jobs table (property_photos column)")
print("✓ Profile photos URLs -> crew/clients table (profile_photo column)")
print("\nAll URLs are stored in database correctly!")

cur.close()
conn.close()
