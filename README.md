# Python Scrapper

A Python-based web scraping application for monitoring product prices and sending SMS notifications when prices drop. This is a Python conversion of the original Node.js scrapper application.

## Features

- **Web Scraping**: Uses Playwright to scrape product prices from e-commerce websites
- **Price Monitoring**: Tracks price changes and stores data in MongoDB
- **SMS Notifications**: Sends SMS alerts via Twilio when prices drop
- **Web Interface**: Flask-based admin interface for managing product URLs
- **Proxy Support**: Optional proxy configuration for scraping
- **Async Processing**: Efficient asynchronous scraping with rate limiting

## Project Structure

```
python-scrapper/
├── app/
│   ├── __init__.py
│   └── url_manager.py          # Flask web application
├── static/
│   ├── styles.css             # CSS styles
│   ├── script.js              # Frontend JavaScript
│   └── test.png               # Test image
├── templates/
│   ├── index.html             # Landing page
│   └── url_manager.html       # Admin interface
├── config.py                  # Configuration management
├── main.py                    # Main entry point
├── scrape_price.py            # Price scraping logic
├── test_twilio.py             # Twilio SMS test
├── requirements.txt           # Python dependencies
├── env.example                # Environment variables template
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud instance)
- Twilio account (for SMS notifications)
- Optional: Proxy service (e.g., BrightData)

### Setup

1. **Clone or download the project**
   ```bash
   cd python-scrapper
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Twilio Configuration
   TWILIO_ACCOUNT_SID=your_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_FROM_NUMBER=+1xxxxxxxxxx
   
   # MongoDB Configuration
   MONGODB_URL=mongodb://localhost:27017/
   MONGODB_DB_NAME=scrapper
   MONGODB_COLLECTION_NAME=products
   
   # Server Configuration
   PORT=3000
   ADMIN_USER=admin
   ADMIN_PASS=your_secure_password
   
   # Proxy Configuration (optional)
   BRIGHTDATA_URL=your_proxy_url
   BRIGHTDATA_PORT=your_proxy_port
   BRIGHTDATA_USER=your_proxy_username
   BRIGHTDATA_PASS=your_proxy_password
   ```

## Usage

### Check Configuration

First, verify your configuration:
```bash
python main.py --config-check
```

### Start the URL Manager (Web Interface)

```bash
python main.py url-manager
```

This starts the Flask web server. Access the admin interface at:
- Main page: http://localhost:3000
- Admin interface: http://localhost:3000/admin

### Run the Price Scraper

```bash
python main.py scraper
```

This will:
1. Connect to MongoDB
2. Fetch all URLs from the URL manager
3. Scrape each URL for product prices
4. Store/update price data in MongoDB
5. Send SMS notifications for price drops

### Test Twilio SMS

```bash
python main.py test-twilio
```

This sends a test SMS to verify your Twilio configuration.

## Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017/` | Yes |
| `MONGODB_DB_NAME` | Database name | `scrapper` | Yes |
| `MONGODB_COLLECTION_NAME` | Products collection name | `products` | Yes |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | - | No |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | - | No |
| `TWILIO_FROM_NUMBER` | Twilio phone number | - | No |
| `PORT` | Web server port | `3000` | No |
| `ADMIN_USER` | Admin username | `admin` | No |
| `ADMIN_PASS` | Admin password | `password` | No |
| `BRIGHTDATA_URL` | Proxy server URL | - | No |
| `BRIGHTDATA_PORT` | Proxy server port | - | No |
| `BRIGHTDATA_USER` | Proxy username | - | No |
| `BRIGHTDATA_PASS` | Proxy password | - | No |

### Scraping Configuration

The scraper includes built-in rate limiting and error handling:
- Random delays between requests (5-15 seconds)
- 30-second page load timeout
- Automatic retry logic
- Memory management

## API Endpoints

### Public Endpoints

- `GET /` - Landing page
- `GET /api/urls` - Get all URLs (for scraper)

### Admin Endpoints (Basic Auth Required)

- `GET /admin` - Admin interface
- `POST /admin/add-url` - Add/update URL
- `POST /admin/delete-url` - Delete URL
- `GET /admin/api/urls-data` - Get URLs with full data

## Database Schema

### URLs Collection
```json
{
  "_id": "ObjectId",
  "url": "https://example.com/product",
  "name": "Product Name",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### Products Collection
```json
{
  "_id": "ObjectId",
  "url": "https://example.com/product",
  "sku": "PRODUCT-SKU",
  "price": "29.99",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check connection string in `.env`
   - Verify network connectivity

2. **Playwright Browser Issues**
   - Run `playwright install chromium`
   - Check system dependencies

3. **Twilio SMS Not Sent**
   - Verify Twilio credentials
   - Check phone number format
   - Ensure sufficient Twilio balance

4. **Scraping Failures**
   - Check target website accessibility
   - Verify proxy configuration
   - Review error logs

### Logs and Debugging

- Enable debug mode by setting `DEBUG=True` in config
- Check console output for detailed error messages
- Monitor MongoDB logs for database issues

## Development

### Running in Development Mode

```bash
# Set debug mode
export FLASK_DEBUG=1

# Run URL manager
python main.py url-manager
```

### Adding New Features

1. **New Scraping Targets**: Modify `scrape_price.py` to handle different website structures
2. **Additional Notifications**: Extend notification system in `scrape_price.py`
3. **Web Interface**: Add new routes in `app/url_manager.py`

## Security Considerations

- Change default admin credentials
- Use HTTPS in production
- Implement proper authentication
- Validate all user inputs
- Use environment variables for sensitive data

## Performance Optimization

- Use connection pooling for MongoDB
- Implement caching for frequently accessed data
- Optimize scraping delays based on target websites
- Monitor memory usage during large scraping operations

## License

This project is open source. Please ensure compliance with target websites' terms of service when scraping.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review error logs
3. Verify configuration settings
4. Test individual components separately
