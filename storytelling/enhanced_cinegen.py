"""
Enhanced CINEGEN Story Director - CLEAN VERSION
Working implementation without syntax errors
"""
import asyncio
import json
import uuid
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed - environment variables may not load")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from storage.vector_store import VectorStore
from storage.db import DatabaseClient


@dataclass
class VideoProductionBreakdown:
    """Professional video production breakdown fields with duration awareness."""
    subject: str
    context_setting: str
    action: str
    style_aesthetic: str
    camera_composition: str
    lighting_ambience: str
    audio_dialogue: str
    generation_prompt: str
    duration_seconds: int
    pacing_notes: str
    reference_notes: Optional[str] = None
    personas_involved: List[str] = None
    scene_transitions: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "subject": self.subject,
            "context_setting": self.context_setting,
            "action": self.action,
            "style_aesthetic": self.style_aesthetic,
            "camera_composition": self.camera_composition,
            "lighting_ambience": self.lighting_ambience,
            "audio_dialogue": self.audio_dialogue,
            "generation_prompt": self.generation_prompt,
            "duration_seconds": self.duration_seconds,
            "pacing_notes": self.pacing_notes,
            "reference_notes": self.reference_notes,
            "personas_involved": self.personas_involved or [],
            "scene_transitions": self.scene_transitions
        }


class EnhancedCinegenAgent:
    """Enhanced CINEGEN Story Director - Clean Implementation"""
    
    def __init__(
        self,
        vector_store: VectorStore = None,
        db_client: DatabaseClient = None,
        google_api_key: str = None,
        temperature: float = 0.9,
        max_tokens: int = 2048
    ):
        self.vector_store = vector_store or VectorStore()
        self.db_client = db_client or DatabaseClient()
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize Gemini
        # Accept either GEMINI_API_KEY (preferred) or GOOGLE_API_KEY for backwards compatibility
        self.google_api_key = (
            google_api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        self.gemini_model = None
        self._initialize_gemini()
        
        # Current story session
        self.active_personas = {}
        self.current_story_id = None
        self.scenes = []
        self.target_video_duration = 60
        self.scene_durations = []
        
        print("Enhanced CINEGEN Story Director initialized")
        print(f"   Gemini AI: {'Active' if self.gemini_model else 'Mock mode'}")
    
    def _initialize_gemini(self):
        """Initialize Google Gemini AI."""
        if not GEMINI_AVAILABLE:
            print("Warning: google-generativeai not installed - using mock responses")
            return
        
        if not self.google_api_key:
            print("Warning: No GEMINI_API_KEY/GOOGLE_API_KEY found - using mock responses")
            print(f"Checked API key: {self.google_api_key}")
            return
        
        try:
            genai.configure(api_key=self.google_api_key)
            # Allow overriding the model from the environment
            requested_model = os.getenv("GEMINI_MODEL")

            def _strip_models_prefix(name: str) -> str:
                return name.split("/", 1)[1] if name and name.startswith("models/") else name

            model_to_try = requested_model or "gemini-1.5-flash-latest"

            try:
                self.gemini_model = genai.GenerativeModel(model_to_try)
            except Exception as e:
                # If the requested/default model isn't available, list models and pick a supported one
                print(f"⚠️ Requested model '{model_to_try}' unavailable: {e}")
                try:
                    available = list(genai.list_models())
                    # Filter to models that support generateContent
                    supported = []
                    for m in available:
                        methods = getattr(m, "supported_generation_methods", []) or []
                        if "generateContent" in methods or "generate_content" in methods:
                            supported.append(_strip_models_prefix(getattr(m, "name", "")))
                    # Prefer flash, then pro
                    preferred = next((m for m in supported if "flash" in m), None) or next((m for m in supported if "pro" in m), None)
                    if preferred:
                        print(f"ℹ️ Auto-selecting available model: {preferred}")
                        self.gemini_model = genai.GenerativeModel(preferred)
                    else:
                        raise RuntimeError("No compatible Gemini models with generateContent found for this API key")
                except Exception as e2:
                    print(f"❌ Could not auto-select a Gemini model: {e2}")
                    self.gemini_model = None

            if self.gemini_model:
                print("✅ Gemini AI initialized successfully")
                print(f"API Key loaded: {self.google_api_key[:10]}...")
                try:
                    # Echo the chosen model name if possible
                    model_name = getattr(self.gemini_model, "model", None) or requested_model or model_to_try
                    if model_name:
                        print(f"Using model: {model_name}")
                except Exception:
                    pass
        except Exception as e:
            print(f"❌ Gemini initialization failed: {e}")
            print(f"API Key value: {self.google_api_key}")
            self.gemini_model = None
    
    async def start_story_session(
        self,
        persona_ids: List[str] = None,
        story_theme: str = None,
        user_input: str = None,
        target_duration: int = 60
    ) -> str:
        """Start a new story session."""
        self.current_story_id = str(uuid.uuid4())
        self.scenes = []
        self.scene_durations = []
        self.target_video_duration = target_duration
        
        # Load personas if provided
        if persona_ids:
            await self.load_personas(persona_ids)
            print(f"Loaded {len(self.active_personas)} personas")
        
        print(f"Started story session: {self.current_story_id}")
        print(f"   Target Duration: {target_duration} seconds")
        
        return self.current_story_id
    
    async def load_personas(self, persona_ids: List[str]) -> Dict[str, Any]:
        """Load personas for the story session."""
        for persona_id in persona_ids:
            try:
                # Simple persona loading - can be enhanced later
                self.active_personas[persona_id] = {
                    "id": persona_id,
                    "name": persona_id.capitalize(),  # Use the persona ID as the name
                    "description": f"Persona {persona_id}"
                }
            except Exception as e:
                print(f"Warning: Could not load persona {persona_id}: {e}")
        
        return self.active_personas
    
    async def process_user_prompt(
        self,
        user_prompt: str,
        scene_number: int = None,
        duration_seconds: int = None
    ) -> VideoProductionBreakdown:
        """Process user prompt and create scene breakdown."""
        
        if not self.current_story_id:
            await self.start_story_session()
        
        scene_number = scene_number or len(self.scenes) + 1
        duration_seconds = duration_seconds or 30
        
        print(f"Processing user prompt for Scene {scene_number}...")
        
        # Generate the breakdown
        breakdown = await self._generate_production_breakdown(
            user_prompt, scene_number, duration_seconds
        )
        
        # Store the scene
        self.scenes.append(breakdown)
        self.scene_durations.append(duration_seconds)
        
        return breakdown
    
    async def _generate_production_breakdown(
        self,
        user_prompt: str,
        scene_number: int,
        duration_seconds: int
    ) -> VideoProductionBreakdown:
        """Generate production breakdown using Gemini or mock."""
        
        if self.gemini_model:
            return await self._generate_with_gemini(user_prompt, scene_number, duration_seconds)
        else:
            return await self._generate_mock_breakdown(user_prompt, scene_number, duration_seconds)
    
    async def _generate_with_gemini(
        self,
        user_prompt: str,
        scene_number: int,
        duration_seconds: int
    ) -> VideoProductionBreakdown:
        """Generate breakdown using Gemini AI."""
        
        # Build story context
        story_context = ""
        if self.scenes:
            story_context = f"\n\nSTORY CONTEXT:\n"
            story_context += f"Previous scenes: {len(self.scenes)}\n"
            if len(self.scenes) >= 1:
                last_scene = self.scenes[-1]
                story_context += f"Previous scene: {last_scene.action[:100]}...\n"
        
        # Retrieve persona context from vector store
        persona_context = await self._get_persona_context(user_prompt)
        
        # Create focused Gemini prompt
        system_prompt = f"""You are CINEGEN, an AI video director. Take the user's scene request and create a professional video breakdown.

IMPORTANT: When the user mentions "I", "me", "myself", they refer to the main persona in the scene.

{persona_context}

USER REQUEST: "{user_prompt}"
SCENE DURATION: {duration_seconds} seconds{story_context}

Your job: Create a SPECIFIC scene breakdown based on exactly what the user described. Don't use templates or generic descriptions.

Respond with:

SUBJECT: [Exactly who is in the scene and what they're doing - be specific to the user's request]

SETTING: [The exact location described - be specific and detailed]

ACTION: [What specifically happens in this {duration_seconds}-second scene - timeline of events]

STYLE: [Visual style that matches this specific scene]

CAMERA: [Camera work that captures this particular action]

LIGHTING: [Lighting that enhances this specific setting and mood]

AUDIO: [Sound design for this exact scene]

GENERATION_PROMPT: [Clean, detailed prompt optimized for Veo - no fluff, just the visual scene]

BE SPECIFIC to the user's request. Don't use generic templates."""
        
        try:
            print("Generating scene breakdown with Gemini AI...")
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                system_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=2048
                )
            )
            
            # Parse the response
            breakdown = self._parse_gemini_response(
                response.text, duration_seconds, scene_number
            )
            return breakdown
            
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            return await self._generate_mock_breakdown(user_prompt, scene_number, duration_seconds)
    
    def _parse_gemini_response(
        self, 
        response_text: str, 
        duration_seconds: int,
        scene_number: int
    ) -> VideoProductionBreakdown:
        """Parse Gemini response into structured breakdown."""
        
        lines = response_text.strip().split('\n')
        breakdown_data = {
            'subject': '',
            'context_setting': '',
            'action': '',
            'style_aesthetic': '',
            'camera_composition': '',
            'lighting_ambience': '',
            'audio_dialogue': '',
            'generation_prompt': ''
        }
        
        current_field = None
        
        # Parse the response
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for field headers
            if line.upper().startswith('SUBJECT:'):
                current_field = 'subject'
                breakdown_data[current_field] = line[8:].strip()
            elif line.upper().startswith('SETTING:'):
                current_field = 'context_setting'
                breakdown_data[current_field] = line[8:].strip()
            elif line.upper().startswith('ACTION:'):
                current_field = 'action'
                breakdown_data[current_field] = line[7:].strip()
            elif line.upper().startswith('STYLE:'):
                current_field = 'style_aesthetic'
                breakdown_data[current_field] = line[6:].strip()
            elif line.upper().startswith('CAMERA:'):
                current_field = 'camera_composition'
                breakdown_data[current_field] = line[7:].strip()
            elif line.upper().startswith('LIGHTING:'):
                current_field = 'lighting_ambience'
                breakdown_data[current_field] = line[9:].strip()
            elif line.upper().startswith('AUDIO:'):
                current_field = 'audio_dialogue'
                breakdown_data[current_field] = line[6:].strip()
            elif line.upper().startswith('GENERATION_PROMPT:'):
                current_field = 'generation_prompt'
                breakdown_data[current_field] = line[18:].strip()
            elif current_field and line and not line.upper().startswith(('SUBJECT:', 'SETTING:', 'ACTION:', 'STYLE:', 'CAMERA:', 'LIGHTING:', 'AUDIO:', 'GENERATION_PROMPT:')):
                # Continue previous field
                breakdown_data[current_field] += ' ' + line
        
        # Create the breakdown object
        return VideoProductionBreakdown(
            subject=breakdown_data['subject'] or "Person in a dynamic scene",
            context_setting=breakdown_data['context_setting'] or "Urban environment",
            action=breakdown_data['action'] or f"Scene unfolds over {duration_seconds} seconds",
            style_aesthetic=breakdown_data['style_aesthetic'] or "Cinematic style",
            camera_composition=breakdown_data['camera_composition'] or "Dynamic camera work",
            lighting_ambience=breakdown_data['lighting_ambience'] or "Natural lighting",
            audio_dialogue=breakdown_data['audio_dialogue'] or "Ambient sound design",
            generation_prompt=breakdown_data['generation_prompt'] or breakdown_data['action'],
            duration_seconds=duration_seconds,
            pacing_notes=f"Scene paced for {duration_seconds} seconds",
            personas_involved=["default_persona"],
            scene_transitions=None
        )
    
    async def _get_persona_context(self, user_prompt: str) -> str:
        """Retrieve relevant persona context from vector store."""
        try:
            if not self.vector_store or not self.vector_store.client:
                print("⚠️ Vector store not available - using fallback persona info")
                return """
PERSONA INFO (fallback):
- Authentic human with 5 distinct emotional states (angry, inspired, neutral, reflective, relief)
- Natural expressions and genuine mannerisms
- Adaptable energy and conversational style
"""
            
            # Generate embedding for the user prompt to find relevant persona info
            print("🔍 Querying vector store for persona context...")
            import sentence_transformers
            model = sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2')
            query_embedding = model.encode(user_prompt).tolist()
            
            results = await self.vector_store.search_similar(
                query_embedding=query_embedding,
                limit=5,  # Get top 5 most relevant chunks
                metadata_filter={}  # Will use any available persona
            )
            
            if results and len(results) > 0:
                print(f"✅ Retrieved {len(results)} relevant persona chunks from embeddings")
                context_parts = []
                
                for result in results:
                    metadata = result.get("metadata", {})
                    # Get the text content
                    text = metadata.get("text", "")
                    chunk_type = metadata.get("type", "unknown")
                    
                    if text:
                        context_parts.append(f"[{chunk_type}]\n{text}")
                        print(f"   - Using {chunk_type} context")
                
                if context_parts:
                    persona_context = "\n\nPERSONA INFO (from your embeddings):\n" + "\n\n".join(context_parts[:3])
                    print(f"✅ Built persona context from {len(context_parts[:3])} chunks")
                    return persona_context
            
            # If we got here, no results or empty results
            print("⚠️ No persona chunks retrieved - using fallback")
            return """
PERSONA INFO (fallback):
- Authentic human with 5 distinct emotional states (angry, inspired, neutral, reflective, relief)
- Natural expressions and genuine mannerisms  
- Adaptable energy and conversational style
"""
        except Exception as e:
            print(f"❌ Error retrieving persona context: {e}")
            import traceback
            traceback.print_exc()
            return """
PERSONA INFO (fallback - error occurred):
- Authentic human with 5 distinct emotional states (angry, inspired, neutral, reflective, relief)
- Natural expressions and genuine mannerisms
- Adaptable energy and conversational style
"""
    
    async def _generate_mock_breakdown(
        self,
        user_prompt: str,
        scene_number: int,
        duration_seconds: int
    ) -> VideoProductionBreakdown:
        """Generate mock breakdown when Gemini is not available."""
        
        print("Generating mock breakdown...")
        
        # Simple mock - can be enhanced
        return VideoProductionBreakdown(
            subject=f"Person as the main character in scene {scene_number}",
            context_setting="Modern urban environment",
            action=f"Based on: {user_prompt}",
            style_aesthetic="Cinematic and dynamic",
            camera_composition="Professional camera work",
            lighting_ambience="Natural lighting with cinematic mood",
            audio_dialogue="Ambient sound design",
            generation_prompt=f"Person in {user_prompt.lower()}",
            duration_seconds=duration_seconds,
            pacing_notes=f"Paced for {duration_seconds} seconds",
            personas_involved=["default_persona"],
            scene_transitions=None
        )
    
    async def get_video_generation_script(
        self,
        breakdown: VideoProductionBreakdown,
        quality: str = "standard",
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """Convert breakdown into Veo-ready video generation script."""
        
        # The generation_prompt is already optimized for Veo by Gemini
        video_prompt = breakdown.generation_prompt
        
        # Fallback to action if generation_prompt is missing
        if not video_prompt or video_prompt == breakdown.action:
            video_prompt = f"{breakdown.subject}. {breakdown.context_setting}. {breakdown.action}"
        
        # Load reference images for subject consistency (YOUR face/body)
        reference_images = self._get_reference_images_for_personas(breakdown.personas_involved)
        
        return {
            "prompt": video_prompt,
            "duration": breakdown.duration_seconds,
            "quality": quality,
            "aspect_ratio": aspect_ratio,
            "style": breakdown.style_aesthetic,
            "camera": breakdown.camera_composition,
            "lighting": breakdown.lighting_ambience,
            "audio": breakdown.audio_dialogue,
            "personas": breakdown.personas_involved or ["default_persona"],
            "reference_images": reference_images,  # Visual reference of YOU
            "metadata": {
                "scene_context": breakdown.context_setting,
                "pacing_notes": breakdown.pacing_notes,
                "reference_notes": breakdown.reference_notes
            }
        }
    
    def _get_reference_images_for_personas(self, personas: List[str]) -> List[str]:
        """Get reference image paths for the personas in the scene."""
        import json
        from pathlib import Path
        
        reference_images = []
        
        # Check if any persona is in the scene
        if not personas or any(persona in ["default_persona"] + list(self.active_personas.keys()) for persona in personas):
            # Load reference frame manifest - find first available persona
            personas_dir = Path(__file__).parent.parent / "personas"
            
            if personas_dir.exists():
                # Get first available persona
                persona_dirs = [d for d in personas_dir.iterdir() if d.is_dir() and d.name != "example_persona"]
                
                for persona_dir in persona_dirs:
                    manifest_path = persona_dir / "reference_frames" / "manifest.json"
                    
                    if manifest_path.exists():
                        try:
                            with open(manifest_path, 'r') as f:
                                manifest = json.load(f)
                            
                            # Get neutral frames as primary reference (most versatile)
                            if "neutral" in manifest.get("reference_frames", {}):
                                reference_images.extend(manifest["reference_frames"]["neutral"])
                                print(f"✅ Loaded {len(manifest['reference_frames']['neutral'])} reference images from {persona_dir.name}")
                                break  # Use first available persona
                        except Exception as e:
                            print(f"⚠️ Could not load reference images from {persona_dir.name}: {e}")
        
        return reference_images
    
    async def export_story(self) -> Dict[str, Any]:
        """Export the current story session."""
        return {
            "story_id": self.current_story_id,
            "scenes": [s.to_dict() for s in self.scenes],
            "scene_count": len(self.scenes),
            "total_duration": sum(self.scene_durations),
            "target_duration": self.target_video_duration,
            "active_personas": list(self.active_personas.keys())
        }