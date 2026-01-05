#!/bin/bash
set -e

# Configuration
AWS_REGION="ap-southeast-2"
AWS_ACCOUNT_ID="400442376703"
ECR_REPO="chat-magic-frontend"
ECS_CLUSTER="chat-magic-cluster"
ECS_SERVICE="chat-magic-frontend"

echo "================================================"
echo "Deploying Frontend to AWS ECS"
echo "================================================"

# Step 1: Build the Docker image for linux/amd64 (AWS Fargate)
echo ""
echo "Step 1: Building Docker image for linux/amd64..."
cd frontend
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

# Step 5: Update ECS service to force new deployment
echo ""
echo "Step 5: Updating ECS service..."
aws ecs update-service \
    --cluster ${ECS_CLUSTER} \
    --service ${ECS_SERVICE} \
    --force-new-deployment \
    --region ${AWS_REGION}

echo ""
echo "================================================"
echo "Deployment initiated successfully!"
echo "================================================"
echo ""
echo "The ECS service is now deploying the new frontend image."
echo "You can monitor the deployment in the AWS Console or by running:"
echo ""
echo "  aws ecs describe-services --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE} --region ${AWS_REGION}"
echo ""
echo "Once deployed, access your application at:"
echo "  https://nicks-apps.com/secure-chat"
echo ""
