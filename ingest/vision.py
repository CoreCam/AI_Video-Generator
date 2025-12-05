"""
Vision processing module for generating captions and embeddings from images and videos.
Clean extraction focusing on core vision functionality.
"""
from typing import List, Any, Optional, Dict
import base64
import io
import hashlib

class VisionProcessor:
    """Handles visual content analysis and embedding generation."""
    
    def __init__(self, model_type: str = "clip", device: str = "cpu"):
        self.model_type = model_type
        self.device = device
        self.model = None
        self.processor = None
        self.tokenizer = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the vision model."""
        print(f"🔄 Initializing {self.model_type} model on {self.device}...")
        
        try:
            if self.model_type == "clip":
                self._initialize_clip()
            elif self.model_type == "blip":
                self._initialize_blip()
            else:
                print(f"⚠️ Unknown model type {self.model_type}, using mock mode")
                self.model = None
        except ImportError as e:
            print(f"⚠️ Required libraries not installed for {self.model_type}: {e}")
            print("💡 Install transformers and torch for vision processing")
            self.model = None
        except Exception as e:
            print(f"⚠️ Failed to initialize {self.model_type}: {e}")
            self.model = None
    
    def _initialize_clip(self):
        """Initialize CLIP model."""
        try:
            from transformers import CLIPProcessor, CLIPModel
            import torch
            
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            if self.device == "cuda" and torch.cuda.is_available():
                self.model = self.model.to("cuda")
            
            print("✅ CLIP model initialized successfully")
        except ImportError:
            raise ImportError("transformers and torch required for CLIP")
    
    def _initialize_blip(self):
        """Initialize BLIP model for image captioning."""
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            import torch
            
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            
            if self.device == "cuda" and torch.cuda.is_available():
                self.model = self.model.to("cuda")
            
            print("✅ BLIP model initialized successfully")
        except ImportError:
            raise ImportError("transformers and torch required for BLIP")
    
    async def generate_caption(self, file: Any) -> str:
        """
        Generate a descriptive caption for an image or video frame.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Generated caption text
        """
        try:
            if not self.model:
                return self._generate_mock_caption(file)
            
            if self._is_image(file):
                return await self._generate_image_caption(file)
            elif self._is_video(file):
                return await self._generate_video_caption(file)
            else:
                return "Unsupported media type for caption generation"
                
        except Exception as e:
            print(f"❌ Error generating caption: {e}")
            return f"Caption generation failed for {getattr(file, 'filename', 'unknown file')}"
    
    async def generate_embedding(self, file: Any) -> List[float]:
        """
        Generate vector embedding for an image or video.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Vector embedding as list of floats
        """
        try:
            if not self.model:
                return self._generate_mock_embedding(file)
            
            if self._is_image(file):
                return await self._generate_image_embedding(file)
            elif self._is_video(file):
                return await self._generate_video_embedding(file)
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return []
    
    async def _generate_image_caption(self, file: Any) -> str:
        """Generate caption specifically for images."""
        try:
            from PIL import Image
            import torch
            
            # Load image
            image = self._load_image(file)
            
            if self.model_type == "blip":
                # BLIP for image captioning
                inputs = self.processor(image, return_tensors="pt")
                if self.device == "cuda":
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
                with torch.no_grad():
                    output = self.model.generate(**inputs, max_length=50)
                    caption = self.processor.decode(output[0], skip_special_tokens=True)
                
                return caption
            
            elif self.model_type == "clip":
                # CLIP with predefined text options
                text_options = [
                    "a photo of a person",
                    "a professional headshot",
                    "a casual portrait",
                    "a person smiling",
                    "a person looking at camera"
                ]
                
                inputs = self.processor(
                    text=text_options,
                    images=image,
                    return_tensors="pt",
                    padding=True
                )
                
                if self.device == "cuda":
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    probs = outputs.logits_per_image.softmax(dim=1)
                    best_match_idx = probs.argmax().item()
                
                return text_options[best_match_idx]
            
        except Exception as e:
            print(f"⚠️ Image caption generation failed: {e}")
            return self._generate_mock_caption(file)
    
    async def _generate_image_embedding(self, file: Any) -> List[float]:
        """Generate embedding specifically for images."""
        try:
            import torch
            
            # Load image
            image = self._load_image(file)
            
            if self.model_type == "clip":
                inputs = self.processor(images=image, return_tensors="pt")
                if self.device == "cuda":
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
                with torch.no_grad():
                    image_features = self.model.get_image_features(**inputs)
                    # Normalize the features
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                    
                return image_features.squeeze().cpu().numpy().tolist()
            
        except Exception as e:
            print(f"⚠️ Image embedding generation failed: {e}")
            return self._generate_mock_embedding(file)
    
    async def _generate_video_caption(self, file: Any) -> str:
        """Generate caption for video by analyzing key frames."""
        try:
            # Extract key frame from video
            frame = self._extract_video_frame(file)
            if frame:
                # Treat as image for captioning
                return await self._generate_image_caption(frame)
            else:
                return "Video content - frame extraction failed"
        except Exception as e:
            print(f"⚠️ Video caption generation failed: {e}")
            return f"Video content - {getattr(file, 'filename', 'unknown video')}"
    
    async def _generate_video_embedding(self, file: Any) -> List[float]:
        """Generate embedding for video by analyzing key frames."""
        try:
            # Extract key frame from video
            frame = self._extract_video_frame(file)
            if frame:
                # Treat as image for embedding
                return await self._generate_image_embedding(frame)
            else:
                return []
        except Exception as e:
            print(f"⚠️ Video embedding generation failed: {e}")
            return []
    
    def _load_image(self, file: Any):
        """Load image from file object."""
        try:
            from PIL import Image
            
            if hasattr(file, 'read'):
                # File-like object
                content = file.read()
                if hasattr(file, 'seek'):
                    file.seek(0)  # Reset file pointer
                image = Image.open(io.BytesIO(content))
            else:
                # Assume it's a path or already processed
                image = Image.open(file)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            print(f"⚠️ Failed to load image: {e}")
            raise
    
    def _extract_video_frame(self, file: Any):
        """Extract a representative frame from video."""
        try:
            # This would require cv2 or moviepy
            # For now, return None to indicate frame extraction not available
            print("⚠️ Video frame extraction not implemented")
            return None
        except Exception as e:
            print(f"⚠️ Video frame extraction failed: {e}")
            return None
    
    def _is_image(self, file: Any) -> bool:
        """Check if file is an image."""
        content_type = getattr(file, 'content_type', '')
        filename = getattr(file, 'filename', '')
        
        return (content_type.startswith('image/') or 
                any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']))
    
    def _is_video(self, file: Any) -> bool:
        """Check if file is a video."""
        content_type = getattr(file, 'content_type', '')
        filename = getattr(file, 'filename', '')
        
        return (content_type.startswith('video/') or 
                any(filename.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']))
    
    def _generate_mock_caption(self, file: Any) -> str:
        """Generate mock caption when model is not available."""
        filename = getattr(file, 'filename', 'unknown')
        
        # Generate deterministic caption based on filename hash
        hash_val = hashlib.md5(filename.encode()).hexdigest()
        
        mock_captions = [
            "A person smiling warmly at the camera",
            "Professional headshot with good lighting",
            "Casual photo showing natural expressions",
            "Portrait capturing personality and character",
            "Image showing clear facial features and expression",
            "Person in a relaxed, natural pose",
            "Well-lit photo with good composition",
            "Friendly expression with direct eye contact"
        ]
        
        # Use hash to select consistent caption
        caption_idx = int(hash_val[:2], 16) % len(mock_captions)
        return f"{mock_captions[caption_idx]} (mock caption)"
    
    def _generate_mock_embedding(self, file: Any) -> List[float]:
        """Generate mock embedding when model is not available."""
        filename = getattr(file, 'filename', 'unknown')
        
        # Generate deterministic embedding based on filename hash
        hash_val = hashlib.md5(filename.encode()).hexdigest()
        
        # Convert hash to numbers for consistent embedding
        embedding_size = 512  # Common CLIP embedding size
        embedding = []
        
        for i in range(0, len(hash_val), 2):
            if len(embedding) >= embedding_size:
                break
            # Convert hex pair to float between -1 and 1
            hex_pair = hash_val[i:i+2]
            value = (int(hex_pair, 16) / 255.0) * 2 - 1
            embedding.append(value)
        
        # Pad with zeros if needed
        while len(embedding) < embedding_size:
            embedding.append(0.0)
        
        return embedding[:embedding_size]
    
    def get_status(self) -> Dict[str, Any]:
        """Get vision processor status."""
        return {
            "model_type": self.model_type,
            "device": self.device,
            "model_loaded": self.model is not None,
            "processor_loaded": self.processor is not None,
            "using_mock": self.model is None
        }