"""
AI Integration Guide for Web Scraper

This module demonstrates how AI can enhance web scraping capabilities
with practical examples and implementation patterns.
"""

import os
from typing import Dict, List, Optional, Any
from web_scraper import WebScraper, ScrapingResult
import json


class SimpleAIEnhancedScraper:
    """
    Simplified AI-enhanced scraper with clear integration patterns
    """
    
    def __init__(self, delay: float = 1.0):
        """Initialize the enhanced scraper"""
        self.scraper = WebScraper(delay=delay)
        self.openai_available = self._check_openai()
        self.anthropic_available = self._check_anthropic()
    
    def _check_openai(self) -> bool:
        """Check if OpenAI is available"""
        try:
            import openai
            return bool(os.environ.get("OPENAI_API_KEY"))
        except ImportError:
            return False
    
    def _check_anthropic(self) -> bool:
        """Check if Anthropic is available"""
        try:
            import anthropic
            return bool(os.environ.get("ANTHROPIC_API_KEY"))
        except ImportError:
            return False
    
    def scrape_with_summary(self, url: str) -> Dict[str, Any]:
        """
        Scrape a page and generate an AI summary
        
        Args:
            url (str): URL to scrape
            
        Returns:
            Dict containing scraping results and AI analysis
        """
        # Perform regular scraping
        result = self.scraper.scrape_page(url)
        
        analysis = {
            "url": url,
            "scraping_successful": not bool(result.error),
            "title": result.title,
            "content_length": len(result.text_content) if result.text_content else 0,
            "links_count": len(result.links) if result.links else 0,
            "ai_summary": None,
            "ai_analysis": None,
            "requires_api_key": True
        }
        
        # Add AI analysis if content available and AI is configured
        if result.text_content and (self.openai_available or self.anthropic_available):
            try:
                analysis["ai_summary"] = self._generate_summary(result.text_content)
                analysis["ai_analysis"] = self._analyze_content(result.text_content)
                analysis["requires_api_key"] = False
            except Exception as e:
                analysis["ai_summary"] = f"AI analysis failed: {str(e)}"
                analysis["ai_analysis"] = {"content_type": "Unknown", "error": str(e)}
        
        return analysis
    
    def _generate_summary(self, text: str) -> str:
        """Generate a summary using available AI service"""
        if not text or len(text.strip()) < 50:
            return "Content too short for meaningful summary"
        
        # Truncate if too long
        content = text[:3000] if len(text) > 3000 else text
        
        if self.openai_available:
            return self._openai_summarize(content)
        elif self.anthropic_available:
            return self._anthropic_summarize(content)
        else:
            return "AI service not configured - API key needed"
    
    def _analyze_content(self, text: str) -> Dict[str, Any]:
        """Analyze content characteristics"""
        analysis = {
            "word_count": len(text.split()),
            "character_count": len(text),
            "estimated_reading_time": len(text.split()) // 200,  # Average reading speed
            "content_type": self._detect_content_type(text),
            "ai_insights": None
        }
        
        if self.openai_available or self.anthropic_available:
            analysis["ai_insights"] = self._get_ai_insights(text[:2000])
        
        return analysis
    
    def _detect_content_type(self, text: str) -> str:
        """Simple content type detection based on text patterns"""
        text_lower = text.lower()
        
        # Look for common patterns
        if any(word in text_lower for word in ["breaking", "news", "reported", "according to"]):
            return "News Article"
        elif any(word in text_lower for word in ["tutorial", "how to", "step", "guide"]):
            return "Tutorial/Guide"
        elif any(word in text_lower for word in ["buy", "price", "$", "cart", "checkout"]):
            return "E-commerce"
        elif any(word in text_lower for word in ["blog", "posted", "author", "comment"]):
            return "Blog Post"
        elif any(word in text_lower for word in ["research", "study", "analysis", "data"]):
            return "Research/Academic"
        else:
            return "General Content"
    
    def _openai_summarize(self, text: str) -> str:
        """Generate summary using OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Summarize the following web content in 2-3 sentences, focusing on the main points."},
                    {"role": "user", "content": text}
                ],
                max_tokens=150
            )
            
            return response.choices[0].message.content or "Summary generation failed"
            
        except Exception as e:
            return f"OpenAI summarization error: {str(e)}"
    
    def _anthropic_summarize(self, text: str) -> str:
        """Generate summary using Anthropic"""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                messages=[
                    {"role": "user", "content": f"Summarize this web content in 2-3 sentences: {text}"}
                ]
            )
            
            return response.content[0].text if response.content else "Summary generation failed"
            
        except Exception as e:
            return f"Anthropic summarization error: {str(e)}"
    
    def _get_ai_insights(self, text: str) -> Dict[str, Any]:
        """Get AI insights about the content"""
        insights = {
            "sentiment": "neutral",
            "key_topics": [],
            "language_quality": "unknown"
        }
        
        try:
            if self.openai_available:
                insights = self._openai_insights(text)
            elif self.anthropic_available:
                insights = self._anthropic_insights(text)
        except Exception as e:
            insights["error"] = str(e)
        
        return insights
    
    def _openai_insights(self, text: str) -> Dict[str, Any]:
        """Get insights using OpenAI"""
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Analyze this text and return JSON with: sentiment (positive/negative/neutral), key_topics (array), language_quality (high/medium/low)"
                },
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            max_tokens=200
        )
        
        return json.loads(response.choices[0].message.content or "{}")
    
    def _anthropic_insights(self, text: str) -> Dict[str, Any]:
        """Get insights using Anthropic"""
        from anthropic import Anthropic
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f"Analyze this text and return JSON with sentiment, key_topics, and language_quality: {text}"
                }
            ]
        )
        
        try:
            return json.loads(response.content[0].text)
        except:
            return {"sentiment": "neutral", "key_topics": [], "language_quality": "unknown"}
    
    def close(self):
        """Clean up resources"""
        self.scraper.close()


def demonstrate_ai_capabilities():
    """
    Demonstrate various AI enhancement possibilities
    """
    print("AI Enhancement Capabilities for Web Scraping")
    print("=" * 50)
    
    capabilities = {
        "Content Analysis": [
            "Automatic summarization of long articles",
            "Sentiment analysis of reviews and comments",
            "Content categorization and tagging",
            "Language detection for multilingual sites",
            "Quality assessment and readability scoring"
        ],
        "Data Extraction": [
            "Intelligent entity extraction (people, places, organizations)",
            "Key phrase and topic identification",
            "Structured data extraction from unstructured text",
            "Contact information detection",
            "Product information parsing"
        ],
        "Content Understanding": [
            "Intent classification (informational, commercial, etc.)",
            "Content freshness and relevance scoring",
            "Fact-checking and verification assistance",
            "Duplicate content detection",
            "Content gap analysis"
        ],
        "Smart Filtering": [
            "Relevance scoring for search results",
            "Content quality filtering",
            "Spam and low-quality content detection",
            "Language-based filtering",
            "Topic-based content routing"
        ],
        "Enhanced Metadata": [
            "Auto-generated descriptions and tags",
            "Content classification and taxonomy",
            "Reading time estimation",
            "Complexity level assessment",
            "Target audience identification"
        ]
    }
    
    for category, features in capabilities.items():
        print(f"\n{category}:")
        for feature in features:
            print(f"  • {feature}")
    
    print(f"\nImplementation Requirements:")
    print(f"  • OpenAI API key for GPT-4o access")
    print(f"  • Anthropic API key for Claude access")
    print(f"  • Appropriate rate limiting and error handling")
    print(f"  • Content length management for API limits")


def example_basic_ai_scraping():
    """
    Basic example of AI-enhanced scraping
    """
    print("\nBasic AI-Enhanced Scraping Example")
    print("-" * 40)
    
    scraper = SimpleAIEnhancedScraper(delay=1.5)
    
    # Test URL
    test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    
    print(f"Analyzing: {test_url}")
    
    # Perform AI-enhanced scraping
    result = scraper.scrape_with_summary(test_url)
    
    # Display results
    print(f"\nResults:")
    print(f"  Successfully scraped: {result['scraping_successful']}")
    print(f"  Page title: {result['title']}")
    print(f"  Content length: {result['content_length']} characters")
    print(f"  Links found: {result['links_count']}")
    print(f"  Content type: {result['ai_analysis']['content_type'] if result['ai_analysis'] else 'Unknown'}")
    
    if result['ai_summary']:
        print(f"  AI Summary: {result['ai_summary']}")
    else:
        print(f"  AI Summary: Not available (requires API key)")
    
    if result['ai_analysis'] and result['ai_analysis']['ai_insights']:
        insights = result['ai_analysis']['ai_insights']
        print(f"  Sentiment: {insights.get('sentiment', 'unknown')}")
        if insights.get('key_topics'):
            print(f"  Key topics: {', '.join(insights['key_topics'][:3])}")
    
    scraper.close()


def ai_integration_checklist():
    """
    Provide a checklist for AI integration
    """
    print("\nAI Integration Checklist")
    print("=" * 30)
    
    checklist = [
        "✓ Choose AI provider (OpenAI, Anthropic, or both)",
        "✓ Obtain and configure API keys",
        "✓ Install required libraries (openai, anthropic)",
        "✓ Implement rate limiting for API calls",
        "✓ Add error handling for API failures",
        "✓ Design content preprocessing (length limits, cleaning)",
        "✓ Create result caching to avoid redundant API calls",
        "✓ Monitor API usage and costs",
        "✓ Test with various content types and languages",
        "✓ Implement fallback mechanisms for API unavailability"
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    print(f"\nAPI Key Configuration:")
    print(f"  export OPENAI_API_KEY='your-openai-key-here'")
    print(f"  export ANTHROPIC_API_KEY='your-anthropic-key-here'")


if __name__ == "__main__":
    """
    Run AI integration demonstrations
    """
    # Show capabilities
    demonstrate_ai_capabilities()
    
    # Show integration checklist
    ai_integration_checklist()
    
    # Run basic example
    example_basic_ai_scraping()
    
    print(f"\n" + "=" * 50)
    print(f"AI integration guide completed!")
    print(f"Ready to enhance your web scraper with AI capabilities.")