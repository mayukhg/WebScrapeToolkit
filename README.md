# Web Scraper

A comprehensive Python web scraping tool built with `requests` and `BeautifulSoup` that provides extensive functionality for extracting data from websites with proper error handling, rate limiting, and respect for robots.txt.

## Features

- **Respectful Scraping**: Built-in rate limiting and robots.txt compliance
- **Comprehensive Data Extraction**: Text content, links, images, and metadata
- **Error Handling**: Robust error handling for various network scenarios
- **Multiple Usage Modes**: Command-line interface, interactive mode, and programmatic API
- **Flexible Configuration**: Customizable headers, delays, and extraction options
- **JSON Export**: Save scraping results in structured JSON format

## Project Structure

```
├── web_scraper.py      # Main WebScraper class with core functionality
├── scraper_examples.py # Practical examples and use cases
├── utils.py           # Utility functions for data processing
├── main.py            # Command-line interface and application entry point
└── README.md          # This documentation file
```

## Installation

The project requires Python 3.11+ and the following dependencies:

```bash
pip install requests beautifulsoup4 lxml
```

## Quick Start

### Basic Usage

```python
from web_scraper import WebScraper

# Initialize the scraper
scraper = WebScraper(delay=1.0)

# Scrape a single page
result = scraper.scrape_page("https://example.com")

# Display results
print(f"Title: {result.title}")
print(f"Links found: {len(result.links)}")
print(f"Text length: {len(result.text_content)} characters")

# Clean up
scraper.close()
```

### Command Line Interface

```bash
# Scrape a single URL
python main.py --url https://example.com --verbose

# Scrape multiple URLs
python main.py --urls https://site1.com https://site2.com --output results.json

# Run example scenarios
python main.py --examples

# Interactive mode
python main.py --interactive
```

## Core Components

### WebScraper Class

The main `WebScraper` class provides comprehensive scraping functionality:

```python
# Initialize with custom settings
scraper = WebScraper(
    delay=1.5,              # Delay between requests (seconds)
    timeout=10,             # Request timeout (seconds)
    respect_robots=True,    # Check robots.txt compliance
    custom_headers={        # Custom HTTP headers
        'User-Agent': 'My Custom Bot 1.0'
    }
)
```

**Key Methods:**
- `scrape_page()` - Extract all data from a single page
- `scrape_multiple_pages()` - Process multiple URLs efficiently
- `fetch_page()` - Low-level page fetching with error handling
- `extract_text()` - Clean text content extraction
- `extract_links()` - Find and categorize all links
- `extract_images()` - Gather image information
- `extract_metadata()` - Collect page metadata

### ScrapingResult Data Structure

Each scraping operation returns a `ScrapingResult` object containing:

```python
result = scraper.scrape_page(url)

# Access extracted data
print(result.url)           # Original URL
print(result.status_code)   # HTTP status code
print(result.title)         # Page title
print(result.text_content)  # Clean text content
print(result.links)         # List of link dictionaries
print(result.images)        # List of image dictionaries
print(result.metadata)      # Page metadata dictionary
print(result.error)         # Error message if any
```

### Utility Functions

The `utils.py` module provides helper functions:

- **URL Processing**: `is_valid_url()`, `extract_domain()`, `normalize_url()`
- **Text Cleaning**: `clean_text()`, `extract_emails_from_text()`, `extract_phone_numbers_from_text()`
- **Link Filtering**: `filter_internal_links()`, `filter_external_links()`
- **Data Analysis**: `create_sitemap_from_links()`, `format_scraping_summary()`

## Examples and Use Cases

### Extract News Headlines

```python
from web_scraper import WebScraper

scraper = WebScraper(delay=2.0)
response = scraper.fetch_page("https://news-website.com")

if response:
    soup = scraper.parse_html(response.text)
    headlines = []
    
    # Look for headline elements
    for selector in ['h1', 'h2', '.headline', '.title']:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(strip=True)
            if text and len(text) > 10:
                headlines.append(text)
    
    print(f"Found {len(headlines)} headlines")
```

### Custom Data Extraction

```python
# Extract external links only
external_links = []
for link in soup.find_all('a', href=True):
    href = link['href']
    if href.startswith('http') and 'current-domain.com' not in href:
        external_links.append({
            'url': href,
            'text': link.get_text(strip=True)
        })

# Find email addresses in page content
import re
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
text_content = scraper.extract_text(soup)
emails = re.findall(email_pattern, text_content)
```

### Batch Processing

```python
# Process multiple URLs
urls = [
    "https://site1.com",
    "https://site2.com", 
    "https://site3.com"
]

results = scraper.scrape_multiple_pages(urls)

# Analyze results
successful = [r for r in results if not r.error]
print(f"Successfully scraped {len(successful)} out of {len(urls)} pages")

# Save all results
scraper.save_results_to_json(results, "batch_results.json")
```

## Configuration Options

### Rate Limiting
Control request frequency to be respectful to target servers:

```python
scraper = WebScraper(delay=2.0)  # 2 second delay between requests
```

### Custom Headers
Customize HTTP headers to appear more like a regular browser:

```python
custom_headers = {
    'User-Agent': 'Mozilla/5.0 (Educational Bot)',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml'
}
scraper = WebScraper(custom_headers=custom_headers)
```

### Selective Data Extraction
Choose what data to extract for faster processing:

```python
result = scraper.scrape_page(
    url,
    extract_text=True,
    extract_links=True,
    extract_images=False,    # Skip images for speed
    extract_metadata=True
)
```

## Error Handling

The scraper includes comprehensive error handling for common scenarios:

- **Network Errors**: Connection timeouts, DNS failures
- **HTTP Errors**: 404, 500, and other status codes  
- **Parsing Errors**: Invalid HTML, encoding issues
- **Robots.txt Violations**: Automatic compliance checking

```python
result = scraper.scrape_page(url)

if result.error:
    print(f"Scraping failed: {result.error}")
else:
    print(f"Success! Status: {result.status_code}")
```

## Interactive Mode

Run the scraper interactively for testing and exploration:

```bash
python main.py --interactive
```

Available commands:
- `scrape <url>` - Scrape a single URL
- `batch <file>` - Scrape URLs from a text file
- `examples` - Run example scenarios
- `help` - Show available commands
- `quit` - Exit the application

## Best Practices

### Respect Website Policies
- Always check robots.txt compliance (enabled by default)
- Use appropriate delays between requests
- Monitor server response times and adjust accordingly

### Efficient Scraping
- Extract only the data you need
- Use batch processing for multiple URLs
- Implement proper error handling

### Data Processing
- Clean extracted text for better readability
- Filter links by domain (internal vs external)
- Validate URLs before processing

## Output Formats

### JSON Export
Save results in structured JSON format for further processing:

```python
# Single result
scraper.save_results_to_json(result, "single_result.json")

# Multiple results
scraper.save_results_to_json(results, "batch_results.json")
```

### Console Output
The scraper provides detailed console output with status indicators:
- ✅ Successful operations
- ❌ Error conditions  
- 📄 Page information
- 🔗 Link statistics
- 🖼️ Image counts

## Troubleshooting

### Common Issues

**Timeout Errors**: Increase the timeout value or check network connectivity
```python
scraper = WebScraper(timeout=30)  # 30 second timeout
```

**Blocked Requests**: Modify headers to appear more like a regular browser
```python
scraper = WebScraper(custom_headers={'User-Agent': 'Mozilla/5.0...'})
```

**Rate Limiting**: Increase delay between requests
```python
scraper = WebScraper(delay=3.0)  # 3 second delay
```

### Debugging
Enable verbose logging to see detailed operation information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is provided as-is for educational and research purposes. Please respect website terms of service and robots.txt files when scraping.

## Contributing

When extending the scraper:
1. Maintain the existing error handling patterns
2. Add comprehensive comments to new functions
3. Include example usage in the documentation
4. Test with various website types and scenarios

---

**Note**: Always ensure you have permission to scrape websites and comply with their terms of service and robots.txt files.