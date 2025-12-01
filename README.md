# Secure Chat 
**(aka _Chat Magic_)**

A sophisticated RAG (Retrieval Augmented Generation) chatbot that searches and answers questions from your Confluence documentation, with built-in PII protection.

URL: http://chat-magic-alb-1100203989.ap-southeast-2.elb.amazonaws.com/
(Todo: update to HTTPS)

## Features

- **Intelligent Search**: Uses OpenAI GPT-4o with RAG to provide accurate answers from your Confluence documentation
- **PII Protection**: Automatically detects and filters personally identifiable information using Microsoft Presidio
- **Real-time Indexing**: Manual and scheduled indexing with progress tracking
- **Modern UI**: ChatGPT-like interface with LinkedIn-inspired color palette
- **Source Attribution**: Every answer includes links to source Confluence pages
- **Multi-Space Support**: Indexes and searches across all Confluence spaces
- **Progress Tracking**: Real-time updates during indexing operations

## Architecture

### Backend (FastAPI + Python)
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **ChromaDB**: Vector database for semantic search
- **OpenAI**: GPT-4o for chat completions and embeddings
- **Microsoft Presidio**: PII detection and anonymization
- **Atlassian Python API**: Confluence integration
- **APScheduler**: Scheduled indexing

### Frontend (Angular)
- **Angular 17**: Modern standalone components
- **LinkedIn Color Palette**: Professional, familiar design
- **Responsive Layout**: ChatGPT-inspired interface
- **Real-time Updates**: Live progress during indexing

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher (for frontend)
- OpenAI API key
- Confluence API credentials

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model for PII detection
python -m spacy download en_core_web_lg

# Configure environment variables (already done in .env file)
# The .env file is already configured with your credentials

# Run the backend server
python -m app.main
```

The backend API will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at: http://localhost:4200

### 3. First-Time Setup

1. Open the application at http://localhost:4200
2. Click the "Start Indexing" button in the left sidebar
3. Wait for indexing to complete (progress will be shown in real-time)
4. Start chatting!

## Project Structure

```
chat-magic/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── models/              # Pydantic models
│   │   ├── services/            # Business logic
│   │   │   ├── confluence_service.py
│   │   │   ├── vector_db_service.py
│   │   │   ├── openai_service.py
│   │   │   ├── pii_service.py
│   │   │   └── indexing_service.py
│   │   └── routers/             # API endpoints
│   │       ├── chat.py
│   │       ├── confluence.py
│   │       └── indexing.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/      # Angular components
│   │   │   ├── services/        # API services
│   │   │   └── models/          # TypeScript interfaces
│   │   ├── styles.css          # Global styles (LinkedIn palette)
│   │   └── environments/       # Environment configs
│   ├── package.json
│   └── angular.json
├── data/
│   └── chroma/                  # ChromaDB vector database
├── logs/                        # Application logs
├── .env                         # Environment variables (configured)
├── .gitignore
└── README.md
```

## Configuration

All configuration is managed through the `.env` file in the project root:

```env
# OpenAI
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=gpt-4o

# Confluence
CONFLUENCE_BASE_URL=https://nickabbott001.atlassian.net
CONFLUENCE_API_KEY=<your-key>

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION_NAME=confluence_documents

# Indexing
INDEXING_SCHEDULE_HOURS=24      # Auto-index every 24 hours
CHUNK_SIZE=1000                 # Text chunk size for embeddings
CHUNK_OVERLAP=200               # Overlap between chunks

# Server
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:4200,http://localhost:8000
```

## Usage

### Chatting

1. Type your question in the input box at the bottom
2. Press Enter or click "Send"
3. The chatbot will search your Confluence documentation and provide an answer
4. Source documents are shown below each response

### PII Protection

When PII is detected in your query:
- It's automatically filtered before sending to OpenAI
- A warning is displayed showing what was filtered
- The count and types of PII are shown (e.g., "2 PERSON, 1 EMAIL")

### Indexing

**Manual Indexing:**
1. Click "Start Indexing" in the sidebar
2. Watch real-time progress updates
3. Indexing can be stopped at any time

**Scheduled Indexing:**
- Runs automatically every 24 hours (configurable)
- Keeps your knowledge base up to date

## API Endpoints

### Chat
- `POST /api/chat/message` - Send a message
- `GET /api/chat/health` - Health check

### Confluence
- `GET /api/confluence/spaces` - List all spaces
- `GET /api/confluence/spaces/{key}/count` - Get document count

### Indexing
- `POST /api/indexing/start` - Start indexing
- `POST /api/indexing/stop` - Stop indexing
- `GET /api/indexing/status` - Get status
- `GET /api/indexing/progress` - Get progress

Full API documentation: http://localhost:8000/docs

## Docker Deployment (Future)

The application is designed to be containerized for AWS ECS Fargate deployment. Docker configuration will be added when you're ready to deploy.

Key considerations for AWS deployment:
- Environment variables via AWS Systems Manager Parameter Store
- Persistent storage for ChromaDB (EFS or S3)
- Load balancing for the backend
- Static hosting for the frontend (S3 + CloudFront)

## Troubleshooting

### PII Detection Not Working

Install the spaCy language model:
```bash
python -m spacy download en_core_web_lg
```

### ChromaDB Issues

Clear the database and re-index:
```bash
rm -rf data/chroma
```

### Confluence Connection Issues

Verify your credentials in `.env`:
- `CONFLUENCE_BASE_URL` should be your Atlassian domain
- `CONFLUENCE_API_KEY` should have read access to all spaces

### Frontend Not Connecting to Backend

Check CORS settings in `.env`:
```env
CORS_ORIGINS=http://localhost:4200,http://localhost:8000
```

## Security

- All API keys are stored in `.env` (never committed to git)
- PII is filtered before sending to OpenAI
- CORS is configured to restrict access
- Confluence credentials are encrypted in transit

## Development

### Adding New Features

1. Backend: Add services in `backend/app/services/`
2. API: Add endpoints in `backend/app/routers/`
3. Frontend: Add components in `frontend/src/app/components/`
4. Models: Define in `backend/app/models/` and `frontend/src/app/models/`

### Testing

Backend tests can be added using pytest:
```bash
pip install pytest pytest-asyncio
pytest
```

Frontend tests using Jasmine/Karma:
```bash
npm test
```

## License

Proprietary - Chat Magic

## Support

For issues or questions, please contact the development team.

---

**Built with ❤️ using FastAPI, Angular, OpenAI, and ChromaDB**
