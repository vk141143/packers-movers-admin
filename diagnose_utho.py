import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

access_key = os.getenv("UTHO_ACCESS_KEY")
secret_key = os.getenv("UTHO_SECRET_KEY")
bucket_name = os.getenv("UTHO_BUCKET_NAME")
endpoint_url = os.getenv("UTHO_ENDPOINT_URL")
region = os.getenv("UTHO_REGION", "in-noida-1")

print("="*60)
print("UTHO BUCKET DIAGNOSTIC")
print("="*60)
print(f"Bucket: {bucket_name}")
print(f"Endpoint: {endpoint_url}")
print(f"Region: {region}")
print(f"Access Key: {access_key[:10]}...")
print()

s3 = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    region_name=region,
    config=Config(signature_version='s3v4')
)

# Test 1: Check bucket exists
print("[TEST 1] Checking if bucket exists...")
try:
    s3.head_bucket(Bucket=bucket_name)
    print("  [OK] Bucket exists")
except ClientError as e:
    print(f"  [FAIL] {e}")

# Test 2: List objects permission
print("\n[TEST 2] Testing LIST permission...")
try:
    response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
    print("  [OK] Can list objects")
except ClientError as e:
    print(f"  [FAIL] {e}")

# Test 3: Get bucket ACL
print("\n[TEST 3] Checking bucket ACL...")
try:
    acl = s3.get_bucket_acl(Bucket=bucket_name)
    print("  [OK] Bucket ACL:")
    for grant in acl['Grants']:
        print(f"    - {grant['Grantee'].get('DisplayName', 'Unknown')}: {grant['Permission']}")
except ClientError as e:
    print(f"  [FAIL] {e}")

# Test 4: Try to upload a test file
print("\n[TEST 4] Testing WRITE permission...")
test_content = b"test file content"
test_key = "test_upload.txt"

try:
    s3.put_object(
        Bucket=bucket_name,
        Key=test_key,
        Body=test_content
    )
    print("  [OK] Upload successful (without ACL)")
    
    # Try to delete test file
    s3.delete_object(Bucket=bucket_name, Key=test_key)
    print("  [OK] Delete successful")
    
except ClientError as e:
    print(f"  [FAIL] {e}")

# Test 5: Try upload with public-read ACL
print("\n[TEST 5] Testing WRITE with public-read ACL...")
try:
    s3.put_object(
        Bucket=bucket_name,
        Key=test_key,
        Body=test_content,
        ACL='public-read'
    )
    print("  [OK] Upload with public-read ACL successful")
    
    # Clean up
    s3.delete_object(Bucket=bucket_name, Key=test_key)
    print("  [OK] Cleanup successful")
    
except ClientError as e:
    print(f"  [FAIL] {e}")
    error_code = e.response['Error']['Code']
    if error_code == 'AccessDenied':
        print("\n  DIAGNOSIS: Your access key doesn't have permission to set ACL")
        print("  SOLUTION: Either:")
        print("    1. Remove ACL='public-read' from upload code")
        print("    2. Contact Utho to grant PutObjectAcl permission")

# Test 6: Check bucket policy
print("\n[TEST 6] Checking bucket policy...")
try:
    policy = s3.get_bucket_policy(Bucket=bucket_name)
    print("  [OK] Bucket policy exists:")
    print(f"    {policy['Policy']}")
except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
        print("  [INFO] No bucket policy set")
    else:
        print(f"  [FAIL] {e}")

print("\n" + "="*60)
print("RECOMMENDATIONS:")
print("="*60)
