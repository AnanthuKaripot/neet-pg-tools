# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Node.js and npm for Tailwind CSS
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Node.js dependency files
COPY package*.json ./
COPY tailwind.config.js ./

# Install Node dependencies
RUN npm install

# Copy application files
COPY . .

# Build Tailwind CSS
RUN npm run build

# Expose port (default 10000, but can be overridden)
EXPOSE 10000

# Start server using gunicorn with dynamic port binding
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]
