import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from typing import Optional
import uuid

load_dotenv()

class UthoStorage:
    def __init__(self):
        self.access_key = os.getenv("UTHO_ACCESS_KEY")
        self.secret_key = os.getenv("UTHO_SECRET_KEY")
        self.bucket_name = os.getenv("UTHO_BUCKET_NAME")
        self.endpoint_url = os.getenv("UTHO_ENDPOINT_URL")
        self.region = os.getenv("UTHO_REGION", "in-noida-1")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
            region_name=self.region,
            config=Config(signature_version='s3v4')
        )
    
    def upload_file(self, file_data, folder: str, filename: str) -> Optional[str]:
        """
        Upload file to Utho object storage
        
        Args:
            file_data: File content (bytes or file-like object)
            folder: Folder path in bucket (e.g., 'crew_documents/crew_id_123')
            filename: Name of the file
            
        Returns:
            Public URL of uploaded file or None if failed
        """
        try:
            object_key = f"{folder}/{filename}"
            
            # Read file content
            if hasattr(file_data, 'read'):
                content = file_data.read()
            else:
                content = file_data
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=content,
                ACL='public-read'
            )
            
            file_url = f"{self.endpoint_url}/{self.bucket_name}/{object_key}"
            return file_url
            
        except ClientError as e:
            print(f"Error uploading file to {folder}/{filename}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error uploading file: {e}")
            return None
    
    def upload_crew_document(self, file_data, crew_id: str, doc_type: str, filename: str) -> Optional[str]:
        """
        Upload crew registration documents
        
        Args:
            file_data: File content
            crew_id: Crew member ID
            doc_type: Type of document (drivers_license, dbs_certificate, etc.)
            filename: Original filename
            
        Returns:
            Public URL of uploaded file
        """
        try:
            folder = f"crew_documents/{crew_id}"
            unique_filename = f"{doc_type}_{uuid.uuid4().hex[:8]}_{filename}"
            url = self.upload_file(file_data, folder, unique_filename)
            print(f"✓ Uploaded {doc_type}: {url}")
            return url
        except Exception as e:
            print(f"✗ Failed to upload {doc_type}: {e}")
            return None
    
    def upload_job_photo(self, file_data, job_id: str, photo_type: str, filename: str) -> Optional[str]:
        """
        Upload job before/after photos
        
        Args:
            file_data: File content
            job_id: Job ID
            photo_type: 'before' or 'after'
            filename: Original filename
            
        Returns:
            Public URL of uploaded file
        """
        folder = f"job_photos/{job_id}/{photo_type}"
        unique_filename = f"{photo_type}_{uuid.uuid4().hex[:8]}_{filename}"
        return self.upload_file(file_data, folder, unique_filename)
    
    def upload_crew_profile_photo(self, file_data, crew_id: str, filename: str) -> Optional[str]:
        """
        Upload crew profile photo
        """
        folder = f"crew_profiles/{crew_id}"
        unique_filename = f"profile_{uuid.uuid4().hex[:8]}_{filename}"
        return self.upload_file(file_data, folder, unique_filename)
    
    def upload_invoice_pdf(self, file_data, invoice_number: str) -> Optional[str]:
        """
        Upload invoice PDF to Utho
        """
        folder = "invoices"
        filename = f"{invoice_number}.pdf"
        return self.upload_file(file_data, folder, filename)
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete file from storage
        
        Args:
            file_url: Full URL of the file
            
        Returns:
            True if deleted successfully
        """
        try:
            object_key = file_url.split(f"{self.bucket_name}/")[1]
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

# Singleton instance
storage = UthoStorage()
