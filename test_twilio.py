#!/usr/bin/env python3
"""
Twilio Test Script - Python version
Tests Twilio SMS functionality
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio credentials from environment variables
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')
TO_NUMBER = '+19206455791'


def test_twilio():
    """Test Twilio SMS functionality"""
    if not ACCOUNT_SID or not AUTH_TOKEN or not FROM_NUMBER:
        print('Missing Twilio credentials. Please set:')
        print('TWILIO_ACCOUNT_SID')
        print('TWILIO_AUTH_TOKEN')
        print('TWILIO_FROM_NUMBER')
        return

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    try:
        print('Sending test SMS...')
        message = client.messages.create(
            body='Test message from your price scraper! Twilio is working correctly.',
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        print('Test SMS sent successfully!')
        print(f'Message SID: {message.sid}')
    except Exception as error:
        print(f'Failed to send test SMS: {error}')


if __name__ == '__main__':
    test_twilio()
