"""
Debug script to check what's actually stored in ChromaDB
"""
import asyncio
from storage.vector_store import VectorStore


async def main():
    print("=" * 60)
    print("🔍 CHROMADB DEBUG - Checking stored embeddings")
    print("=" * 60)
    
    vector_store = VectorStore(store_type="chroma")
    
    if not vector_store.client:
        print("❌ ChromaDB not initialized")
        return
    
    # Get all items in the collection
    try:
        collection = vector_store.collection
        count = collection.count()
        print(f"\n📊 Total items in collection: {count}")
        
        # Get all items
        all_items = collection.get()
        
        print(f"\n📋 IDs stored ({len(all_items['ids'])} items):")
        for id in all_items['ids'][:5]:
            print(f"   - {id}")
        if len(all_items['ids']) > 5:
            print(f"   ... and {len(all_items['ids']) - 5} more")
        
        print(f"\n📝 Sample metadata:")
        for i, (id, metadata) in enumerate(zip(all_items['ids'][:3], all_items['metadatas'][:3])):
            print(f"\n   Item {i+1}: {id}")
            print(f"   Type: {metadata.get('type')}")
            print(f"   Has text: {'text' in metadata}")
            if 'text' in metadata:
                print(f"   Text preview: {metadata['text'][:100]}...")
        
        # Try a simple query without filter
        print(f"\n🔍 Testing query (no filter)...")
        query_embedding = [0.1] * 384
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        print(f"   Results: {len(results['ids'][0])} items found")
        
        # Try query WITH filter
        print(f"\n🔍 Testing query (with persona_id filter)...")
        results_filtered = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where={"persona_id": {"$exists": True}}
        )
        print(f"   Results: {len(results_filtered['ids'][0])} items found")
        
        if results_filtered['ids'][0]:
            print(f"\n   Found items:")
            for id, metadata in zip(results_filtered['ids'][0], results_filtered['metadatas'][0]):
                print(f"      - {id}: {metadata.get('type')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
