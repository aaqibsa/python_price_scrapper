#!/usr/bin/env python3
"""
Main entry point for the Python Scrapper application
"""

import sys
import argparse
import asyncio
from app.url_manager import start_server
from scrape_price import main as scrape_main
from test_twilio import test_twilio
from config import Config


def run_url_manager():
    """Run the URL manager Flask application"""
    print("Starting URL Manager...")
    start_server()


def run_scraper():
    """Run the price scraper"""
    print("Starting Price Scraper...")
    asyncio.run(scrape_main())


def run_twilio_test():
    """Run Twilio test"""
    print("Testing Twilio...")
    test_twilio()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Python Scrapper Application')
    parser.add_argument(
        'command',
        choices=['url-manager', 'scraper', 'test-twilio', 'all'],
        help='Command to run'
    )
    parser.add_argument(
        '--config-check',
        action='store_true',
        help='Check configuration and exit'
    )
    
    args = parser.parse_args()
    
    # Check configuration if requested
    if args.config_check:
        try:
            Config.validate_config()
            print("✓ Configuration is valid")
            
            if Config.is_twilio_configured():
                print("✓ Twilio is configured")
            else:
                print("⚠ Twilio is not configured (SMS notifications will be disabled)")
            
            if Config.is_proxy_configured():
                print("✓ Proxy is configured")
            else:
                print("⚠ Proxy is not configured (will use direct connection)")
                
        except ValueError as e:
            print(f"✗ Configuration error: {e}")
            sys.exit(1)
        return
    
    # Run the requested command
    if args.command == 'url-manager':
        run_url_manager()
    elif args.command == 'scraper':
        run_scraper()
    elif args.command == 'test-twilio':
        run_twilio_test()
    elif args.command == 'all':
        print("Running all components...")
        print("Note: Run components separately for better control")
        print("Use 'python main.py url-manager' to start the web interface")
        print("Use 'python main.py scraper' to run the price scraper")
        print("Use 'python main.py test-twilio' to test SMS functionality")


if __name__ == '__main__':
    main()
