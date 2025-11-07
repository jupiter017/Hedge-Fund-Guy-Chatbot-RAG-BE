"""
Setup Script for RAG System
Run this script once to initialize the Pinecone index and load the knowledge base
"""

import os
from rag_system import RAGSystem
from dotenv import load_dotenv

load_dotenv()


def setup_rag():
    """Initialize RAG system with knowledge base"""
    print("="*60)
    print("RAG System Setup - Insomniac Hedge Fund Guy")
    print("="*60)
    
    # Check if API keys are configured
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file")
        return False
    
    if not os.getenv("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY not found in .env file")
        return False
    
    print("\n✅ API keys found")
    
    try:
        # Initialize RAG system
        print("\n📡 Initializing RAG system...")
        rag = RAGSystem()
        
        # Create index
        print("\n🔨 Creating/connecting to Pinecone index...")
        rag.create_index()
        
        # Check for knowledge base file
        docx_path = "RAG Source File.docx"
        
        if not os.path.exists(docx_path):
            print(f"\n❌ Knowledge base file not found: {docx_path}")
            print(f"Please provide the RAG Source File.docx in the backend directory")
            return False
        
        print(f"✅ Found knowledge base: {docx_path}")
        kb_path = docx_path
        
        # Index the knowledge base
        print(f"\n📚 Indexing knowledge base from {kb_path}...")
        rag.index_knowledge_base(kb_path)
        
        # Show index stats
        print("\n📊 Index Statistics:")
        stats = rag.get_index_stats()
        print(f"  Total vectors: {stats.get('total_vector_count', 0)}")
        
        # Test retrieval
        print("\n🧪 Testing retrieval...")
        test_query = "What is momentum trading?"
        contexts = rag.retrieve_context(test_query, top_k=2)
        print(f"  Query: '{test_query}'")
        print(f"  Retrieved {len(contexts)} relevant contexts")
        if contexts:
            print(f"  Top match score: {contexts[0]['score']:.4f}")
        
        print("\n" + "="*60)
        print("✅ RAG System Setup Complete!")
        print("="*60)
        print("\nYou can now run: python main.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = setup_rag()
    exit(0 if success else 1)

