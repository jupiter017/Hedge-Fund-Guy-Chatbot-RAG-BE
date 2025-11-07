"""
Quick Setup Helper for RAG Improvements
Guides you through applying the improvements step by step
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment...")
    print()
    
    issues = []
    
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("❌ OPENAI_API_KEY not found in .env")
    else:
        print("✅ OPENAI_API_KEY found")
    
    if not os.getenv("PINECONE_API_KEY"):
        issues.append("❌ PINECONE_API_KEY not found in .env")
    else:
        print("✅ PINECONE_API_KEY found")
    
    if not os.path.exists("RAG Source File.docx"):
        issues.append("❌ RAG Source File.docx not found in backend directory")
    else:
        print("✅ RAG Source File.docx found")
    
    print()
    
    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   {issue}")
        print()
        return False
    
    return True


def check_current_index():
    """Check current index configuration"""
    print("📊 Checking current Pinecone index...")
    print()
    
    try:
        from rag_system import RAGSystem
        rag = RAGSystem()
        stats = rag.get_index_stats()
        
        if "error" in stats:
            print("⚠️  Index not found or not accessible")
            print()
            return "missing"
        
        dimension = stats.get('dimension', 0)
        vector_count = stats.get('total_vector_count', 0)
        
        print(f"  Dimension: {dimension}")
        print(f"  Vector Count: {vector_count}")
        print()
        
        if dimension == 512:
            print("⚠️  Index is using old configuration (512 dimensions)")
            print("   Needs to be recreated with 1536 dimensions")
            print()
            return "old"
        elif dimension == 1536:
            print("✅ Index is using improved configuration (1536 dimensions)")
            print()
            return "good"
        else:
            print(f"⚠️  Unknown dimension: {dimension}")
            print()
            return "unknown"
    
    except Exception as e:
        print(f"❌ Error checking index: {str(e)}")
        print()
        return "error"


def main():
    """Main setup helper"""
    print()
    print("="*70)
    print(" "*15 + "RAG IMPROVEMENTS SETUP HELPER")
    print("="*70)
    print()
    print("This script will guide you through applying the RAG improvements.")
    print()
    
    # Step 1: Check environment
    print("━"*70)
    print("STEP 1: Environment Check")
    print("━"*70)
    print()
    
    if not check_environment():
        print("❌ Please fix the environment issues above and try again.")
        print()
        return False
    
    # Step 2: Check current index
    print("━"*70)
    print("STEP 2: Current Index Check")
    print("━"*70)
    print()
    
    index_status = check_current_index()
    
    # Step 3: Provide recommendations
    print("━"*70)
    print("STEP 3: Recommendations")
    print("━"*70)
    print()
    
    if index_status == "missing":
        print("📝 Your Pinecone index doesn't exist yet.")
        print()
        print("ACTION REQUIRED:")
        print("  Run: python setup_rag.py")
        print()
        print("This will:")
        print("  ✓ Create a new index with 1536 dimensions")
        print("  ✓ Load and chunk your knowledge base")
        print("  ✓ Generate embeddings and upload to Pinecone")
        print()
    
    elif index_status == "old":
        print("📝 Your Pinecone index is using the old configuration.")
        print()
        print("ACTION REQUIRED:")
        print("  1. Delete the old index:")
        print("     python reset_rag.py")
        print()
        print("  2. Create a new index with improvements:")
        print("     python setup_rag.py")
        print()
        print("⚠️  NOTE: You'll need to re-index your knowledge base.")
        print("   This is necessary because Pinecone doesn't allow")
        print("   changing dimensions on an existing index.")
        print()
    
    elif index_status == "good":
        print("✅ Your index is already configured correctly!")
        print()
        print("OPTIONAL:")
        print("  Run tests to verify everything is working:")
        print("     python test_rag_improvements.py")
        print()
        print("  Or view a detailed comparison:")
        print("     python show_rag_comparison.py")
        print()
    
    else:
        print("⚠️  Unable to determine index status.")
        print()
        print("TRY:")
        print("  1. Check your Pinecone credentials in .env")
        print("  2. Verify your internet connection")
        print("  3. Run: python setup_rag.py")
        print()
    
    # Step 4: Code changes info
    print("━"*70)
    print("STEP 4: Code Changes")
    print("━"*70)
    print()
    print("✅ Code improvements have already been applied to:")
    print("   - backend/rag_system.py")
    print("   - backend/chatbot.py")
    print()
    print("Changes include:")
    print("   ✓ Embedding dimensions: 512 → 1536 (3x richer)")
    print("   ✓ Contexts retrieved: 2 → 5 (2.5x more info)")
    print("   ✓ Chunk size: 500 → 300 (more precise)")
    print("   ✓ Chunk overlap: 50 → 100 (better context)")
    print("   ✓ Added quality filtering (score ≤ 0.7)")
    print("   ✓ Added relevance indicators")
    print()
    
    # Step 5: What's next
    print("━"*70)
    print("STEP 5: What's Next")
    print("━"*70)
    print()
    
    if index_status in ["missing", "old"]:
        print("🚀 After you recreate your index:")
        print()
        print("   1. Test the improvements:")
        print("      python test_rag_improvements.py")
        print()
        print("   2. Start your application:")
        print("      python api.py")
        print()
        print("   3. Ask the chatbot specific questions from your")
        print("      knowledge base and observe how it now references")
        print("      specific facts and information!")
        print()
    else:
        print("🎉 You're all set!")
        print()
        print("   Your RAG system is properly configured.")
        print("   Start your application and enjoy better knowledge reference:")
        print("      python api.py")
        print()
    
    print("━"*70)
    print()
    print("📚 For detailed information, see:")
    print("   - RAG_IMPROVEMENTS.md (comprehensive guide)")
    print("   - python show_rag_comparison.py (visual comparison)")
    print()
    print("="*70)
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup helper cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

