# Use the official Python image as the base image
FROM python:3.11-slim-bookworm

# Set environment variables to prevent Python from writing .pyc files to disk
# and buffer the stdout/stderr output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install dependencies
# Combine apt-get commands and clean up to reduce image size
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy only requirements first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script and set execute permissions
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy the rest of the project files
COPY . /app/

# Set the entrypoint to the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]