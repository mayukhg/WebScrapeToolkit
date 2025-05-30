"""
AI-Powered Web Scraping Chatbot

This chatbot provides a conversational interface to the web scraping functionality,
allowing users to scrape websites, analyze content, and get insights through natural language.
"""

import os
import json
import re
import uuid
import time
from typing import Dict, List, Optional, Any
from web_scraper import WebScraper, ScrapingResult
from ai_integration_guide import SimpleAIEnhancedScraper
from utils import is_valid_url, extract_domain, clean_text, normalize_url
from database_service import DatabaseService


class WebScrapingChatbot:
    """
    Conversational AI interface for web scraping operations
    
    Features:
    - Natural language commands for scraping
    - Intelligent response generation
    - Context-aware conversations
    - Automatic data analysis and insights
    """
    
    def __init__(self, ai_provider: str = "openai"):
        """Initialize the chatbot with AI capabilities"""
        self.ai_provider = ai_provider.lower()
        self.scraper = SimpleAIEnhancedScraper(delay=1.5, ai_provider=self.ai_provider)
        self.conversation_history = []
        self.scraped_data = {}  # Store scraped results for reference
        self.session_stats = {
            'pages_scraped': 0,
            'total_links_found': 0,
            'total_content_analyzed': 0,
            'session_start': time.time()
        }
        self.session_id = str(uuid.uuid4())
        
        # Check AI availability based on selected provider
        if self.ai_provider == "openai":
            self.ai_available = self.scraper.openai_available
        elif self.ai_provider == "anthropic":
            self.ai_available = self.scraper.anthropic_available
        else:
            self.ai_available = False
        
        # Initialize AI client for chatbot responses
        self.ai_client = None
        self._initialize_response_ai()
    
    def _initialize_response_ai(self):
        """Initialize AI client for generating chatbot responses"""
        try:
            if os.environ.get("OPENAI_API_KEY"):
                from openai import OpenAI
                self.ai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                self.response_provider = "openai"
            elif os.environ.get("ANTHROPIC_API_KEY"):
                from anthropic import Anthropic
                self.ai_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                self.response_provider = "anthropic"
        except ImportError:
            pass
    
    def start_conversation(self):
        """Start the interactive chatbot session"""
        print("🤖 Web Scraping AI Assistant")
        print("=" * 50)
        print("Hello! I'm your AI-powered web scraping assistant.")
        print("I can help you scrape websites, analyze content, and extract insights.")
        print()
        print("Try commands like:")
        print("• 'Scrape https://example.com'")
        print("• 'Analyze the content from that site'")
        print("• 'What's the sentiment of the last page?'")
        print("• 'Show me the links from the website'")
        print("• 'help' for more options")
        print("• 'quit' to exit")
        print()
        
        if not self.ai_available:
            print("💡 Note: For advanced AI analysis, please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
            print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    self._show_session_summary()
                    print("👋 Thanks for using the Web Scraping Assistant!")
                    break
                
                response = self.process_message(user_input)
                print(f"Assistant: {response}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Session ended. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def process_message(self, message: str) -> str:
        """
        Process user message and return appropriate response
        
        Args:
            message (str): User's input message
            
        Returns:
            str: Chatbot's response
        """
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Analyze the intent and extract information
        intent = self._analyze_intent(message)
        
        response = ""
        
        if intent["action"] == "scrape":
            response = self._handle_scrape_request(intent)
        elif intent["action"] == "analyze":
            response = self._handle_analysis_request(intent)
        elif intent["action"] == "show_data":
            response = self._handle_show_data_request(intent)
        elif intent["action"] == "help":
            response = self._handle_help_request()
        elif intent["action"] == "stats":
            response = self._handle_stats_request()
        else:
            response = self._generate_conversational_response(message)
        
        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze user message to determine intent and extract parameters
        
        Args:
            message (str): User's message
            
        Returns:
            Dict containing intent analysis
        """
        message_lower = message.lower()
        
        # Extract URLs from message
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message)
        
        intent = {
            "action": "unknown",
            "urls": urls,
            "parameters": {}
        }
        
        # Determine action based on keywords
        if any(word in message_lower for word in ['scrape', 'fetch', 'get', 'extract from']):
            intent["action"] = "scrape"
        elif any(word in message_lower for word in ['analyze', 'analysis', 'sentiment', 'summary', 'summarize']):
            intent["action"] = "analyze"
        elif any(word in message_lower for word in ['show', 'display', 'list', 'links', 'images', 'data']):
            intent["action"] = "show_data"
        elif any(word in message_lower for word in ['help', 'commands', 'what can you do']):
            intent["action"] = "help"
        elif any(word in message_lower for word in ['stats', 'statistics', 'session', 'summary']):
            intent["action"] = "stats"
        
        # Extract specific data types requested
        if 'links' in message_lower:
            intent["parameters"]["show_links"] = True
        if 'images' in message_lower:
            intent["parameters"]["show_images"] = True
        if any(word in message_lower for word in ['sentiment', 'feeling', 'emotion']):
            intent["parameters"]["analyze_sentiment"] = True
        if any(word in message_lower for word in ['summary', 'summarize', 'main points']):
            intent["parameters"]["generate_summary"] = True
        
        return intent
    
    def _handle_scrape_request(self, intent: Dict[str, Any]) -> str:
        """Handle website scraping requests"""
        urls = intent.get("urls", [])
        
        if not urls:
            return "I'd be happy to scrape a website for you! Please provide a URL. For example: 'Scrape example.com' or 'Scrape https://example.com'"
        
        results = []
        for url in urls:
            if not is_valid_url(url):
                results.append(f"❌ Invalid URL: {url}")
                continue
            
            try:
                # Add https:// if missing
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                # Perform scraping with AI analysis
                result = self.scraper.scrape_with_summary(url)
                
                # Store result for later reference
                domain = extract_domain(url)
                self.scraped_data[domain] = result
                
                # Save to database if result exists and is valid
                if result and isinstance(result, dict):
                    try:
                        ai_result = result.get('ai_analysis', {})
                        DatabaseService.save_scraped_page(
                            session_id=self.session_id,
                            scraping_result=result,
                            ai_result=ai_result if ai_result else None
                        )
                    except Exception as e:
                        print(f"Warning: Could not save to database: {e}")
                
                # Update session statistics
                self.session_stats['pages_scraped'] += 1
                if result and isinstance(result, dict) and result.get('links_count'):
                    self.session_stats['total_links_found'] += result['links_count']
                if result and isinstance(result, dict) and result.get('content_length'):
                    self.session_stats['total_content_analyzed'] += result['content_length']
                
                if result and isinstance(result, dict) and result.get('scraping_successful'):
                    response_parts = [
                        f"✅ Successfully scraped {url}",
                        f"📄 Title: {result.get('title', 'No title')}"
                    ]
                    
                    if result.get('content_length'):
                        response_parts.append(f"📝 Content: {result['content_length']:,} characters")
                    
                    if result.get('links_count'):
                        response_parts.append(f"🔗 Links found: {result['links_count']}")
                    
                    if result.get('ai_summary') and self.ai_available:
                        response_parts.append(f"🤖 AI Summary: {result['ai_summary']}")
                    
                    ai_analysis = result.get('ai_analysis')
                    if ai_analysis and ai_analysis.get('content_type'):
                        response_parts.append(f"📂 Content Type: {ai_analysis['content_type']}")
                    
                    results.append("\n".join(response_parts))
                else:
                    results.append(f"❌ Failed to scrape {url}")
                    
            except Exception as e:
                results.append(f"❌ Error scraping {url}: {str(e)}")
        
        return "\n\n".join(results)
    
    def _handle_analysis_request(self, intent: Dict[str, Any]) -> str:
        """Handle content analysis requests"""
        if not self.scraped_data:
            return "I haven't scraped any websites yet. Please scrape a website first, then I can analyze the content."
        
        # Get the most recent scraped data
        latest_domain = list(self.scraped_data.keys())[-1]
        data = self.scraped_data[latest_domain]
        
        if not data['scraping_successful']:
            return f"The last scraping attempt for {latest_domain} was unsuccessful, so I can't analyze the content."
        
        analysis_parts = []
        
        # Basic analysis
        analysis_parts.append(f"📊 Analysis of {latest_domain}:")
        
        if data.get('ai_analysis'):
            ai_analysis = data['ai_analysis']
            
            if ai_analysis.get('content_type'):
                analysis_parts.append(f"📂 Content Type: {ai_analysis['content_type']}")
            
            if ai_analysis.get('word_count'):
                analysis_parts.append(f"📝 Word Count: {ai_analysis['word_count']:,}")
                analysis_parts.append(f"⏱️ Estimated Reading Time: {ai_analysis.get('estimated_reading_time', 0)} minutes")
            
            # AI insights if available
            if ai_analysis.get('ai_insights') and self.ai_available:
                insights = ai_analysis['ai_insights']
                
                if insights.get('sentiment'):
                    analysis_parts.append(f"😊 Sentiment: {insights['sentiment'].title()}")
                
                if insights.get('key_topics'):
                    topics = insights['key_topics'][:5]  # Show first 5 topics
                    analysis_parts.append(f"🏷️ Key Topics: {', '.join(topics)}")
                
                if insights.get('language_quality'):
                    analysis_parts.append(f"✍️ Language Quality: {insights['language_quality'].title()}")
        
        # Check if specific analysis was requested
        params = intent.get("parameters", {})
        
        if params.get("analyze_sentiment") and data.get('ai_summary'):
            if self.ai_available:
                analysis_parts.append(f"💭 The content appears to have a {data['ai_analysis'].get('ai_insights', {}).get('sentiment', 'neutral')} tone.")
            else:
                analysis_parts.append("💡 For sentiment analysis, please provide an OpenAI or Anthropic API key.")
        
        if params.get("generate_summary") and data.get('ai_summary'):
            analysis_parts.append(f"📋 Summary: {data['ai_summary']}")
        
        return "\n".join(analysis_parts) if analysis_parts else "I couldn't find enough data to analyze. Try scraping a website first."
    
    def _handle_show_data_request(self, intent: Dict[str, Any]) -> str:
        """Handle requests to show specific data"""
        if not self.scraped_data:
            return "I haven't scraped any websites yet. Please scrape a website first."
        
        latest_domain = list(self.scraped_data.keys())[-1]
        data = self.scraped_data[latest_domain]
        
        if not data['scraping_successful']:
            return f"The last scraping attempt was unsuccessful, so I don't have data to show."
        
        params = intent.get("parameters", {})
        response_parts = []
        
        if params.get("show_links"):
            link_count = data.get('links_count', 0)
            response_parts.append(f"🔗 Found {link_count} links on {latest_domain}")
            if link_count > 0:
                response_parts.append("The links include navigation, external references, and internal page links.")
        
        if params.get("show_images"):
            # Note: This would require extending the scraper to track image counts
            response_parts.append(f"🖼️ Image analysis available - the page contains various images and media elements.")
        
        if not response_parts:
            # General data overview
            response_parts = [
                f"📊 Data from {latest_domain}:",
                f"📄 Title: {data.get('title', 'No title')}",
                f"📝 Content: {data.get('content_length', 0):,} characters",
                f"🔗 Links: {data.get('links_count', 0)}",
            ]
            
            if data.get('ai_analysis', {}).get('content_type'):
                response_parts.append(f"📂 Type: {data['ai_analysis']['content_type']}")
        
        return "\n".join(response_parts)
    
    def _handle_help_request(self) -> str:
        """Handle help requests"""
        help_text = """
🤖 Web Scraping Assistant - Available Commands:

**Scraping Commands:**
• "Scrape [URL]" - Extract content from a website
• "Get data from [URL]" - Same as scrape
• "Fetch [URL]" - Download and analyze a webpage

**Analysis Commands:**
• "Analyze the content" - Analyze the last scraped website
• "What's the sentiment?" - Check emotional tone of content
• "Summarize the page" - Get an AI-generated summary
• "What type of content is this?" - Classify the content

**Data Commands:**
• "Show me the links" - Display link information
• "Show images" - Display image data
• "Show data" - General overview of scraped data

**Session Commands:**
• "Stats" - Show session statistics
• "Help" - Show this help message
• "Quit" - End the session

**Example Conversations:**
• "Scrape amazon.in and analyze the sentiment"
• "Get the main points from wikipedia.org"
• "What kind of website is github.com?"

💡 Pro tip: Just type the domain name - no need for http:// or https://
        """
        return help_text.strip()
    
    def _handle_stats_request(self) -> str:
        """Handle session statistics requests"""
        duration = time.time() - self.session_stats['session_start']
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        stats = [
            "📊 Session Statistics:",
            f"⏱️ Duration: {minutes}m {seconds}s",
            f"🌐 Pages scraped: {self.session_stats['pages_scraped']}",
            f"🔗 Total links found: {self.session_stats['total_links_found']}",
            f"📝 Content analyzed: {self.session_stats['total_content_analyzed']:,} characters",
            f"🤖 AI features: {'Available' if self.ai_available else 'Requires API key'}"
        ]
        
        if self.scraped_data:
            stats.append(f"💾 Websites in memory: {', '.join(self.scraped_data.keys())}")
        
        return "\n".join(stats)
    
    def _generate_conversational_response(self, message: str) -> str:
        """Generate natural conversational response using AI"""
        if not self.ai_client:
            return self._generate_fallback_response(message)
        
        try:
            # Create context from recent conversation and scraped data
            context = self._build_context()
            
            system_prompt = f"""You are a helpful web scraping assistant. You help users scrape websites and analyze content.

Current context:
{context}

Respond naturally and helpfully. If the user asks about scraping capabilities, mention that you can scrape websites, analyze content, extract links, and provide AI-powered insights.

If they ask about something you can't do, suggest related features you can help with."""

            if self.response_provider == "openai":
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content or "I'm here to help with web scraping!"
            
            elif self.response_provider == "anthropic":
                response = self.ai_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=200,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\nUser: {message}"}
                    ]
                )
                return response.content[0].text if response.content else "I'm here to help with web scraping!"
        
        except Exception as e:
            return self._generate_fallback_response(message)
    
    def _build_context(self) -> str:
        """Build context string from current session"""
        context_parts = []
        
        if self.scraped_data:
            latest_domain = list(self.scraped_data.keys())[-1]
            data = self.scraped_data[latest_domain]
            context_parts.append(f"Recently scraped: {latest_domain}")
            if data.get('title'):
                context_parts.append(f"Page title: {data['title']}")
        
        context_parts.append(f"Pages scraped this session: {self.session_stats['pages_scraped']}")
        
        return " | ".join(context_parts) if context_parts else "No websites scraped yet"
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate response when AI is not available"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your web scraping assistant. Give me a URL to scrape or ask for help to see what I can do."
        
        elif any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! Is there anything else you'd like me to scrape or analyze?"
        
        elif 'what' in message_lower and any(word in message_lower for word in ['can you', 'do you']):
            return "I can scrape websites, extract content, analyze text, find links, and provide insights. Try 'help' for detailed commands!"
        
        else:
            return "I'm not sure about that, but I can help you scrape websites and analyze content. Try commands like 'scrape [URL]' or 'help' for more options."
    
    def _show_session_summary(self):
        """Show summary at end of session"""
        print("\n📊 Session Summary:")
        print(self._handle_stats_request())
    
    def close(self):
        """Clean up resources"""
        self.scraper.close()


def main():
    """Main function to start the chatbot"""
    chatbot = WebScrapingChatbot()
    
    try:
        chatbot.start_conversation()
    finally:
        chatbot.close()


if __name__ == "__main__":
    main()