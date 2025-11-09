# Multi-stage build for optimized image size
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies in user space
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install system runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ffmpeg \
    portaudio19-dev \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set PATH to include user packages
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Create non-root user for runtime
RUN useradd -m -u 1000 agent && \
    mkdir -p /app /app/apps/content-gen /app/output_logs /app/apps/content-gen/storage

# Copy application code
WORKDIR /app
COPY . .

# Install Playwright browsers as root (required)
RUN playwright install chromium && \
    playwright install-deps chromium

# Set ownership to non-root user
RUN chown -R agent:agent /app

# Switch to non-root user
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import sys; from big_three_realtime_agents import config; sys.exit(0)"

# Expose ports (for potential web UI or API)
EXPOSE 8000 8080

# Default command
CMD ["python", "-m", "apps.realtime-poc.big_three_realtime_agents.main", "--input", "text", "--output", "text"]
