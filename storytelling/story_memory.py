"""
Story Memory System for CINEGEN Agent.
Manages story continuity and persona context using vector embeddings.
"""
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from storage.vector_store import VectorStore
from storage.db import DatabaseClient


class StoryMemory:
    """
    Memory system for maintaining story continuity and persona context.
    Integrates with SoRa Core's vector store for embedding-based memory.
    """
    
    def __init__(
        self,
        vector_store: VectorStore = None,
        db_client: DatabaseClient = None,
        memory_table: str = "story_memory",
        context_type: str = "embeddings_user_persona"
    ):
        self.vector_store = vector_store or VectorStore()
        self.db_client = db_client or DatabaseClient()
        self.memory_table = memory_table
        self.context_type = context_type
        
        print(f"🧠 Story Memory initialized")
        print(f"   Table: {self.memory_table}")
        print(f"   Context Type: {self.context_type}")
    
    async def store_story_event(
        self,
        story_id: str,
        event_type: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store a story event with embedding for semantic search.
        
        Args:
            story_id: Unique story session ID
            event_type: Type of event (scene_generated, persona_interaction, etc.)
            content: Text content to embed
            metadata: Additional metadata
            
        Returns:
            Memory entry ID
        """
        entry_id = str(uuid.uuid4())
        
        try:
            # Create memory entry
            memory_entry = {
                "id": entry_id,
                "story_id": story_id,
                "event_type": event_type,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in vector store with embedding
            await self.vector_store.store_memory(
                collection_name=self.memory_table,
                entry_id=entry_id,
                content=content,
                metadata=memory_entry
            )
            
            print(f"💾 Stored story memory: {event_type} ({entry_id[:8]})")
            return entry_id
            
        except Exception as e:
            print(f"❌ Error storing story memory: {e}")
            return None
    
    async def retrieve_story_context(
        self,
        story_id: str,
        query: str = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant story context for continuity.
        
        Args:
            story_id: Story session ID
            query: Optional semantic query for relevant memories
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memory entries
        """
        try:
            if query:
                # Semantic search for relevant memories
                results = await self.vector_store.search_similar(
                    collection_name=self.memory_table,
                    query_text=query,
                    limit=limit,
                    filter_metadata={"story_id": story_id}
                )
            else:
                # Get recent memories for this story
                results = await self.vector_store.get_recent_memories(
                    collection_name=self.memory_table,
                    story_id=story_id,
                    limit=limit
                )
            
            print(f"🔍 Retrieved {len(results)} story memories")
            return results
            
        except Exception as e:
            print(f"❌ Error retrieving story context: {e}")
            return []
    
    async def get_persona_traits(
        self,
        persona_id: str,
        trait_type: str = None
    ) -> Dict[str, Any]:
        """
        Get persona traits and characteristics from embeddings.
        
        Args:
            persona_id: Persona ID
            trait_type: Optional specific trait type to filter
            
        Returns:
            Persona traits and characteristics
        """
        try:
            # Get persona embeddings and analyze for traits
            embeddings = await self.vector_store.get_persona_embeddings(persona_id)
            
            if not embeddings:
                return {"traits": [], "characteristics": []}
            
            # Mock trait extraction - in real implementation would use ML
            traits = await self._extract_persona_traits(embeddings, trait_type)
            
            print(f"🎭 Retrieved persona traits for {persona_id}")
            return traits
            
        except Exception as e:
            print(f"❌ Error getting persona traits: {e}")
            return {"traits": [], "characteristics": []}
    
    async def analyze_story_arc(self, story_id: str) -> Dict[str, Any]:
        """
        Analyze the overall story arc and suggest narrative direction.
        
        Args:
            story_id: Story session ID
            
        Returns:
            Story arc analysis and suggestions
        """
        try:
            # Get all story memories
            memories = await self.retrieve_story_context(story_id, limit=50)
            
            if not memories:
                return {
                    "arc_stage": "beginning",
                    "emotional_progression": "neutral",
                    "suggestions": ["Establish setting and character", "Introduce conflict or goal"]
                }
            
            # Analyze story progression
            analysis = await self._analyze_narrative_arc(memories)
            
            print(f"📊 Analyzed story arc for {story_id}")
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing story arc: {e}")
            return {"error": str(e)}
    
    async def get_emotional_context(
        self,
        story_id: str,
        scene_number: int = None
    ) -> Dict[str, Any]:
        """
        Get emotional context for scene generation.
        
        Args:
            story_id: Story session ID
            scene_number: Optional specific scene number
            
        Returns:
            Emotional context and mood suggestions
        """
        try:
            # Get recent emotional beats from story
            query = "emotion mood feeling atmosphere tone"
            memories = await self.retrieve_story_context(story_id, query, limit=3)
            
            # Extract emotional progression
            emotional_context = await self._extract_emotional_context(memories)
            
            print(f"💭 Retrieved emotional context for story {story_id}")
            return emotional_context
            
        except Exception as e:
            print(f"❌ Error getting emotional context: {e}")
            return {"mood": "neutral", "energy": "balanced"}
    
    async def _extract_persona_traits(
        self,
        embeddings: List[Dict[str, Any]],
        trait_type: str = None
    ) -> Dict[str, Any]:
        """Extract personality traits from persona embeddings (mock implementation)."""
        
        # Mock trait extraction - real implementation would use ML analysis
        base_traits = [
            "confident", "creative", "analytical", "empathetic", "energetic",
            "thoughtful", "expressive", "calm", "dynamic", "authentic"
        ]
        
        # Simulate trait extraction based on embedding count and metadata
        num_traits = min(len(embeddings), 5)
        selected_traits = base_traits[:num_traits]
        
        characteristics = [
            "Natural speaking rhythm with authentic pauses",
            "Expressive body language and gestures",
            "Engaging eye contact and facial expressions",
            "Consistent emotional tone throughout interactions"
        ]
        
        return {
            "traits": selected_traits,
            "characteristics": characteristics,
            "confidence_score": 0.85,
            "embedding_count": len(embeddings)
        }
    
    async def _analyze_narrative_arc(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze narrative progression from story memories (mock implementation)."""
        
        scene_count = len([m for m in memories if m.get("event_type") == "scene_generated"])
        
        if scene_count <= 1:
            arc_stage = "beginning"
            suggestions = ["Establish character motivation", "Introduce central conflict"]
        elif scene_count <= 3:
            arc_stage = "development"
            suggestions = ["Build tension", "Develop character relationships", "Add complications"]
        elif scene_count <= 5:
            arc_stage = "climax"
            suggestions = ["Reach emotional peak", "Resolve main conflict", "Character transformation"]
        else:
            arc_stage = "resolution"
            suggestions = ["Wrap up loose ends", "Show character growth", "Satisfying conclusion"]
        
        return {
            "arc_stage": arc_stage,
            "scene_count": scene_count,
            "emotional_progression": "building",
            "pacing": "balanced",
            "suggestions": suggestions
        }
    
    async def _extract_emotional_context(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract emotional context from recent memories (mock implementation)."""
        
        if not memories:
            return {"mood": "neutral", "energy": "balanced", "tone": "conversational"}
        
        # Mock emotional analysis
        recent_moods = []
        for memory in memories:
            content = memory.get("content", "").lower()
            if any(word in content for word in ["happy", "joy", "excited", "celebration"]):
                recent_moods.append("positive")
            elif any(word in content for word in ["sad", "melancholy", "loss", "grief"]):
                recent_moods.append("negative")
            elif any(word in content for word in ["tense", "conflict", "dramatic", "intense"]):
                recent_moods.append("dramatic")
            else:
                recent_moods.append("neutral")
        
        # Determine overall emotional context
        if recent_moods:
            dominant_mood = max(set(recent_moods), key=recent_moods.count)
        else:
            dominant_mood = "neutral"
        
        return {
            "mood": dominant_mood,
            "energy": "building" if dominant_mood == "dramatic" else "balanced",
            "tone": "cinematic",
            "recent_progression": recent_moods[-3:] if recent_moods else []
        }
    
    async def cleanup_old_memories(self, days_old: int = 30) -> int:
        """Clean up old story memories to maintain performance."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # In real implementation, would delete old memories from vector store
            print(f"🧹 Cleaned up memories older than {days_old} days")
            return 0  # Mock return
            
        except Exception as e:
            print(f"❌ Error cleaning up memories: {e}")
            return 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get memory system status."""
        return {
            "memory_backend": type(self.vector_store).__name__,
            "table": self.memory_table,
            "context_type": self.context_type,
            "status": "active"
        }