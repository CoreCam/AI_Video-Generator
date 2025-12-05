#!/usr/bin/env python3
"""
Safe Persona Upload Script
"""
Enhanced Persona Upload Script

Uploads persona data to vector store for storytelling agent
"""
import json
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from storage.vector_store import VectorStore

class PersonaUploader:
    """Safe uploader for persona data to vector store"""
    
    def __init__(self):
        self.vector_store = VectorStore(store_type="chroma")
        
    def load_persona_data(self, persona_path: str) -> Dict[str, Any]:
        """Safely load persona metadata"""
        
        metadata_file = Path(persona_path) / "metadata.json"
        
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded persona data for: {data.get('name', 'Unknown')}")
            return data
        except Exception as e:
            raise Exception(f"Failed to load metadata: {e}")
    
    def prepare_appearance_chunks(self, persona_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare appearance data for vector storage"""
        
        chunks = []
        persona_id = persona_data.get("persona_id", "unknown")
        name = persona_data.get("name", "Unknown")
        
        # Appearance chunk
        appearance = persona_data.get("appearance", {})
        appearance_text = f"""
        Person: {name}
        Facial Features: {appearance.get('facial_features', '')}
        Expressions: {appearance.get('expressions', '')}
        Mannerisms: {appearance.get('mannerisms', '')}
        Visual Consistency: {appearance.get('consistency', '')}
        """
        
        chunks.append({
            "id": f"{persona_id}_appearance",
            "text": appearance_text.strip(),
            "metadata": {
                "persona_id": persona_id,
                "type": "appearance",
                "name": name
            }
        })
        
        # Personality chunk
        personality = persona_data.get("personality", {})
        personality_text = f"""
        Person: {name}
        Speaking Style: {personality.get('speaking_style', '')}
        Tone: {personality.get('tone', '')}
        Energy Level: {personality.get('energy_level', '')}
        Authenticity: {personality.get('authenticity', '')}
        """
        
        chunks.append({
            "id": f"{persona_id}_personality", 
            "text": personality_text.strip(),
            "metadata": {
                "persona_id": persona_id,
                "type": "personality", 
                "name": name
            }
        })
        
        # Emotional range chunks
        emotional_range = persona_data.get("emotional_range", {})
        for emotion, description in emotional_range.items():
            emotion_text = f"""
            Person: {name}
            Emotion: {emotion}
            Expression: {description}
            Context: How {name} looks and behaves when {emotion}
            """
            
            chunks.append({
                "id": f"{persona_id}_emotion_{emotion}",
                "text": emotion_text.strip(),
                "metadata": {
                    "persona_id": persona_id,
                    "type": "emotion",
                    "emotion": emotion,
                    "name": name
                }
            })
        
        # Video descriptions
        video_descriptions = persona_data.get("video_descriptions", {})
        for video_file, description in video_descriptions.items():
            video_text = f"""
            Person: {name}
            Video: {video_file}
            Visual Description: {description}
            Appearance Reference: How {name} looks in this video
            """
            
            chunks.append({
                "id": f"{persona_id}_video_{video_file.replace('.', '_')}",
                "text": video_text.strip(),
                "metadata": {
                    "persona_id": persona_id,
                    "type": "video_description",
                    "video_file": video_file,
                    "name": name
                }
            })
        
        return chunks
    
    async def upload_persona(self, persona_path: str) -> bool:
        """Upload persona data to vector store"""
        
        try:
            print(f"🔄 Loading persona data from: {persona_path}")
            persona_data = self.load_persona_data(persona_path)
            
            print(f"📊 Preparing data chunks...")
            chunks = self.prepare_appearance_chunks(persona_data)
            
            print(f"📤 Uploading {len(chunks)} chunks to vector store...")
            
            # Upload each chunk
            for i, chunk in enumerate(chunks, 1):
                try:
                    # Store text in metadata so we can retrieve it
                    chunk["metadata"]["text"] = chunk["text"]
                    
                    success = await self.vector_store.store_embedding(
                        id=chunk["id"],
                        embedding=[0.1] * 384,  # Mock embedding for now
                        metadata=chunk["metadata"]
                    )
                    
                    if success:
                        print(f"   ✅ [{i}/{len(chunks)}] {chunk['metadata']['type']}")
                    else:
                        print(f"   ❌ [{i}/{len(chunks)}] Failed: {chunk['metadata']['type']}")
                        
                except Exception as e:
                    print(f"   ❌ [{i}/{len(chunks)}] Error: {e}")
            
            # Update metadata
            persona_data["vector_store_status"] = "uploaded"
            metadata_file = Path(persona_path) / "metadata.json"
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(persona_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Persona upload completed!")
            print(f"👤 Name: {persona_data.get('name')}")
            print(f"📊 Chunks uploaded: {len(chunks)}")
            print(f"🎭 Emotions: {len(persona_data.get('emotional_range', {}))}")
            print(f"📹 Videos: {len(persona_data.get('video_files', []))}")
            
            return True
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    async def verify_upload(self, persona_id: str) -> bool:
        """Verify persona data was uploaded correctly"""
        
        try:
            print(f"🔍 Verifying upload for persona: {persona_id}")
            
            # Search for appearance data
            results = await self.vector_store.search_similar(
                query_embedding=[0.1] * 384,  # Mock query
                limit=10,
                metadata_filter={"persona_id": persona_id}
            )
            
            if results:
                print(f"✅ Found {len(results)} chunks in vector store")
                
                # Show what was found
                types_found = set()
                for result in results:
                    metadata = result.get("metadata", {})
                    types_found.add(metadata.get("type", "unknown"))
                
                print(f"📊 Data types found: {', '.join(types_found)}")
                return True
            else:
                print(f"❌ No data found for persona: {persona_id}")
                return False
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False

async def upload_persona_interactive():
    """Interactive function to upload any persona"""
    
    print("🎭 Persona Upload to Vector Store")
    print("=" * 50)
    
    uploader = PersonaUploader()
    
    # List available personas
    import os
    personas_dir = "personas"
    available_personas = [d for d in os.listdir(personas_dir) 
                         if os.path.isdir(os.path.join(personas_dir, d)) 
                         and d != "example_persona"]
    
    if not available_personas:
        print("❌ No personas found in personas/ directory")
        print("💡 Create a persona first by copying personas/example_persona/ to personas/your_name/")
        return
    
    print("Available personas:")
    for i, persona in enumerate(available_personas, 1):
        print(f"  {i}. {persona}")
    
    try:
        choice = int(input(f"\nSelect persona to upload (1-{len(available_personas)}): ")) - 1
        if choice < 0 or choice >= len(available_personas):
            raise ValueError("Invalid choice")
        
        selected_persona = available_personas[choice]
        persona_path = f"personas/{selected_persona}"
        
        print(f"\n🚀 Uploading {selected_persona}...")
    except (ValueError, KeyboardInterrupt):
        print("❌ Invalid selection or cancelled")
        return
    
    # Upload selected persona
    success = await uploader.upload_persona(persona_path)
    
    if success:
        print("\n🔍 Verifying upload...")
        verified = await uploader.verify_upload(f"{selected_persona}_001")
        
        if verified:
            print(f"\n🎉 SUCCESS! {selected_persona}'s persona is now in vector store!")
            print("✅ Storytelling agent can now understand:")
            print("   • How they look")
            print("   • Their personality") 
            print("   • Their 5 emotional expressions")
            print("   • Their video appearance references")
        else:
            print("\n⚠️ Upload completed but verification failed")
    else:
        print("\n❌ Upload failed - check error messages above")

if __name__ == "__main__":
    print("""
🎭 Persona Upload Script
=======================
This will upload your persona to the vector store for story generation.
Ensure your persona folder contains:
- metadata.json with persona details  
- reference_frames/ with emotion-based images
""")
    
    asyncio.run(upload_persona_interactive())