# ==========================================
# Stage 1: Alpine Builder (Isolate compilation)
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
# Stage 2: Pure Alpine Runtime (Zero Debian Layers)
# ==========================================
FROM python:3.11-alpine
WORKDIR /app

# Copy only the compiled virtual environment and code
COPY --from=builder /app/venv /app/venv
COPY --from=builder /app/*.py /app/

ENV PATH="/app/venv/bin:$PATH"
EXPOSE 8080
CMD ["python", "app.py"]