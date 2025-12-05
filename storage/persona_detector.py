"""
Smart Persona Detection System
Automatically detect which personas (if any) should be in a video based on the prompt.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class PersonaDetector:
    """Detect which personas should be included based on prompt content."""
    
    def __init__(self, personas_dir: str = "personas"):
        self.personas_dir = Path(personas_dir)
        self._load_persona_index()
    
    def _load_persona_index(self):
        """Build an index of all available personas and their names/aliases."""
        self.persona_index = {}
        
        if not self.personas_dir.exists():
            print(f"⚠️ Personas directory not found: {self.personas_dir}")
            return
        
        # Directories to skip (not real personas)
        skip_dirs = {'chroma_db', '__pycache__', '.git'}
        
        # Scan personas directory for subdirectories
        for persona_dir in self.personas_dir.iterdir():
            if persona_dir.is_dir() and not persona_dir.name.startswith('.') and persona_dir.name not in skip_dirs:
                persona_id = persona_dir.name
                
                # Load metadata to get full name and aliases
                metadata_file = persona_dir / "metadata.json"
                if metadata_file.exists():
                    import json
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        
                        # Build list of names this persona responds to
                        names = [persona_id]  # Directory name (e.g., "john")
                        
                        if 'name' in metadata:
                            names.append(metadata['name'].lower())  # Full name (e.g., "john")
                        
                        if 'aliases' in metadata:
                            names.extend([alias.lower() for alias in metadata['aliases']])
                        
                        self.persona_index[persona_id] = {
                            'names': list(set(names)),  # Remove duplicates
                            'metadata': metadata
                        }
                        
                    except Exception as e:
                        print(f"⚠️ Error loading metadata for {persona_id}: {e}")
                        # Fallback: just use directory name
                        self.persona_index[persona_id] = {
                            'names': [persona_id],
                            'metadata': {}
                        }
                else:
                    # No metadata, just use directory name
                    self.persona_index[persona_id] = {
                        'names': [persona_id],
                        'metadata': {}
                    }
        
        print(f"📇 Loaded {len(self.persona_index)} personas: {list(self.persona_index.keys())}")
    
    def detect_personas_in_prompt(self, prompt: str) -> List[str]:
        """
        Detect which personas are mentioned in the prompt.
        Uses word boundary matching to avoid false positives (e.g., "Camera" vs "Cam").
        
        Args:
            prompt: The text prompt to analyze
            
        Returns:
            List of persona IDs mentioned in the prompt (e.g., ["john", "sarah"])
        """
        if not prompt:
            return []
        
        import re
        
        prompt_lower = prompt.lower()
        detected_personas = []
        
        for persona_id, persona_info in self.persona_index.items():
            # Check if any of this persona's names appear in the prompt
            for name in persona_info['names']:
                # Use word boundaries to avoid partial matches
                # \b ensures we match whole words only
                pattern = r'\b' + re.escape(name.lower()) + r'\b'
                if re.search(pattern, prompt_lower):
                    detected_personas.append(persona_id)
                    print(f"✅ Detected persona '{persona_id}' (matched: '{name}')")
                    break  # Don't add same persona twice
        
        if not detected_personas:
            print(f"ℹ️ No personas detected in prompt")
        
        return detected_personas
    
    def get_persona_metadata(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific persona."""
        if persona_id in self.persona_index:
            return self.persona_index[persona_id]['metadata']
        return None
    
    def list_available_personas(self) -> List[str]:
        """Get list of all available persona IDs."""
        return list(self.persona_index.keys())


if __name__ == "__main__":
    # Test the detector
    detector = PersonaDetector()
    
    test_prompts = [
        "John working at a modern desk",
        "A person walking in the park",
        "Sarah presenting to an audience",
        "Alex and John having a conversation",
        "A beautiful sunset over the ocean"
    ]
    
    print("\n🧪 Testing persona detection:\n")
    for prompt in test_prompts:
        print(f"Prompt: '{prompt}'")
        personas = detector.detect_personas_in_prompt(prompt)
        print(f"Detected: {personas if personas else 'None'}")
        print()
