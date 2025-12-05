"""
Personal AI Avatar Video Generation System
Transform text prompts into videos starring YOU using your embedded persona
"""
import asyncio
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from ingest.create_persona import PersonaCreator
from video_clients.velo_client import VeloClient
from storytelling.enhanced_cinegen import EnhancedCinegenAgent

class PersonalAvatarGenerator:
    """Generate videos starring YOU using AI video generation"""
    
    def __init__(self, persona_id: str = None):
        self.persona_id = persona_id
        self.velo_client = VeloClient()
        self.cinegen_agent = EnhancedCinegenAgent()
        self.persona_creator = PersonaCreator()
        
        # Emotion mapping from your videos
        self.emotions = {
            "angry": "expressing anger, intense emotions, dramatic tension",
            "inspired": "showing excitement, enthusiasm, breakthrough moments", 
            "neutral": "calm, natural expression, everyday scenarios",
            "reflective": "thoughtful, contemplative, introspective moments",
            "relief": "satisfaction, accomplishment, peaceful resolution"
        }
    
    async def generate_avatar_video(
        self, 
        scenario: str, 
        emotion: str = "neutral",
        duration: int = 30,
        style: str = "cinematic"
    ) -> Dict[str, Any]:
        """
        Generate video of YOU in any scenario
        
        Args:
            scenario: What you want to do (e.g., "flying through clouds")
            emotion: Which emotional state to use
            duration: Video length in seconds
            style: Visual style (cinematic, realistic, dramatic, etc.)
            
        Returns:
            Generated video information
        """
        
        print(f"🎬 Generating Avatar Video:")
        print(f"   Scenario: {scenario}")
        print(f"   Emotion: {emotion}")
        print(f"   Duration: {duration}s")
        print(f"   Style: {style}")
        
        try:
            # Step 1: Create enhanced prompt with persona integration
            enhanced_prompt = await self._create_persona_prompt(scenario, emotion, style)
            print(f"📝 Enhanced prompt created")
            
            # Step 2: Generate professional breakdown via CINEGEN
            breakdown = await self.cinegen_agent.process_user_prompt(
                enhanced_prompt,
                scene_number=1,
                duration_seconds=duration
            )
            print(f"📋 Professional breakdown generated")
            
            # Step 3: Extract video generation script
            video_script = await self.cinegen_agent.get_video_generation_script(breakdown)
            print(f"🎯 Video script prepared")
            
            # Step 4: Generate video using Velo 3.1
            async with self.velo_client as velo:
                video_result = await velo.generate_video(
                    script=video_script,
                    duration=duration,
                    style=style,
                    quality="high"
                )
            
            if video_result.get("success"):
                print(f"✅ Video generated successfully!")
                return {
                    "success": True,
                    "video_url": video_result.get("video_url"),
                    "scenario": scenario,
                    "emotion": emotion,
                    "duration": duration,
                    "breakdown": breakdown,
                    "script": video_script,
                    "persona_id": self.persona_id
                }
            else:
                print(f"❌ Video generation failed: {video_result.get('error')}")
                return {"success": False, "error": video_result.get("error")}
                
        except Exception as e:
            print(f"❌ Avatar generation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_persona_prompt(self, scenario: str, emotion: str, style: str) -> str:
        """Create enhanced prompt that includes persona information"""
        
        # Get emotion description
        emotion_desc = self.emotions.get(emotion, "natural expression")
        
        # Get persona information (if available)
        persona_info = "Person with authentic mannerisms and natural appearance"
        if self.persona_id:
            try:
                persona_data = await self.persona_creator._get_persona_data(self.persona_id)
                persona_info = f"{persona_data.get('name', 'Person')}, {persona_data.get('description', 'authentic person')}"
            except:
                pass  # Use default if persona lookup fails
        
        # Construct enhanced prompt
        enhanced_prompt = f"""
        {persona_info} {scenario}.
        
        Emotional state: {emotion_desc}
        Visual style: {style}
        
        Important: This should feature the specific person with their recognizable appearance, 
        facial features, and mannerisms as captured in their video embeddings. The person should 
        be clearly identifiable as the same individual across all generated content.
        
        Technical requirements:
        - High-quality realistic rendering
        - Consistent character appearance 
        - Smooth, natural movement
        - Appropriate lighting and cinematography
        - {emotion} emotional expression throughout
        """
        
        return enhanced_prompt.strip()
    
    async def quick_generate(self, prompt: str) -> Dict[str, Any]:
        """Quick generation with smart defaults"""
        
        # Auto-detect emotion from prompt
        emotion = self._detect_emotion_from_prompt(prompt)
        
        # Auto-set duration based on complexity
        duration = 15 if len(prompt.split()) < 10 else 30
        
        return await self.generate_avatar_video(
            scenario=prompt,
            emotion=emotion,
            duration=duration,
            style="cinematic"
        )
    
    def _detect_emotion_from_prompt(self, prompt: str) -> str:
        """Smart emotion detection from prompt text"""
        prompt_lower = prompt.lower()
        
        # Emotion keywords
        if any(word in prompt_lower for word in ["angry", "mad", "furious", "rage"]):
            return "angry"
        elif any(word in prompt_lower for word in ["excited", "amazing", "breakthrough", "discovery"]):
            return "inspired"  
        elif any(word in prompt_lower for word in ["thinking", "contemplating", "wondering", "pondering"]):
            return "reflective"
        elif any(word in prompt_lower for word in ["accomplished", "finished", "relief", "peaceful"]):
            return "relief"
        else:
            return "neutral"
    
    def get_available_emotions(self) -> Dict[str, str]:
        """Get all available emotional states"""
        return self.emotions.copy()
    
    async def get_generation_history(self) -> List[Dict[str, Any]]:
        """Get history of generated videos (placeholder)"""
        # This would connect to your database/storage
        return []

# Quick usage functions
async def generate_persona_video(prompt: str, persona_id: str = None, emotion: str = "auto") -> str:
    """Quick function to generate video with any available persona"""
    # Auto-detect first available persona if none specified
    if not persona_id:
        from pathlib import Path
        personas_dir = Path(__file__).parent.parent / "personas"
        if personas_dir.exists():
            persona_dirs = [d for d in personas_dir.iterdir() if d.is_dir() and d.name != "example_persona"]
            if persona_dirs:
                persona_id = f"{persona_dirs[0].name}_001"
            else:
                raise ValueError("No personas found. Please create a persona first.")
    
    generator = PersonalAvatarGenerator(persona_id=persona_id)
    
    if emotion == "auto":
        result = await generator.quick_generate(prompt)
    else:
        result = await generator.generate_avatar_video(prompt, emotion=emotion)
    
    if result.get("success"):
        return result.get("video_url", "Video generated successfully")
    else:
        return f"Error: {result.get('error')}"

# Example usage
async def demo_avatar_generation():
    """Demo the avatar generation system"""
    
    generator = PersonalAvatarGenerator()
    
    scenarios = [
        "John standing on a mountain peak, then suddenly taking flight and soaring through the clouds",
        "Sarah discovering a hidden magical portal in her backyard", 
        "Alex working intensely on a breakthrough scientific discovery in his lab",
        "Maria having a peaceful moment of reflection while watching a sunset"
    ]
    
    print("🎬 Personal Avatar Video Generation Demo")
    print("=" * 50)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Demo {i}: {scenario[:50]}...")
        
        result = await generator.quick_generate(scenario)
        
        if result.get("success"):
            print(f"✅ Generated: {result.get('video_url', 'Success')}")
            print(f"   Emotion: {result.get('emotion')}")
            print(f"   Duration: {result.get('duration')}s")
        else:
            print(f"❌ Failed: {result.get('error')}")
        
        await asyncio.sleep(1)  # Brief pause between generations

if __name__ == "__main__":
    print("🚀 Personal AI Avatar Video Generation System")
    print("Generate videos of yourself doing ANYTHING!")
    
    # Run demo
    asyncio.run(demo_avatar_generation())