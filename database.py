"""
PostgreSQL Database Models and Setup
"""

from sqlalchemy import create_engine, Column, String, DateTime, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class Session(Base):
    """Database model for chat sessions"""
    __tablename__ = 'sessions'
    
    session_id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='active')
    completed_at = Column(DateTime, nullable=True)
    
    # User data
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    income = Column(String(100), nullable=True)
    
    # Metadata
    data_collected = Column(JSON, default=dict)
    conversation_history = Column(JSON, default=list)


class ConversationEntry(Base):
    """Database model for individual conversation messages"""
    __tablename__ = 'conversation_entries'
    
    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), index=True)
    role = Column(String(20))  # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Settings(Base):
    """Database model for application settings"""
    __tablename__ = 'settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database connection
def get_database_url():
    """Get PostgreSQL connection URL from environment"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/hedge_fund_db"
    )


def create_database_engine():
    """Create SQLAlchemy engine"""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=False)
    return engine


def init_database():
    """Initialize database tables"""
    engine = create_database_engine()
    Base.metadata.create_all(engine)
    print("✅ Database tables created successfully")
    return engine


def get_session_maker():
    """Get SQLAlchemy session maker"""
    engine = create_database_engine()
    return sessionmaker(bind=engine)


if __name__ == "__main__":
    # Test database initialization
    init_database()
    print("Database initialization complete!")

