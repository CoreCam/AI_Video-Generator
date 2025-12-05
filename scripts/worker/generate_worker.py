"""
Background worker for processing video generation jobs.
Clean extraction focusing on core worker functionality.
"""
import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class GenerationWorker:
    """Worker for processing video generation jobs with multiple AI providers."""
    
    def __init__(self, redis_client=None, db_client=None, video_client=None):
        self.redis_client = redis_client
        self.db_client = db_client
        self.video_client = video_client
        self.is_running = False
        self.worker_id = str(uuid.uuid4())
        self.job_queue = []  # Mock queue for when Redis is not available
        
    async def start_worker(self):
        """Start the worker to process jobs from the queue."""
        self.is_running = True
        print(f"🚀 Starting worker {self.worker_id}")
        
        while self.is_running:
            try:
                # Check for new jobs in the queue
                job = await self._get_next_job()
                
                if job:
                    await self._process_job(job)
                else:
                    # No jobs available, wait before checking again
                    await asyncio.sleep(5)
                    
            except Exception as e:
                print(f"❌ Worker error: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def stop_worker(self):
        """Stop the worker gracefully."""
        print(f"🛑 Stopping worker {self.worker_id}")
        self.is_running = False
    
    async def queue_generation_job(
        self,
        job_type: str,
        persona_ids: list,
        prompt: str,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Queue a new generation job.
        
        Args:
            job_type: Type of job ('video')
            persona_ids: List of persona IDs to use
            prompt: Generation prompt
            parameters: Additional parameters
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        job_data = {
            "id": job_id,
            "type": job_type,
            "persona_ids": persona_ids,
            "prompt": prompt,
            "parameters": parameters,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
            "worker_id": None,
            "progress": 0,
            "current_step": "queued",
            "result_url": None,
            "error_message": None
        }
        
        # Add to database
        if self.db_client:
            try:
                await self.db_client.create_generation_job(job_data)
                print(f"✅ Job {job_id} saved to database")
            except Exception as e:
                print(f"⚠️ Failed to save job to database: {e}")
        
        # Add to Redis queue or mock queue
        await self._add_to_queue(job_data)
        
        print(f"📋 Queued {job_type} generation job {job_id}")
        return job_id
    
    async def _get_next_job(self) -> Optional[Dict[str, Any]]:
        """Get the next job from the queue."""
        try:
            if self.redis_client:
                # Try to get job from Redis
                job_data = await self._get_from_redis_queue()
                if job_data:
                    return job_data
            
            # Fallback to mock queue
            if self.job_queue:
                return self.job_queue.pop(0)
                
            return None
            
        except Exception as e:
            print(f"⚠️ Error getting next job: {e}")
            return None
    
    async def _process_job(self, job: Dict[str, Any]):
        """Process a generation job."""
        job_id = job["id"]
        job_type = job["type"]
        
        print(f"🔄 Processing {job_type} job {job_id}")
        
        try:
            # Update job status
            await self._update_job_status(job_id, "processing", 10, "Starting generation")
            
            if job_type == "video":
                result = await self._process_video_job(job)
            else:
                raise ValueError(f"Unknown job type: {job_type}")
            
            # Update job with results
            if result.get("success"):
                await self._update_job_status(
                    job_id, "completed", 100, "Generation completed",
                    result_url=result.get("video_url"),
                    result_data=result
                )
                print(f"✅ Job {job_id} completed successfully")
            else:
                await self._update_job_status(
                    job_id, "failed", 0, "Generation failed",
                    error_message=result.get("error", "Unknown error")
                )
                print(f"❌ Job {job_id} failed: {result.get('error')}")
            
        except Exception as e:
            print(f"❌ Error processing job {job_id}: {e}")
            await self._update_job_status(
                job_id, "failed", 0, "Processing error",
                error_message=str(e)
            )
    
    async def _process_video_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Process a video generation job."""
        if not self.video_client:
            from ..video_clients import UnifiedVideoClient
            self.video_client = UnifiedVideoClient()
        
        # Prepare script from job data
        script = {
            "prompt": job["prompt"],
            "scenes": [{
                "description": job["prompt"],
                "duration": job["parameters"].get("duration", 30)
            }],
            "duration": job["parameters"].get("duration", 30),
            "persona_ids": job["persona_ids"]
        }
        
        # Update progress
        await self._update_job_status(job["id"], "processing", 30, "Generating video")
        
        # Generate video
        result = await self.video_client.generate_video(
            script=script,
            provider=job["parameters"].get("provider"),
            quality=job["parameters"].get("quality", "hd"),
            **job["parameters"]
        )
        
        # Update progress
        await self._update_job_status(job["id"], "processing", 90, "Finalizing")
        
        return result
    
    async def _add_to_queue(self, job_data: Dict[str, Any]):
        """Add job to the queue."""
        try:
            if self.redis_client:
                # Add to Redis queue
                await self.redis_client.lpush("generation_queue", json.dumps(job_data))
                print(f"📋 Added job {job_data['id']} to Redis queue")
            else:
                # Add to mock queue
                self.job_queue.append(job_data)
                print(f"📋 Added job {job_data['id']} to mock queue")
        except Exception as e:
            print(f"⚠️ Failed to add job to queue: {e}")
            # Fallback to mock queue
            self.job_queue.append(job_data)
    
    async def _get_from_redis_queue(self) -> Optional[Dict[str, Any]]:
        """Get job from Redis queue."""
        try:
            if self.redis_client:
                job_json = await self.redis_client.brpop("generation_queue", timeout=1)
                if job_json:
                    return json.loads(job_json[1])
            return None
        except Exception as e:
            print(f"⚠️ Error getting job from Redis: {e}")
            return None
    
    async def _update_job_status(
        self,
        job_id: str,
        status: str,
        progress: int,
        current_step: str,
        result_url: str = None,
        result_data: Dict[str, Any] = None,
        error_message: str = None
    ):
        """Update job status in database."""
        try:
            updates = {
                "status": status,
                "progress": progress,
                "current_step": current_step,
                "updated_at": datetime.utcnow().isoformat(),
                "worker_id": self.worker_id
            }
            
            if result_url:
                updates["result_url"] = result_url
            
            if result_data:
                updates["result_data"] = result_data
            
            if error_message:
                updates["error_message"] = error_message
            
            if self.db_client:
                await self.db_client.update_generation_job(job_id, updates)
            else:
                print(f"Mock: Updated job {job_id} status to {status}")
                
        except Exception as e:
            print(f"⚠️ Failed to update job status: {e}")
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific job."""
        try:
            if self.db_client:
                return await self.db_client.get_generation_job(job_id)
            else:
                # Mock response
                return {
                    "id": job_id,
                    "status": "completed",
                    "progress": 100,
                    "current_step": "completed",
                    "result_url": f"https://mock-results.com/{job_id}.mp4"
                }
        except Exception as e:
            print(f"⚠️ Failed to get job status: {e}")
            return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a queued or processing job."""
        try:
            if self.db_client:
                await self.db_client.update_generation_job(job_id, {
                    "status": "cancelled",
                    "current_step": "cancelled",
                    "updated_at": datetime.utcnow().isoformat()
                })
                return True
            else:
                print(f"Mock: Cancelled job {job_id}")
                return True
        except Exception as e:
            print(f"⚠️ Failed to cancel job: {e}")
            return False
    
    async def list_jobs(
        self,
        status: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List jobs with optional status filtering."""
        try:
            if self.db_client:
                # This would need to be implemented in the database client
                # For now, return empty list
                return []
            else:
                # Mock response
                return [
                    {
                        "id": "mock_job_1",
                        "type": "video",
                        "status": "completed",
                        "progress": 100,
                        "created_at": datetime.utcnow().isoformat()
                    }
                ]
        except Exception as e:
            print(f"⚠️ Failed to list jobs: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get worker status."""
        return {
            "worker_id": self.worker_id,
            "is_running": self.is_running,
            "redis_client": self.redis_client is not None,
            "db_client": self.db_client is not None,
            "video_client": self.video_client is not None,
            "mock_queue_size": len(self.job_queue)
        }