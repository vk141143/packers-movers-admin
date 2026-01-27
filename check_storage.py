import boto3
from botocore.client import Config
import os
from dotenv import load_dotenv

load_dotenv()

# Utho credentials
access_key = os.getenv("UTHO_ACCESS_KEY")
secret_key = os.getenv("UTHO_SECRET_KEY")
bucket_name = os.getenv("UTHO_BUCKET_NAME")
endpoint_url = os.getenv("UTHO_ENDPOINT_URL")
region = os.getenv("UTHO_REGION", "in-noida-1")

print("Utho Object Storage Configuration:")
print(f"  Bucket: {bucket_name}")
print(f"  Endpoint: {endpoint_url}")
print(f"  Region: {region}")
print()

# Create S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    region_name=region,
    config=Config(signature_version='s3v4')
)

print("Checking bucket contents...\n")

try:
    # List all objects in bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    
    if 'Contents' not in response:
        print("[INFO] Bucket is empty - no files uploaded yet")
    else:
        objects = response['Contents']
        print(f"Total files in bucket: {len(objects)}\n")
        
        # Categorize files
        crew_docs = []
        job_photos_before = []
        job_photos_after = []
        crew_profiles = []
        other_files = []
        
        for obj in objects:
            key = obj['Key']
            size = obj['Size']
            
            if key.startswith('crew_documents/'):
                crew_docs.append((key, size))
            elif 'job_photos/' in key and '/before/' in key:
                job_photos_before.append((key, size))
            elif 'job_photos/' in key and '/after/' in key:
                job_photos_after.append((key, size))
            elif key.startswith('crew_profiles/'):
                crew_profiles.append((key, size))
            else:
                other_files.append((key, size))
        
        # Display results
        print(f"[CREW DOCUMENTS] {len(crew_docs)} files")
        for key, size in crew_docs[:5]:  # Show first 5
            print(f"  - {key} ({size} bytes)")
        if len(crew_docs) > 5:
            print(f"  ... and {len(crew_docs) - 5} more")
        
        print(f"\n[JOB PHOTOS - BEFORE] {len(job_photos_before)} files")
        for key, size in job_photos_before[:5]:
            print(f"  - {key} ({size} bytes)")
        if len(job_photos_before) > 5:
            print(f"  ... and {len(job_photos_before) - 5} more")
        
        print(f"\n[JOB PHOTOS - AFTER] {len(job_photos_after)} files")
        for key, size in job_photos_after[:5]:
            print(f"  - {key} ({size} bytes)")
        if len(job_photos_after) > 5:
            print(f"  ... and {len(job_photos_after) - 5} more")
        
        print(f"\n[CREW PROFILES] {len(crew_profiles)} files")
        for key, size in crew_profiles[:5]:
            print(f"  - {key} ({size} bytes)")
        if len(crew_profiles) > 5:
            print(f"  ... and {len(crew_profiles) - 5} more")
        
        if other_files:
            print(f"\n[OTHER FILES] {len(other_files)} files")
            for key, size in other_files[:5]:
                print(f"  - {key} ({size} bytes)")
        
        # Test URL generation
        print("\n" + "="*60)
        print("Sample URLs:")
        print("="*60)
        if crew_docs:
            sample_url = f"{endpoint_url}/{bucket_name}/{crew_docs[0][0]}"
            print(f"Crew Doc: {sample_url}")
        if job_photos_before:
            sample_url = f"{endpoint_url}/{bucket_name}/{job_photos_before[0][0]}"
            print(f"Before Photo: {sample_url}")
        if job_photos_after:
            sample_url = f"{endpoint_url}/{bucket_name}/{job_photos_after[0][0]}"
            print(f"After Photo: {sample_url}")
        
        print("\n[SUCCESS] Storage is working correctly!")
        
except Exception as e:
    print(f"[ERROR] {e}")
