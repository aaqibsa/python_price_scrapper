#!/bin/bash

# Price Scraper Cron Job Script
# This script ensures proper environment setup for the scraper

# Set the project directory
PROJECT_DIR="/var/www/html/python_price_scrapper"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
source venv/bin/activate || exit 1

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the scraper
python scrape_price.py

# Deactivate virtual environment
deactivate
