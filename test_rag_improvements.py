"""
Test script to verify RAG improvements
This script tests the improved RAG system with various queries
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_rag_improvements():
    """Test the improved RAG system"""
    print("="*70)
    print("RAG SYSTEM IMPROVEMENTS TEST")
    print("="*70)
    
    # Check if required API keys are present
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env")
        return False
    
    if not os.getenv("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY not found in .env")
        return False
    
    print("✅ API keys found\n")
    
    try:
        from rag_system import RAGSystem
        
        # Initialize RAG system
        print("📡 Initializing RAG system...")
        rag = RAGSystem()
        print("✅ RAG system initialized\n")
        
        # Check index stats
        print("📊 Index Statistics:")
        print("-" * 70)
        stats = rag.get_index_stats()
        
        if "error" in stats:
            print(f"❌ Error getting stats: {stats['error']}")
            print("\n⚠️  Your index might not exist or needs to be recreated.")
            print("   Run: python setup_rag.py")
            return False
        
        dimension = stats.get('dimension', 0)
        vector_count = stats.get('total_vector_count', 0)
        
        print(f"  Dimension: {dimension}")
        print(f"  Total Vectors: {vector_count}")
        print(f"  Index Fullness: {stats.get('index_fullness', 0):.2%}")
        
        # Check if dimension is correct
        if dimension == 512:
            print("\n⚠️  WARNING: Index still using 512 dimensions!")
            print("   You need to recreate the index to use 1536 dimensions.")
            print("   Steps:")
            print("   1. Run: python reset_rag.py")
            print("   2. Run: python setup_rag.py")
            return False
        elif dimension == 1536:
            print("\n✅ Index using improved 1536 dimensions!")
        else:
            print(f"\n⚠️  Unexpected dimension: {dimension}")
        
        if vector_count == 0:
            print("\n⚠️  WARNING: Index is empty!")
            print("   Run: python setup_rag.py")
            return False
        
        print()
        
        # Test queries
        test_queries = [
            "What is momentum trading?",
            "How do I manage risk in trading?",
            "What are the best trading strategies?",
            "Tell me about technical indicators"
        ]
        
        print("🧪 Testing Retrieval Quality:")
        print("-" * 70)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n[Test {i}/4] Query: \"{query}\"")
            print()
            
            try:
                # Test with improved parameters
                contexts = rag.retrieve_context(
                    query, 
                    top_k=5, 
                    score_threshold=0.7
                )
                
                if not contexts:
                    print("  ⚠️  No relevant contexts found")
                    print("  Possible reasons:")
                    print("    - Query not related to knowledge base")
                    print("    - Score threshold too strict (try 0.8)")
                    print("    - Index needs more data")
                else:
                    print(f"  ✅ Retrieved {len(contexts)} relevant contexts")
                    print()
                    
                    for j, ctx in enumerate(contexts, 1):
                        score = ctx['score']
                        text_preview = ctx['text'][:100].replace('\n', ' ')
                        
                        if score < 0.3:
                            relevance = "🟢 Very High"
                        elif score < 0.5:
                            relevance = "🟡 High"
                        else:
                            relevance = "🟠 Moderate"
                        
                        print(f"    Context {j}:")
                        print(f"      Relevance: {relevance} (score: {score:.3f})")
                        print(f"      Preview: {text_preview}...")
                        print()
            
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
        
        print("="*70)
        print("✅ RAG IMPROVEMENTS TEST COMPLETE!")
        print("="*70)
        print()
        print("📝 Summary:")
        print(f"  - Embedding Dimension: {dimension} ({'✅ Improved' if dimension == 1536 else '❌ Needs upgrade'})")
        print(f"  - Vector Count: {vector_count} ({'✅' if vector_count > 0 else '❌'})")
        print(f"  - Retrieval: {'✅ Working' if contexts else '⚠️ Check queries'}")
        print()
        
        if dimension == 1536 and vector_count > 0:
            print("🎉 Your RAG system is properly configured with improvements!")
            print()
            print("💡 Tips for best results:")
            print("  1. Ask specific questions related to your knowledge base")
            print("  2. If getting too few results, increase score_threshold to 0.8")
            print("  3. If getting too many results, decrease score_threshold to 0.6")
            print("  4. Monitor relevance scores in the chatbot output")
            return True
        else:
            print("⚠️  Please follow the steps above to complete the improvements.")
            return False
    
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("\nMake sure you've installed all dependencies:")
        print("  pip install -r requirements.txt")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_rag_improvements()
    sys.exit(0 if success else 1)

