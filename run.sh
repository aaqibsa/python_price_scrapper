#!/bin/bash
# Python Scrapper - Unix Run Script

echo "Python Scrapper"
echo "================"

if [ $# -eq 0 ]; then
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  url-manager    Start the web interface"
    echo "  scraper        Run the price scraper"
    echo "  test-twilio    Test SMS functionality"
    echo "  setup          Run setup script"
    echo "  config-check   Check configuration"
    echo ""
    exit 1
fi

case "$1" in
    "setup")
        echo "Running setup..."
        python3 setup.py
        ;;
    "config-check")
        echo "Checking configuration..."
        python3 main.py --config-check
        ;;
    "url-manager")
        echo "Starting URL Manager..."
        python3 main.py url-manager
        ;;
    "scraper")
        echo "Starting Price Scraper..."
        python3 main.py scraper
        ;;
    "test-twilio")
        echo "Testing Twilio..."
        python3 main.py test-twilio
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        echo "Available commands:"
        echo "  url-manager    Start the web interface"
        echo "  scraper        Run the price scraper"
        echo "  test-twilio    Test SMS functionality"
        echo "  setup          Run setup script"
        echo "  config-check   Check configuration"
        echo ""
        exit 1
        ;;
esac
