# ==========================================
# Stage 1: Alpine Builder
# ==========================================
FROM python:3.11-alpine AS builder
WORKDIR /app

RUN apk add --no-cache build-base

COPY requirements.txt .
RUN python -m venv venv && \
    ./venv/bin/pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" wheel && \
    ./venv/bin/pip install --no-cache-dir --upgrade "msgpack>=1.2.1" && \
    ./venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app

# ==========================================
# Stage 2: Pure Alpine Runtime
# ==========================================
FROM python:3.11-alpine
WORKDIR /app

COPY --from=builder /app/venv /app/venv
COPY --from=builder /app/*.py /app/

ENV PATH="/app/venv/bin:$PATH"
EXPOSE 8080
CMD ["python", "app.py"]