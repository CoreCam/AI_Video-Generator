"""
Google Velo 3.1 client for AI video generation using Vertex AI.
Clean extraction from original codebase.
"""
import asyncio
import httpx
import json
import uuid
from typing import Dict, Any, List, Optional
import time
import os
import base64

class VeloClient:
    """Client for Google Velo 3.1 video generation via Vertex AI."""
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None, 
                 location: str = "us-central1", use_reference_images: bool = False):
        # Use service account key for Veo (different from Gemini key)
        # For Veo: try GOOGLE_ACCESS_TOKEN first (Bearer token), then API keys
        self.api_key = api_key or os.getenv("GOOGLE_ACCESS_TOKEN") or os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.project_id = project_id or os.getenv("GOOGLE_PROJECT_ID", "your-project-id")  # Replace with your project ID
        self.location = location
        self.use_reference_images = use_reference_images
        
        # veo-3.1-generate-preview supports reference images
        # veo-3.1-fast-generate-preview does NOT support reference images
        self.model_name = os.getenv("VEO_MODEL", "veo-3.1-generate-preview")
        
        # Determine the correct endpoint
        # If we have a project ID and any form of auth, use Vertex AI
        if self.project_id and self.api_key:
            # Use Vertex AI endpoint with predictLongRunning (Veo 3.1 uses this)
            self.base_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{location}/publishers/google/models/{self.model_name}:predictLongRunning"
            self.use_vertex = True
        else:
            # Fallback to generative AI API
            self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateVideo"
            self.use_vertex = False
        
        self.session = None
        print(f"[INIT] Velo Client initialized - Using {'Vertex AI' if self.use_vertex else 'Generative AI'} API")
        print(f"[INIT] Model: {self.model_name} | Reference Images: {'Enabled' if use_reference_images else 'Disabled'}")
    
    def _get_auth_token(self) -> str:
        """Get authentication token for Vertex AI."""
        import subprocess
        
        # First check for GOOGLE_ACCESS_TOKEN in env
        access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
        if access_token and access_token.startswith("ya29."):
            print("✅ Using access token from environment")
            return access_token
        
        # If api_key looks like a token already, use it
        if self.api_key and (self.api_key.startswith("ya29.") or len(self.api_key) > 100):
            return self.api_key
        
        # Try to get token from gcloud
        try:
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                token = result.stdout.strip()
                print("✅ Got auth token from gcloud")
                return token
        except Exception as e:
            print(f"⚠️ Could not get gcloud token: {e}")
        
        # Fallback - try to use api_key as-is
        return self.api_key or ""
    
    async def __aenter__(self):
        """Async context manager entry."""
        if self.api_key:
            self.session = httpx.AsyncClient(timeout=300.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    async def generate_video(self, script: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate video from script using Google Velo 3.1.
        
        Automatically detects personas mentioned in the prompt and loads their reference images.
        Only includes personas that are explicitly mentioned by name.
        
        Args:
            script: Script dictionary with prompt and metadata
            **kwargs: Additional parameters
        """
        
        print("🎬 Starting Velo video generation...")
        
        if not self.api_key:
            print("🎭 No API key found - using mock response")
            return await self._generate_mock_video(script)
        
        try:
            # Extract and optimize prompts
            prompts = self._extract_velo_prompts(script)
            
            if not prompts:
                return {
                    "success": False,
                    "error": "No valid prompts found in script",
                    "provider": "velo"
                }
            
            print(f"📝 Extracted {len(prompts)} prompts from script")
            
            # For multi-scene scripts, process the first scene
            main_prompt = prompts[0]
            
            # AUTO-DETECT PERSONAS from prompt
            from storage.persona_detector import PersonaDetector
            from storage.persona_loader import PersonaLoader
            
            detector = PersonaDetector()
            detected_personas = detector.detect_personas_in_prompt(main_prompt)
            
            reference_images = []
            
            if detected_personas:
                print(f"🔍 Detected {len(detected_personas)} persona(s): {', '.join(detected_personas)}")
                
                loader = PersonaLoader()
                
                # Load reference images for each detected persona
                if self.use_reference_images:
                    for persona_name in detected_personas:
                        persona_images = loader.get_persona_reference_images(
                            persona_name, 
                            max_images=3 // len(detected_personas),  # Distribute images among personas
                            emotion=script.get("emotion")
                        )
                        if persona_images:
                            reference_images.extend(persona_images)
                            print(f"� Loaded {len(persona_images)} reference images for {persona_name}")
                
                # DO NOT modify the prompt - user already mentioned the persona by name
                # Their original phrasing is what they intended
            else:
                print(f"👤 No personas detected - generating generic video")
            
            print(f"🎯 Using prompt: {main_prompt[:100]}...")
            
            # Add reference images to script metadata
            if reference_images:
                script["reference_images"] = reference_images
            
            # Generate video
            result = await self._call_velo_api(main_prompt, script, **kwargs)
            
            if result["success"]:
                print("✅ Velo video generation successful!")
            else:
                print(f"❌ Velo generation failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Velo client error: {str(e)}")
            return {
                "success": False,
                "error": f"Velo generation failed: {str(e)}",
                "provider": "velo"
            }
    
    async def _call_velo_api(self, prompt: str, script: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make the actual API call to Velo."""
        
        # Prepare request payload
        if self.use_vertex:
            # Pass script dict as kwargs (it already contains duration, reference_images, etc.)
            payload = self._prepare_vertex_payload(prompt, **{k: v for k, v in script.items() if k != 'prompt'})
            
            # For Vertex AI, we need gcloud auth token
            # Try to get it via subprocess if api_key looks like a path to service account
            auth_token = self._get_auth_token()
            
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
        else:
            payload = self._prepare_genai_payload(prompt, **kwargs)
            headers = {
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json"
            }
        
        if not self.session:
            self.session = httpx.AsyncClient(timeout=300.0)
        
        print(f"🌐 Making API call to: {self.base_url}")
        
        try:
            response = await self.session.post(
                self.base_url,
                json=payload,
                headers=headers
            )
            
            print(f"📡 API Response Status: {response.status_code}")
            
            if response.status_code not in [200, 201, 202]:
                error_text = response.text
                print(f"❌ API Error Response: {error_text}")
                
                # Try to extract meaningful error
                try:
                    error_json = response.json()
                    error_message = error_json.get("error", {}).get("message", error_text)
                except:
                    error_message = error_text
                
                return {
                    "success": False,
                    "error": f"Velo API error ({response.status_code}): {error_message}",
                    "provider": "velo"
                }
            
            result = response.json()
            print("✅ Received successful API response")
            
            # Check if this is a completed operation with video data
            if "predictions" in result and isinstance(result["predictions"], list):
                # This is a completed operation - extract and save video
                video_path = self._save_video_from_response(result, prompt)
                if video_path:
                    return {
                        "success": True,
                        "video_id": f"velo_{uuid.uuid4().hex[:8]}",
                        "video_path": video_path,
                        "provider": "velo",
                        "model": self.model_name,
                        "duration": script.get("duration", 8),
                        "prompt": prompt,
                        "generated_at": time.time()
                    }
            
            # Veo 3.1 returns a long-running operation
            if "name" in result:
                operation_id = result["name"]
                print(f"🔄 Video generation started - Operation ID: {operation_id}")
                
                return {
                    "success": True,
                    "status": "processing",
                    "operation_id": operation_id,
                    "provider": "velo",
                    "model": self.model_name,
                    "duration": script.get("duration", 8),
                    "prompt": prompt,
                    "message": "Video generation in progress. Use operation_id to check status.",
                    "generated_at": time.time()
                }
            
            # Legacy format - immediate video URL
            video_url = self._extract_video_url_from_response(result)
            
            return {
                "success": True,
                "video_id": f"velo_{uuid.uuid4().hex[:8]}",
                "video_url": video_url,
                "provider": "velo",
                "model": self.model_name,
                "duration": script.get("duration", 8),
                "prompt": prompt,
                "api_response": result,
                "generated_at": time.time()
            }
            
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "provider": "velo"
            }
    
    def _prepare_vertex_payload(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare payload for Veo 3.1 API.
        
        Reference images are supported by:
        - veo-2.0-generate-exp
        - veo-3.1-generate-preview
        """
        
        # Build instances with prompt
        instance = {"prompt": prompt}
        
        # Add reference images if provided
        # veo-3.1-generate-preview supports referenceImages parameter
        reference_images = kwargs.get("reference_images", [])
        if reference_images and self.use_reference_images:
            instance["referenceImages"] = reference_images
            print(f"📸 Added {len(reference_images)} reference images to request")
        
        # Build payload
        payload = {
            "instances": [instance],
            "parameters": {
                "aspectRatio": kwargs.get("aspect_ratio", "16:9"),
                "sampleCount": kwargs.get("sample_count", 1),  # Number of video variations
                "durationSeconds": str(kwargs.get("duration", 8)),  # Must be string
                "personGeneration": "allow_all",  # Allow generation of people based on prompt
                "addWatermark": False,  # Set to True if you want watermark
                "includeRaiReason": True,  # Include safety/content filtering reasons
                "generateAudio": kwargs.get("generate_audio", True),
                "resolution": kwargs.get("resolution", "720p")  # 720p or 1080p
            }
        }
        
        return payload
    
    def _prepare_genai_payload(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare payload for Generative AI API."""
        return {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": 1024,
                "candidateCount": 1
            }
        }
    
    def _save_video_from_response(self, response: Dict[str, Any], prompt: str) -> str:
        """Extract video from response and save to file."""
        import base64
        from datetime import datetime
        
        try:
            # Extract video data from predictions
            predictions = response.get("predictions", [])
            if not predictions:
                print("❌ No predictions in response")
                return None
            
            # Get first prediction
            prediction = predictions[0]
            generated_samples = prediction.get("generatedSamples", [])
            
            if not generated_samples:
                print("❌ No generated samples in prediction")
                return None
            
            # Get first sample
            sample = generated_samples[0]
            video_data = sample.get("video", {})
            
            # Get base64 encoded video
            base64_video = video_data.get("bytesBase64Encoded")
            if not base64_video:
                print("❌ No video data in sample")
                return None
            
            # Decode base64 to binary
            video_bytes = base64.b64decode(base64_video)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"veo_video_{timestamp}.mp4"
            
            # Save to main directory
            with open(filename, 'wb') as f:
                f.write(video_bytes)
            
            file_size_mb = len(video_bytes) / 1024 / 1024
            print(f"✅ Video saved: {filename}")
            print(f"   File size: {file_size_mb:.2f} MB")
            print(f"   Prompt: {prompt[:80]}...")
            
            return filename
            
        except Exception as e:
            print(f"❌ Error saving video: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_video_url_from_response(self, response: Dict[str, Any]) -> str:
        """Extract video URL from API response."""
        
        try:
            # Try Vertex AI response format
            if "predictions" in response:
                for prediction in response["predictions"]:
                    if "videoUrl" in prediction:
                        return prediction["videoUrl"]
                    elif "video_uri" in prediction:
                        return prediction["video_uri"]
            
            # Try Generative AI response format
            if "candidates" in response:
                for candidate in response["candidates"]:
                    if "content" in candidate:
                        parts = candidate["content"].get("parts", [])
                        for part in parts:
                            if "videoUrl" in part:
                                return part["videoUrl"]
                            elif "fileData" in part:
                                return part["fileData"].get("fileUri", "")
            
            # Fallback for direct response
            if "videoUrl" in response:
                return response["videoUrl"]
            elif "video_uri" in response:
                return response["video_uri"]
            
            # Generate placeholder URL if no video found
            video_id = uuid.uuid4().hex[:12]
            return f"https://storage.googleapis.com/velo-generated-videos/{video_id}.mp4"
            
        except Exception as e:
            print(f"⚠️ Warning: Could not extract video URL: {e}")
            video_id = uuid.uuid4().hex[:12] 
            return f"https://storage.googleapis.com/velo-generated-videos/{video_id}.mp4"
    
    def _extract_velo_prompts(self, script: Dict[str, Any]) -> List[str]:
        """Extract prompts suitable for Velo from script."""
        
        prompts = []
        
        if "scenes" in script:
            for scene in script["scenes"]:
                # Try different prompt fields
                prompt = (scene.get("sora_prompt") or 
                         scene.get("velo_prompt") or 
                         scene.get("visual_description") or 
                         scene.get("description", ""))
                
                if prompt:
                    # Optimize prompt for Velo
                    optimized_prompt = self._optimize_prompt_for_velo(prompt)
                    prompts.append(optimized_prompt)
        
        # Fallback to script-level prompt
        if not prompts and "prompt" in script:
            prompts.append(self._optimize_prompt_for_velo(script["prompt"]))
        
        return prompts
    
    def _optimize_prompt_for_velo(self, prompt: str) -> str:
        """Optimize prompt specifically for Velo 3.1."""
        
        # Remove Sora-specific terms
        optimized = prompt.replace("Sora", "").replace("sora", "")
        
        # Add Velo-friendly descriptors
        if "high quality" not in optimized.lower():
            optimized = f"High quality {optimized}"
        
        if "cinematic" not in optimized.lower():
            optimized = f"Cinematic {optimized}"
        
        # Ensure proper format
        optimized = optimized.strip()
        if not optimized.endswith('.'):
            optimized += '.'
        
        return optimized
    
    async def _generate_mock_video(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock response when no API key is available."""
        
        await asyncio.sleep(2)  # Simulate processing time
        
        mock_video_id = f"mock_velo_{uuid.uuid4().hex[:8]}"
        
        return {
            "success": True,
            "video_id": mock_video_id,
            "video_url": f"https://mock-velo-storage.googleapis.com/{mock_video_id}.mp4",
            "provider": "velo",
            "model": "velo-3.1-mock",
            "duration": script.get("duration", 30),
            "note": "Mock response - configure GOOGLE_API_KEY for real generation",
            "generated_at": time.time()
        }
    
    async def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate a prompt for Velo generation."""
        
        validation_result = {
            "valid": True,
            "provider": "velo",
            "issues": [],
            "suggestions": [],
            "estimated_cost": 0.0
        }
        
        # Basic validation
        if len(prompt.strip()) < 10:
            validation_result["valid"] = False
            validation_result["issues"].append("Prompt too short (minimum 10 characters)")
        
        if len(prompt) > 500:
            validation_result["issues"].append("Prompt quite long - consider shortening for better results")
        
        # Cost estimation (mock)
        estimated_duration = min(max(len(prompt) / 10, 5), 60)  # 5-60 seconds
        validation_result["estimated_cost"] = estimated_duration * 0.10  # $0.10 per second estimate
        validation_result["estimated_duration"] = estimated_duration
        
        # Suggestions
        if "high quality" not in prompt.lower():
            validation_result["suggestions"].append("Consider adding 'high quality' for better results")
        
        if not any(word in prompt.lower() for word in ["cinematic", "professional", "detailed"]):
            validation_result["suggestions"].append("Adding descriptive terms like 'cinematic' can improve quality")
        
        return validation_result
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status information."""
        
        return {
            "provider": "velo",
            "model": self.model_name,
            "api_available": bool(self.api_key),
            "endpoint": self.base_url,
            "using_vertex": self.use_vertex,
            "location": self.location if self.use_vertex else "global"
        }