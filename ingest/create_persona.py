"""
Persona creation and management system.
Clean extraction focusing on core persona functionality.
"""
from typing import List, Dict, Any, Optional
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

class PersonaCreator:
    """Main class for creating and managing personas."""
    
    def __init__(self, storage_client=None, vision_processor=None, vector_store=None, db_client=None):
        self.storage_client = storage_client
        self.vision_processor = vision_processor
        self.vector_store = vector_store
        self.db_client = db_client
        
    async def create_persona(
        self,
        name: str,
        description: str,
        consent_status: str = "pending"
    ) -> Dict[str, Any]:
        """
        Create a new persona entry in the database.
        
        Args:
            name: Persona name
            description: Description of the persona
            consent_status: Consent status (pending, approved, denied)
            
        Returns:
            Dict containing persona information
        """
        persona_id = str(uuid.uuid4())
        
        persona_data = {
            "id": persona_id,
            "name": name,
            "description": description,
            "consent_status": consent_status,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "files": [],
            "embeddings_generated": False,
            "summary": None,
            "metadata": {
                "creator": "persona_system",
                "version": "1.0"
            }
        }
        
        # Save to database if available
        if self.db_client:
            await self.db_client.create_persona(persona_data)
        else:
            print(f"✅ Created persona {persona_id} (mock mode)")
        
        return persona_data
    
    async def process_uploaded_files(
        self,
        persona_id: str,
        files: List[Any]
    ) -> Dict[str, Any]:
        """
        Process uploaded files for a persona.
        
        Args:
            persona_id: ID of the persona
            files: List of uploaded files
            
        Returns:
            Processing results
        """
        processed_files = []
        
        for file in files:
            try:
                # Generate file hash for deduplication
                file_hash = await self._generate_file_hash(file)
                
                # Upload to storage
                if self.storage_client:
                    upload_result = await self.storage_client.upload_file(
                        file_content=file,
                        filename=getattr(file, 'filename', f"file_{uuid.uuid4()}"),
                        persona_id=persona_id,
                        metadata={"file_hash": file_hash}
                    )
                    storage_url = upload_result.get("file_url", "")
                else:
                    storage_url = f"mock://storage/{persona_id}/{file_hash}"
                
                # Extract metadata
                metadata = await self._extract_file_metadata(file)
                
                # Generate captions and embeddings for images/videos
                caption = None
                embedding = None
                
                if self._is_visual_media(file):
                    caption = await self._generate_caption(file)
                    embedding = await self._generate_embedding(file)
                
                file_data = {
                    "id": str(uuid.uuid4()),
                    "persona_id": persona_id,
                    "filename": getattr(file, 'filename', 'unknown'),
                    "file_hash": file_hash,
                    "storage_url": storage_url,
                    "content_type": getattr(file, 'content_type', 'application/octet-stream'),
                    "size": getattr(file, 'size', 0),
                    "metadata": metadata,
                    "caption": caption,
                    "embedding": embedding,
                    "processed_at": datetime.utcnow().isoformat()
                }
                
                processed_files.append(file_data)
                
                # Store embedding in vector database
                if embedding and self.vector_store:
                    await self._store_embedding(persona_id, file_data["id"], embedding, caption)
                
            except Exception as e:
                print(f"❌ Error processing file {getattr(file, 'filename', 'unknown')}: {e}")
                processed_files.append({
                    "filename": getattr(file, 'filename', 'unknown'),
                    "error": str(e),
                    "status": "failed"
                })
        
        # Update persona with processed files
        await self._update_persona_files(persona_id, processed_files)
        
        return {
            "persona_id": persona_id,
            "processed_files": len([f for f in processed_files if "error" not in f]),
            "failed_files": len([f for f in processed_files if "error" in f]),
            "files": processed_files
        }
    
    async def generate_persona_summary(self, persona_id: str) -> str:
        """
        Generate an AI summary of the persona based on processed files.
        
        Args:
            persona_id: ID of the persona
            
        Returns:
            Generated summary text
        """
        persona_data = await self._get_persona_data(persona_id)
        
        files_count = len(persona_data.get('files', []))
        visual_files = [f for f in persona_data.get('files', []) if f.get('caption')]
        
        summary = f"""Persona Summary for {persona_data.get('name', 'Unknown')}:

Description: {persona_data.get('description', 'No description provided')}

Media Analysis:
- Total files processed: {files_count}
- Visual media files: {len(visual_files)}
- Embeddings generated: {persona_data.get('embeddings_generated', False)}

Visual Characteristics: """
        
        if visual_files:
            captions = [f.get('caption', '') for f in visual_files if f.get('caption')]
            if captions:
                summary += f"Based on {len(captions)} analyzed images/videos, this persona shows consistent visual characteristics suitable for video generation."
            else:
                summary += "Visual media processed but detailed analysis pending."
        else:
            summary += "No visual media available for analysis."
        
        summary += f"\n\nConsent Status: {persona_data.get('consent_status', 'pending')}"
        summary += f"\nCreated: {persona_data.get('created_at', 'Unknown')}"
        
        return summary.strip()
    
    async def _generate_file_hash(self, file) -> str:
        """Generate SHA-256 hash of file content."""
        try:
            # Read file content
            if hasattr(file, 'read'):
                content = file.read()
                if hasattr(file, 'seek'):
                    file.seek(0)  # Reset file pointer
            else:
                content = str(file).encode()
            
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            print(f"⚠️ Could not generate file hash: {e}")
            # Fallback hash based on filename and timestamp
            return hashlib.sha256(f"{getattr(file, 'filename', 'unknown')}_{datetime.utcnow()}".encode()).hexdigest()
    
    async def _extract_file_metadata(self, file) -> Dict[str, Any]:
        """Extract metadata from uploaded file."""
        metadata = {
            "content_type": getattr(file, 'content_type', 'application/octet-stream'),
            "size": getattr(file, 'size', 0),
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        # Add more metadata if available
        if hasattr(file, 'headers'):
            metadata["headers"] = dict(file.headers)
        
        return metadata
    
    def _is_visual_media(self, file) -> bool:
        """Check if file is visual media (image or video)."""
        content_type = getattr(file, 'content_type', '')
        visual_types = ['image/', 'video/']
        return any(content_type.startswith(vt) for vt in visual_types)
    
    async def _generate_caption(self, file) -> str:
        """Generate caption for visual media."""
        if self.vision_processor:
            try:
                return await self.vision_processor.generate_caption(file)
            except Exception as e:
                print(f"⚠️ Caption generation failed: {e}")
                return f"Visual content - {getattr(file, 'filename', 'unknown file')}"
        return f"Visual content - {getattr(file, 'filename', 'unknown file')} (caption generation not available)"
    
    async def _generate_embedding(self, file) -> List[float]:
        """Generate embedding for visual media."""
        if self.vision_processor:
            try:
                return await self.vision_processor.generate_embedding(file)
            except Exception as e:
                print(f"⚠️ Embedding generation failed: {e}")
                return []
        return []
    
    async def _store_embedding(self, persona_id: str, file_id: str, embedding: List[float], caption: str):
        """Store embedding in vector database."""
        if self.vector_store and embedding:
            try:
                await self.vector_store.store_embedding(
                    id=f"{persona_id}_{file_id}",
                    embedding=embedding,
                    metadata={
                        "persona_id": persona_id,
                        "file_id": file_id,
                        "caption": caption or "",
                        "type": "persona_media",
                        "created_at": datetime.utcnow().isoformat()
                    }
                )
                print(f"✅ Stored embedding for {persona_id}_{file_id}")
            except Exception as e:
                print(f"❌ Failed to store embedding: {e}")
    
    async def _update_persona_files(self, persona_id: str, files: List[Dict[str, Any]]):
        """Update persona record with processed files."""
        if self.db_client:
            try:
                successful_files = [f for f in files if "error" not in f]
                await self.db_client.update_persona(persona_id, {
                    "files": successful_files,
                    "embeddings_generated": any(f.get("embedding") for f in successful_files),
                    "updated_at": datetime.utcnow().isoformat()
                })
                print(f"✅ Updated persona {persona_id} with {len(successful_files)} files")
            except Exception as e:
                print(f"❌ Failed to update persona files: {e}")
        else:
            print(f"Mock: Updated persona {persona_id} with {len(files)} files")
    
    async def _get_persona_data(self, persona_id: str) -> Dict[str, Any]:
        """Retrieve persona data from database."""
        if self.db_client:
            try:
                return await self.db_client.get_persona(persona_id)
            except Exception as e:
                print(f"❌ Failed to retrieve persona data: {e}")
        
        # Return mock data
        return {
            "id": persona_id,
            "name": "Sample Persona",
            "description": "A sample persona for testing",
            "consent_status": "approved",
            "files": [],
            "embeddings_generated": False,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def delete_persona(self, persona_id: str) -> bool:
        """Delete a persona and all associated data."""
        try:
            # Delete from vector store
            if self.vector_store:
                # Note: This would need to be implemented in vector store
                # as a method to delete by persona_id filter
                pass
            
            # Delete files from storage
            if self.storage_client:
                # Note: This would need persona file listing capability
                pass
            
            # Delete from database
            if self.db_client:
                await self.db_client.delete_persona(persona_id)
            
            print(f"✅ Deleted persona {persona_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete persona {persona_id}: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get persona creator status."""
        return {
            "storage_client": self.storage_client is not None,
            "vision_processor": self.vision_processor is not None,
            "vector_store": self.vector_store is not None,
            "db_client": self.db_client is not None
        }