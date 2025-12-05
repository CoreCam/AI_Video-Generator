"""
File upload and storage management.
Clean extraction supporting local, S3, and Supabase storage.
"""
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, BinaryIO
import mimetypes

class StorageClient:
    """Client for managing file uploads and storage."""
    
    def __init__(self, storage_type: str = "local", config: Dict[str, Any] = None):
        self.storage_type = storage_type
        self.config = config or {}
        self.client = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage client based on type."""
        if self.storage_type == "s3":
            try:
                import boto3
                self.client = boto3.client(
                    's3',
                    aws_access_key_id=self.config.get("access_key"),
                    aws_secret_access_key=self.config.get("secret_key"),
                    region_name=self.config.get("region", "us-east-1")
                )
                print(f"✅ S3 storage client initialized")
            except ImportError:
                print("⚠️ boto3 not installed - falling back to local storage")
                self.storage_type = "local"
            except Exception as e:
                print(f"⚠️ S3 initialization failed: {e} - falling back to local storage")
                self.storage_type = "local"
        
        elif self.storage_type == "supabase":
            try:
                from supabase import create_client
                self.client = create_client(
                    self.config.get("url"),
                    self.config.get("key")
                )
                print(f"✅ Supabase storage client initialized")
            except ImportError:
                print("⚠️ Supabase client not installed - falling back to local storage")
                self.storage_type = "local"
            except Exception as e:
                print(f"⚠️ Supabase initialization failed: {e} - falling back to local storage")
                self.storage_type = "local"
        
        # Set up local storage directory
        if self.storage_type == "local":
            self.local_dir = Path(self.config.get("upload_dir", "data/uploads"))
            self.local_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Local storage initialized at {self.local_dir}")
    
    async def upload_file(
        self,
        file_content: BinaryIO,
        filename: str,
        persona_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to storage.
        
        Args:
            file_content: File content as binary stream
            filename: Original filename
            persona_id: Optional persona ID for organization
            metadata: Additional metadata
            
        Returns:
            Upload result with file URL and metadata
        """
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix
            stored_filename = f"{file_id}{file_extension}"
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or "application/octet-stream"
            
            # Build storage path
            if persona_id:
                storage_path = f"personas/{persona_id}/{stored_filename}"
            else:
                storage_path = f"uploads/{stored_filename}"
            
            # Upload based on storage type
            if self.storage_type == "s3":
                file_url = await self._upload_to_s3(
                    file_content, storage_path, content_type, metadata
                )
            elif self.storage_type == "supabase":
                file_url = await self._upload_to_supabase(
                    file_content, storage_path, metadata
                )
            else:  # local
                file_url = await self._upload_to_local(
                    file_content, storage_path, metadata
                )
            
            return {
                "success": True,
                "file_id": file_id,
                "file_url": file_url,
                "filename": filename,
                "stored_filename": stored_filename,
                "storage_path": storage_path,
                "content_type": content_type,
                "storage_type": self.storage_type,
                "metadata": metadata or {}
            }
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _upload_to_s3(
        self,
        file_content: BinaryIO,
        storage_path: str,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Upload file to S3."""
        bucket = self.config.get("bucket", "sora-core")
        
        # Prepare S3 metadata
        s3_metadata = {}
        if metadata:
            for key, value in metadata.items():
                s3_metadata[f"x-amz-meta-{key}"] = str(value)
        
        # Upload to S3
        self.client.upload_fileobj(
            file_content,
            bucket,
            storage_path,
            ExtraArgs={
                "ContentType": content_type,
                "Metadata": s3_metadata
            }
        )
        
        # Return public URL
        region = self.config.get("region", "us-east-1")
        return f"https://{bucket}.s3.{region}.amazonaws.com/{storage_path}"
    
    async def _upload_to_supabase(
        self,
        file_content: BinaryIO,
        storage_path: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Upload file to Supabase Storage."""
        bucket = self.config.get("bucket", "uploads")
        
        # Upload to Supabase
        result = self.client.storage.from_(bucket).upload(
            storage_path,
            file_content.read(),
            file_options={"metadata": metadata or {}}
        )
        
        # Get public URL
        url_result = self.client.storage.from_(bucket).get_public_url(storage_path)
        return url_result
    
    async def _upload_to_local(
        self,
        file_content: BinaryIO,
        storage_path: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Upload file to local storage."""
        # Create directory structure
        full_path = self.local_dir / storage_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(full_path, "wb") as f:
            f.write(file_content.read())
        
        # Save metadata if provided
        if metadata:
            metadata_path = full_path.with_suffix(full_path.suffix + ".meta")
            import json
            with open(metadata_path, "w") as f:
                json.dump(metadata, f)
        
        # Return local URL
        return f"file://{full_path.absolute()}"
    
    async def delete_file(self, storage_path: str) -> bool:
        """Delete a file from storage."""
        try:
            if self.storage_type == "s3":
                bucket = self.config.get("bucket", "sora-core")
                self.client.delete_object(Bucket=bucket, Key=storage_path)
            
            elif self.storage_type == "supabase":
                bucket = self.config.get("bucket", "uploads")
                self.client.storage.from_(bucket).remove([storage_path])
            
            else:  # local
                full_path = self.local_dir / storage_path
                if full_path.exists():
                    full_path.unlink()
                    
                # Remove metadata file if exists
                metadata_path = full_path.with_suffix(full_path.suffix + ".meta")
                if metadata_path.exists():
                    metadata_path.unlink()
            
            print(f"✅ Deleted file: {storage_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting file {storage_path}: {e}")
            return False
    
    async def get_file_info(self, storage_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a stored file."""
        try:
            if self.storage_type == "s3":
                bucket = self.config.get("bucket", "sora-core")
                response = self.client.head_object(Bucket=bucket, Key=storage_path)
                
                return {
                    "storage_path": storage_path,
                    "size": response.get("ContentLength"),
                    "content_type": response.get("ContentType"),
                    "last_modified": response.get("LastModified"),
                    "metadata": response.get("Metadata", {})
                }
            
            elif self.storage_type == "supabase":
                bucket = self.config.get("bucket", "uploads")
                file_list = self.client.storage.from_(bucket).list(
                    path=os.path.dirname(storage_path),
                    search=os.path.basename(storage_path)
                )
                
                if file_list and len(file_list) > 0:
                    file_info = file_list[0]
                    return {
                        "storage_path": storage_path,
                        "size": file_info.get("metadata", {}).get("size"),
                        "content_type": file_info.get("metadata", {}).get("mimetype"),
                        "last_modified": file_info.get("updated_at"),
                        "metadata": file_info.get("metadata", {})
                    }
            
            else:  # local
                full_path = self.local_dir / storage_path
                if full_path.exists():
                    stat = full_path.stat()
                    metadata = {}
                    
                    # Load metadata if available
                    metadata_path = full_path.with_suffix(full_path.suffix + ".meta")
                    if metadata_path.exists():
                        import json
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                    
                    return {
                        "storage_path": storage_path,
                        "size": stat.st_size,
                        "content_type": mimetypes.guess_type(str(full_path))[0],
                        "last_modified": stat.st_mtime,
                        "metadata": metadata
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting file info for {storage_path}: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get storage client status."""
        return {
            "storage_type": self.storage_type,
            "client_available": self.client is not None,
            "local_dir": str(self.local_dir) if hasattr(self, 'local_dir') else None,
            "config_keys": list(self.config.keys()) if self.config else []
        }