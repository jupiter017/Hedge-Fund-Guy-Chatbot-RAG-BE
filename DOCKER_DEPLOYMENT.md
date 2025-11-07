# 🐳 Docker Deployment Guide

Complete guide for deploying the Insomniac Hedge Fund Guy backend using Docker.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Production Deployment](#production-deployment)
3. [Development Setup](#development-setup)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Usage](#advanced-usage)

---

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+ and Docker Compose 2.0+
- Your API keys (OpenAI, Pinecone)
- PostgreSQL not already running on port 5432

### 1. Set Up Environment Variables

```bash
cd backend
cp .env.docker.example .env
# Edit .env with your actual credentials
```

### 2. Build and Run

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 4. Stop the Application

```bash
docker-compose down

# To also remove volumes (database data)
docker-compose down -v
```

---

## 🏭 Production Deployment

### File Structure

```
backend/
├── Dockerfile              # Production-optimized image
├── docker-compose.yml      # Production compose file
├── .dockerignore          # Files to exclude from image
├── docker-entrypoint.sh   # Startup script
├── .env                   # Environment variables (create this)
└── .env.docker.example    # Template for .env
```

### Step-by-Step Production Deployment

#### 1. Configure Environment

```bash
cd backend
cp .env.docker.example .env
nano .env  # or use your preferred editor
```

**Required Configuration:**

```env
# OpenAI (Required)
OPENAI_API_KEY=sk-your-real-api-key

# Pinecone (Required)
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=hedge-fund-knowledge

# PostgreSQL (Change defaults!)
POSTGRES_PASSWORD=your-strong-password-here
POSTGRES_DB=hedge_fund_db
POSTGRES_USER=postgres

# Email (Optional)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com
```

#### 2. Create Required Directories

```bash
# Create data directory for knowledge base files (optional)
mkdir -p data
```

#### 3. Build and Deploy

```bash
# Build the Docker image
docker-compose build

# Start all services
docker-compose up -d

# Watch the logs
docker-compose logs -f
```

#### 4. Initialize RAG System (First Time Only)

```bash
# If you need to set up your RAG index
docker-compose exec backend python setup_rag.py

# Or if you have a knowledge base file
docker cp "RAG Source File.docx" hedge_fund_backend:/app/data/
docker-compose exec backend python setup_rag.py
```

#### 5. Verify Deployment

```bash
# Check health
curl http://localhost:8000/health

# Check API docs
curl http://localhost:8000/docs

# Check database connection
docker-compose exec backend python -c "from database import check_database; check_database()"
```

### Production Best Practices

#### Security

1. **Change Default Passwords**
   ```env
   POSTGRES_PASSWORD=use-a-strong-random-password
   ```

2. **Use Secrets Management** (for production)
   - Use Docker secrets or external secret managers
   - Don't commit `.env` to version control

3. **Network Security**
   - Use reverse proxy (nginx/traefik) for HTTPS
   - Don't expose database port externally
   - Configure firewall rules

#### Performance

1. **Resource Limits** (add to docker-compose.yml)
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 4G
           reservations:
             cpus: '1'
             memory: 2G
   ```

2. **Database Tuning**
   ```yaml
   postgres:
     command:
       - "postgres"
       - "-c"
       - "shared_buffers=256MB"
       - "-c"
       - "max_connections=100"
   ```

3. **Multiple Workers** (for high traffic)
   ```yaml
   backend:
     command: uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
   ```

#### Monitoring

1. **Container Health**
   ```bash
   docker-compose ps
   docker stats
   ```

2. **Application Logs**
   ```bash
   docker-compose logs -f backend
   docker-compose logs --tail=100 postgres
   ```

3. **Database Backup**
   ```bash
   docker-compose exec postgres pg_dump -U postgres hedge_fund_db > backup.sql
   ```

---

## 💻 Development Setup

For local development with hot-reload:

### 1. Use Development Docker Compose

```bash
cd backend

# Build and start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend
```

### 2. Features

- **Hot Reload**: Code changes automatically restart the server
- **Volume Mounting**: Your local code is mounted into container
- **PgAdmin**: Database management UI at http://localhost:5050
  - Email: `admin@admin.com`
  - Password: `admin`
- **Different Port**: Uses 5433 for PostgreSQL to avoid conflicts

### 3. Development Commands

```bash
# Restart backend only
docker-compose -f docker-compose.dev.yml restart backend

# Access backend shell
docker-compose -f docker-compose.dev.yml exec backend bash

# Run tests
docker-compose -f docker-compose.dev.yml exec backend python test_rag_improvements.py

# Stop all services
docker-compose -f docker-compose.dev.yml down
```

---

## ⚙️ Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ | - | OpenAI API key |
| `PINECONE_API_KEY` | ✅ | - | Pinecone API key |
| `PINECONE_INDEX_NAME` | ❌ | hedge-fund-knowledge | Pinecone index name |
| `POSTGRES_HOST` | ❌ | postgres | Database host |
| `POSTGRES_PORT` | ❌ | 5432 | Database port |
| `POSTGRES_DB` | ❌ | hedge_fund_db | Database name |
| `POSTGRES_USER` | ❌ | postgres | Database user |
| `POSTGRES_PASSWORD` | ✅ | - | Database password |
| `SMTP_SERVER` | ❌ | smtp.gmail.com | SMTP server |
| `SMTP_PORT` | ❌ | 587 | SMTP port |
| `SENDER_EMAIL` | ❌ | - | Sender email |
| `SENDER_PASSWORD` | ❌ | - | Email password |
| `API_PORT` | ❌ | 8000 | API port |

### Docker Compose Services

#### Backend Service
- **Image**: Built from `Dockerfile`
- **Port**: 8000 (configurable via `API_PORT`)
- **Health Check**: HTTP GET /health every 30s
- **Restart Policy**: unless-stopped

#### PostgreSQL Service
- **Image**: postgres:16-alpine
- **Port**: 5432 (configurable via `POSTGRES_PORT`)
- **Health Check**: pg_isready every 10s
- **Data Persistence**: Named volume `postgres_data`

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Port already in use"

**Problem**: Port 8000 or 5432 already in use

**Solution**:
```bash
# Change ports in .env
API_PORT=8001
POSTGRES_PORT=5433

# Or stop conflicting services
sudo systemctl stop postgresql
```

#### 2. "Connection refused to PostgreSQL"

**Problem**: Backend can't connect to database

**Solution**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart services
docker-compose restart postgres backend
```

#### 3. "Module not found" errors

**Problem**: Missing Python dependencies

**Solution**:
```bash
# Rebuild the image
docker-compose build --no-cache backend
docker-compose up -d
```

#### 4. "Pinecone dimension mismatch"

**Problem**: Old index with 512 dimensions vs new 1536

**Solution**:
```bash
# Reset and recreate RAG index
docker-compose exec backend python reset_rag.py
docker-compose exec backend python setup_rag.py
```

#### 5. "Permission denied" errors

**Problem**: File permission issues in container

**Solution**:
```bash
# Fix ownership
sudo chown -R 1000:1000 data/

# Or run as root (not recommended for production)
docker-compose exec -u root backend bash
```

### Debugging Commands

```bash
# View container logs
docker-compose logs -f backend
docker-compose logs --tail=100 postgres

# Access backend shell
docker-compose exec backend bash

# Check environment variables
docker-compose exec backend env

# Test database connection
docker-compose exec backend python -c "
from database import check_database
check_database()
"

# Check Python dependencies
docker-compose exec backend pip list

# View running processes
docker-compose exec backend ps aux
```

### Clean Reset

If everything is broken:

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

---

## 🔧 Advanced Usage

### Using Docker without Docker Compose

```bash
# Build image
docker build -t hedge-fund-backend:latest .

# Run PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=hedge_fund_db \
  -p 5432:5432 \
  postgres:16-alpine

# Run backend
docker run -d \
  --name backend \
  --link postgres:postgres \
  -e OPENAI_API_KEY=your-key \
  -e PINECONE_API_KEY=your-key \
  -e POSTGRES_HOST=postgres \
  -e POSTGRES_PASSWORD=changeme \
  -p 8000:8000 \
  hedge-fund-backend:latest
```

### Multi-Stage Build Benefits

The production Dockerfile uses multi-stage builds:

- **Stage 1 (builder)**: Installs build dependencies and Python packages
- **Stage 2 (runtime)**: Copies only necessary files, resulting in smaller image

**Size Comparison**:
- Without multi-stage: ~1.2 GB
- With multi-stage: ~600 MB

### Custom Entrypoint

Create `docker-entrypoint.sh` for custom initialization:

```bash
chmod +x docker-entrypoint.sh

# Use in docker-compose.yml
services:
  backend:
    entrypoint: ["/app/docker-entrypoint.sh"]
    command: ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Database Migrations

```bash
# Create backup before migration
docker-compose exec postgres pg_dump -U postgres hedge_fund_db > backup.sql

# Run migration script
docker-compose exec backend python your_migration_script.py

# Restore if needed
docker-compose exec -T postgres psql -U postgres hedge_fund_db < backup.sql
```

### Scaling with Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml hedge-fund

# Scale backend
docker service scale hedge-fund_backend=3

# View services
docker stack services hedge-fund
```

### Integration with CI/CD

**GitHub Actions Example**:

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: |
          cd backend
          docker build -t myregistry/hedge-fund-backend:${{ github.sha }} .
      
      - name: Push to registry
        run: docker push myregistry/hedge-fund-backend:${{ github.sha }}
      
      - name: Deploy to server
        run: |
          ssh user@server "docker pull myregistry/hedge-fund-backend:${{ github.sha }}"
          ssh user@server "docker-compose up -d"
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Built-in health check
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready

# Container health status
docker inspect --format='{{.State.Health.Status}}' hedge_fund_backend
```

### Log Management

```bash
# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Since specific time
docker-compose logs --since 2024-01-01T00:00:00

# Save logs to file
docker-compose logs > application.log
```

### Database Backup & Restore

```bash
# Automated backup
docker-compose exec postgres pg_dump -U postgres hedge_fund_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U postgres hedge_fund_db

# Scheduled backups (cron)
0 2 * * * cd /path/to/backend && docker-compose exec postgres pg_dump -U postgres hedge_fund_db > /backups/backup_$(date +\%Y\%m\%d).sql
```

---

## 🎯 Summary

### Production Deployment Checklist

- [ ] Configure `.env` with all required credentials
- [ ] Change default PostgreSQL password
- [ ] Build Docker images: `docker-compose build`
- [ ] Start services: `docker-compose up -d`
- [ ] Initialize database: Automatic on first run
- [ ] Set up RAG index: `docker-compose exec backend python setup_rag.py`
- [ ] Verify health: `curl http://localhost:8000/health`
- [ ] Configure reverse proxy (nginx/traefik) for HTTPS
- [ ] Set up monitoring and log aggregation
- [ ] Configure automated backups
- [ ] Test failover and recovery procedures

### Development Setup Checklist

- [ ] Use `docker-compose.dev.yml`
- [ ] Mount local code for hot-reload
- [ ] Access PgAdmin at http://localhost:5050
- [ ] Use different ports to avoid conflicts
- [ ] Install development dependencies

---

## 🆘 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify environment: `docker-compose exec backend env`
3. Test connections: `docker-compose exec backend python -c "from database import check_database; check_database()"`
4. Clean restart: `docker-compose down && docker-compose up -d`

For more help, see:
- **API Documentation**: http://localhost:8000/docs
- **Docker Documentation**: https://docs.docker.com
- **FastAPI Documentation**: https://fastapi.tiangolo.com

---

**Happy Deploying! 🚀**

