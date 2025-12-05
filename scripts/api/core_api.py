"""
Core API for SoRa video generation platform.
Clean FastAPI implementation without UI dependencies.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid

# Pydantic models for request/response
class PersonaCreate(BaseModel):
    name: str
    description: str
    consent_status: str = "pending"

class VideoGenerationRequest(BaseModel):
    persona_ids: List[str]
    prompt: str
    provider: Optional[str] = None
    quality: str = "hd"
    duration: int = 30

class JobStatus(BaseModel):
    id: str
    status: str
    progress: int
    current_step: str
    result_url: Optional[str] = None
    error_message: Optional[str] = None

def create_core_api(
    storage_client=None,
    db_client=None,
    vector_store=None,
    video_client=None,
    worker=None,
    vision_processor=None
) -> FastAPI:
    """Create the core API with dependency injection."""
    
    app = FastAPI(
        title="SoRa Core API",
        description="Core video generation API without UI dependencies",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize components if not provided
    if not storage_client:
        from ..storage import StorageClient
        storage_client = StorageClient()
    
    if not db_client:
        from ..storage import DatabaseClient
        db_client = DatabaseClient()
    
    if not vector_store:
        from ..storage import VectorStore
        vector_store = VectorStore()
    
    if not video_client:
        from ..video_clients import UnifiedVideoClient
        video_client = UnifiedVideoClient()
    
    if not worker:
        from ..worker import GenerationWorker
        worker = GenerationWorker(
            db_client=db_client,
            video_client=video_client
        )
    
    if not vision_processor:
        from ..ingest import VisionProcessor
        vision_processor = VisionProcessor()
    
    # Include enhanced storytelling router
    try:
        from ..storytelling.enhanced_api import create_enhanced_storytelling_router
        enhanced_router = create_enhanced_storytelling_router(
            vector_store=vector_store,
            db_client=db_client,
            video_client=video_client
        )
        app.include_router(enhanced_router)
        print("✅ Enhanced CINEGEN API endpoints included")
    except ImportError as e:
        print(f"⚠️ Enhanced CINEGEN API not available: {e}")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "components": {
                "storage": storage_client.get_status(),
                "database": db_client.get_status(),
                "vector_store": vector_store.get_status(),
                "video_client": video_client.get_status(),
                "worker": worker.get_status(),
                "vision": vision_processor.get_status()
            }
        }
    
    # Persona management endpoints
    @app.post("/personas", response_model=Dict[str, Any])
    async def create_persona(persona: PersonaCreate):
        """Create a new persona."""
        try:
            from ..ingest import PersonaCreator
            creator = PersonaCreator(
                storage_client=storage_client,
                vision_processor=vision_processor,
                vector_store=vector_store,
                db_client=db_client
            )
            
            result = await creator.create_persona(
                name=persona.name,
                description=persona.description,
                consent_status=persona.consent_status
            )
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/personas/{persona_id}")
    async def get_persona(persona_id: str):
        """Get persona by ID."""
        try:
            persona = await db_client.get_persona(persona_id)
            if not persona:
                raise HTTPException(status_code=404, detail="Persona not found")
            return persona
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/personas")
    async def list_personas(
        limit: int = 50,
        offset: int = 0,
        consent_status: Optional[str] = None
    ):
        """List personas with optional filtering."""
        try:
            personas = await db_client.list_personas(
                limit=limit,
                offset=offset,
                consent_status=consent_status
            )
            return {"personas": personas, "count": len(personas)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/personas/{persona_id}/upload")
    async def upload_persona_files(
        persona_id: str,
        files: List[UploadFile] = File(...)
    ):
        """Upload files for a persona."""
        try:
            from ..ingest import PersonaCreator
            creator = PersonaCreator(
                storage_client=storage_client,
                vision_processor=vision_processor,
                vector_store=vector_store,
                db_client=db_client
            )
            
            result = await creator.process_uploaded_files(persona_id, files)
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/personas/{persona_id}")
    async def delete_persona(persona_id: str):
        """Delete a persona."""
        try:
            from ..ingest import PersonaCreator
            creator = PersonaCreator(
                storage_client=storage_client,
                vision_processor=vision_processor,
                vector_store=vector_store,
                db_client=db_client
            )
            
            success = await creator.delete_persona(persona_id)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to delete persona")
            
            return {"message": "Persona deleted successfully"}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Video generation endpoints
    @app.post("/generate/video")
    async def generate_video(request: VideoGenerationRequest):
        """Generate a video using the specified personas and prompt."""
        try:
            job_id = await worker.queue_generation_job(
                job_type="video",
                persona_ids=request.persona_ids,
                prompt=request.prompt,
                parameters={
                    "provider": request.provider,
                    "quality": request.quality,
                    "duration": request.duration
                }
            )
            
            return {
                "job_id": job_id,
                "status": "queued",
                "message": "Video generation job queued successfully"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/generate/jobs/{job_id}")
    async def get_job_status(job_id: str):
        """Get the status of a generation job."""
        try:
            status = await worker.get_job_status(job_id)
            if not status:
                raise HTTPException(status_code=404, detail="Job not found")
            return status
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/generate/jobs/{job_id}")
    async def cancel_job(job_id: str):
        """Cancel a generation job."""
        try:
            success = await worker.cancel_job(job_id)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to cancel job")
            
            return {"message": "Job cancelled successfully"}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/generate/jobs")
    async def list_jobs(
        status: Optional[str] = None,
        limit: int = 50
    ):
        """List generation jobs."""
        try:
            jobs = await worker.list_jobs(status=status, limit=limit)
            return {"jobs": jobs, "count": len(jobs)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Video client management
    @app.get("/providers")
    async def get_providers():
        """Get available video generation providers."""
        try:
            providers = video_client.get_available_providers()
            return {"providers": providers}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/validate/script")
    async def validate_script(script: Dict[str, Any]):
        """Validate a script for video generation."""
        try:
            validation = await video_client.validate_script(script)
            return validation
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Vector search endpoints
    @app.post("/search/similar")
    async def search_similar_personas(
        query_embedding: List[float],
        limit: int = 10
    ):
        """Search for similar personas using vector similarity."""
        try:
            results = await vector_store.search_similar(
                query_embedding=query_embedding,
                limit=limit
            )
            return {"results": results, "count": len(results)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

# Convenience function to create app with default settings
def create_app() -> FastAPI:
    """Create app with default configuration."""
    return create_core_api()