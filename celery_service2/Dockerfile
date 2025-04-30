# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (if needed)
ENV PYTHONUNBUFFERED=1

# Command to run the Celery worker for streaming tasks
CMD ["celery", "-A", "celery_service2.worker_stream", "worker", "--loglevel=info", "--queues=stream"]
