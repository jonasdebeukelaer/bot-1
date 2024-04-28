# /bin/bash
set -e

docker build -t bot-1-local-run .

docker run \
    -v "$(pwd)/.env:/mnt2/secrets.env" \
    -v "${HOME}/.config/gcloud:/root/.config/gcloud" \
    -e "GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json" \
    bot-1-local-run
