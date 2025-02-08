# Use official Python slim image as base
FROM python:3.11-slim

# Install system dependencies required for matplotlib and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    libffi-dev \
    libfreetype-dev \
    libpng-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files to container
COPY . .

# Set environment variables
ENV FLASK_APP=app
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]