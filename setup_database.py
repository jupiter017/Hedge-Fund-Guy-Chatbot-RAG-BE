"""
PostgreSQL Database Setup Script
Run this to create the database and tables
"""

import os
import sys
from dotenv import load_dotenv
from database import init_database, get_database_url

load_dotenv()


def check_postgresql_connection():
    """Check if PostgreSQL is accessible"""
    try:
        from sqlalchemy import create_engine
        database_url = get_database_url()
        engine = create_engine(database_url)
        connection = engine.connect()
        connection.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


def setup_database():
    """Setup PostgreSQL database"""
    print("="*60)
    print("PostgreSQL Database Setup - Insomniac Hedge Fund Guy")
    print("="*60)
    
    # Check if DATABASE_URL is configured
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("\n❌ DATABASE_URL not found in .env file")
        print("\nPlease add to your .env file:")
        print("DATABASE_URL=postgresql://postgres:password@localhost:5432/hedge_fund_db")
        return False
    
    print(f"\n📊 Database URL: {database_url}")
    
    # Check PostgreSQL connection
    print("\n🔍 Checking PostgreSQL connection...")
    if not check_postgresql_connection():
        print("\n❌ Cannot connect to PostgreSQL")
        print("\nTroubleshooting steps:")
        print("1. Ensure PostgreSQL is installed")
        print("2. Ensure PostgreSQL server is running")
        print("3. Check DATABASE_URL in .env file")
        print("4. Verify database exists: CREATE DATABASE hedge_fund_db;")
        print("5. Check username and password")
        return False
    
    print("✅ PostgreSQL connection successful")
    
    # Initialize database tables
    print("\n🔨 Creating database tables...")
    try:
        init_database()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ PostgreSQL Database Setup Complete!")
    print("="*60)
    print("\nDatabase is ready to use!")
    print("\nNext steps:")
    print("1. Run: python setup_rag.py")
    print("2. Run: python api.py")
    
    return True


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)

