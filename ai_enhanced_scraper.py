"""
AI-Enhanced Web Scraper

This module extends the basic web scraper with AI capabilities for intelligent
content analysis, summarization, and data extraction using OpenAI and Anthropic APIs.
"""

import json
import os
from typing import Dict, List, Optional, Any
from web_scraper import WebScraper, ScrapingResult
from dataclasses import dataclass


@dataclass
class AIAnalysisResult:
    """Data class to store AI analysis results"""
    summary: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_confidence: Optional[float] = None
    key_topics: Optional[List[str]] = None
    content_category: Optional[str] = None
    extracted_entities: Optional[Dict[str, List[str]]] = None
    readability_score: Optional[float] = None
    language_detected: Optional[str] = None


class AIEnhancedScraper(WebScraper):
    """
    Enhanced web scraper with AI-powered analysis capabilities
    
    Features:
    - Intelligent content summarization
    - Sentiment analysis of scraped content
    - Automatic content categorization
    - Entity extraction (people, places, organizations)
    - Language detection
    - Content quality assessment
    """
    
    def __init__(self, ai_provider: str = "openai", **kwargs):
        """
        Initialize the AI-enhanced scraper
        
        Args:
            ai_provider (str): AI service to use ("openai" or "anthropic")
            **kwargs: Additional arguments passed to WebScraper
        """
        super().__init__(**kwargs)
        self.ai_provider = ai_provider.lower()
        self.ai_client = None
        self.ai_available = False
        
        # Initialize AI client based on provider
        self._initialize_ai_client()
    
    def _initialize_ai_client(self):
        """Initialize the AI client based on the selected provider"""
        try:
            if self.ai_provider == "openai":
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    self.logger.warning("OPENAI_API_KEY not found. AI features will be disabled.")
                    return
                self.ai_client = OpenAI(api_key=api_key)
                self.ai_available = True
                self.logger.info("OpenAI client initialized successfully")
                
            elif self.ai_provider == "anthropic":
                from anthropic import Anthropic
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    self.logger.warning("ANTHROPIC_API_KEY not found. AI features will be disabled.")
                    return
                self.ai_client = Anthropic(api_key=api_key)
                self.ai_available = True
                self.logger.info("Anthropic client initialized successfully")
                
            else:
                self.logger.error(f"Unsupported AI provider: {self.ai_provider}")
                
        except ImportError as e:
            self.logger.error(f"Failed to import AI library: {e}")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI client: {e}")
    
    def summarize_content(self, text: str, max_length: int = 200) -> str:
        """
        Generate an intelligent summary of the scraped content
        
        Args:
            text (str): Text content to summarize
            max_length (int): Maximum length of the summary
            
        Returns:
            str: AI-generated summary
        """
        if not self.ai_client or not text.strip():
            return ""
        
        try:
            # Truncate text if too long (most APIs have token limits)
            if len(text) > 4000:
                text = text[:4000] + "..."
            
            if self.ai_provider == "openai":
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are an expert content summarizer. Create a concise, informative summary of the provided text in maximum {max_length} words. Focus on the main points and key information."
                        },
                        {
                            "role": "user",
                            "content": f"Summarize this content:\n\n{text}"
                        }
                    ],
                    max_tokens=max_length * 2  # Rough estimate for token count
                )
                content = response.choices[0].message.content
                return content.strip() if content else ""
                
            elif self.ai_provider == "anthropic":
                response = self.ai_client.messages.create(
                    model="claude-3-5-sonnet-20241022",  # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
                    max_tokens=max_length * 2,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Please summarize the following content in maximum {max_length} words, focusing on the main points and key information:\n\n{text}"
                        }
                    ]
                )
                if response.content and len(response.content) > 0:
                    return response.content[0].text
                return ""
                
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return ""
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze the sentiment of the scraped content
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            Dict[str, float]: Sentiment score and confidence
        """
        if not self.ai_client or not text.strip():
            return {"score": 0.0, "confidence": 0.0}
        
        try:
            if len(text) > 3000:
                text = text[:3000] + "..."
            
            if self.ai_provider == "openai":
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a sentiment analysis expert. Analyze the sentiment of the text and respond with JSON containing 'score' (float from -1.0 to 1.0, where -1 is very negative, 0 is neutral, 1 is very positive) and 'confidence' (float from 0.0 to 1.0)."
                        },
                        {
                            "role": "user",
                            "content": f"Analyze the sentiment of this text:\n\n{text}"
                        }
                    ],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
                
            elif self.ai_provider == "anthropic":
                response = self.ai_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=200,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Analyze the sentiment of this text and respond with JSON containing 'score' (float from -1.0 to 1.0) and 'confidence' (float from 0.0 to 1.0):\n\n{text}"
                        }
                    ]
                )
                return json.loads(response.content[0].text)
                
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return {"score": 0.0, "confidence": 0.0}
    
    def categorize_content(self, text: str, title: str = "") -> str:
        """
        Automatically categorize the content type/topic
        
        Args:
            text (str): Text content to categorize
            title (str): Page title for additional context
            
        Returns:
            str: Content category
        """
        if not self.ai_client or not text.strip():
            return "Unknown"
        
        try:
            content_with_title = f"Title: {title}\n\nContent: {text[:2000]}"
            
            categories = [
                "News & Current Events", "Technology & Science", "Business & Finance",
                "Entertainment & Media", "Sports", "Health & Medical", "Education",
                "Travel & Lifestyle", "Politics & Government", "E-commerce & Shopping",
                "Blog & Personal", "Reference & Documentation", "Other"
            ]
            
            if self.ai_provider == "openai":
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": f"Categorize the following content into one of these categories: {', '.join(categories)}. Respond with only the category name."
                        },
                        {
                            "role": "user",
                            "content": content_with_title
                        }
                    ],
                    max_tokens=50
                )
                return response.choices[0].message.content.strip()
                
            elif self.ai_provider == "anthropic":
                response = self.ai_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=50,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Categorize this content into one of these categories: {', '.join(categories)}. Respond with only the category name.\n\n{content_with_title}"
                        }
                    ]
                )
                return response.content[0].text.strip()
                
        except Exception as e:
            self.logger.error(f"Error categorizing content: {e}")
            return "Unknown"
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities (people, places, organizations) from the content
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            Dict[str, List[str]]: Dictionary of entity types and their values
        """
        if not self.ai_client or not text.strip():
            return {"people": [], "places": [], "organizations": [], "other": []}
        
        try:
            if len(text) > 3000:
                text = text[:3000] + "..."
            
            if self.ai_provider == "openai":
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "Extract named entities from the text and return as JSON with keys: 'people', 'places', 'organizations', 'other'. Each key should contain a list of unique entities found."
                        },
                        {
                            "role": "user",
                            "content": f"Extract entities from this text:\n\n{text}"
                        }
                    ],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
                
            elif self.ai_provider == "anthropic":
                response = self.ai_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Extract named entities from this text and return as JSON with keys 'people', 'places', 'organizations', 'other':\n\n{text}"
                        }
                    ]
                )
                return json.loads(response.content[0].text)
                
        except Exception as e:
            self.logger.error(f"Error extracting entities: {e}")
            return {"people": [], "places": [], "organizations": [], "other": []}
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the content
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            str: Detected language code or name
        """
        if not self.ai_client or not text.strip():
            return "unknown"
        
        try:
            sample_text = text[:500]  # Use first 500 characters for detection
            
            if self.ai_provider == "openai":
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "Detect the language of the given text. Respond with the language name in English (e.g., 'English', 'Spanish', 'French')."
                        },
                        {
                            "role": "user",
                            "content": f"What language is this text: {sample_text}"
                        }
                    ],
                    max_tokens=20
                )
                return response.choices[0].message.content.strip()
                
            elif self.ai_provider == "anthropic":
                response = self.ai_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=20,
                    messages=[
                        {
                            "role": "user",
                            "content": f"What language is this text? Respond with just the language name: {sample_text}"
                        }
                    ]
                )
                return response.content[0].text.strip()
                
        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            return "unknown"
    
    def analyze_content_quality(self, text: str) -> float:
        """
        Assess the quality and readability of the content
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            float: Quality score from 0.0 to 1.0
        """
        if not self.ai_client or not text.strip():
            return 0.0
        
        try:
            sample_text = text[:2000]
            
            if self.ai_provider == "openai":
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "Assess the quality of this text content on a scale of 0.0 to 1.0, considering factors like clarity, coherence, informativeness, and readability. Respond with only a number between 0.0 and 1.0."
                        },
                        {
                            "role": "user",
                            "content": f"Rate the quality of this content: {sample_text}"
                        }
                    ],
                    max_tokens=10
                )
                return float(response.choices[0].message.content.strip())
                
            elif self.ai_provider == "anthropic":
                response = self.ai_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=10,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Rate the quality of this content on a scale of 0.0 to 1.0. Respond with only a number: {sample_text}"
                        }
                    ]
                )
                return float(response.content[0].text.strip())
                
        except Exception as e:
            self.logger.error(f"Error analyzing content quality: {e}")
            return 0.0
    
    def scrape_with_ai_analysis(self, url: str, **kwargs) -> tuple[ScrapingResult, AIAnalysisResult]:
        """
        Scrape a page and perform comprehensive AI analysis
        
        Args:
            url (str): URL to scrape
            **kwargs: Additional arguments for scraping
            
        Returns:
            tuple: (ScrapingResult, AIAnalysisResult)
        """
        # First, perform regular scraping
        scraping_result = self.scrape_page(url, **kwargs)
        
        # Initialize AI analysis result
        ai_result = AIAnalysisResult()
        
        # If scraping failed or no AI client available, return empty analysis
        if scraping_result.error or not self.ai_client or not scraping_result.text_content:
            return scraping_result, ai_result
        
        self.logger.info(f"Performing AI analysis for {url}")
        
        try:
            # Perform various AI analyses
            ai_result.summary = self.summarize_content(scraping_result.text_content)
            
            sentiment_data = self.analyze_sentiment(scraping_result.text_content)
            ai_result.sentiment_score = sentiment_data.get("score", 0.0)
            ai_result.sentiment_confidence = sentiment_data.get("confidence", 0.0)
            
            ai_result.content_category = self.categorize_content(
                scraping_result.text_content, 
                scraping_result.title or ""
            )
            
            ai_result.extracted_entities = self.extract_entities(scraping_result.text_content)
            ai_result.language_detected = self.detect_language(scraping_result.text_content)
            ai_result.readability_score = self.analyze_content_quality(scraping_result.text_content)
            
            self.logger.info(f"AI analysis completed for {url}")
            
        except Exception as e:
            self.logger.error(f"Error during AI analysis: {e}")
        
        return scraping_result, ai_result
    
    def save_ai_results_to_json(self, scraping_result: ScrapingResult, ai_result: AIAnalysisResult, filename: str):
        """
        Save both scraping and AI analysis results to JSON
        
        Args:
            scraping_result (ScrapingResult): Original scraping results
            ai_result (AIAnalysisResult): AI analysis results
            filename (str): Output filename
        """
        try:
            # Combine results into a single structure
            combined_result = {
                "scraping": {
                    "url": scraping_result.url,
                    "status_code": scraping_result.status_code,
                    "title": scraping_result.title,
                    "text_length": len(scraping_result.text_content) if scraping_result.text_content else 0,
                    "links_count": len(scraping_result.links) if scraping_result.links else 0,
                    "images_count": len(scraping_result.images) if scraping_result.images else 0,
                    "error": scraping_result.error
                },
                "ai_analysis": {
                    "summary": ai_result.summary,
                    "sentiment_score": ai_result.sentiment_score,
                    "sentiment_confidence": ai_result.sentiment_confidence,
                    "content_category": ai_result.content_category,
                    "extracted_entities": ai_result.extracted_entities,
                    "language_detected": ai_result.language_detected,
                    "readability_score": ai_result.readability_score
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(combined_result, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"AI-enhanced results saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving AI results: {e}")