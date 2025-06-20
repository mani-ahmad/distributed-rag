# FROM python:3.9-slim

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8000

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]

# Start from a slim, stable Python base image for ECS
FROM --platform=linux/amd64 python:3.9-slim

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install dependencies separately for layer caching and avoid timeouts
COPY requirements.txt .

# Use longer timeout and fallback PyPI mirror for reliability
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Copy application code after dependencies
COPY . .

# Expose port ECS expects
EXPOSE 8000

# Start the app using gunicorn (use "app:app" assuming app.py has `app = Flask(...)`)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]

