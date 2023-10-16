# Use an official Python base image from the Docker Hub
FROM python:3.10-slim AS base

# Install utilities
RUN apt-get update && apt-get install -y \
    curl jq wget git build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


FROM base as release

# Set environment variables
ENV PIP_NO_CACHE_DIR=yes \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="$PATH:/root/.local/bin"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY gcloud-run.sh .
COPY dummy_server.py .

CMD ["./gcloud-run.sh"]
