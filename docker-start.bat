@echo off
REM Quick start script for Docker deployment (Windows)

echo ==================================================
echo Insomniac Hedge Fund Guy - Docker Quick Start
echo ==================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed. Please install Docker first.
    echo Visit: https://docs.docker.com/get-docker/
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo Error: Docker Compose is not installed.
        echo Visit: https://docs.docker.com/compose/install/
        exit /b 1
    )
)

echo Docker and Docker Compose are installed
echo.

REM Navigate to backend directory
cd /d "%~dp0"

REM Check if .env exists
if not exist .env (
    echo Warning: .env file not found
    echo.
    
    if exist env.docker.template (
        echo Creating .env from template...
        copy env.docker.template .env
        echo .env file created
        echo.
        echo IMPORTANT: Edit .env and add your API keys before continuing!
        echo.
        echo Required keys:
        echo   - OPENAI_API_KEY
        echo   - PINECONE_API_KEY
        echo   - POSTGRES_PASSWORD ^(change the default!^)
        echo.
        pause
    ) else (
        echo Error: Template file not found. Please create .env manually.
        exit /b 1
    )
)

echo Environment variables configured
echo.

REM Menu
echo What would you like to do?
echo.
echo 1^) Production deployment ^(docker-compose.yml^)
echo 2^) Development setup ^(docker-compose.dev.yml with hot-reload^)
echo 3^) Stop all containers
echo 4^) View logs
echo 5^) Clean reset ^(remove all containers and volumes^)
echo.
set /p choice="Enter choice [1-5]: "

if "%choice%"=="1" (
    echo.
    echo Starting production deployment...
    echo.
    
    docker-compose build
    docker-compose up -d
    
    echo.
    echo Services started!
    echo.
    echo Container status:
    docker-compose ps
    echo.
    echo Access points:
    echo   API: http://localhost:8000
    echo   API Docs: http://localhost:8000/docs
    echo   Health Check: http://localhost:8000/health
    echo.
    echo View logs with: docker-compose logs -f
    
) else if "%choice%"=="2" (
    echo.
    echo Starting development setup...
    echo.
    
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml up -d
    
    echo.
    echo Development services started!
    echo.
    echo Container status:
    docker-compose -f docker-compose.dev.yml ps
    echo.
    echo Access points:
    echo   API: http://localhost:8000 ^(with hot-reload^)
    echo   API Docs: http://localhost:8000/docs
    echo   PgAdmin: http://localhost:5050
    echo     Email: admin@admin.com
    echo     Password: admin
    echo.
    echo View logs with: docker-compose -f docker-compose.dev.yml logs -f
    
) else if "%choice%"=="3" (
    echo.
    echo Stopping containers...
    
    docker-compose down 2>nul
    docker-compose -f docker-compose.dev.yml down 2>nul
    
    echo All containers stopped
    
) else if "%choice%"=="4" (
    echo.
    echo Which environment?
    echo 1^) Production
    echo 2^) Development
    set /p log_choice="Enter choice [1-2]: "
    
    if "%log_choice%"=="1" (
        docker-compose logs -f
    ) else if "%log_choice%"=="2" (
        docker-compose -f docker-compose.dev.yml logs -f
    ) else (
        echo Invalid choice
        exit /b 1
    )
    
) else if "%choice%"=="5" (
    echo.
    echo WARNING: This will remove all containers, volumes, and data!
    set /p confirm="Are you sure? (yes/no): "
    
    if "%confirm%"=="yes" (
        echo.
        echo Cleaning up...
        
        docker-compose down -v 2>nul
        docker-compose -f docker-compose.dev.yml down -v 2>nul
        docker-compose down --rmi all 2>nul
        docker-compose -f docker-compose.dev.yml down --rmi all 2>nul
        
        echo Cleanup complete!
    ) else (
        echo Cleanup cancelled
    )
    
) else (
    echo Invalid choice
    exit /b 1
)

echo.
echo ==================================================
echo For more information, see DOCKER_DEPLOYMENT.md
echo ==================================================
pause

