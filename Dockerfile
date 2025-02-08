FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    libffi-dev \
    libfreetype-dev \
    libpng-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/instance

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=production

# Set permissions for SQLite database directory
RUN mkdir -p /app/instance && \
    chown -R www-data:www-data /app/instance

# Use www-data instead of nobody
USER www-data

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]