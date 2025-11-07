# Backend API

FastAPI-based REST API and WebSocket server for the Insomniac Hedge Fund Guy chatbot system.

## Features

- **REST API**: Complete CRUD operations for sessions
- **WebSocket**: Real-time chat communication
- **Clean Architecture**: Separated concerns and modular design
- **Async Support**: Fast, non-blocking operations
- **CORS Enabled**: Ready for frontend integration

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.template` to `.env`
2. Fill in your API keys and credentials

## Running the Server

### Development Mode (with auto-reload):
```bash
python api.py
```

Or:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### REST Endpoints

#### Health Check
```
GET /health
```
Returns system health status

#### Create Session
```
POST /api/sessions
```
Creates a new chat session

#### Get Session
```
GET /api/sessions/{session_id}
```
Retrieves session data

#### List All Sessions
```
GET /api/sessions
```
Returns all sessions

#### Chat
```
POST /api/chat
Body: {"message": "your message", "session_id": "session-id"}
```
Sends message and receives response

#### Get Greeting
```
GET /api/greeting
```
Returns a random greeting

### WebSocket Endpoint

```
WS /ws/{session_id}
```

Real-time bidirectional communication

**Client sends:**
```json
{
  "message": "What do you think about momentum trading?"
}
```

**Server responds:**
```json
{
  "type": "message",
  "message": "Bot response here...",
  "data_collected": {
    "name": false,
    "email": false,
    "income": false
  },
  "is_complete": false
}
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── api.py                  # FastAPI application
├── chatbot.py             # Chatbot logic (Layer 1)
├── rag_system.py          # RAG integration (Layer 2)
├── data_storage.py        # Data storage (Layer 3)
├── email_sender.py        # Email delivery (Layer 4)
├── knowledge_base.txt     # Knowledge source
├── requirements.txt       # Dependencies
├── .env.template         # Environment template
└── README.md             # This file
```

## Testing

### Test REST API
```bash
curl http://localhost:8000/health
```

### Test Session Creation
```bash
curl -X POST http://localhost:8000/api/sessions
```

### Test Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "your-session-id"}'
```

## WebSocket Testing

Use a WebSocket client or the frontend application.

Example with Python:
```python
import asyncio
import websockets
import json

async def test_websocket():
    async with websockets.connect('ws://localhost:8000/ws/test-session-id') as websocket:
        # Receive greeting
        greeting = await websocket.recv()
        print(f"Received: {greeting}")
        
        # Send message
        await websocket.send(json.dumps({"message": "Hello!"}))
        
        # Receive response
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(test_websocket())
```

## Error Handling

The API includes comprehensive error handling:
- 404: Resource not found
- 500: Internal server error
- WebSocket disconnection handling
- Graceful degradation if RAG/email unavailable

## Performance

- Async/await for non-blocking operations
- Connection pooling for databases
- Efficient WebSocket management
- Optimized for concurrent connections

## Security Notes

- CORS configured for frontend origins
- Environment variables for secrets
- Input validation with Pydantic
- WebSocket authentication recommended for production

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Systemd Service
Create `/etc/systemd/system/hedge-fund-api.service`:
```ini
[Unit]
Description=Hedge Fund Guy API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

## Monitoring

Consider adding:
- Logging (structlog, loguru)
- Metrics (Prometheus)
- Tracing (OpenTelemetry)
- Health checks (kubernetes probes)

## License

Part of the Insomniac Hedge Fund Guy assessment project.

