"""
Main Application - Insomniac Hedge Fund Guy
Integrates all four layers into a functional chatbot system
"""

import os
from dotenv import load_dotenv
from chatbot import StockMarketChatbot
from rag_system import RAGSystem
from data_storage import DataStorage
from email_sender import EmailSender

load_dotenv()


def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🏦  INSOMNIAC HEDGE FUND GUY  🏦                      ║
    ║                                                              ║
    ║        AI-Powered Stock Market Chatbot                       ║
    ║        Sharp. Direct. No Nonsense.                           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease set these in your .env file")
        return False
    
    return True


def run_chatbot():
    """Main chatbot application loop"""
    print_banner()
    
    # Check environment
    if not check_environment():
        return
    
    print("🔧 Initializing system components...\n")
    
    try:
        # Initialize Layer 2: RAG System
        print("📚 Loading RAG system...")
        rag = RAGSystem()
        
        # Check if index is populated
        stats = rag.get_index_stats()
        if stats.get('total_vector_count', 0) == 0:
            print("\n⚠️  Warning: Pinecone index appears empty!")
            print("Please run 'python setup_rag.py' first to index the knowledge base.\n")
            use_rag = False
            rag = None
        else:
            print(f"✅ RAG system ready ({stats.get('total_vector_count', 0)} vectors loaded)")
            use_rag = True
        
        # Initialize Layer 3: Data Storage
        print("💾 Initializing data storage...")
        storage = DataStorage()
        session_id = storage.create_session()
        print(f"✅ Session created: {session_id[:8]}...")
        
        # Initialize Layer 4: Email Sender
        print("📧 Initializing email sender...")
        email_sender = EmailSender()
        print("✅ Email sender ready")
        
        # Initialize Layer 1: Chatbot
        print("🤖 Initializing chatbot...\n")
        bot = StockMarketChatbot(rag_system=rag if use_rag else None, data_storage=storage)
        bot.initialize_session(session_id)
        
        print("="*60)
        print("System ready! Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("="*60)
        print()
        
        # Start conversation
        greeting = bot.get_greeting()
        print(f"🤖 Bot: {greeting}\n")
        
        # Main conversation loop
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("\n🤖 Bot: Later. Don't lose all your money out there. 💰\n")
                    break
                
                # Get bot response
                response = bot.chat(user_input)
                print(f"\n🤖 Bot: {response}\n")
                
                # Check if data collection is complete
                if bot.is_data_collection_complete():
                    if storage.is_data_complete(session_id):
                        # Mark session as complete
                        storage.mark_session_complete(session_id)
                        
                        print("\n" + "="*60)
                        print("✅ All information collected!")
                        print("="*60)
                        
                        # Get session data
                        session_data = storage.get_session_data(session_id)
                        
                        # Display collected data
                        print("\n📋 Collected Information:")
                        print(f"   Name: {session_data['data']['name']}")
                        print(f"   Email: {session_data['data']['email']}")
                        print(f"   Income: {session_data['data']['income']}")
                        
                        # Send email
                        print("\n📧 Sending data via email...")
                        email_success = email_sender.send_user_data(session_data)
                        
                        if email_success:
                            print("✅ Data successfully sent!")
                        else:
                            print("⚠️  Email sending failed (check your email configuration)")
                        
                        print("\nFeel free to continue chatting or type 'quit' to exit.\n")
                
            except KeyboardInterrupt:
                print("\n\n🤖 Bot: Interrupted. Catch you later. 👋\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
                continue
        
        # Final summary
        print("\n" + "="*60)
        print("Session Summary")
        print("="*60)
        
        session_data = storage.get_session_data(session_id)
        print(f"Session ID: {session_id}")
        print(f"Status: {session_data['status']}")
        print(f"Messages exchanged: {len(session_data['conversation_history'])}")
        
        collected = storage.get_collected_fields(session_id)
        print(f"Data collected: {sum(collected.values())}/3 fields")
        
        print("\n💾 Session data saved to: user_data.json")
        print()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Application entry point"""
    try:
        run_chatbot()
    except Exception as e:
        print(f"❌ Application error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

