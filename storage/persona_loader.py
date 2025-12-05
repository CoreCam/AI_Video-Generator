"""
Persona loader for extracting and encoding reference images for video generation.
"""
import os
import base64
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from PIL import Image
import io


class PersonaLoader:
    """Load and prepare persona reference images for VEO video generation."""
    
    def __init__(self, personas_dir: str = "personas"):
        self.personas_dir = Path(personas_dir)
    
    def get_persona_reference_images(
        self, 
        persona_name: str, 
        max_images: int = 3,
        emotion: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Load and encode persona reference images for VEO.
        
        Args:
            persona_name: Name of the persona (e.g., "john")
            max_images: Maximum number of reference images to return (default 3)
            emotion: Optional emotion filter (e.g., "neutral", "inspired")
        
        Returns:
            List of dicts with format: {"bytesBase64Encoded": str, "mimeType": str}
        """
        persona_path = self.personas_dir / persona_name
        
        if not persona_path.exists():
            print(f"⚠️ Persona '{persona_name}' not found at {persona_path}")
            return []
        
        # Try to load from reference_frames first
        reference_images = self._load_from_reference_frames(persona_path, emotion, max_images)
        
        if reference_images:
            print(f"✅ Loaded {len(reference_images)} reference images for {persona_name}")
            return reference_images
        
        # Fallback: try processed directory
        reference_images = self._load_from_processed(persona_path, max_images)
        
        if reference_images:
            print(f"✅ Loaded {len(reference_images)} reference images from processed/ for {persona_name}")
            return reference_images
        
        print(f"⚠️ No reference images found for {persona_name}")
        return []
    
    def _load_from_reference_frames(
        self, 
        persona_path: Path, 
        emotion: Optional[str], 
        max_images: int
    ) -> List[Dict[str, str]]:
        """Load images from reference_frames directory."""
        ref_frames_dir = persona_path / "reference_frames"
        
        if not ref_frames_dir.exists():
            return []
        
        # If emotion specified, load from that subfolder
        if emotion:
            emotion_dir = ref_frames_dir / emotion
            if emotion_dir.exists():
                return self._encode_images_from_dir(emotion_dir, max_images)
        
        # Otherwise, load from neutral or first available
        neutral_dir = ref_frames_dir / "neutral"
        if neutral_dir.exists():
            return self._encode_images_from_dir(neutral_dir, max_images)
        
        # Load from first available emotion
        for subdir in ref_frames_dir.iterdir():
            if subdir.is_dir():
                images = self._encode_images_from_dir(subdir, max_images)
                if images:
                    return images
        
        return []
    
    def _load_from_processed(self, persona_path: Path, max_images: int) -> List[Dict[str, str]]:
        """Load images from processed directory."""
        processed_dir = persona_path / "processed"
        
        if not processed_dir.exists():
            return []
        
        return self._encode_images_from_dir(processed_dir, max_images)
    
    def _encode_images_from_dir(self, directory: Path, max_images: int) -> List[Dict[str, str]]:
        """Encode all images in a directory to base64."""
        encoded_images = []
        
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        image_files = [
            f for f in directory.iterdir() 
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        # Sort for consistency
        image_files.sort()
        
        # Limit to max_images
        image_files = image_files[:max_images]
        
        for image_file in image_files:
            try:
                encoded_image = self._encode_image(image_file)
                if encoded_image:
                    encoded_images.append(encoded_image)
            except Exception as e:
                print(f"⚠️ Error encoding {image_file.name}: {e}")
                continue
        
        return encoded_images
    
    def _encode_image(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """
        Encode a single image to base64 in VEO-compatible format.
        
        Returns:
            Dict with VEO API format:
            {
                "image": {
                    "bytesBase64Encoded": str,
                    "mimeType": str
                },
                "referenceType": "asset"
            }
        """
        try:
            # Open and potentially resize image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (VEO has size limits)
                max_dimension = 1024
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Save to bytes
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=90)
                image_bytes = buffer.getvalue()
                
                # Encode to base64
                base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
                
                # VEO API format for subject/asset images
                return {
                    "image": {
                        "bytesBase64Encoded": base64_encoded,
                        "mimeType": "image/jpeg"
                    },
                    "referenceType": "asset"  # "asset" for person/character, "style" for artistic style
                }
        
        except Exception as e:
            print(f"❌ Failed to encode {image_path}: {e}")
            return None
    
    def get_persona_metadata(self, persona_name: str) -> Dict[str, Any]:
        """Load persona metadata.json if it exists."""
        metadata_path = self.personas_dir / persona_name / "metadata.json"
        
        if not metadata_path.exists():
            return {}
        
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading metadata for {persona_name}: {e}")
            return {}
    
    def get_character_description(self, persona_name: str) -> str:
        """
        Get character description from metadata for prompt enhancement.
        
        Returns a string describing the character's appearance.
        """
        metadata = self.get_persona_metadata(persona_name)
        
        # Try to extract physical description
        description = metadata.get("physical_description", "")
        if description:
            return description
        
        # Extract from appearance metadata
        appearance = metadata.get("appearance", {})
        if isinstance(appearance, dict):
            facial = appearance.get("facial_features", "")
            if facial and "authentic" not in facial.lower():
                return f"{metadata.get('name', persona_name)}, {facial}"
        
        # Fallback: just use the name
        name = metadata.get("name", persona_name)
        return name
