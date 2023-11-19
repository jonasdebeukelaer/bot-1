FROM python:3.8.6-slim AS base

RUN apt-get update && \
    apt-get install -y curl jq wget git build-essential ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


FROM base as release

ENV PIP_NO_CACHE_DIR=yes \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="$PATH:/root/.local/bin"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY gcloud-run.sh .

CMD ["./gcloud-run.sh"]
