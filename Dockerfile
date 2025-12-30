FROM python:3.12-slim

WORKDIR /app

# Install dependencies
# google-cloud-language, google-generativeai, requests, google-cloud-firestore
COPY pyproject.toml .
RUN pip install --no-cache-dir requests google-generativeai google-cloud-language google-cloud-firestore

# Copy source code
COPY server ./server
COPY prompts ./prompts
# creds are not copied; they should be provided via environment variables or secret manager in production

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Run the application
CMD ["python", "-m", "server.app"]
