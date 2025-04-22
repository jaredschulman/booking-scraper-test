FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl wget gnupg \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxcomposite1 libxdamage1 libxfixes3 \
    libgbm1 libxrandr2 libasound2 libxss1 libxtst6 \
    libgtk-3-0 libx11-xcb1 libxshmfence1 \
    fonts-liberation libnss3-dev libdrm2 libudev1 \
    ca-certificates unzip && apt-get clean

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser dependencies
RUN python -m playwright install --with-deps

# Run your script
CMD ["python", "booking_scraper_test.py"]
