# Docker Deployment Guide

This guide explains how to run Chat Magic using Docker containers.

## Prerequisites

- Docker Desktop or Docker Engine (20.10+)
- Docker Compose (2.0+)
- `.env` file configured with your API keys (see below)

## Environment Configuration

Create a `.env` file in the project root with your credentials:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# Confluence
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_API_KEY=your_confluence_api_key_here

# ChromaDB
CHROMA_COLLECTION_NAME=confluence_documents

# Indexing
INDEXING_SCHEDULE_HOURS=24
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

**Important:** Never commit the `.env` file to version control!

## Quick Start

### 1. Build and Start All Services

```bash
docker-compose up --build
```

This will:
- Build the backend Python/FastAPI container
- Build the frontend Angular container with nginx
- Start both services with proper networking
- Create persistent volumes for ChromaDB data

### 2. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 3. First-Time Setup

1. Open http://localhost in your browser
2. Click "Start Indexing" to index your Confluence content
3. Wait for indexing to complete
4. Start chatting!

## Docker Commands

### Start Services (Detached Mode)

```bash
docker-compose up -d
```

### Stop Services

```bash
docker-compose down
```

### Stop and Remove All Data

```bash
docker-compose down -v
```

**Warning:** This will delete the ChromaDB vector database!

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Rebuild After Code Changes

```bash
# Rebuild everything
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
docker-compose up --build frontend
```

### Check Service Health

```bash
docker-compose ps
```

Healthy services will show "(healthy)" in the status.

## Architecture

### Backend Container
- **Base Image**: python:3.11-slim
- **Port**: 8000
- **Key Features**:
  - FastAPI with uvicorn
  - ChromaDB with persistent volume
  - Microsoft Presidio for PII detection
  - spaCy language model pre-downloaded
  - Health checks every 30s

### Frontend Container
- **Build Stage**: node:18-alpine
- **Serve Stage**: nginx:alpine
- **Port**: 80
- **Key Features**:
  - Production-optimized Angular build
  - nginx with gzip compression
  - Security headers
  - Health checks every 30s

### Networking
- Both containers on `chat-magic-network` bridge
- Frontend waits for backend health check before starting
- CORS configured for inter-service communication

### Volumes
- `chroma-data`: Persistent ChromaDB vector database
- `./logs`: Application logs (bind mount)

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker-compose logs backend
```

Common issues:
- Missing `.env` file
- Invalid API keys
- Port conflicts (8000 or 80 already in use)

### Port Conflicts

Change ports in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change 8001 to any available port

  frontend:
    ports:
      - "8080:80"    # Change 8080 to any available port
```

If you change the backend port, update `CORS_ORIGINS` in docker-compose.yml.

### ChromaDB Data Corruption

Remove and recreate the volume:
```bash
docker-compose down
docker volume rm pythonproject_chroma-data
docker-compose up
```

Then re-index your Confluence content.

### Backend Health Check Failing

The backend requires ~40 seconds to start (spaCy model loading). If health checks continue to fail:

1. Check environment variables
2. Verify API keys are valid
3. Increase `start_period` in docker-compose.yml:
   ```yaml
   healthcheck:
     start_period: 60s  # Increase from 40s
   ```

### Frontend Can't Connect to Backend

Verify:
1. Backend is running: `curl http://localhost:8000/api/chat/health`
2. CORS origins include your frontend URL
3. Browser console for detailed error messages

## Development vs Production

### Development Mode (Current)

The current setup is optimized for development:
- Frontend uses environment.ts with localhost:8000
- Logs are visible in real-time
- Volumes allow data persistence between restarts

### Production Considerations

For production deployment:

1. **Use production environment variables**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
   ```

2. **Secure the .env file**
   - Use secrets management (AWS Secrets Manager, etc.)
   - Never expose .env in containers

3. **Use a reverse proxy**
   - nginx or Traefik in front of both services
   - Single domain with /api/* routing to backend

4. **Scale with orchestration**
   - Kubernetes for auto-scaling
   - AWS ECS Fargate (as mentioned in README)

5. **Persistent storage**
   - EFS or S3 for ChromaDB in cloud deployments
   - Regular backups of vector database

## AWS ECS Fargate Deployment

The application is designed for AWS deployment:

### Components
- **ECS Tasks**: Backend and Frontend containers
- **EFS**: Persistent storage for ChromaDB
- **ALB**: Application Load Balancer for routing
- **CloudFront**: CDN for frontend static assets
- **Secrets Manager**: Secure credential storage

### Deployment Steps

1. Push images to ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

   docker tag chat-magic-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/chat-magic-backend:latest
   docker tag chat-magic-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/chat-magic-frontend:latest

   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/chat-magic-backend:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/chat-magic-frontend:latest
   ```

2. Create ECS task definitions
3. Configure ALB routing
4. Mount EFS for ChromaDB
5. Configure secrets in Secrets Manager

## Maintenance

### Update Dependencies

Backend:
```bash
cd backend
# Update requirements.txt
docker-compose build backend
```

Frontend:
```bash
cd frontend
# Update package.json
docker-compose build frontend
```

### Backup ChromaDB

```bash
# Create backup
docker run --rm -v pythonproject_chroma-data:/data -v $(pwd):/backup ubuntu tar czf /backup/chroma-backup.tar.gz /data

# Restore backup
docker run --rm -v pythonproject_chroma-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/chroma-backup.tar.gz -C /
```

### Monitor Resource Usage

```bash
docker stats
```

Shows CPU, memory, and network usage for each container.

## Security Best Practices

1. **Never commit secrets**
   - Use `.env` for local development
   - Use secrets management for production

2. **Keep images updated**
   - Regularly rebuild with latest base images
   - Monitor for security vulnerabilities

3. **Limit container permissions**
   - Containers run as non-root where possible
   - Network segmentation via Docker networks

4. **Use HTTPS in production**
   - Terminate SSL at load balancer or reverse proxy
   - Update frontend environment for https:// API URLs

## Support

For issues with Docker deployment:
1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Test services independently: `docker-compose up backend` or `docker-compose up frontend`

---

**Happy Dockerizing! 🐳**
