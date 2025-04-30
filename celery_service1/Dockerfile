# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies for pdfplumber
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables 
ENV PYTHONUNBUFFERED=1

# Command to run the Celery worker
CMD ["celery", "-A", "celery_service1.worker_general", "worker", "--loglevel=info", "--queues=general"]
