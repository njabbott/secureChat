#!/bin/bash
set -e

# Configuration
AWS_REGION="ap-southeast-2"
AWS_ACCOUNT_ID="400442376703"
ECR_REPO="chat-magic-backend"
ECS_CLUSTER="chat-magic-cluster"
ECS_SERVICE="chat-magic-backend"

echo "================================================"
echo "Retrying Backend Push & Deployment"
echo "================================================"

# Step 1: Login to ECR
echo ""
echo "Step 1: Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Step 2: Push the image to ECR (retry)
echo ""
echo "Step 2: Pushing image to ECR (retry)..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest

# Step 3: Register new task definition
echo ""
echo "Step 3: Registering new task definition..."
TASK_DEFINITION_ARN=$(aws ecs register-task-definition \
    --cli-input-json file://backend-task-def.json \
    --region ${AWS_REGION} \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "New task definition registered: ${TASK_DEFINITION_ARN}"

# Step 4: Update ECS service with new task definition
echo ""
echo "Step 4: Updating ECS service..."
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
echo "Deployment complete!"
echo "================================================"
echo ""
echo "Monitor logs with:"
echo "  aws logs tail /ecs/chat-magic-backend --region ${AWS_REGION} --follow"
echo ""
