# --- Stage 1: Build dependencies ---
FROM python:3.11-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN python -m venv venv && \
    ./venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app

# --- Stage 2: Clean Runtime Image ---
FROM python:3.11-slim
WORKDIR /app

# Copy only the virtual environment and app code from the builder stage
COPY --from=builder /app/venv /app/venv
COPY --from=builder /app/*.py /app/

ENV PATH="/app/venv/bin:$PATH"
EXPOSE 8080
CMD ["python", "app.py"]