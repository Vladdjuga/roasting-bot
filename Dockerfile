# Simple Dockerfile for the Telegram Roast Bot
FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# The app reads TELEGRAM_API_KEY and HF_READ_TOKEN from the environment.
# Do NOT bake secrets into the image; pass them at runtime via -e or --env-file.

# Start the bot
CMD ["python", "main.py"]
