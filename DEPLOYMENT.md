# Secure Chat - Deployment Guide

This guide covers deploying Secure Chat to both local Docker and AWS ECS Fargate environments.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Local Docker Deployment](#local-docker-deployment)
- [AWS Deployment](#aws-deployment)
- [Important Considerations](#important-considerations)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

### Local Docker Architecture
```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       v
┌─────────────┐         ┌──────────────┐
│   Nginx     │────────>│   Backend    │
│  Frontend   │  Proxy  │   FastAPI    │
│  Container  │ /api/*  │  Container   │
└─────────────┘         └──────────────┘
```

In local Docker:
- Frontend nginx serves Angular app
- nginx proxies `/api/*` requests to backend container
- Direct container-to-container communication via Docker network

### AWS ECS Architecture
```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       v
┌─────────────┐
│     ALB     │
│  (Port 443) │
└──────┬──────┘
       │
       ├─ /api/*        ──> Backend ECS Service (FastAPI)
       │
       └─ /secure-chat* ──> Frontend ECS Service (Nginx + Angular)
```

In AWS:
- ALB routes `/api/*` to backend ECS service
- ALB routes `/secure-chat*` to frontend ECS service
- Frontend nginx never sees `/api/*` requests (ALB handles routing)

## Local Docker Deployment

### Prerequisites
- Docker and Docker Compose installed
- `.env` file configured with API keys

### Build and Run

```bash
# Build and start both services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## AWS Deployment

### Prerequisites
- AWS CLI configured with credentials
- Docker installed locally
- ECR repositories created:
  - `chat-magic-frontend`
  - `chat-magic-backend`
- ECS cluster created: `chat-magic-cluster`
- ALB configured with routing rules

### Deployment Scripts

#### Deploy Frontend
```bash
./deploy-frontend.sh
```

This script:
1. Builds Docker image for `linux/arm64` (Fargate architecture)
2. Tags image for ECR
3. Pushes to ECR repository
4. Forces new ECS deployment

#### Deploy Backend
```bash
./deploy-backend.sh
```

Similar process for backend service.

### Manual Deployment Steps

If scripts aren't available:

```bash
# 1. Login to ECR
aws ecr get-login-password --region ap-southeast-2 | \
  docker login --username AWS --password-stdin \
  400442376703.dkr.ecr.ap-southeast-2.amazonaws.com

# 2. Build for linux/arm64
cd frontend
docker build --platform linux/arm64 -t chat-magic-frontend:latest .

# 3. Tag for ECR
docker tag chat-magic-frontend:latest \
  400442376703.dkr.ecr.ap-southeast-2.amazonaws.com/chat-magic-frontend:latest

# 4. Push to ECR
docker push 400442376703.dkr.ecr.ap-southeast-2.amazonaws.com/chat-magic-frontend:latest

# 5. Update ECS service
aws ecs update-service \
  --cluster chat-magic-cluster \
  --service chat-magic-frontend \
  --force-new-deployment \
  --region ap-southeast-2

# 6. Monitor deployment
aws ecs describe-services \
  --cluster chat-magic-cluster \
  --services chat-magic-frontend \
  --region ap-southeast-2
```

## Important Considerations

### Critical: Nginx Configuration for Dual Environments

The nginx configuration must work in BOTH local Docker and AWS environments. This is achieved using dynamic DNS resolution:

```nginx
location /api/ {
    # Use Docker's DNS resolver with dynamic resolution
    resolver 127.0.0.11 valid=30s;
    set $backend "chat-magic-backend:8000";
    proxy_pass http://$backend;

    # Graceful error handling for AWS (where ALB handles routing)
    proxy_intercept_errors on;
    error_page 502 503 504 = @backend_unavailable;
}

location @backend_unavailable {
    return 200 "API routing handled by load balancer";
    add_header Content-Type text/plain;
}
```

**Why this is critical:**
- **Without the variable (`set $backend`)**: nginx tries to resolve `chat-magic-backend` at startup
- **In AWS**: This hostname doesn't exist, causing container crash (exit code 1)
- **With the variable**: nginx resolves hostname at request time, not startup
- **In AWS**: Requests never reach this block (ALB handles `/api/*`), so it doesn't matter if the backend is unreachable

**DO NOT** remove or modify this configuration without testing in both environments!

### Environment-Specific Behavior

| Aspect | Local Docker | AWS ECS |
|--------|-------------|---------|
| API Routing | nginx proxies to backend container | ALB routes before nginx |
| Backend URL | `chat-magic-backend:8000` | Not used (ALB handles) |
| Networking | Docker network | AWS VPC with service discovery |
| SSL/TLS | No (HTTP only) | Yes (ALB with ACM certificate) |

### CPU Architecture

**MUST** build for `linux/arm64` when deploying to AWS Fargate (Graviton):

```bash
docker build --platform linux/arm64 -t image-name .
```

Without `--platform`, Docker may build for a different architecture. Always specify explicitly.

### Health Checks

ECS performs health checks on containers. Ensure:
- Frontend: nginx responds to GET `/` with 200 OK
- Backend: FastAPI responds to GET `/api/chat/health` with 200 OK

### Secrets Management

- **Local**: Stored in `.env` file (gitignored)
- **AWS**: Stored in AWS Systems Manager Parameter Store
  - `/chat-magic/openai-api-key`
  - `/chat-magic/confluence-api-key`
  - `/chat-magic/confluence-base-url`
  - `/chat-magic/confluence-email`
  - `/chat-magic/confluence-org-id`

### Persistent Storage

- **Local**: Volumes mounted from host (ChromaDB data)
- **AWS**: EFS volume mounted to backend container
  - File System ID: `fs-04f4621770bb91c19`
  - Mount path: `/mnt/efs`
  - ChromaDB persists to `/mnt/efs/chroma`

## Troubleshooting

### Container Fails to Start in AWS

**Symptom**: Container exits with code 1, deployment keeps failing

**Cause**: nginx trying to resolve backend hostname at startup

**Solution**: Verify nginx config uses variable-based proxy_pass (see configuration above)

### Deployment Stuck "IN_PROGRESS"

**Check task status:**
```bash
aws ecs list-tasks --cluster chat-magic-cluster \
  --service-name chat-magic-frontend \
  --desired-status STOPPED \
  --region ap-southeast-2
```

**Check logs:**
```bash
aws logs tail /ecs/chat-magic-frontend \
  --since 10m \
  --region ap-southeast-2
```

### Health Check Failures

**View service events:**
```bash
aws ecs describe-services \
  --cluster chat-magic-cluster \
  --services chat-magic-frontend \
  --region ap-southeast-2 \
  --query 'services[0].events[:10]'
```

### Platform Mismatch Error

**Error**: "Manifest does not contain descriptor matching platform 'linux/arm64'"

**Cause**: Image built for wrong CPU architecture

**Solution**: Rebuild with `--platform linux/arm64` flag

### API Requests Failing (404 or 502)

**Local Docker:**
- Check backend container is running: `docker ps`
- Check backend logs: `docker logs chat-magic-backend`
- Verify nginx config has `/api/` proxy block

**AWS:**
- Check ALB routing rules include `/api/*` → backend target group
- Verify backend ECS service is healthy
- Check backend target group health

## Monitoring Deployment

### Watch ECS deployment progress:
```bash
watch -n 5 'aws ecs describe-services \
  --cluster chat-magic-cluster \
  --services chat-magic-frontend \
  --region ap-southeast-2 \
  --query "services[0].{Running:runningCount,Desired:desiredCount,Status:deployments[0].rolloutState}"'
```

### Check if deployment reached steady state:
```bash
aws ecs describe-services \
  --cluster chat-magic-cluster \
  --services chat-magic-frontend \
  --region ap-southeast-2 \
  --query 'services[0].events[0].message'
```

Expected output when successful:
```
"(service chat-magic-frontend) has reached a steady state."
```

## Rollback

If deployment fails, ECS maintains the previous working task. To manually rollback:

```bash
# Stop the new deployment
aws ecs update-service \
  --cluster chat-magic-cluster \
  --service chat-magic-frontend \
  --force-new-deployment \
  --region ap-southeast-2
```

Then redeploy the last known good image version.

## Production URL

Live application: https://nicks-apps.com/secure-chat

---

**Last Updated**: December 2025
