#!/bin/bash
# Quick start script for Docker deployment

set -e

echo "=================================================="
echo "Insomniac Hedge Fund Guy - Docker Quick Start"
echo "=================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo ""
    
    if [ -f env.docker.template ]; then
        echo "📝 Creating .env from template..."
        cp env.docker.template .env
        echo "✅ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your API keys before continuing!"
        echo ""
        echo "Required keys:"
        echo "  - OPENAI_API_KEY"
        echo "  - PINECONE_API_KEY"
        echo "  - POSTGRES_PASSWORD (change the default!)"
        echo ""
        read -p "Press Enter after you've updated .env, or Ctrl+C to exit..."
    else
        echo "❌ Template file not found. Please create .env manually."
        exit 1
    fi
fi

# Validate critical environment variables
source .env 2>/dev/null || true

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" == "sk-your-openai-api-key-here" ]; then
    echo "❌ OPENAI_API_KEY not configured in .env"
    echo "   Please edit .env and add your OpenAI API key"
    exit 1
fi

if [ -z "$PINECONE_API_KEY" ] || [ "$PINECONE_API_KEY" == "your-pinecone-api-key-here" ]; then
    echo "❌ PINECONE_API_KEY not configured in .env"
    echo "   Please edit .env and add your Pinecone API key"
    exit 1
fi

echo "✅ Environment variables configured"
echo ""

# Ask what to do
echo "What would you like to do?"
echo ""
echo "1) Production deployment (docker-compose.yml)"
echo "2) Development setup (docker-compose.dev.yml with hot-reload)"
echo "3) Stop all containers"
echo "4) View logs"
echo "5) Clean reset (remove all containers and volumes)"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting production deployment..."
        echo ""
        
        # Build and start
        docker-compose build
        docker-compose up -d
        
        echo ""
        echo "✅ Services started!"
        echo ""
        echo "📊 Container status:"
        docker-compose ps
        echo ""
        echo "🌐 Access points:"
        echo "   API: http://localhost:${API_PORT:-8000}"
        echo "   API Docs: http://localhost:${API_PORT:-8000}/docs"
        echo "   Health Check: http://localhost:${API_PORT:-8000}/health"
        echo ""
        echo "📝 View logs with: docker-compose logs -f"
        ;;
        
    2)
        echo ""
        echo "💻 Starting development setup..."
        echo ""
        
        # Build and start dev environment
        docker-compose -f docker-compose.dev.yml build
        docker-compose -f docker-compose.dev.yml up -d
        
        echo ""
        echo "✅ Development services started!"
        echo ""
        echo "📊 Container status:"
        docker-compose -f docker-compose.dev.yml ps
        echo ""
        echo "🌐 Access points:"
        echo "   API: http://localhost:${API_PORT:-8000} (with hot-reload)"
        echo "   API Docs: http://localhost:${API_PORT:-8000}/docs"
        echo "   PgAdmin: http://localhost:5050"
        echo "     Email: admin@admin.com"
        echo "     Password: admin"
        echo ""
        echo "📝 View logs with: docker-compose -f docker-compose.dev.yml logs -f"
        ;;
        
    3)
        echo ""
        echo "🛑 Stopping containers..."
        
        # Try both compose files
        docker-compose down 2>/dev/null || true
        docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
        
        echo "✅ All containers stopped"
        ;;
        
    4)
        echo ""
        echo "Which environment?"
        echo "1) Production"
        echo "2) Development"
        read -p "Enter choice [1-2]: " log_choice
        
        case $log_choice in
            1)
                docker-compose logs -f
                ;;
            2)
                docker-compose -f docker-compose.dev.yml logs -f
                ;;
            *)
                echo "Invalid choice"
                exit 1
                ;;
        esac
        ;;
        
    5)
        echo ""
        echo "⚠️  WARNING: This will remove all containers, volumes, and data!"
        read -p "Are you sure? (yes/no): " confirm
        
        if [ "$confirm" == "yes" ]; then
            echo ""
            echo "🧹 Cleaning up..."
            
            # Stop and remove everything
            docker-compose down -v 2>/dev/null || true
            docker-compose -f docker-compose.dev.yml down -v 2>/dev/null || true
            
            # Remove images
            docker-compose down --rmi all 2>/dev/null || true
            docker-compose -f docker-compose.dev.yml down --rmi all 2>/dev/null || true
            
            echo "✅ Cleanup complete!"
        else
            echo "❌ Cleanup cancelled"
        fi
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "For more information, see DOCKER_DEPLOYMENT.md"
echo "=================================================="

