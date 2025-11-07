"""
Reset RAG System - Delete and recreate the Pinecone index
Run this script to clear existing vectors and prepare for fresh indexing
"""

import os
from rag_system import RAGSystem
from dotenv import load_dotenv

load_dotenv()


def reset_rag():
    """Delete existing index and prepare for fresh indexing"""
    print("="*60)
    print("RAG System Reset - Deleting Existing Index")
    print("="*60)
    
    try:
        print("\n📡 Initializing RAG system...")
        rag = RAGSystem()
        
        index_name = os.getenv("PINECONE_INDEX_NAME", "hedge-fund-knowledge")
        
        # Check if index exists
        existing_indexes = [index.name for index in rag.pc.list_indexes()]
        
        if index_name in existing_indexes:
            print(f"\n🗑️  Found existing index: {index_name}")
            
            # Get index stats
            stats = rag.get_index_stats()
            print(f"   Current vectors: {stats.get('total_vector_count', 0)}")
            
            response = input(f"\n⚠️  Are you sure you want to delete '{index_name}'? (yes/no): ")
            
            if response.lower() == 'yes':
                print(f"\n🗑️  Deleting index '{index_name}'...")
                rag.pc.delete_index(index_name)
                print(f"✅ Index '{index_name}' deleted successfully")
                print("\n" + "="*60)
                print("✅ Reset Complete!")
                print("="*60)
                print("\nNext steps:")
                print("  1. Run: python setup_rag.py")
                print("  2. This will create a fresh index with cleaned data")
            else:
                print("❌ Operation cancelled")
        else:
            print(f"\n✅ Index '{index_name}' does not exist. Nothing to delete.")
            print("\nNext steps:")
            print("  Run: python setup_rag.py to create a new index")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Reset failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = reset_rag()
    exit(0 if success else 1)

