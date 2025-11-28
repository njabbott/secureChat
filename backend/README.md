insta# Chat Magic - Backend

FastAPI-based backend for Chat Magic, a RAG-powered Confluence chatbot with PII protection.

## Features

- **RAG (Retrieval Augmented Generation)**: Uses ChromaDB vector database and OpenAI for intelligent responses
- **Confluence Integration**: Fetches and indexes content from all Confluence spaces
- **PII Protection**: Automatically detects and filters personally identifiable information using Microsoft Presidio
- **Real-time Indexing**: Manual and scheduled indexing with progress tracking
- **RESTful API**: Clean API endpoints for chat, Confluence info, and indexing control

## Architecture

### Services

- **ConfluenceService**: Integrates with Confluence API to fetch spaces and documents
- **VectorDBService**: Manages ChromaDB for vector storage and semantic search
- **OpenAIService**: Handles chat completions using OpenAI GPT-4o
- **PIIService**: Detects and anonymizes PII using Microsoft Presidio
- **IndexingService**: Coordinates indexing process with progress tracking

### API Endpoints

#### Chat
- `POST /api/chat/message` - Send a message to the chatbot
- `GET /api/chat/health` - Health check for chat services

#### Confluence
- `GET /api/confluence/spaces` - Get all Confluence spaces with document counts
- `GET /api/confluence/spaces/{space_key}/count` - Get document count for a specific space

#### Indexing
- `POST /api/indexing/start` - Start indexing process
- `POST /api/indexing/stop` - Stop indexing process
- `GET /api/indexing/status` - Get indexing status and metadata
- `GET /api/indexing/progress` - Get real-time indexing progress

## Setup

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)

### Installation

1. Create and activate virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download spaCy language model (required for PII detection):
```bash
python -m spacy download en_core_web_lg
```

4. Configure environment variables:
   - Copy `.env.example` to `.env` (or use the existing `.env` in project root)
   - Update with your API keys and configuration

### Running the Server

Development mode with auto-reload:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or run directly:
```bash
cd backend
python -m app.main
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Configuration

All configuration is managed through environment variables in `.env`:

```env
# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o

# Confluence
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_API_KEY=your-confluence-api-key

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION_NAME=confluence_documents

# Indexing
INDEXING_SCHEDULE_HOURS=24  # Auto-index every 24 hours
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Server
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:4200,http://localhost:8000
```

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models/              # Pydantic models
│   │   ├── chat.py
│   │   ├── confluence.py
│   │   └── indexing.py
│   ├── services/            # Business logic
│   │   ├── confluence_service.py
│   │   ├── vector_db_service.py
│   │   ├── openai_service.py
│   │   ├── pii_service.py
│   │   └── indexing_service.py
│   ├── routers/             # API endpoints
│   │   ├── chat.py
│   │   ├── confluence.py
│   │   └── indexing.py
│   └── utils/               # Utility functions
├── requirements.txt
└── README.md
```

### Adding New Features

1. **New Service**: Add to `app/services/`
2. **New Endpoint**: Add to appropriate router in `app/routers/`
3. **New Model**: Add to `app/models/`

## Docker Support

The application is designed to be containerized for AWS ECS Fargate deployment. Docker configuration will be added in a future update.

## Logging

Logs are configured in `main.py` with configurable log level via `LOG_LEVEL` environment variable.

Default format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Security

- PII is automatically detected and filtered before sending to OpenAI
- API keys are managed through environment variables
- CORS is configured to restrict access to specified origins

## Troubleshooting

### PII Detection Not Working

Install the spaCy language model:
```bash
python -m spacy download en_core_web_lg
```

### ChromaDB Issues

Clear the ChromaDB data:
```bash
rm -rf data/chroma
```

Then restart the server and re-index.

### Confluence Connection Issues

Verify your Confluence API key and base URL in `.env`. The API key should have read access to all spaces you want to index.
