"""
FastAPI Application - Main Entry Point with MongoDB
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime
import asyncio
import json

# Import our modules
from chatbot import StockMarketChatbot
from rag_system import RAGSystem
from data_storage import DataStorage
from email_sender import EmailSender

# Initialize FastAPI app
app = FastAPI(
    title="Insomniac Hedge Fund Guy API",
    description="AI-powered stock market chatbot with PostgreSQL and RAG integration",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
rag_system = None
data_storage = None     
email_sender = None
active_sessions = {}  # Store active chatbot sessions

# ==================== Models ====================

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    data_collected: Dict[str, bool]
    is_complete: bool

class SessionCreate(BaseModel):
    pass

class SessionResponse(BaseModel):
    session_id: str
    timestamp: str
    status: str

class SessionData(BaseModel):
    session_id: str
    timestamp: str
    data: Dict[str, Optional[str]]
    conversation_history: List[Dict]
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None

class HealthCheck(BaseModel):
    status: str
    rag_ready: bool
    storage_ready: bool
    email_ready: bool
    postgresql_ready: bool

class SettingsUpdate(BaseModel):
    recipient_email: EmailStr

class SettingsResponse(BaseModel):
    recipient_email: Optional[str]
    email_notifications_enabled: bool
    auto_send_on_complete: bool
    is_configured: bool

# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Initialize system components on startup"""
    global rag_system, data_storage, email_sender
    
    print("🚀 Starting Insomniac Hedge Fund Guy API...")
    
    # Initialize PostgreSQL Storage
    try:
        print("💾 Initializing PostgreSQL storage...")
        data_storage = DataStorage()
        print("✅ PostgreSQL storage initialized")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        raise
    
    # Initialize RAG System
    try:
        print("📚 Loading RAG system...")
        rag_system = RAGSystem()
        print("✅ RAG system ready")
    except Exception as e:
        print(f"⚠️  RAG system initialization failed: {e}")
        rag_system = None
    
    # Initialize Email Sender
    try:
        print("📧 Initializing email sender...")
        email_sender = EmailSender(data_storage=data_storage)
        print("✅ Email sender ready")
    except Exception as e:
        print(f"⚠️  Email sender initialization failed: {e}")
        email_sender = None
    
    print("✅ API Ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down...")
    active_sessions.clear()

# ==================== REST Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Insomniac Hedge Fund Guy API",
        "version": "2.0.0",
        "storage": "PostgreSQL",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Check system health"""
    postgresql_ready = data_storage is not None
    
    return HealthCheck(
        status="healthy",
        rag_ready=rag_system is not None,
        storage_ready=data_storage is not None,
        email_ready=email_sender is not None,
        postgresql_ready=postgresql_ready
    )

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new chat session"""
    if not data_storage:
        raise HTTPException(status_code=500, detail="Data storage not initialized")
    
    session_id = data_storage.create_session()
    session_data = data_storage.get_session_data(session_id)
    
    # Create chatbot instance for this session
    bot = StockMarketChatbot(rag_system=rag_system, data_storage=data_storage)
    bot.initialize_session(session_id)
    active_sessions[session_id] = bot
    
    return SessionResponse(
        session_id=session_id,
        timestamp=session_data["timestamp"],
        status=session_data["status"]
    )

@app.get("/api/sessions/{session_id}", response_model=SessionData)
async def get_session(session_id: str):
    """Get session data"""
    if not data_storage:
        raise HTTPException(status_code=500, detail="Data storage not initialized")
    
    session_data = data_storage.get_session_data(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionData(**session_data)

@app.get("/api/sessions", response_model=List[SessionData])
async def list_sessions(limit: int = 100, skip: int = 0):
    """List all sessions with pagination"""
    if not data_storage:
        raise HTTPException(status_code=500, detail="Data storage not initialized")
    
    sessions = data_storage.get_all_sessions()
    return [SessionData(**session) for session in sessions]

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if not data_storage:
        raise HTTPException(status_code=500, detail="Data storage not initialized")
    
    session_data = data_storage.get_session_data(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Remove from active sessions
    if session_id in active_sessions:
        del active_sessions[session_id]
    
    return {"message": "Session deleted successfully"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Send a message and get a response"""
    if not data_storage:
        raise HTTPException(status_code=500, detail="Data storage not initialized")
    
    session_id = message.session_id
    
    # Get or create chatbot for this session
    if session_id not in active_sessions:
        session_exists = data_storage.get_session_data(session_id)
        if not session_exists:
            raise HTTPException(status_code=404, detail="Session not found")
        
        bot = StockMarketChatbot(rag_system=rag_system, data_storage=data_storage)
        bot.initialize_session(session_id)
        active_sessions[session_id] = bot
    else:
        bot = active_sessions[session_id]
    
    # Generate response
    try:
        response = bot.chat(message.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
    
    # Check if data collection is complete
    is_complete = bot.is_data_collection_complete()
    
    # If complete and not already sent, send email
    if is_complete and data_storage.is_data_complete(session_id):
        session_data = data_storage.get_session_data(session_id)
        if session_data["status"] != "complete":
            data_storage.mark_session_complete(session_id)
            if email_sender:
                try:
                    email_sender.send_user_data(session_data)
                except Exception as e:
                    print(f"Email sending failed: {e}")
    
    return ChatResponse(
        response=response,
        session_id=session_id,
        data_collected=bot.collected_data,
        is_complete=is_complete
    )

@app.get("/api/greeting")
async def get_greeting():
    """Get a random greeting"""
    bot = StockMarketChatbot()
    return {"greeting": bot.get_greeting()}

@app.get("/api/admin/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard statistics"""
    if not data_storage:
        raise HTTPException(status_code=500, detail="Data storage not initialized")
    
    try:
        # Get all sessions
        all_sessions = data_storage.get_all_sessions()
        
        # Calculate statistics
        total_sessions = len(all_sessions)
        completed_sessions = len([s for s in all_sessions if s.get('status') == 'complete'])
        active_sessions = len([s for s in all_sessions if s.get('status') == 'active'])
        
        # Data collection stats
        total_names = len([s for s in all_sessions if s.get('data', {}).get('name')])
        total_emails = len([s for s in all_sessions if s.get('data', {}).get('email')])
        total_incomes = len([s for s in all_sessions if s.get('data', {}).get('income')])
        
        # Calculate total messages
        total_messages = sum(len(s.get('conversation_history', [])) for s in all_sessions)
        
        # Sort all sessions by timestamp (most recent first)
        sorted_sessions = sorted(
            all_sessions, 
            key=lambda x: x.get('timestamp', ''), 
            reverse=True
        )
        
        # System health
        rag_ready = rag_system is not None
        rag_stats = {}
        if rag_ready:
            try:
                rag_stats = rag_system.get_index_stats()
            except Exception as e:
                print(f"Error getting RAG stats: {e}")
                rag_stats = {}
        
        return {
            "statistics": {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "active_sessions": active_sessions,
                "total_messages": total_messages,
                "data_collection": {
                    "names_collected": total_names,
                    "emails_collected": total_emails,
                    "incomes_collected": total_incomes,
                    "completion_rate": round((completed_sessions / total_sessions * 100) if total_sessions > 0 else 0, 1)
                }
            },
            "system_health": {
                "rag_ready": rag_ready,
                "storage_ready": data_storage is not None,
                "email_ready": email_sender is not None,
                "rag_vectors": rag_stats.get('total_vector_count', 0) if rag_stats else 0
            },
            "recent_sessions": sorted_sessions  # Now returns all sessions, sorted by timestamp
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

@app.get("/api/admin/settings", response_model=SettingsResponse)
async def get_settings():
    """Get application settings"""
    if not data_storage:
        raise HTTPException(status_code=500, detail="Data storage not initialized")
    
    try:
        recipient_email = data_storage.get_setting("recipient_email")
        email_notifications_enabled = data_storage.get_setting("email_notifications_enabled")
        auto_send_on_complete = data_storage.get_setting("auto_send_on_complete")
        
        # Convert string booleans to actual booleans
        email_enabled = email_notifications_enabled != "false" if email_notifications_enabled else True
        auto_send = auto_send_on_complete != "false" if auto_send_on_complete else True
        
        is_configured = bool(recipient_email and '@' in recipient_email)
        
        return SettingsResponse(
            recipient_email=recipient_email,
            email_notifications_enabled=email_enabled,
            auto_send_on_complete=auto_send,
            is_configured=is_configured
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

@app.post("/api/admin/settings", response_model=SettingsResponse)
async def update_settings(settings_update: SettingsUpdate):
    """Update application settings"""
    if not data_storage:
        raise HTTPException(status_code=500, detail="Data storage not initialized")
    
    try:
        # Update the recipient email
        success = data_storage.set_setting("recipient_email", settings_update.recipient_email)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save settings")
        
        # Return updated settings
        recipient_email = data_storage.get_setting("recipient_email")
        email_notifications_enabled = data_storage.get_setting("email_notifications_enabled")
        auto_send_on_complete = data_storage.get_setting("auto_send_on_complete")
        
        # Convert string booleans to actual booleans
        email_enabled = email_notifications_enabled != "false" if email_notifications_enabled else True
        auto_send = auto_send_on_complete != "false" if auto_send_on_complete else True
        
        is_configured = bool(recipient_email and '@' in recipient_email)
        
        return SettingsResponse(
            recipient_email=recipient_email,
            email_notifications_enabled=email_enabled,
            auto_send_on_complete=auto_send,
            is_configured=is_configured
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@app.post("/api/chat/stream")
async def chat_stream(message: ChatMessage):
    """Stream a chat response using Server-Sent Events"""
    if not data_storage:
        raise HTTPException(status_code=500, detail="Data storage not initialized")
    
    session_id = message.session_id
    
    # Get or create chatbot for this session
    if session_id not in active_sessions:
        session_exists = data_storage.get_session_data(session_id)
        if not session_exists:
            raise HTTPException(status_code=404, detail="Session not found")
        
        bot = StockMarketChatbot(rag_system=rag_system, data_storage=data_storage)
        bot.initialize_session(session_id)
        active_sessions[session_id] = bot
    else:
        bot = active_sessions[session_id]
    
    async def event_generator():
        """Generate SSE events"""
        try:
            # Stream the chat response
            for chunk in bot.chat_stream(message.message):
                # Send the text chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            
            # After streaming is complete, send metadata
            is_complete = bot.is_data_collection_complete()
            
            # Check if data collection is complete and send email
            if is_complete and data_storage.is_data_complete(session_id):
                session_data = data_storage.get_session_data(session_id)
                if session_data["status"] != "complete":
                    data_storage.mark_session_complete(session_id)
                    if email_sender:
                        try:
                            email_sender.send_user_data(session_data)
                            yield f"data: {json.dumps({'type': 'email_sent', 'message': '✅ Data successfully sent via email!'})}\n\n"
                        except Exception as e:
                            print(f"Email sending failed: {e}")
            
            # Send completion event with metadata
            yield f"data: {json.dumps({'type': 'done', 'data_collected': bot.collected_data, 'is_complete': is_complete})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )

# ==================== WebSocket Endpoint ====================

class ConnectionManager:
    """Manage WebSocket connections"""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, session_id)
    
    # Check if session exists
    session_exists = data_storage.get_session_data(session_id)
    if not session_exists:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    # Get or create chatbot for this session
    if session_id not in active_sessions:
        bot = StockMarketChatbot(rag_system=rag_system, data_storage=data_storage)
        bot.initialize_session(session_id)
        active_sessions[session_id] = bot
    else:
        bot = active_sessions[session_id]
    
    # Send initial greeting
    greeting = bot.get_greeting()
    await manager.send_message({
        "type": "greeting",
        "message": greeting,
        "data_collected": bot.collected_data,
        "is_complete": False
    }, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            user_message = data.get("message", "")
            
            if not user_message:
                continue
            
            # Generate response
            response = bot.chat(user_message)
            
            # Check completion
            is_complete = bot.is_data_collection_complete()
            
            # Send email if complete
            if is_complete and data_storage.is_data_complete(session_id):
                session_data = data_storage.get_session_data(session_id)
                if session_data["status"] != "complete":
                    data_storage.mark_session_complete(session_id)
                    if email_sender:
                        try:
                            email_sender.send_user_data(session_data)
                            await manager.send_message({
                                "type": "email_sent",
                                "message": "✅ Data successfully sent via email!"
                            }, session_id)
                        except Exception as e:
                            print(f"Email sending failed: {e}")
            
            # Send response to client
            await manager.send_message({
                "type": "message",
                "message": response,
                "data_collected": bot.collected_data,
                "is_complete": is_complete
            }, session_id)
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(session_id)

# ==================== Run Server ====================

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
