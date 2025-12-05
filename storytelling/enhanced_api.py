"""
Enhanced Storytelling API endpoints with multi-persona support and Gemini integration.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from ..storytelling.enhanced_cinegen import EnhancedCinegenAgent, VideoProductionBreakdown


# Enhanced Pydantic models
class EnhancedStorySessionCreate(BaseModel):
    persona_ids: List[str]  # Multiple personas as main characters
    story_theme: Optional[str] = None
    user_input: Optional[str] = None
    target_duration: int = 60  # Target total video duration in seconds

class SimplePromptRequest(BaseModel):
    user_prompt: str  # Simple user input
    scene_number: Optional[int] = None
    duration_seconds: Optional[int] = None  # Custom scene duration

class VideoGenerationFromBreakdown(BaseModel):
    scene_number: int
    quality: str = "hd"
    duration: int = 15


def create_enhanced_storytelling_router(
    vector_store=None,
    db_client=None,
    video_client=None
) -> APIRouter:
    """Create enhanced storytelling API router with multi-persona support."""
    
    router = APIRouter(prefix="/cinegen", tags=["enhanced-storytelling"])
    
    # Initialize enhanced agent
    enhanced_agent = EnhancedCinegenAgent(
        vector_store=vector_store,
        db_client=db_client
    )
    
    @router.post("/sessions")
    async def create_enhanced_story_session(request: EnhancedStorySessionCreate):
        """Start a new story session with multiple personas."""
        try:
            story_id = await enhanced_agent.start_story_session(
                persona_ids=request.persona_ids,
                story_theme=request.story_theme,
                user_input=request.user_input,
                target_duration=request.target_duration
            )
            
            return {
                "story_id": story_id,
                "status": "active",
                "message": "Enhanced story session started",
                "personas_loaded": len(enhanced_agent.active_personas),
                "character_names": [p.get('name', 'Unknown') for p in enhanced_agent.active_personas.values()],
                "theme": request.story_theme
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/sessions/{story_id}/process")
    async def process_user_prompt(story_id: str, request: SimplePromptRequest):
        """Process a simple user prompt into professional video production breakdown."""
        try:
            if enhanced_agent.current_story_id != story_id:
                # In a real implementation, would restore session state
                enhanced_agent.current_story_id = story_id
            
            # The heavy lifting happens here
            breakdown = await enhanced_agent.process_user_prompt(
                user_prompt=request.user_prompt,
                scene_number=request.scene_number,
                duration_seconds=request.duration_seconds
            )
            
            # Format for display
            formatted_output = enhanced_agent.format_breakdown_output(
                breakdown, 
                request.scene_number or len(enhanced_agent.scenes)
            )
            
            return {
                "breakdown": breakdown.to_dict(),
                "formatted_output": formatted_output,
                "story_id": story_id,
                "scene_number": request.scene_number or len(enhanced_agent.scenes),
                "ready_for_video": True,
                "personas_involved": breakdown.personas_involved
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/sessions/{story_id}/breakdown/{scene_number}")
    async def get_scene_breakdown(story_id: str, scene_number: int):
        """Get a specific scene breakdown."""
        try:
            if enhanced_agent.current_story_id != story_id:
                raise HTTPException(status_code=404, detail="Story session not found")
            
            if scene_number > len(enhanced_agent.scenes) or scene_number < 1:
                raise HTTPException(status_code=404, detail="Scene not found")
            
            breakdown = enhanced_agent.scenes[scene_number - 1]
            formatted_output = enhanced_agent.format_breakdown_output(breakdown, scene_number)
            video_script = await enhanced_agent.get_video_generation_script(breakdown)
            
            return {
                "breakdown": breakdown.to_dict(),
                "formatted_output": formatted_output,
                "video_script": video_script,
                "scene_number": scene_number
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/sessions/{story_id}/breakdown/{scene_number}/generate-video")
    async def generate_video_from_breakdown(
        story_id: str, 
        scene_number: int, 
        request: VideoGenerationFromBreakdown
    ):
        """Generate video from a professional breakdown."""
        try:
            if not video_client:
                raise HTTPException(status_code=503, detail="Video generation not available")
            
            if enhanced_agent.current_story_id != story_id:
                raise HTTPException(status_code=404, detail="Story session not found")
            
            if scene_number > len(enhanced_agent.scenes) or scene_number < 1:
                raise HTTPException(status_code=404, detail="Scene not found")
            
            breakdown = enhanced_agent.scenes[scene_number - 1]
            
            # Get video generation script
            script = await enhanced_agent.get_video_generation_script(breakdown)
            script["quality"] = request.quality
            script["duration"] = request.duration
            
            # Generate video using SoRa Core
            result = await video_client.generate_video(script)
            
            return {
                "scene_number": scene_number,
                "story_id": story_id,
                "breakdown_used": breakdown.to_dict(),
                "video_generation": result,
                "script_used": script,
                "personas_involved": breakdown.personas_involved
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/sessions/{story_id}")
    async def get_enhanced_story_session(story_id: str):
        """Get enhanced story session details."""
        try:
            if enhanced_agent.current_story_id != story_id:
                raise HTTPException(status_code=404, detail="Story session not found")
            
            story_export = await enhanced_agent.export_story()
            return story_export
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/sessions/{story_id}/breakdowns")
    async def list_scene_breakdowns(story_id: str):
        """List all scene breakdowns in the story."""
        try:
            if enhanced_agent.current_story_id != story_id:
                raise HTTPException(status_code=404, detail="Story session not found")
            
            breakdowns = [scene.to_dict() for scene in enhanced_agent.scenes]
            
            return {
                "story_id": story_id,
                "breakdowns": breakdowns,
                "total_scenes": len(breakdowns),
                "personas_involved": list(enhanced_agent.active_personas.keys())
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/demo/prompts")
    async def get_demo_prompts():
        """Get example prompts for different scenarios."""
        return {
            "single_character": [
                "Someone walking through a park and having a moment of realization",
                "A person sitting in a coffee shop, writing in their journal",
                "Someone discovering something amazing in their backyard"
            ],
            "multi_character": [
                "Two friends meeting for lunch and sharing exciting news",
                "Three colleagues brainstorming in a creative workspace",
                "A group of friends exploring a new city together"
            ],
            "action_scenes": [
                "Two people running through the city streets",
                "Someone climbing a mountain with determination",
                "A group working together to solve an urgent problem"
            ],
            "emotional_moments": [
                "A heartfelt conversation between old friends",
                "Someone receiving life-changing news",
                "A moment of quiet reflection by the ocean"
            ]
        }
    
    @router.get("/sessions/{story_id}/timing")
    async def get_story_timing(story_id: str):
        """Get detailed timing information for the story."""
        try:
            if enhanced_agent.current_story_id != story_id:
                raise HTTPException(status_code=404, detail="Story session not found")
            
            timing_info = enhanced_agent.get_timing_info()
            return timing_info
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/status")
    async def get_enhanced_storytelling_status():
        """Get enhanced storytelling system status."""
        try:
            return {
                "enhanced_agent": enhanced_agent.get_status(),
                "gemini_ai_available": bool(enhanced_agent.gemini_model),
                "multi_persona_support": True,
                "professional_breakdown": True,
                "duration_awareness": True,
                "detailed_responses": True
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router