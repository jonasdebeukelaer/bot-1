#!/bin/bash
set -e

PROJECT_ID="crypto-gpt-69"
REGION="europe-west1"

# Check if the user is logged in
if [[ $(gcloud auth list --filter=status:ACTIVE --format="value(account)") == "" ]]; then
    echo "You're not logged in. Doing that now..."
    gcloud auth  application-default login --scopes="https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform"
fi

gcloud config set project $PROJECT_ID

# Submit a new build to Cloud Build
BUILD_ID=$(gcloud builds submit --config cloudbuild.yaml . --format="value(id)" --region $REGION)
echo "Deployment started (Build ID: $BUILD_ID)."

echo ""
echo "Streaming build logs:"
gcloud builds log $BUILD_ID --region $REGION --stream

# Get the status of the completed build
BUILD_STATUS=$(gcloud builds describe $BUILD_ID --region $REGION --format="value(status)")

if [[ $BUILD_STATUS == "SUCCESS" ]]; then
    echo "Deploy successful"
else 
    echo "DEPLOY FAILED"
    exit 1
fi
