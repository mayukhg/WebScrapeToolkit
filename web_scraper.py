"""
Advanced Web Scraper using requests and BeautifulSoup

This module provides a comprehensive web scraping solution with extensive
error handling, rate limiting, and various data extraction methods.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import urllib.parse
from typing import Dict, List, Optional, Union, Any
import logging
from dataclasses import dataclass
from urllib.robotparser import RobotFileParser


@dataclass
class ScrapingResult:
    """
    Data class to store scraping results with metadata
    """
    url: str
    status_code: int
    title: Optional[str] = None
    text_content: Optional[str] = None
    links: Optional[List[Dict[str, str]]] = None
    images: Optional[List[Dict[str, str]]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WebScraper:
    """
    A comprehensive web scraper class using requests and BeautifulSoup
    
    Features:
    - Configurable headers and user agents
    - Rate limiting to be respectful to servers
    - Error handling for various scenarios
    - Support for different content types
    - Robots.txt respect (optional)
    """
    
    def __init__(self, 
                 delay: float = 1.0,
                 timeout: int = 10,
                 respect_robots: bool = True,
                 custom_headers: Optional[Dict[str, str]] = None):
        """
        Initialize the WebScraper with configuration options
        
        Args:
            delay (float): Delay between requests in seconds
            timeout (int): Request timeout in seconds
            respect_robots (bool): Whether to check robots.txt
            custom_headers (dict): Custom headers to include in requests
        """
        # Set up logging for debugging and monitoring
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Configuration parameters
        self.delay = delay
        self.timeout = timeout
        self.respect_robots = respect_robots
        
        # Default headers to mimic a real browser and avoid blocking
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Merge custom headers with defaults
        if custom_headers:
            self.default_headers.update(custom_headers)
        
        # Create a session for connection pooling and cookie persistence
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)
        
        # Keep track of last request time for rate limiting
        self.last_request_time = 0

    def _rate_limit(self):
        """
        Implement rate limiting to be respectful to target servers
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.delay:
            sleep_time = self.delay - time_since_last_request
            self.logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _check_robots_txt(self, url: str) -> bool:
        """
        Check if scraping is allowed according to robots.txt
        
        Args:
            url (str): The URL to check
            
        Returns:
            bool: True if scraping is allowed, False otherwise
        """
        if not self.respect_robots:
            return True
        
        try:
            # Parse the base URL to construct robots.txt URL
            parsed_url = urllib.parse.urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            # Create a RobotFileParser instance
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            # Check if our user agent can fetch the URL
            user_agent = self.default_headers.get('User-Agent', '*')
            can_fetch = rp.can_fetch(user_agent, url)
            
            if not can_fetch:
                self.logger.warning(f"Robots.txt disallows scraping {url}")
            
            return can_fetch
            
        except Exception as e:
            # If we can't check robots.txt, assume it's okay to proceed
            self.logger.warning(f"Could not check robots.txt for {url}: {e}")
            return True

    def fetch_page(self, url: str) -> Optional[requests.Response]:
        """
        Fetch a web page with error handling and rate limiting
        
        Args:
            url (str): The URL to fetch
            
        Returns:
            requests.Response: The response object if successful, None otherwise
        """
        try:
            # Check robots.txt compliance
            if not self._check_robots_txt(url):
                self.logger.error(f"Robots.txt disallows scraping {url}")
                return None
            
            # Implement rate limiting
            self._rate_limit()
            
            self.logger.info(f"Fetching: {url}")
            
            # Make the HTTP request
            response = self.session.get(url, timeout=self.timeout)
            
            # Check if the request was successful
            response.raise_for_status()
            
            self.logger.info(f"Successfully fetched {url} (Status: {response.status_code})")
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    def parse_html(self, html_content: str, parser: str = 'html.parser') -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup
        
        Args:
            html_content (str): The HTML content to parse
            parser (str): The parser to use ('html.parser', 'lxml', 'xml')
            
        Returns:
            BeautifulSoup: Parsed HTML object
        """
        try:
            # Create BeautifulSoup object with specified parser
            soup = BeautifulSoup(html_content, parser)
            return soup
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {e}")
            # Fallback to basic parser if the specified one fails
            return BeautifulSoup(html_content, 'html.parser')

    def extract_text(self, soup: BeautifulSoup, 
                    clean_text: bool = True,
                    remove_scripts: bool = True) -> str:
        """
        Extract all text content from parsed HTML
        
        Args:
            soup (BeautifulSoup): Parsed HTML object
            clean_text (bool): Whether to clean and normalize text
            remove_scripts (bool): Whether to remove script and style tags
            
        Returns:
            str: Extracted text content
        """
        try:
            # Remove script and style elements if requested
            if remove_scripts:
                for script in soup(["script", "style"]):
                    script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            if clean_text:
                # Clean up the text: remove extra whitespace and normalize
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return ""

    def extract_links(self, soup: BeautifulSoup, base_url: str = "") -> List[Dict[str, str]]:
        """
        Extract all links from parsed HTML
        
        Args:
            soup (BeautifulSoup): Parsed HTML object
            base_url (str): Base URL for resolving relative links
            
        Returns:
            List[Dict[str, str]]: List of dictionaries containing link information
        """
        links = []
        
        try:
            # Find all anchor tags with href attributes
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                # Resolve relative URLs to absolute URLs
                if base_url and not href.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                    href = urllib.parse.urljoin(base_url, href)
                
                # Extract additional link attributes
                link_data = {
                    'url': href,
                    'text': text,
                    'title': link.get('title', ''),
                    'target': link.get('target', ''),
                }
                
                links.append(link_data)
                
        except Exception as e:
            self.logger.error(f"Error extracting links: {e}")
        
        return links

    def extract_images(self, soup: BeautifulSoup, base_url: str = "") -> List[Dict[str, str]]:
        """
        Extract all images from parsed HTML
        
        Args:
            soup (BeautifulSoup): Parsed HTML object
            base_url (str): Base URL for resolving relative image URLs
            
        Returns:
            List[Dict[str, str]]: List of dictionaries containing image information
        """
        images = []
        
        try:
            # Find all img tags
            for img in soup.find_all('img'):
                src = img.get('src', '')
                
                # Skip if no src attribute
                if not src:
                    continue
                
                # Resolve relative URLs to absolute URLs
                if base_url and not src.startswith(('http://', 'https://', 'data:')):
                    src = urllib.parse.urljoin(base_url, src)
                
                # Extract image metadata
                image_data = {
                    'src': src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', ''),
                }
                
                images.append(image_data)
                
        except Exception as e:
            self.logger.error(f"Error extracting images: {e}")
        
        return images

    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract page metadata (title, description, keywords, etc.)
        
        Args:
            soup (BeautifulSoup): Parsed HTML object
            
        Returns:
            Dict[str, Any]: Dictionary containing page metadata
        """
        metadata = {}
        
        try:
            # Extract page title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text(strip=True)
            
            # Extract meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', '').lower()
                property_attr = meta.get('property', '').lower()
                content = meta.get('content', '')
                
                if name and content:
                    metadata[f'meta_{name}'] = content
                elif property_attr and content:
                    metadata[f'property_{property_attr}'] = content
            
            # Extract Open Graph data
            og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
            for og in og_tags:
                property_name = og.get('property', '').replace('og:', '')
                content = og.get('content', '')
                if property_name and content:
                    metadata[f'og_{property_name}'] = content
            
            # Extract canonical URL
            canonical = soup.find('link', rel='canonical')
            if canonical:
                metadata['canonical_url'] = canonical.get('href', '')
                
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {e}")
        
        return metadata

    def scrape_page(self, url: str, 
                   extract_text: bool = True,
                   extract_links: bool = True,
                   extract_images: bool = True,
                   extract_metadata: bool = True) -> ScrapingResult:
        """
        Complete scraping pipeline for a single page
        
        Args:
            url (str): The URL to scrape
            extract_text (bool): Whether to extract text content
            extract_links (bool): Whether to extract links
            extract_images (bool): Whether to extract images
            extract_metadata (bool): Whether to extract metadata
            
        Returns:
            ScrapingResult: Object containing all extracted data
        """
        result = ScrapingResult(url=url, status_code=0)
        
        try:
            # Fetch the page
            response = self.fetch_page(url)
            if not response:
                result.error = "Failed to fetch page"
                return result
            
            result.status_code = response.status_code
            
            # Parse HTML
            soup = self.parse_html(response.text)
            
            # Extract data based on parameters
            if extract_text:
                result.text_content = self.extract_text(soup)
            
            if extract_links:
                result.links = self.extract_links(soup, url)
            
            if extract_images:
                result.images = self.extract_images(soup, url)
            
            if extract_metadata:
                result.metadata = self.extract_metadata(soup)
                # Also extract title for easy access
                if result.metadata and 'title' in result.metadata:
                    result.title = result.metadata['title']
            
            self.logger.info(f"Successfully scraped {url}")
            
        except Exception as e:
            error_msg = f"Error scraping {url}: {e}"
            self.logger.error(error_msg)
            result.error = error_msg
        
        return result

    def scrape_multiple_pages(self, urls: List[str], **kwargs) -> List[ScrapingResult]:
        """
        Scrape multiple pages with the same configuration
        
        Args:
            urls (List[str]): List of URLs to scrape
            **kwargs: Additional arguments to pass to scrape_page
            
        Returns:
            List[ScrapingResult]: List of scraping results
        """
        results = []
        
        self.logger.info(f"Starting to scrape {len(urls)} pages")
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Scraping page {i}/{len(urls)}: {url}")
            result = self.scrape_page(url, **kwargs)
            results.append(result)
        
        self.logger.info(f"Completed scraping {len(urls)} pages")
        return results

    def save_results_to_json(self, results: Union[ScrapingResult, List[ScrapingResult]], 
                           filename: str):
        """
        Save scraping results to a JSON file
        
        Args:
            results: Single result or list of results to save
            filename (str): Output filename
        """
        try:
            # Convert results to serializable format
            if isinstance(results, ScrapingResult):
                data = results.__dict__
            else:
                data = [result.__dict__ for result in results]
            
            # Save to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving results to {filename}: {e}")

    def close(self):
        """
        Close the session and clean up resources
        """
        if hasattr(self, 'session'):
            self.session.close()
            self.logger.info("WebScraper session closed")
