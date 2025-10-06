#!/usr/bin/env python3
"""
Configuration file for the Python Scrapper application
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class"""
    
    # MongoDB Configuration
    MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'scrapper')
    MONGODB_COLLECTION_NAME = os.getenv('MONGODB_COLLECTION_NAME', 'products')
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')
    TO_NUMBER = '+19206455791'
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 3000))
    ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
    ADMIN_PASS = os.getenv('ADMIN_PASS', 'password')
    
    # Proxy Configuration (optional)
    BRIGHTDATA_URL = os.getenv('BRIGHTDATA_URL')
    BRIGHTDATA_PORT = os.getenv('BRIGHTDATA_PORT')
    BRIGHTDATA_USER = os.getenv('BRIGHTDATA_USER')
    BRIGHTDATA_PASS = os.getenv('BRIGHTDATA_PASS')
    
    # Scraping Configuration
    SCRAPING_DELAY_MIN = 5  # seconds
    SCRAPING_DELAY_MAX = 15  # seconds
    PAGE_TIMEOUT = 30000  # milliseconds
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        required_vars = [
            'MONGODB_URL',
            'MONGODB_DB_NAME',
            'MONGODB_COLLECTION_NAME'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required configuration: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def is_twilio_configured(cls):
        """Check if Twilio is properly configured"""
        return all([
            cls.TWILIO_ACCOUNT_SID,
            cls.TWILIO_AUTH_TOKEN,
            cls.TWILIO_FROM_NUMBER
        ])
    
    @classmethod
    def is_proxy_configured(cls):
        """Check if proxy is properly configured"""
        return all([
            cls.BRIGHTDATA_URL,
            cls.BRIGHTDATA_PORT,
            cls.BRIGHTDATA_USER,
            cls.BRIGHTDATA_PASS
        ])


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
