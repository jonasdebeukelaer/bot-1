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
BUILD_ID=$(gcloud builds submit --config cloudbuild.yaml . --async --format="value(id)" --region $REGION)
echo "Deployment started (Build ID: $BUILD_ID)."

echo ""
echo "Streaming build logs:"
gcloud beta builds log $BUILD_ID --region $REGION --stream

# Polling the build status
while : ; do
    BUILD_STATUS=$(gcloud builds describe $BUILD_ID --region $REGION --format="value(status)")
    if [[ $BUILD_STATUS != "WORKING" && $BUILD_STATUS != "QUEUED" ]]; then
        break
    fi
    echo "Build is still in progress... checking again in 10 seconds."
    sleep 10
done

if [[ $BUILD_STATUS == "SUCCESS" ]]; then
    echo "Deploy successful"
else 
    echo "DEPLOY FAILED"
    exit 1
fi
