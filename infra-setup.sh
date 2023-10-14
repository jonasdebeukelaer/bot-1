#!/bin/bash
set -e

PROJECT_ID="crypto-gpt-69"
REGION="europe-west1"
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format 'value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

ENV_VAR_SECRETS_NAME="crypto-gpt-env-secrets"

# Check if the user is logged in
if [[ $(gcloud auth list --filter=status:ACTIVE --format="value(account)") == "" ]]; then
    echo "You are not logged in to gcloud. Please run 'gcloud auth login' and try again."
    exit 1
fi

gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# allow Cloudbuild to work with cloud run services
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role "roles/run.admin"

# allow google cloud run access to ai settings
gcloud secrets add-iam-policy-binding ${ENV_VAR_SECRETS_NAME} \
  --member "serviceAccount:${SERVICE_ACCOUNT}" \
  --role roles/secretmanager.secretAccessor
