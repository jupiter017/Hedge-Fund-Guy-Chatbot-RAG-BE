"""
Demo Helper Script
Provides utilities for testing and demonstrating the system
"""

import json
import os
from datetime import datetime


def display_session_data(session_file: str = "user_data.json"):
    """Display all collected session data in a readable format"""
    if not os.path.exists(session_file):
        print(f"❌ No session data found at {session_file}")
        return
    
    with open(session_file, 'r') as f:
        sessions = json.load(f)
    
    if not sessions:
        print("No sessions found")
        return
    
    print("\n" + "="*70)
    print(f"COLLECTED SESSION DATA - {len(sessions)} Total Sessions")
    print("="*70)
    
    for i, session in enumerate(sessions, 1):
        print(f"\n{'─'*70}")
        print(f"Session #{i}")
        print(f"{'─'*70}")
        print(f"📝 Session ID: {session['session_id']}")
        print(f"📅 Started: {session['timestamp']}")
        print(f"✅ Status: {session['status']}")
        
        if session.get('completed_at'):
            print(f"🏁 Completed: {session['completed_at']}")
        
        print(f"\n👤 Collected Data:")
        data = session['data']
        print(f"   Name: {data['name'] or 'Not collected'}")
        print(f"   Email: {data['email'] or 'Not collected'}")
        print(f"   Income: {data['income'] or 'Not collected'}")
        
        print(f"\n💬 Conversation: {len(session.get('conversation_history', []))} messages")
        
        if session.get('conversation_history'):
            print("\n   Recent exchanges:")
            for entry in session['conversation_history'][-4:]:
                role_icon = "👤" if entry['role'] == 'user' else "🤖"
                content = entry['content'][:80] + "..." if len(entry['content']) > 80 else entry['content']
                print(f"   {role_icon} {content}")
    
    print("\n" + "="*70 + "\n")


def clear_session_data(session_file: str = "user_data.json"):
    """Clear all session data (for testing)"""
    response = input(f"⚠️  Are you sure you want to clear all data in {session_file}? (yes/no): ")
    if response.lower() == 'yes':
        with open(session_file, 'w') as f:
            json.dump([], f)
        print("✅ Session data cleared")
    else:
        print("❌ Operation cancelled")


def export_session_data(session_file: str = "user_data.json", output_file: str = None):
    """Export session data to a formatted file"""
    if not os.path.exists(session_file):
        print(f"❌ No session data found at {session_file}")
        return
    
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"session_export_{timestamp}.txt"
    
    with open(session_file, 'r') as f:
        sessions = json.load(f)
    
    with open(output_file, 'w') as f:
        f.write("INSOMNIAC HEDGE FUND GUY - SESSION EXPORT\n")
        f.write("="*70 + "\n")
        f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Sessions: {len(sessions)}\n")
        f.write("="*70 + "\n\n")
        
        for i, session in enumerate(sessions, 1):
            f.write(f"\nSESSION #{i}\n")
            f.write("-"*70 + "\n")
            f.write(f"Session ID: {session['session_id']}\n")
            f.write(f"Started: {session['timestamp']}\n")
            f.write(f"Status: {session['status']}\n")
            
            if session.get('completed_at'):
                f.write(f"Completed: {session['completed_at']}\n")
            
            f.write(f"\nCollected Data:\n")
            data = session['data']
            f.write(f"  Name: {data['name'] or 'Not collected'}\n")
            f.write(f"  Email: {data['email'] or 'Not collected'}\n")
            f.write(f"  Income: {data['income'] or 'Not collected'}\n")
            
            f.write(f"\nConversation History ({len(session.get('conversation_history', []))} messages):\n")
            for entry in session.get('conversation_history', []):
                role = entry['role'].upper()
                timestamp = entry.get('timestamp', 'N/A')
                content = entry['content']
                f.write(f"\n[{role}] {timestamp}\n{content}\n")
            
            f.write("\n" + "="*70 + "\n")
    
    print(f"✅ Session data exported to: {output_file}")


def check_system_health():
    """Check if all system components are properly configured"""
    print("\n" + "="*70)
    print("SYSTEM HEALTH CHECK")
    print("="*70 + "\n")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    checks = {
        "OpenAI API Key": os.getenv("OPENAI_API_KEY"),
        "Pinecone API Key": os.getenv("PINECONE_API_KEY"),
        "SMTP Server": os.getenv("SMTP_SERVER"),
        "Sender Email": os.getenv("SENDER_EMAIL"),
        "Sender Password": os.getenv("SENDER_PASSWORD"),
        "Recipient Email": os.getenv("RECIPIENT_EMAIL"),
    }
    
    files = {
        "requirements.txt": "requirements.txt",
        "Knowledge Base": "knowledge_base.txt",
        "Main App": "main.py",
        "Chatbot": "chatbot.py",
        "RAG System": "rag_system.py",
        "Data Storage": "data_storage.py",
        "Email Sender": "email_sender.py",
    }
    
    print("Environment Variables:")
    all_env_ok = True
    for name, value in checks.items():
        status = "✅" if value else "❌"
        masked_value = "*" * 20 if value else "Not set"
        print(f"  {status} {name}: {masked_value}")
        if not value:
            all_env_ok = False
    
    print("\nRequired Files:")
    all_files_ok = True
    for name, filepath in files.items():
        exists = os.path.exists(filepath)
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {filepath}")
        if not exists:
            all_files_ok = False
    
    print("\n" + "="*70)
    if all_env_ok and all_files_ok:
        print("✅ System is healthy and ready to run!")
    else:
        print("⚠️  System has configuration issues. Please review above.")
    print("="*70 + "\n")


def interactive_menu():
    """Interactive menu for demo helper functions"""
    while True:
        print("\n" + "="*70)
        print("DEMO HELPER - Insomniac Hedge Fund Guy")
        print("="*70)
        print("\nOptions:")
        print("  1. Display session data")
        print("  2. Export session data")
        print("  3. Clear session data")
        print("  4. Check system health")
        print("  5. Exit")
        print()
        
        choice = input("Select an option (1-5): ").strip()
        
        if choice == "1":
            display_session_data()
        elif choice == "2":
            export_session_data()
        elif choice == "3":
            clear_session_data()
        elif choice == "4":
            check_system_health()
        elif choice == "5":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid option. Please select 1-5.\n")


if __name__ == "__main__":
    interactive_menu()

