#!/usr/bin/env python3
"""
URL Manager - Flask application for managing product URLs
"""

import os
import asyncio
import threading
from datetime import datetime
from typing import List, Dict, Any

from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.middleware.proxy_fix import ProxyFix

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MONGO_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DB_NAME', 'scrapper')
URL_COLLECTION_NAME = 'urls'
PORT = int(os.getenv('PORT', 3000))

# Admin credentials
ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'password')

# Create Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.wsgi_app = ProxyFix(app.wsgi_app)

# MongoDB connection
mongo_client = None
db = None
urls_collection = None

# Scraper status tracking
scraper_status = {
    'running': False,
    'last_run': None,
    'last_status': None,
    'error': None
}


def connect_to_mongo():
    """Connect to MongoDB and ensure collections exist"""
    global mongo_client, db, urls_collection
    
    try:
        mongo_client = MongoClient(MONGO_URL)
        print('Connected to MongoDB server')
        
        # Get or create the database
        db = mongo_client[DB_NAME]
        
        # Test the database connection and ensure collection exists
        try:
            collections = db.list_collection_names()
            
            # Check if our collection exists
            if URL_COLLECTION_NAME not in collections:
                db.create_collection(URL_COLLECTION_NAME)
                
        except Exception as db_error:
            # Try to create the collection anyway
            try:
                db.create_collection(URL_COLLECTION_NAME)
            except Exception:
                print(f"Collection '{URL_COLLECTION_NAME}' will be created on first data insertion")
        
        urls_collection = db[URL_COLLECTION_NAME]
        print(f"Successfully connected to MongoDB database '{DB_NAME}'")
        
    except Exception as err:
        print(f"Failed to connect to MongoDB: {err}")
        raise


def check_auth(username: str, password: str) -> bool:
    """Check admin credentials"""
    return username == ADMIN_USER and password == ADMIN_PASS


def authenticate():
    """Send 401 response that enables basic auth"""
    return 'Authentication required', 401, {
        'WWW-Authenticate': 'Basic realm="Login Required"'
    }


def run_scraper_async():
    """Run the scraper in a separate thread"""
    global scraper_status
    
    try:
        scraper_status['running'] = True
        scraper_status['error'] = None
        scraper_status['last_status'] = 'Starting scraper...'
        
        # Import and run the scraper
        from scrape_price import main as scrape_main
        asyncio.run(scrape_main())
        
        scraper_status['last_status'] = 'Scraper completed successfully'
        scraper_status['last_run'] = datetime.now().isoformat()
        
    except Exception as e:
        scraper_status['error'] = str(e)
        scraper_status['last_status'] = f'Scraper failed: {str(e)}'
        print(f'Scraper error: {e}')
    finally:
        scraper_status['running'] = False


# Routes
@app.route('/')
def index():
    """Serve the main landing page"""
    return render_template('index.html')


@app.route('/admin')
def admin():
    """Admin URL manager page"""
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    return render_template('url-manager.html')


@app.route('/admin/add-url', methods=['POST'])
def add_url():
    """Add or update a URL"""
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    try:
        data = request.get_json()
        url = data.get('url')
        name = data.get('name')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'}), 400
        
        # Check if URL already exists
        existing_url = urls_collection.find_one({'url': url})
        
        if existing_url:
            # Update existing record
            urls_collection.update_one(
                {'url': url},
                {
                    '$set': {
                        'name': name or existing_url.get('name'),
                        'updatedAt': datetime.now()
                    }
                }
            )
            print(f'URL updated: {url}')
            message = 'URL updated'
        else:
            # Insert new record
            urls_collection.insert_one({
                'url': url,
                'name': name,
                'createdAt': datetime.now()
            })
            print(f'URL added: {url}')
            message = 'URL added'
        
        return jsonify({'success': True, 'message': message})
        
    except Exception as err:
        print(f'Error adding/updating URL: {err}')
        return jsonify({'success': False, 'error': 'Error adding URL'}), 500


@app.route('/admin/delete-url', methods=['POST'])
def delete_url():
    """Delete a URL"""
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    try:
        data = request.get_json()
        url_id = data.get('id')
        
        if not url_id:
            return jsonify({'success': False, 'error': 'URL ID is required'}), 400
        
        urls_collection.delete_one({'_id': ObjectId(url_id)})
        return redirect(url_for('admin'))
        
    except Exception as err:
        print(f'Error deleting URL: {err}')
        return jsonify({'success': False, 'error': 'Error deleting URL'}), 500


@app.route('/admin/api/urls-data')
def get_urls_data():
    """API endpoint to get all URLs with full data (for the frontend)"""
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    try:
        urls = list(urls_collection.find({}))
        # Convert ObjectId to string for JSON serialization
        for url in urls:
            url['_id'] = str(url['_id'])
        return jsonify(urls)
        
    except Exception as err:
        print(f'Error fetching URLs: {err}')
        return jsonify({'error': 'Error fetching URLs'}), 500


@app.route('/api/urls')
def get_urls():
    """API endpoint to get all URLs (for the scraper)"""
    try:
        urls = list(urls_collection.find({}))
        return jsonify([url['url'] for url in urls])
        
    except Exception as err:
        print(f'Error fetching URLs: {err}')
        return jsonify({'error': 'Error fetching URLs'}), 500


@app.route('/admin/run-scraper', methods=['POST'])
def run_scraper():
    """Start the scraper"""
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    global scraper_status
    
    if scraper_status['running']:
        return jsonify({'success': False, 'error': 'Scraper is already running'}), 400
    
    # Start scraper in a separate thread
    thread = threading.Thread(target=run_scraper_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Scraper started'})


@app.route('/admin/scraper-status')
def get_scraper_status():
    """Get current scraper status"""
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    return jsonify(scraper_status)


def start_server():
    """Start the Flask server"""
    connect_to_mongo()
    app.run(host='0.0.0.0', port=PORT, debug=True)


if __name__ == '__main__':
    start_server()
