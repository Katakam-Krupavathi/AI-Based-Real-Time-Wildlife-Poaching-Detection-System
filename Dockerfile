# AI-Based Real-Time Wildlife Poaching Detection System
# Multi-Modal Vision + Acoustic Surveillance Container

FROM python:3.12-slim

# Install system runtime dependencies for OpenCV, Librosa, and FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies first for caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and models
COPY . /app

# Expose Central Server dashboard / API port
EXPOSE 5000

# Health check using the self-test endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Launch central server command center
CMD ["python", "automation_scripts/central_server.py"]
