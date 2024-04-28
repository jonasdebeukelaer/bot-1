FROM python:3.11.9-slim AS base

RUN apt-get update && \
    apt-get install -y curl jq wget git build-essential ca-certificates openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


FROM base as release

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="$PATH:/root/.local/bin" \
    GOOGLE_CLOUD_PROJECT="crypto-gpt-69"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY gcloud-run.sh .

CMD ["./gcloud-run.sh"]
