# ==========================================
# Stage 1: Builder Stage
# ==========================================
FROM python:3.11-alpine AS builder
WORKDIR /app

RUN apk add --no-cache build-base

COPY requirements.txt .
RUN python -m venv venv && \
    ./venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    ./venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app

# ==========================================
# Stage 2: Clean Production Runtime Stage
# ==========================================
FROM python:3.11-alpine
WORKDIR /app

COPY --from=builder /app/venv /app/venv
COPY --from=builder /app/*.py /app/

ENV PATH="/app/venv/bin:$PATH"
EXPOSE 8080
CMD ["python", "app.py"]