import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

access_key = "twMDcBefWv3mlIC5QZphKTiuxgNXRkor6GE7"
secret_key = "MytpownPzqx1CYTdbgaZsQ9UXehARf45lOFS"
bucket_name = "mybucket-moveaway-mhr"
endpoint_url = "https://innoida.utho.io"
region = "in-noida-1"

print("Testing OLD Utho credentials...")
print(f"Bucket: {bucket_name}\n")

s3 = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    region_name=region,
    config=Config(signature_version='s3v4')
)

test_content = b"test"
test_key = "test.txt"

try:
    s3.put_object(Bucket=bucket_name, Key=test_key, Body=test_content, ACL='public-read')
    print("[OK] Upload successful!")
    s3.delete_object(Bucket=bucket_name, Key=test_key)
    print("[OK] Credentials WORKING!")
except ClientError as e:
    print(f"[FAIL] {e}")
    print("\nCredentials NOT working - use the NEW ones instead")
