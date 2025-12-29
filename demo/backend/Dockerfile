# Django NIS2 Shield Demo Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Railway uses PORT env variable
ENV PORT=8000
EXPOSE $PORT

# Use shell form to expand $PORT variable
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 demo_project.wsgi:application
