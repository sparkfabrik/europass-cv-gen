# Multi-stage Docker image for CV generation
# Uses official Python image with LaTeX tools for PDF compilation

FROM python:3.11-slim as base

# Install system dependencies and LaTeX
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    latexmk \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY scripts/ ./scripts/
COPY template/ ./template/
COPY data/ ./data/

# Create build directory with proper permissions
RUN mkdir -p build && chmod 755 build

# Create a non-root user for running the application
RUN groupadd -r cvgen && useradd -r -g cvgen cvgen
RUN chown -R cvgen:cvgen /app

# Switch to non-root user
USER cvgen

# Set entrypoint to the CV generation script
ENTRYPOINT ["python", "scripts/generate_cv.py"]

# Default command shows help
CMD ["--help"]