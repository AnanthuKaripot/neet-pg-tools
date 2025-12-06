FROM python:3.12-slim

# Install Node.js for Tailwind CSS
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tailwind.config.js ./

# Install Node dependencies
RUN npm install

# Copy Python requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Build Tailwind CSS
RUN npm run build

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
