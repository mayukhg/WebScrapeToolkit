"""
Examples demonstrating various web scraping scenarios

This module provides practical examples of how to use the WebScraper class
for different types of websites and data extraction tasks.
"""

from web_scraper import WebScraper
import json


def example_basic_scraping():
    """
    Basic example: Scrape a simple website and extract all data
    """
    print("=== Basic Scraping Example ===")
    
    # Initialize the scraper with default settings
    scraper = WebScraper(delay=1.0)
    
    # Example URL (using a public API documentation page)
    url = "https://httpbin.org/"
    
    # Scrape the page
    result = scraper.scrape_page(url)
    
    # Display results
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"Title: {result.title}")
        print(f"Status Code: {result.status_code}")
        print(f"Number of links found: {len(result.links) if result.links else 0}")
        print(f"Number of images found: {len(result.images) if result.images else 0}")
        print(f"Text content length: {len(result.text_content) if result.text_content else 0} characters")
    
    # Clean up
    scraper.close()


def example_extract_news_headlines():
    """
    Example: Extract headlines from a news website
    This demonstrates selective data extraction
    """
    print("\n=== News Headlines Extraction Example ===")
    
    # Initialize scraper with custom headers
    custom_headers = {
        'User-Agent': 'Educational Web Scraper 1.0'
    }
    scraper = WebScraper(delay=2.0, custom_headers=custom_headers)
    
    # Example news website (BBC News)
    url = "https://www.bbc.com/news"
    
    # Fetch and parse the page
    response = scraper.fetch_page(url)
    if response:
        soup = scraper.parse_html(response.text)
        
        # Extract headlines using specific CSS selectors
        # Note: These selectors are examples and may need adjustment
        headlines = []
        
        # Look for common headline patterns
        for selector in ['h1', 'h2', 'h3', '.headline', '.title']:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Filter out very short text
                    headlines.append(text)
        
        # Remove duplicates while preserving order
        unique_headlines = list(dict.fromkeys(headlines))
        
        print(f"Found {len(unique_headlines)} potential headlines:")
        for i, headline in enumerate(unique_headlines[:10], 1):  # Show first 10
            print(f"{i}. {headline}")
    
    scraper.close()


def example_extract_product_information():
    """
    Example: Extract product information from an e-commerce site
    This demonstrates structured data extraction
    """
    print("\n=== Product Information Extraction Example ===")
    
    scraper = WebScraper(delay=1.5)
    
    # Example product page (using a demo e-commerce site)
    url = "https://fakestoreapi.com/"
    
    result = scraper.scrape_page(url)
    
    if not result.error:
        # Parse the HTML for product-specific information
        response = scraper.fetch_page(url)
        if response:
            soup = scraper.parse_html(response.text)
            
            # Extract product information
            product_info = {}
            
            # Look for price information
            price_selectors = ['.price', '.cost', '[class*="price"]', '[data-price]']
            for selector in price_selectors:
                price_elements = soup.select(selector)
                if price_elements:
                    product_info['prices'] = [elem.get_text(strip=True) for elem in price_elements]
                    break
            
            # Look for product titles
            title_selectors = ['h1', '.product-title', '.item-title', '[class*="title"]']
            for selector in title_selectors:
                title_elements = soup.select(selector)
                if title_elements:
                    product_info['titles'] = [elem.get_text(strip=True) for elem in title_elements]
                    break
            
            print("Product Information Found:")
            for key, value in product_info.items():
                print(f"{key}: {value}")
    
    scraper.close()


def example_scrape_multiple_pages():
    """
    Example: Scrape multiple pages efficiently
    """
    print("\n=== Multiple Pages Scraping Example ===")
    
    scraper = WebScraper(delay=1.0)
    
    # List of URLs to scrape
    urls = [
        "https://httpbin.org/",
        "https://httpbin.org/json",
        "https://httpbin.org/xml",
    ]
    
    # Scrape all pages
    results = scraper.scrape_multiple_pages(
        urls, 
        extract_text=True, 
        extract_links=True,
        extract_images=False  # Skip images for faster scraping
    )
    
    # Process results
    for result in results:
        print(f"\nURL: {result.url}")
        print(f"Status: {result.status_code}")
        print(f"Title: {result.title}")
        if result.error:
            print(f"Error: {result.error}")
        else:
            print(f"Links found: {len(result.links) if result.links else 0}")
    
    # Save results to JSON
    scraper.save_results_to_json(results, "scraping_results.json")
    
    scraper.close()


def example_custom_data_extraction():
    """
    Example: Custom data extraction with specific patterns
    """
    print("\n=== Custom Data Extraction Example ===")
    
    scraper = WebScraper()
    
    # Example URL
    url = "https://httpbin.org/"
    
    response = scraper.fetch_page(url)
    if response:
        soup = scraper.parse_html(response.text)
        
        # Custom extraction: Find all external links
        external_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and 'httpbin.org' not in href:
                external_links.append({
                    'url': href,
                    'text': link.get_text(strip=True)
                })
        
        print(f"Found {len(external_links)} external links:")
        for link in external_links:
            print(f"- {link['text']}: {link['url']}")
        
        # Custom extraction: Find all email addresses
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        text_content = scraper.extract_text(soup)
        emails = re.findall(email_pattern, text_content)
        
        if emails:
            print(f"\nFound {len(emails)} email addresses:")
            for email in set(emails):  # Remove duplicates
                print(f"- {email}")
        else:
            print("\nNo email addresses found")
    
    scraper.close()


def example_error_handling():
    """
    Example: Demonstrate error handling for various scenarios
    """
    print("\n=== Error Handling Example ===")
    
    scraper = WebScraper(timeout=5)
    
    # Test scenarios that might cause errors
    test_urls = [
        "https://httpbin.org/status/404",  # 404 error
        "https://httpbin.org/delay/10",    # Timeout (with 5s timeout setting)
        "https://invalid-domain-that-does-not-exist.com",  # DNS error
        "https://httpbin.org/status/200",  # Successful request
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        result = scraper.scrape_page(url)
        
        if result.error:
            print(f"Error encountered: {result.error}")
        else:
            print(f"Success! Status code: {result.status_code}")
    
    scraper.close()


if __name__ == "__main__":
    """
    Run all examples when script is executed directly
    """
    print("Web Scraper Examples")
    print("=" * 50)
    
    # Run all examples
    example_basic_scraping()
    example_extract_news_headlines()
    example_extract_product_information()
    example_scrape_multiple_pages()
    example_custom_data_extraction()
    example_error_handling()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
