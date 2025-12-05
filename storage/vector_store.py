"""
Vector store operations for managing embeddings and similarity search.
Clean extraction supporting ChromaDB and Supabase Vector extensions.
"""
from typing import List, Dict, Any, Optional
import uuid

class VectorStore:
    """Vector database client for storing and querying embeddings."""
    
    def __init__(self, store_type: str = "chroma", connection_params: Dict[str, Any] = None):
        self.store_type = store_type
        self.connection_params = connection_params or {}
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize vector store client."""
        if self.store_type == "chroma":
            try:
                import chromadb
                from pathlib import Path
                
                # Use persistent storage so embeddings survive restarts
                db_path = Path(__file__).parent.parent / "personas" / "chroma_db"
                db_path.mkdir(parents=True, exist_ok=True)
                
                self.client = chromadb.PersistentClient(path=str(db_path))
                self.collection = self.client.get_or_create_collection("personas")
                print(f"✅ ChromaDB client initialized (persistent: {db_path})")
            except ImportError:
                print("⚠️ ChromaDB not installed - using mock mode")
                self.client = None
        elif self.store_type == "supabase":
            try:
                from supabase import create_client
                if "url" in self.connection_params and "key" in self.connection_params:
                    self.client = create_client(
                        self.connection_params["url"],
                        self.connection_params["key"]
                    )
                    print(f"✅ Supabase client initialized")
                else:
                    print("⚠️ Supabase credentials missing - using mock mode")
                    self.client = None
            except ImportError:
                print("⚠️ Supabase client not installed - using mock mode")
                self.client = None
        
        print(f"Vector store initialized: {self.store_type}")
    
    async def store_embedding(
        self,
        id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Store an embedding with metadata.
        
        Args:
            id: Unique identifier for the embedding
            embedding: Vector embedding as list of floats
            metadata: Associated metadata dictionary
            
        Returns:
            True if successful
        """
        try:
            if self.store_type == "chroma" and self.client:
                self.collection.add(
                    embeddings=[embedding],
                    metadatas=[metadata],
                    ids=[id]
                )
            elif self.store_type == "supabase" and self.client:
                # Insert into vector table using pgvector
                result = self.client.table("embeddings").insert({
                    "id": id,
                    "embedding": embedding,
                    "metadata": metadata
                }).execute()
            else:
                # Mock storage
                print(f"Mock: Stored embedding {id} with {len(embedding)} dimensions")
            
            print(f"✅ Stored embedding {id} with {len(embedding)} dimensions")
            return True
            
        except Exception as e:
            print(f"❌ Error storing embedding {id}: {e}")
            return False
    
    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 10,
        metadata_filter: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: Query vector to search for
            limit: Maximum number of results
            metadata_filter: Optional metadata filtering
            
        Returns:
            List of similar embeddings with metadata and distances
        """
        try:
            if self.store_type == "chroma" and self.client:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=metadata_filter
                )
                return self._format_chroma_results(results)
                
            elif self.store_type == "supabase" and self.client:
                # Use Supabase RPC for vector similarity search
                results = self.client.rpc("match_embeddings", {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.7,
                    "match_count": limit,
                    "filter": metadata_filter
                }).execute()
                return self._format_supabase_results(results.data)
            
            else:
                # Mock search results
                return self._generate_mock_results(query_embedding, limit)
            
        except Exception as e:
            print(f"❌ Error searching embeddings: {e}")
            return []
    
    def _format_chroma_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format ChromaDB results."""
        formatted = []
        
        try:
            if not results:
                return []
            
            if "ids" not in results or not results["ids"]:
                return []
            
            # ChromaDB returns lists of lists
            ids = results["ids"][0] if results["ids"] else []
            metadatas_raw = results.get("metadatas") or [[]]
            distances_raw = results.get("distances") or [[]]
            embeddings_raw = results.get("embeddings") or [[]]
            
            metadatas = metadatas_raw[0] if metadatas_raw else []
            distances = distances_raw[0] if distances_raw else []
            embeddings = embeddings_raw[0] if embeddings_raw else []
            
            for i, id in enumerate(ids):
                formatted.append({
                    "id": id,
                    "distance": distances[i] if i < len(distances) else 0.0,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "embedding": embeddings[i] if i < len(embeddings) else []
                })
        except Exception as e:
            print(f"❌ Error formatting ChromaDB results: {e}")
            import traceback
            traceback.print_exc()
        
        return formatted
    
    def _format_supabase_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format Supabase results."""
        formatted = []
        
        for result in results:
            formatted.append({
                "id": result.get("id"),
                "distance": result.get("similarity", 0.0),
                "metadata": result.get("metadata", {}),
                "embedding": result.get("embedding", [])
            })
        
        return formatted
    
    def _generate_mock_results(self, query_embedding: List[float], limit: int) -> List[Dict[str, Any]]:
        """Generate mock search results."""
        mock_results = []
        
        for i in range(min(limit, 3)):  # Return up to 3 mock results
            mock_results.append({
                "id": f"mock_embedding_{i}",
                "distance": 0.1 + (i * 0.1),  # Simulate increasing distance
                "metadata": {
                    "persona_id": f"persona_{i}",
                    "name": f"Mock Persona {i}",
                    "created_at": "2024-01-01T00:00:00Z"
                },
                "embedding": [0.0] * len(query_embedding)  # Mock embedding
            })
        
        return mock_results
    
    async def delete_embedding(self, id: str) -> bool:
        """Delete an embedding by ID."""
        try:
            if self.store_type == "chroma" and self.client:
                self.collection.delete(ids=[id])
            elif self.store_type == "supabase" and self.client:
                self.client.table("embeddings").delete().eq("id", id).execute()
            else:
                print(f"Mock: Deleted embedding {id}")
            
            print(f"✅ Deleted embedding {id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting embedding {id}: {e}")
            return False
    
    async def update_embedding(
        self,
        id: str,
        embedding: List[float] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Update an existing embedding."""
        try:
            if self.store_type == "chroma" and self.client:
                # ChromaDB doesn't support updates, need to delete and re-add
                if embedding and metadata:
                    self.collection.delete(ids=[id])
                    self.collection.add(
                        embeddings=[embedding],
                        metadatas=[metadata],
                        ids=[id]
                    )
            elif self.store_type == "supabase" and self.client:
                update_data = {}
                if embedding:
                    update_data["embedding"] = embedding
                if metadata:
                    update_data["metadata"] = metadata
                
                self.client.table("embeddings").update(update_data).eq("id", id).execute()
            else:
                print(f"Mock: Updated embedding {id}")
            
            print(f"✅ Updated embedding {id}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating embedding {id}: {e}")
            return False
    
    async def list_embeddings(
        self,
        limit: int = 100,
        offset: int = 0,
        metadata_filter: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """List embeddings with optional filtering."""
        try:
            if self.store_type == "chroma" and self.client:
                # ChromaDB doesn't have direct pagination
                results = self.collection.get(
                    where=metadata_filter,
                    limit=limit,
                    offset=offset
                )
                return self._format_chroma_get_results(results)
                
            elif self.store_type == "supabase" and self.client:
                query = self.client.table("embeddings").select("*")
                
                if metadata_filter:
                    for key, value in metadata_filter.items():
                        query = query.eq(f"metadata->>{key}", value)
                
                results = query.range(offset, offset + limit - 1).execute()
                return results.data
            
            else:
                # Mock listing
                return self._generate_mock_results([0.0] * 384, min(limit, 5))
            
        except Exception as e:
            print(f"❌ Error listing embeddings: {e}")
            return []
    
    def _format_chroma_get_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format ChromaDB get results."""
        formatted = []
        
        if results and "ids" in results:
            for i, id in enumerate(results["ids"]):
                formatted.append({
                    "id": id,
                    "metadata": results["metadatas"][i] if "metadatas" in results else {},
                    "embedding": results["embeddings"][i] if "embeddings" in results else []
                })
        
        return formatted
    
    def get_status(self) -> Dict[str, Any]:
        """Get vector store status."""
        return {
            "store_type": self.store_type,
            "client_available": self.client is not None,
            "collection_name": "personas" if self.store_type == "chroma" else "embeddings"
        }