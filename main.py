"""
Main application demonstrating the comprehensive web scraper

This script provides a command-line interface for the web scraper and
demonstrates various scraping scenarios with real-world examples.
"""

import argparse
import sys
import json
from typing import List
from web_scraper import WebScraper, ScrapingResult
from scraper_examples import *
from utils import *


def scrape_single_url(url: str, output_file: str = None, verbose: bool = False):
    """
    Scrape a single URL and display/save the results
    
    Args:
        url (str): URL to scrape
        output_file (str): Optional output file for JSON results
        verbose (bool): Whether to display detailed output
    """
    print(f"Scraping: {url}")
    print("-" * 50)
    
    # Initialize scraper with verbose logging if requested
    scraper = WebScraper(delay=1.0)
    
    # Validate URL first
    if not is_valid_url(url):
        print(f"Error: Invalid URL format: {url}")
        return
    
    # Scrape the page
    result = scraper.scrape_page(url)
    
    # Display results
    if result.error:
        print(f"❌ Error: {result.error}")
    else:
        print(f"✅ Successfully scraped {url}")
        print(f"📄 Title: {result.title or 'No title found'}")
        print(f"🌐 Status Code: {result.status_code}")
        
        if result.text_content:
            print(f"📝 Text content: {len(result.text_content)} characters")
            if verbose:
                print(f"\nFirst 500 characters of text content:")
                print("-" * 30)
                print(result.text_content[:500] + "..." if len(result.text_content) > 500 else result.text_content)
        
        if result.links:
            print(f"🔗 Links found: {len(result.links)}")
            if verbose:
                internal_links = filter_internal_links(result.links, extract_domain(url))
                external_links = filter_external_links(result.links, extract_domain(url))
                print(f"   - Internal links: {len(internal_links)}")
                print(f"   - External links: {len(external_links)}")
                
                print("\nFirst 5 links:")
                for i, link in enumerate(result.links[:5], 1):
                    print(f"   {i}. {link['text'][:50]}... -> {link['url']}")
        
        if result.images:
            print(f"🖼️  Images found: {len(result.images)}")
            if verbose:
                print("\nFirst 5 images:")
                for i, img in enumerate(result.images[:5], 1):
                    print(f"   {i}. {img['alt'][:30]}... -> {img['src']}")
        
        if result.metadata:
            print(f"📊 Metadata fields: {len(result.metadata)}")
            if verbose:
                print("\nKey metadata:")
                for key, value in list(result.metadata.items())[:5]:
                    if isinstance(value, str) and len(value) < 100:
                        print(f"   {key}: {value}")
    
    # Save to file if requested
    if output_file:
        scraper.save_results_to_json(result, output_file)
        print(f"💾 Results saved to {output_file}")
    
    scraper.close()


def scrape_multiple_urls(urls: List[str], output_file: str = None):
    """
    Scrape multiple URLs and provide a summary
    
    Args:
        urls (List[str]): List of URLs to scrape
        output_file (str): Optional output file for JSON results
    """
    print(f"Scraping {len(urls)} URLs")
    print("=" * 50)
    
    scraper = WebScraper(delay=1.5)  # Slightly longer delay for multiple requests
    
    # Validate URLs
    valid_urls = []
    for url in urls:
        if is_valid_url(url):
            valid_urls.append(url)
        else:
            print(f"⚠️  Skipping invalid URL: {url}")
    
    if not valid_urls:
        print("❌ No valid URLs to scrape")
        return
    
    # Scrape all valid URLs
    results = scraper.scrape_multiple_pages(valid_urls)
    
    # Display summary
    print("\n" + "=" * 50)
    print("SCRAPING SUMMARY")
    print("=" * 50)
    
    successful = [r for r in results if not r.error]
    failed = [r for r in results if r.error]
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📊 Success rate: {len(successful)/len(results)*100:.1f}%")
    
    # Show details for each result
    for i, result in enumerate(results, 1):
        status_icon = "✅" if not result.error else "❌"
        print(f"\n{i}. {status_icon} {result.url}")
        if result.error:
            print(f"   Error: {result.error}")
        else:
            print(f"   Title: {result.title or 'No title'}")
            print(f"   Links: {len(result.links) if result.links else 0}")
            print(f"   Images: {len(result.images) if result.images else 0}")
    
    # Save results if requested
    if output_file:
        scraper.save_results_to_json(results, output_file)
        print(f"\n💾 All results saved to {output_file}")
    
    scraper.close()


def run_interactive_mode():
    """
    Run the scraper in interactive mode
    """
    print("🕷️  Interactive Web Scraper")
    print("=" * 50)
    print("Commands:")
    print("  scrape <url>     - Scrape a single URL")
    print("  batch <file>     - Scrape URLs from a text file (one per line)")
    print("  examples         - Run example scraping scenarios")
    print("  help             - Show this help message")
    print("  quit             - Exit the application")
    print()
    
    scraper = WebScraper()
    
    while True:
        try:
            command = input("scraper> ").strip()
            
            if not command:
                continue
            
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'help':
                print("Available commands: scrape, batch, examples, help, quit")
            elif cmd == 'examples':
                print("Running example scenarios...")
                example_basic_scraping()
                example_custom_data_extraction()
            elif cmd == 'scrape' and len(parts) > 1:
                url = parts[1]
                scrape_single_url(url, verbose=True)
            elif cmd == 'batch' and len(parts) > 1:
                filename = parts[1]
                try:
                    with open(filename, 'r') as f:
                        urls = [line.strip() for line in f if line.strip()]
                    scrape_multiple_urls(urls)
                except FileNotFoundError:
                    print(f"❌ File not found: {filename}")
            else:
                print("❌ Invalid command. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    scraper.close()


def main():
    """
    Main function with command-line argument parsing
    """
    parser = argparse.ArgumentParser(
        description="Comprehensive Web Scraper using requests and BeautifulSoup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url https://example.com
  python main.py --url https://example.com --output results.json --verbose
  python main.py --urls https://site1.com https://site2.com --output batch_results.json
  python main.py --examples
  python main.py --interactive
        """
    )
    
    parser.add_argument('--url', help='Single URL to scrape')
    parser.add_argument('--urls', nargs='+', help='Multiple URLs to scrape')
    parser.add_argument('--output', help='Output JSON file for results')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--examples', action='store_true', help='Run example scraping scenarios')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    # Run examples
    if args.examples:
        print("🕷️  Running Web Scraper Examples")
        print("=" * 50)
        example_basic_scraping()
        example_extract_news_headlines()
        example_scrape_multiple_pages()
        example_custom_data_extraction()
        example_error_handling()
        return
    
    # Run interactive mode
    if args.interactive:
        run_interactive_mode()
        return
    
    # Scrape single URL
    if args.url:
        scrape_single_url(args.url, args.output, args.verbose)
        return
    
    # Scrape multiple URLs
    if args.urls:
        scrape_multiple_urls(args.urls, args.output)
        return
    
    # If we get here, show help
    parser.print_help()


if __name__ == "__main__":
    main()
