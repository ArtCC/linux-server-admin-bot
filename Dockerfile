# Multi-stage build for smaller image size
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies to a specific location
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# Final stage
FROM python:3.11-slim

LABEL maintainer="your-email@example.com"
LABEL description="Linux Server Admin Bot for Telegram"
LABEL version="1.0.0"

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY bot/ ./bot/
COPY config/ ./config/
COPY main.py .

# Create non-root user for security
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Create logs directory with correct permissions
RUN mkdir -p logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the bot
CMD ["python", "-u", "main.py"]
