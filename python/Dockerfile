# ==========================================
# Stage 1: Alpine Builder
# ==========================================
FROM python:3.11-alpine AS builder
WORKDIR /app

# Install system build tools
RUN apk add --no-cache build-base

# Copy requirements and install with strict upgrades to clear CVEs
COPY requirements.txt .
RUN python -m venv venv && \
    ./venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    ./venv/bin/pip install --no-cache-dir --upgrade msgpack && \
    ./venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app

# ==========================================
# Stage 2: Pure Alpine Runtime (Zero Debian)
# ==========================================
FROM python:3.11-alpine
WORKDIR /app

# Copy the clean virtual environment and app code
COPY --from=builder /app/venv /app/venv
COPY --from=builder /app/*.py /app/

ENV PATH="/app/venv/bin:$PATH"
EXPOSE 8080
CMD ["python", "app.py"]