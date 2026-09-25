FROM python:3.11-slim

# Update Debian system packages to patch OS vulnerabilities
RUN apt-get update && apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
EXPOSE 8080
CMD ["python", "app.py"]