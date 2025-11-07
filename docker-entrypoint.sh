#!/bin/bash
# Docker entrypoint script for backend initialization

set -e

echo "=================================================="
echo "Insomniac Hedge Fund Guy - Backend Startup"
echo "=================================================="
echo ""

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "⏳ Waiting for PostgreSQL to be ready..."
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'postgres'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'hedge_fund_db'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'changeme')
    )
    conn.close()
    print('✅ PostgreSQL is ready')
    exit(0)
except Exception as e:
    exit(1)
" 2>/dev/null; then
            break
        fi
        
        echo "  Attempt $attempt/$max_attempts - PostgreSQL not ready yet, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo "❌ Failed to connect to PostgreSQL after $max_attempts attempts"
        exit 1
    fi
}

# Function to initialize database
initialize_database() {
    echo ""
    echo "🔧 Initializing database..."
    
    if python setup_database.py 2>&1; then
        echo "✅ Database initialized successfully"
    else
        echo "⚠️  Database initialization had issues (may already be initialized)"
    fi
}

# Function to check environment variables
check_environment() {
    echo ""
    echo "🔍 Checking environment variables..."
    
    required_vars=(
        "OPENAI_API_KEY"
        "PINECONE_API_KEY"
        "POSTGRES_HOST"
        "POSTGRES_DB"
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
    )
    
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        echo "✅ All required environment variables are set"
    else
        echo "⚠️  Missing environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "   - $var"
        done
        echo ""
        echo "Please set these variables in your .env file or docker-compose.yml"
    fi
}

# Main execution
main() {
    check_environment
    wait_for_postgres
    initialize_database
    
    echo ""
    echo "=================================================="
    echo "🚀 Starting FastAPI Application..."
    echo "=================================================="
    echo ""
    
    # Execute the command passed to the container
    exec "$@"
}

# Run main function
main "$@"

