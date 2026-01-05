#!/bin/bash
set -e

# Configuration
AWS_REGION="ap-southeast-2"
AWS_ACCOUNT_ID="400442376703"
ECR_REPO="chat-magic-backend"
ECS_CLUSTER="chat-magic-cluster"
ECS_SERVICE="chat-magic-backend"

echo "================================================"
echo "Complete Backend Deployment to AWS ECS"
echo "================================================"

# Step 1: Build the Docker image for linux/amd64
echo ""
echo "Step 1: Building Docker image for linux/amd64..."
cd backend
docker build --platform linux/amd64 -t ${ECR_REPO}:latest .
cd ..

# Step 2: Tag the image for ECR
echo ""
echo "Step 2: Tagging image for ECR..."
docker tag ${ECR_REPO}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest

# Step 3: Login to ECR
echo ""
echo "Step 3: Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Step 4: Push the image to ECR
echo ""
echo "Step 4: Pushing image to ECR..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest

# Step 5: Register new task definition
echo ""
echo "Step 5: Registering new task definition..."
TASK_DEFINITION_ARN=$(aws ecs register-task-definition \
    --cli-input-json file://backend-task-def.json \
    --region ${AWS_REGION} \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "New task definition registered: ${TASK_DEFINITION_ARN}"

# Step 6: Update ECS service with new task definition
echo ""
echo "Step 6: Updating ECS service..."
aws ecs update-service \
    --cluster ${ECS_CLUSTER} \
    --service ${ECS_SERVICE} \
    --task-definition ${TASK_DEFINITION_ARN} \
    --force-new-deployment \
    --region ${AWS_REGION} \
    --query 'service.[serviceName,taskDefinition]' \
    --output table

echo ""
echo "================================================"
echo "Deployment initiated successfully!"
echo "================================================"
echo ""
echo "New task definition: ${TASK_DEFINITION_ARN}"
echo ""
echo "The backend container will start with enhanced logging."
echo "Monitor logs with:"
echo "  aws logs tail /ecs/chat-magic-backend --region ${AWS_REGION} --follow"
echo ""
echo "Check health with:"
echo "  curl https://nicks-apps.com/api/health"
echo ""
