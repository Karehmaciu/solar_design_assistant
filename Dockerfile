FROM python:3.10.13-slim-bookworm

# Create a non-root user for added security
RUN groupadd -r solarapp && useradd -r -g solarapp solarapp

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies with pinned versions
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pip-audit && \
    pip-audit && \
    apt-get update && \
    apt-get install -y --no-install-recommends tini && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Create logs directory with proper permissions
RUN mkdir -p logs && chown -R solarapp:solarapp /app

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV PORT=8003

# Important: The OpenAI API key should be passed as an environment variable at runtime
# DO NOT hardcode API keys in the Dockerfile

# Switch to non-root user
USER solarapp

# Use tini as init system
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run with gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT "app:create_app('production')" --workers 4