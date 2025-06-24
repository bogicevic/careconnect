# CareConnect Multi-Agent System Dockerfile
# Multi-stage build for production deployment

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user
RUN groupadd -r careconnect && useradd -r -g careconnect careconnect

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/careconnect/.local

# Copy application code
COPY agent/ ./agent/
COPY test_system.py .
COPY README.md .

# Set ownership
RUN chown -R careconnect:careconnect /app

# Switch to non-root user
USER careconnect

# Set environment variables
ENV PATH=/home/careconnect/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app'); from agent.agent import CareConnectAgent; print('Health check passed')" || exit 1

# Expose port for A2A communication
EXPOSE 8080

# Default command - can be overridden
CMD ["python", "-m", "adk", "run", "agent"]

# Alternative commands:
# For web interface: CMD ["python", "-m", "adk", "web"]
# For direct testing: CMD ["python", "agent/agent.py"]
# For system test: CMD ["python", "test_system.py"]