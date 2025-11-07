"""
Layer 3: Data Storage System with PostgreSQL
Handles structured storage of user information using PostgreSQL database
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session as DBSession
from database import Session, ConversationEntry, Settings, get_session_maker, init_database


class DataStorage:
    """Manages storage of user data in PostgreSQL database"""
    
    def __init__(self):
        # Initialize database
        try:
            init_database()
            self.SessionMaker = get_session_maker()
            print("✅ PostgreSQL data storage initialized")
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
            raise
    
    def _get_db(self) -> DBSession:
        """Get database session"""
        return self.SessionMaker()
    
    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        
        db = self._get_db()
        try:
            session = Session(
                session_id=session_id,
                timestamp=datetime.utcnow(),
                status='active',
                data_collected={'name': False, 'email': False, 'income': False},
                conversation_history=[]
            )
            db.add(session)
            db.commit()
            print(f"✅ Created session in PostgreSQL: {session_id}")
            return session_id
        finally:
            db.close()
    
    def update_session_data(self, session_id: str, field: str, value: str):
        """Update a specific field in the session data"""
        db = self._get_db()
        try:
            session = db.query(Session).filter(Session.session_id == session_id).first()
            if session:
                # Update the field
                if field == 'name':
                    session.name = value
                elif field == 'email':
                    session.email = value
                elif field == 'income':
                    session.income = value
                
                # Update data_collected tracker
                data_collected = session.data_collected or {}
                data_collected[field] = True
                session.data_collected = data_collected
                
                db.commit()
                print(f"✅ Updated {field} in PostgreSQL for session {session_id}")
        finally:
            db.close()
    
    def add_conversation_entry(self, session_id: str, role: str, content: str):
        """Add a conversation entry to the database"""
        db = self._get_db()
        try:
            entry = ConversationEntry(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role=role,
                content=content,
                timestamp=datetime.utcnow()
            )
            db.add(entry)
            db.commit()
        finally:
            db.close()
    
    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Retrieve session data by session ID"""
        db = self._get_db()
        try:
            session = db.query(Session).filter(Session.session_id == session_id).first()
            if not session:
                return None
            
            # Get conversation history
            conversations = db.query(ConversationEntry).filter(
                ConversationEntry.session_id == session_id
            ).order_by(ConversationEntry.timestamp).all()
            
            conversation_history = [
                {
                    'role': conv.role,
                    'content': conv.content,
                    'timestamp': conv.timestamp.isoformat()
                }
                for conv in conversations
            ]
            
            return {
                'session_id': session.session_id,
                'timestamp': session.timestamp.isoformat(),
                'status': session.status,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'data': {
                    'name': session.name,
                    'email': session.email,
                    'income': session.income
                },
                'data_collected': session.data_collected or {},
                'conversation_history': conversation_history
            }
        finally:
            db.close()
    
    def mark_session_complete(self, session_id: str):
        """Mark a session as complete"""
        db = self._get_db()
        try:
            session = db.query(Session).filter(Session.session_id == session_id).first()
            if session:
                session.status = 'complete'
                session.completed_at = datetime.utcnow()
                db.commit()
                print(f"✅ Marked session {session_id} as complete in PostgreSQL")
        finally:
            db.close()
    
    def is_data_complete(self, session_id: str) -> bool:
        """Check if all required data has been collected"""
        session_data = self.get_session_data(session_id)
        if not session_data:
            return False
        
        data = session_data['data']
        return all([
            data.get('name'),
            data.get('email'),
            data.get('income')
        ])
    
    def get_all_sessions(self) -> List[Dict]:
        """Retrieve all stored sessions"""
        db = self._get_db()
        try:
            sessions = db.query(Session).order_by(Session.timestamp.desc()).all()
            
            result = []
            for session in sessions:
                # Get conversation history for each session
                conversations = db.query(ConversationEntry).filter(
                    ConversationEntry.session_id == session.session_id
                ).order_by(ConversationEntry.timestamp).all()
                
                conversation_history = [
                    {
                        'role': conv.role,
                        'content': conv.content,
                        'timestamp': conv.timestamp.isoformat()
                    }
                    for conv in conversations
                ]
                
                result.append({
                    'session_id': session.session_id,
                    'timestamp': session.timestamp.isoformat(),
                    'status': session.status,
                    'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                    'data': {
                        'name': session.name,
                        'email': session.email,
                        'income': session.income
                    },
                    'conversation_history': conversation_history
                })
        
            return result
        finally:
            db.close()
    
    def get_collected_fields(self, session_id: str) -> Dict[str, bool]:
        """Return which fields have been collected for a session"""
        session_data = self.get_session_data(session_id)
        if not session_data:
            return {"name": False, "email": False, "income": False}
        
        data = session_data['data']
        return {
            "name": bool(data.get('name')),
            "email": bool(data.get('email')),
            "income": bool(data.get('income'))
        }
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all sessions for admin dashboard"""
        db = self._get_db()
        try:
            from database import Session as SessionModel, ConversationEntry
            
            sessions = db.query(SessionModel).all()
            result = []
            
            for session in sessions:
                # Get conversation history
                messages = db.query(ConversationEntry).filter(
                    ConversationEntry.session_id == session.session_id
                ).order_by(ConversationEntry.timestamp).all()
                
                conversation_history = [
                    {
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat()
                    }
                    for msg in messages
                ]
                
                result.append({
                    'session_id': session.session_id,
                    'status': session.status,
                    'timestamp': session.timestamp.isoformat(),
                    'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                    'data': {
                        'name': session.name,
                        'email': session.email,
                        'income': session.income
                    },
                    'conversation_history': conversation_history,
                    'message_count': len(conversation_history)
                })
            
            return result
        finally:
            db.close()
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value by key"""
        db = self._get_db()
        try:
            from database import Settings
            setting = db.query(Settings).filter(Settings.key == key).first()
            return setting.value if setting else None
        finally:
            db.close()
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value"""
        db = self._get_db()
        try:
            from database import Settings
            setting = db.query(Settings).filter(Settings.key == key).first()
            
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = Settings(key=key, value=value)
                db.add(setting)
            
            db.commit()
            print(f"✅ Saved setting: {key}")
            return True
        except Exception as e:
            print(f"❌ Error saving setting: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings as a dictionary"""
        db = self._get_db()
        try:
            from database import Settings
            settings = db.query(Settings).all()
            return {s.key: s.value for s in settings}
        finally:
            db.close()


if __name__ == "__main__":
    # Test the storage system
    storage = DataStorage()
            
    # Create a session
    session_id = storage.create_session()
    print(f"Created session: {session_id}")
            
    # Update data
    storage.update_session_data(session_id, "name", "John Doe")
    storage.update_session_data(session_id, "email", "john@example.com")
    storage.update_session_data(session_id, "income", "$100k-$150k")
            
    # Add conversation history
    storage.add_conversation_entry(session_id, "user", "Hello!")
    storage.add_conversation_entry(session_id, "assistant", "Hey there!")
            
    # Check if complete
    print(f"Is complete: {storage.is_data_complete(session_id)}")
            
    # Mark complete
    storage.mark_session_complete(session_id)
            
    # Retrieve and display
    session = storage.get_session_data(session_id)
    print("\nSession data:")
    print(f"  Name: {session['data']['name']}")
    print(f"  Email: {session['data']['email']}")
    print(f"  Income: {session['data']['income']}")
    print(f"  Status: {session['status']}")
    print(f"  Messages: {len(session['conversation_history'])}")
