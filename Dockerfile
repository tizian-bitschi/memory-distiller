FROM python:3.11-slim

WORKDIR /app

# Copy application code
COPY . .

# Install project and dependencies
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8501

# Environment
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run
CMD ["streamlit", "run", "memory_distiller/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
