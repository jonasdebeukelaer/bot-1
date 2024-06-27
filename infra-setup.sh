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

# allow cloud run to access cloud functions
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role "roles/cloudfunctions.admin"

# allow google cloud run access to ai settings
gcloud secrets add-iam-policy-binding ${ENV_VAR_SECRETS_NAME} \
  --member "serviceAccount:${SERVICE_ACCOUNT}" \
  --role roles/secretmanager.secretAccessor

# service account for cloud scheduler
gcloud iam service-accounts create scheduler-invoker \
        --display-name "Cloud Scheduler Invoker" 2>/dev/null

# allow cloud scheduler to invoke cloud functions
gcloud functions add-invoker-policy-binding data-ingestor \
      --region="europe-west1" \
      --member "serviceAccount:scheduler-invoker@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud functions add-invoker-policy-binding bot \
      --region="europe-west1" \
      --member "serviceAccount:scheduler-invoker@${PROJECT_ID}.iam.gserviceaccount.com"

# create scheduler jobs
gcloud scheduler jobs create http data-ingestor-scheduler-job \
        --schedule "25,55 * * * *" \
        --http-method POST \
        --uri "https://europe-west1-crypto-gpt-69.cloudfunctions.net/data-ingestor" \
        --oidc-service-account-email "scheduler-invoker@${PROJECT_ID}.iam.gserviceaccount.com" \
        --time-zone "Etc/UTC"
gcloud scheduler jobs create http bot-scheduler-job \
        --schedule "59 * * * *" \
        --http-method POST \
        --uri "https://europe-west1-crypto-gpt-69.cloudfunctions.net/bot" \
        --oidc-service-account-email "scheduler-invoker@${PROJECT_ID}.iam.gserviceaccount.com" \
        --time-zone "Etc/UTC"

# firebase indexes created manually
