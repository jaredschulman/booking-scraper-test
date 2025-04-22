FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y wget gnupg curl libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libxshmfence1 libxss1 libxtst6 libx11-xcb1 libgtk-3-0 libx11-dev

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright browsers (esp. chromium)
RUN playwright install --with-deps

# Default command
CMD ["python", "booking_scraper_test.py"]
