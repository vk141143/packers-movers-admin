import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

access_key = "6RGuMfqhlOH40CvWES3PQ5K7mBipwNjI1ZFn"
secret_key = "wUjgzrLViRPA4maNOQ3X8CDhIfYvdk7oZe65"
bucket_name = "mybucket6utholiftaway1"
endpoint_url = "https://innoida.utho.io"
region = "ap-south-1"

print("Testing NEW Utho credentials...")
print(f"Bucket: {bucket_name}")
print(f"Endpoint: {endpoint_url}\n")

s3 = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    region_name=region,
    config=Config(signature_version='s3v4')
)

# Test upload
test_content = b"test file"
test_key = "test_upload.txt"

try:
    s3.put_object(Bucket=bucket_name, Key=test_key, Body=test_content, ACL='public-read')
    print("[OK] Upload with ACL successful!")
    
    s3.delete_object(Bucket=bucket_name, Key=test_key)
    print("[OK] Delete successful!")
    print("\nCredentials are WORKING!")
    
except ClientError as e:
    print(f"[FAIL] {e}")
    print("\nCredentials NOT working")
