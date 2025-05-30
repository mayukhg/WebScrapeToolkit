"""
Utility functions for web scraping operations

This module provides helper functions that complement the main WebScraper class,
including data cleaning, URL validation, and common scraping patterns.
"""

import re
import urllib.parse
from typing import List, Dict, Any, Optional
import time
import random
from dataclasses import dataclass


@dataclass
class URLInfo:
    """Data class for URL information"""
    url: str
    domain: str
    path: str
    is_valid: bool
    scheme: str


def clean_text(text: str) -> str:
    """
    Clean and normalize text content extracted from web pages
    
    Args:
        text (str): Raw text content
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove common unwanted characters
    text = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\']', '', text)
    
    return text


def normalize_url(url: str) -> str:
    """
    Normalize URL by adding appropriate protocol if missing
    
    Args:
        url (str): URL that may be missing protocol
        
    Returns:
        str: URL with proper protocol
    """
    if not url:
        return url
    
    # If URL already has protocol, return as is
    if url.startswith(('http://', 'https://')):
        return url
    
    # Remove any leading slashes
    url = url.lstrip('/')
    
    # Try HTTPS first for most domains
    return 'https://' + url


def extract_domain(url: str) -> str:
    """
    Extract domain from URL
    
    Args:
        url (str): Full URL
        
    Returns:
        str: Domain name
    """
    try:
        # Normalize URL first
        if not url.startswith(('http://', 'https://')):
            url = normalize_url(url)
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc
    except Exception:
        return ""


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid and properly formatted
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Add protocol if no scheme is provided
        if not url.startswith(('http://', 'https://')):
            url = normalize_url(url)
        
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False


def parse_url(url: str) -> URLInfo:
    """
    Parse URL and extract detailed information
    
    Args:
        url (str): URL to parse
        
    Returns:
        URLInfo: Object containing URL information
    """
    try:
        parsed = urllib.parse.urlparse(url)
        return URLInfo(
            url=url,
            domain=parsed.netloc,
            path=parsed.path,
            is_valid=bool(parsed.scheme and parsed.netloc),
            scheme=parsed.scheme
        )
    except Exception:
        return URLInfo(
            url=url,
            domain="",
            path="",
            is_valid=False,
            scheme=""
        )


def filter_internal_links(links: List[Dict[str, str]], base_domain: str) -> List[Dict[str, str]]:
    """
    Filter links to only include internal links (same domain)
    
    Args:
        links (List[Dict[str, str]]): List of link dictionaries
        base_domain (str): Base domain to filter by
        
    Returns:
        List[Dict[str, str]]: Filtered list of internal links
    """
    internal_links = []
    
    for link in links:
        url = link.get('url', '')
        if not url:
            continue
        
        domain = extract_domain(url)
        
        # Include relative links and links from the same domain
        if not domain or domain == base_domain:
            internal_links.append(link)
    
    return internal_links


def filter_external_links(links: List[Dict[str, str]], base_domain: str) -> List[Dict[str, str]]:
    """
    Filter links to only include external links (different domain)
    
    Args:
        links (List[Dict[str, str]]): List of link dictionaries
        base_domain (str): Base domain to filter against
        
    Returns:
        List[Dict[str, str]]: Filtered list of external links
    """
    external_links = []
    
    for link in links:
        url = link.get('url', '')
        if not url:
            continue
        
        domain = extract_domain(url)
        
        # Include only links from different domains
        if domain and domain != base_domain:
            external_links.append(link)
    
    return external_links


def extract_emails_from_text(text: str) -> List[str]:
    """
    Extract email addresses from text content
    
    Args:
        text (str): Text content to search
        
    Returns:
        List[str]: List of unique email addresses found
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # Remove duplicates


def extract_phone_numbers_from_text(text: str) -> List[str]:
    """
    Extract phone numbers from text content
    
    Args:
        text (str): Text content to search
        
    Returns:
        List[str]: List of phone numbers found
    """
    # Pattern for various phone number formats
    phone_patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
        r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
        r'\b\d{3}\.\d{3}\.\d{4}\b',  # 123.456.7890
        r'\b\d{10}\b',  # 1234567890
        r'\+1\s*\d{3}\s*\d{3}\s*\d{4}\b',  # +1 123 456 7890
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phone_numbers.extend(matches)
    
    return list(set(phone_numbers))  # Remove duplicates


def create_random_delay(min_delay: float, max_delay: float) -> float:
    """
    Create a random delay between min and max values
    This helps make scraping look more human-like
    
    Args:
        min_delay (float): Minimum delay in seconds
        max_delay (float): Maximum delay in seconds
        
    Returns:
        float: Random delay value
    """
    return random.uniform(min_delay, max_delay)





def get_file_extension_from_url(url: str) -> str:
    """
    Extract file extension from URL
    
    Args:
        url (str): URL to analyze
        
    Returns:
        str: File extension (without dot) or empty string
    """
    try:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        if '.' in path:
            return path.split('.')[-1].lower()
        return ""
    except Exception:
        return ""


def is_image_url(url: str) -> bool:
    """
    Check if URL points to an image file
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if URL appears to be an image
    """
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'}
    extension = get_file_extension_from_url(url)
    return extension in image_extensions


def is_document_url(url: str) -> bool:
    """
    Check if URL points to a document file
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if URL appears to be a document
    """
    document_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'}
    extension = get_file_extension_from_url(url)
    return extension in document_extensions


def create_sitemap_from_links(links: List[Dict[str, str]], base_domain: str) -> Dict[str, Any]:
    """
    Create a simple sitemap structure from extracted links
    
    Args:
        links (List[Dict[str, str]]): List of link dictionaries
        base_domain (str): Base domain for the sitemap
        
    Returns:
        Dict[str, Any]: Sitemap structure
    """
    sitemap = {
        'domain': base_domain,
        'total_links': len(links),
        'internal_links': [],
        'external_links': [],
        'image_links': [],
        'document_links': [],
        'other_links': []
    }
    
    for link in links:
        url = link.get('url', '')
        if not url:
            continue
        
        domain = extract_domain(url)
        
        # Categorize the link
        if domain == base_domain or not domain:
            sitemap['internal_links'].append(link)
        else:
            sitemap['external_links'].append(link)
        
        if is_image_url(url):
            sitemap['image_links'].append(link)
        elif is_document_url(url):
            sitemap['document_links'].append(link)
        else:
            sitemap['other_links'].append(link)
    
    return sitemap


def format_scraping_summary(results: List[Any]) -> str:
    """
    Create a formatted summary of scraping results
    
    Args:
        results (List[Any]): List of scraping results
        
    Returns:
        str: Formatted summary string
    """
    if not results:
        return "No scraping results to summarize."
    
    successful = sum(1 for r in results if not hasattr(r, 'error') or not r.error)
    failed = len(results) - successful
    
    summary = f"""
Scraping Summary:
================
Total pages processed: {len(results)}
Successful: {successful}
Failed: {failed}
Success rate: {(successful/len(results)*100):.1f}%

Results breakdown:
"""
    
    for i, result in enumerate(results, 1):
        status = "✓" if not hasattr(result, 'error') or not result.error else "✗"
        url = getattr(result, 'url', f'Result {i}')
        summary += f"{status} {url}\n"
    
    return summary
