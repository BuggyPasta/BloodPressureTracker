FROM python:3.11-slim

# Install system dependencies (removed some that were only needed for matplotlib)
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/config /app/db

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=production

# Ensure directories exist and have proper permissions
RUN chmod 777 /app/data /app/config /app/db

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]