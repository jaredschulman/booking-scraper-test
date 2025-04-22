FROM python:3.11-slim

# Install system dependencies (includes all required for Chromium)
RUN apt-get update && apt-get install -y \
    curl wget gnupg unzip \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxcomposite1 libxdamage1 libxfixes3 \
    libgbm1 libxrandr2 libasound2 libxss1 libxtst6 \
    libgtk-3-0 libx11-xcb1 libxshmfence1 \
    fonts-liberation libnss3-dev libdrm2 libudev1 \
    ca-certificates \
    libsoup-3.0-0 \
    libgstgl-1.0-0 \
    libgstcodecparsers-1.0-0 \
    libenchant-2-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libgles2 \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and required browsers
RUN python -m playwright install --with-deps

# Run script
CMD ["python", "booking_scraper_test.py"]
