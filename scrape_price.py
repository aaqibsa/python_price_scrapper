#!/usr/bin/env python3
"""
Price Scraper - Python version
Scrapes product prices from URLs and stores them in MongoDB
"""

import os
import json
import time
import random
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pymongo import MongoClient
from twilio.rest import Client as TwilioClient

# Load environment variables
load_dotenv()

# Configuration
MONGO_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DB_NAME', 'scrapper')
COLLECTION_NAME = os.getenv('MONGODB_COLLECTION_NAME', 'products')

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')
TO_NUMBER = '+19206455791'

# Initialize Twilio client if credentials are available
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


class PriceScraper:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.products_collection = None
        self.urls_collection = None

    async def ensure_database_and_collection(self):
        """Ensure database and collections exist"""
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            
            # Test the database connection and ensure collections exist
            try:
                collections = self.db.list_collection_names()
                
                # Check if our collections exist
                if COLLECTION_NAME not in collections:
                    self.db.create_collection(COLLECTION_NAME)
                
                if 'urls' not in collections:
                    self.db.create_collection('urls')
                    
            except Exception as db_error:
                # Try to create the collections anyway
                try:
                    self.db.create_collection(COLLECTION_NAME)
                except Exception:
                    print(f"Collection '{COLLECTION_NAME}' will be created on first data insertion")
                
                try:
                    self.db.create_collection('urls')
                except Exception:
                    print("Collection 'urls' will be created on first data insertion")
            
            self.products_collection = self.db[COLLECTION_NAME]
            self.urls_collection = self.db['urls']
            
            print(f"Successfully connected to MongoDB database '{DB_NAME}'")
            
        except Exception as err:
            print(f"Failed to connect to MongoDB: {err}")
            raise

    def get_urls_from_manager(self) -> list:
        """Get URLs from the URL manager collection"""
        try:
            urls = list(self.urls_collection.find({}))
            return [url['url'] for url in urls]
        except Exception as error:
            print(f"Error fetching URLs from manager: {error}")
            return []

    async def fetch_price(self, url: str, max_retries: int = 2):
        """Fetch price from a single URL with retry logic"""
        for attempt in range(max_retries):
            playwright = None
            browser = None
            context = None
            page = None
            
            try:
                print(f"Attempt {attempt + 1}/{max_retries} for URL: {url}")
                
                # Initialize playwright
                playwright = await async_playwright().start()
                
                # Enhanced context options with better headers
                context_options = {
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'viewport': {'width': 1920, 'height': 1080},
                    'extra_http_headers': {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': '"Windows"',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                        'Connection': 'keep-alive',
                        'DNT': '1'
                    },
                    'locale': 'en-US',
                    'timezone_id': 'America/New_York'
                }
                
                # Check for BrightData Browser API credentials
                brightdata_auth = os.getenv('BRIGHTDATA_AUTH')
                use_brightdata = brightdata_auth and brightdata_auth != 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD'
                
                # Validate BrightData credentials if provided
                if brightdata_auth and brightdata_auth == 'SBR_ZONE_FULL_USERNAME:SBR_ZONE_PASSWORD':
                    print("Warning: BrightData credentials not properly configured!")
                    print("Please set BRIGHTDATA_AUTH environment variable with your actual credentials")
                    print("Format: BRIGHTDATA_AUTH=your-username:your-password")
                    use_brightdata = False
                
                if use_brightdata:
                    try:
                        print(f"Using BrightData Browser API with auth: {brightdata_auth[:20]}...")
                        # Use BrightData Browser API via CDP connection
                        endpoint_url = f'wss://{brightdata_auth}@brd.superproxy.io:9222'
                        browser = await playwright.chromium.connect_over_cdp(endpoint_url)
                        print("Connected to BrightData Browser API!")
                    except Exception as cdp_error:
                        print(f"Failed to connect to BrightData Browser API: {cdp_error}")
                        print("Falling back to local browser...")
                        use_brightdata = False
                        # Fall back to local browser
                        browser = await playwright.chromium.launch(
                            headless=False,
                            args=[
                                '--no-sandbox',
                                '--disable-dev-shm-usage',
                                '--disable-blink-features=AutomationControlled',
                                '--disable-features=VizDisplayCompositor',
                                '--disable-extensions',
                                '--disable-plugins',
                                '--disable-images',
                                '--disable-web-security',
                                '--disable-features=IsolateOrigins,site-per-process',
                                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                            ]
                        )
                else:
                    print("Using local browser (no BrightData)")
                    # Use local browser
                    browser = await playwright.chromium.launch(
                        headless=False,  # Use headless for better performance and less detection
                        args=[
                            '--no-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-blink-features=AutomationControlled',
                            '--disable-features=VizDisplayCompositor',
                            '--disable-extensions',
                            '--disable-plugins',
                            '--disable-images',  # Speed up loading
                            # '--disable-javascript',  # Commented out - some sites need JS for content
                            '--disable-web-security',
                            '--disable-features=IsolateOrigins,site-per-process',
                            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                        ]
                    )

                context = await browser.new_context(**context_options)
                
                # Apply network optimizations early
                # await self.apply_network_optimizations(context)

                page = await context.new_page()

                # Navigate to the page with enhanced retry logic
                try:
                    print(f"Navigating to: {url}")
                    
                    # Add a small delay before navigation to avoid rapid requests
                    await asyncio.sleep(random.uniform(1, 3))
                    
                    # Try different navigation strategies
                    navigation_success = False
                    
                    # Strategy 1: Try with domcontentloaded
                    try:
                        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                        navigation_success = True
                        print("Page loaded successfully with domcontentloaded")
                    except Exception as e1:
                        print(f"domcontentloaded failed: {e1}")
                        
                        # Strategy 2: Try with networkidle (more conservative)
                        try:
                            await page.goto(url, wait_until='networkidle', timeout=60000)
                            navigation_success = True
                            print("Page loaded successfully with networkidle")
                        except Exception as e2:
                            print(f"networkidle failed: {e2}")
                            
                            # Strategy 3: Try with load event (most basic)
                            try:
                                await page.goto(url, wait_until='load', timeout=60000)
                                navigation_success = True
                                print("Page loaded successfully with load")
                            except Exception as e3:
                                print(f"load failed: {e3}")
                                raise e3  # Raise the last error
                    
                    if not navigation_success:
                        raise Exception("All navigation strategies failed")
                        
                except Exception as nav_error:
                    print(f"Navigation error on attempt {attempt + 1}: {nav_error}")
                    if attempt < max_retries - 1:
                        await self._cleanup_browser(playwright, browser, context, page)
                        # Use exponential backoff with jitter
                        wait_time = (2 ** attempt) + random.uniform(1, 3)
                        print(f"Retrying in {wait_time:.1f} seconds...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise nav_error


                try:
                    await page.wait_for_selector('#itemDetailPage', timeout=4000)
                except Exception:
                    await page.wait_for_timeout(1500)

                print("DOM content loaded")

                # Take screenshot
                await page.screenshot(path='test2.png')
                print("Screenshot taken")

                # Get the page content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # Find the <script type="application/ld+json"> tag
                ld_json_script = soup.find('script', type='application/ld+json')
                
                if ld_json_script:
                    try:
                        json_data = json.loads(ld_json_script.string)
                        
                        # Extract price from JSON-LD
                        price = None
                        if 'offers' in json_data:
                            offers = json_data['offers']
                            if isinstance(offers, list) and len(offers) > 0:
                                price = offers[0].get('price')
                            elif isinstance(offers, dict):
                                price = offers.get('price')
                        
                        # Extract SKU
                        sku = json_data.get('sku')
                        
                        if price:
                            print(f"Product Price for {url}: {price}")
                            # Store in MongoDB
                            await self.store_in_mongo({'url': url, 'sku': sku, 'price': price})
                            await self._cleanup_browser(playwright, browser, context, page)
                            return  # Success, exit retry loop
                        else:
                            print(f"Price not found in JSON for {url}.")
                            
                    except json.JSONDecodeError as json_err:
                        print(f"Error parsing JSON from ld+json for {url}: {json_err}")
                else:
                    print(f"No <script type=\"application/ld+json\"> tag found for {url}.")
                
                # Fallback: Try to find price in HTML elements
                price_element = soup.find('span', class_='price') or soup.find('div', class_='price') or soup.find('span', {'data-testid': 'price'})
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    # Extract numeric price
                    import re
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace('$', '').replace(',', ''))
                    if price_match:
                        price = float(price_match.group())
                        print(f"Product Price for {url} (fallback): {price}")
                        await self.store_in_mongo({'url': url, 'sku': None, 'price': price})
                        await self._cleanup_browser(playwright, browser, context, page)
                        return
                
                # If we reach here, the page loaded but no price was found
                # This is not a network error, so don't retry
                print(f"Could not extract price from {url}")
                await self._cleanup_browser(playwright, browser, context, page)
                return

            except Exception as error:
                error_msg = str(error)
                print(f"Error fetching the product page {url} (attempt {attempt + 1}): {error}")
                
                # Log specific error types for debugging
                if "ERR_EMPTY_RESPONSE" in error_msg:
                    print("  -> Empty response error - likely proxy issues, server blocking, or rate limiting")
                    print("  -> If using proxy, try disabling it with PROXY_ENABLED=false")
                elif "ERR_CONNECTION_REFUSED" in error_msg:
                    print("  -> Connection refused - server may be down, blocking, or proxy issue")
                elif "ERR_TIMED_OUT" in error_msg:
                    print("  -> Timeout error - server took too long to respond or proxy timeout")
                elif "ERR_PROXY_CONNECTION_FAILED" in error_msg:
                    print("  -> Proxy connection failed - check proxy credentials and availability")
                elif "net::ERR_" in error_msg:
                    print("  -> Network error detected - may be proxy-related")
                
                await self._cleanup_browser(playwright, browser, context, page)
                if attempt < max_retries - 1:
                    # Wait before retrying with exponential backoff and jitter
                    wait_time = (2 ** attempt) + random.uniform(2, 8)
                    print(f"Retrying in {wait_time:.1f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"Failed to fetch {url} after {max_retries} attempts")
                    # Log the failed URL for manual inspection
                    print(f"Consider checking this URL manually: {url}")

    async def _cleanup_browser(self, playwright, browser, context, page):
        """Clean up browser resources"""
        try:
            if page:
                await page.close()
            if context:
                await context.close()
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    async def store_in_mongo(self, product: Dict[str, Any]):
        """Store or update product data in MongoDB"""
        try:
            # Use SKU if available, otherwise use URL as unique identifier
            query = {'sku': product['sku']} if product['sku'] else {'url': product['url']}
            existing = self.products_collection.find_one(query)
            
            if existing:
                if existing['price'] != product['price']:
                    self.products_collection.update_one(
                        query,
                        {'$set': {'price': product['price'], 'updatedAt': datetime.now()}}
                    )
                    print('Product price updated in MongoDB:', product)

                    # Send SMS notification if price decreased and Twilio is configured
                    if existing['price'] > product['price'] and twilio_client and TWILIO_FROM_NUMBER:
                        try:
                            message = twilio_client.messages.create(
                                body=f"Price changed for product (SKU: {product['sku'] or 'N/A'}): {existing['price']} -> {product['price']}\nURL: {product['url']}",
                                from_=TWILIO_FROM_NUMBER,
                                to=TO_NUMBER
                            )
                            print('SMS notification sent.')
                        except Exception as sms_err:
                            print(f'Failed to send SMS notification: {sms_err}')
                else:
                    print('Product price unchanged. No update needed.')
            else:
                product['createdAt'] = datetime.now()
                self.products_collection.insert_one(product)
                print('Product stored in MongoDB:', product)

        except Exception as err:
            print(f'Error storing product in MongoDB: {err}')

    async def scrape_all_products(self):
        """Scrape all products from the URL manager"""
        # Ensure database and collections exist before starting
        await self.ensure_database_and_collection()

        urls = self.get_urls_from_manager()
        if not urls:
            print('No URLs found. Please add URLs using the URL Manager.')
            return

        print(f'Starting to scrape {len(urls)} products...')
        
        for i, url in enumerate(urls):
            print(f'\nScraping {i+1}/{len(urls)}: {url}')
            await self.fetch_price(url)
            
            # Add progressive delay between requests to avoid rate limiting
            if i < len(urls) - 1:  # Don't delay after the last URL
                # Base delay increases with more URLs processed
                base_delay = 3  # Start at 10s, increase by 2s each URL
                random_delay = random.uniform(5, 15)  # Add 5-15s random component
                total_delay = base_delay + random_delay
                
                print(f'Waiting {total_delay:.1f} seconds before next request...')
                await asyncio.sleep(total_delay)
        
        print('\nFinished scraping all products.')


    async def apply_network_optimizations(context):
        """Block non-essential resources to speed up page loads."""
        try:
            # Reduce default timeouts to fail fast on missing elements
            context.set_default_timeout(20000)

            async def route_handler(route):
                try:
                    request = route.request
                    resource_type = request.resource_type
                    url = request.url

                    # Block heavy or non-essential assets
                    if resource_type in {"image", "media", "font", "stylesheet"}:
                        return await route.abort()

                    # Block common analytics/ads/tracking
                    block_hosts = [
                        'doubleclick.net', 'googletagmanager.com', 'google-analytics.com',
                        'facebook.net', 'adsystem.com', 'adservice.google.com',
                        'snap.licdn.com', 'bat.bing.com'
                    ]
                    if any(host in url for host in block_hosts):
                        return await route.abort()

                    return await route.continue_()
                except Exception:
                    # If anything goes wrong, allow the request to proceed
                    try:
                        return await route.continue_()
                    except Exception:
                        return

            await context.route("**/*", route_handler)
        except Exception:
            pass

    def close(self):
        """Close MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()


async def main():
    """Main function to run the scraper"""
    scraper = PriceScraper()
    try:
        await scraper.scrape_all_products()
    finally:
        scraper.close()


if __name__ == '__main__':
    asyncio.run(main())
