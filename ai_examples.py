"""
AI-Enhanced Web Scraping Examples

This module demonstrates practical applications of AI-powered web scraping,
showing how to combine traditional scraping with modern AI analysis.
"""

from ai_enhanced_scraper import AIEnhancedScraper
import json


def example_news_analysis():
    """
    Example: Scrape news articles and perform AI analysis
    """
    print("=== AI-Enhanced News Analysis ===")
    
    # Initialize AI-enhanced scraper (will need API key)
    scraper = AIEnhancedScraper(ai_provider="openai", delay=2.0)
    
    # Example news URLs for analysis
    news_urls = [
        "https://www.bbc.com/news",
        "https://techcrunch.com",
        "https://www.reuters.com"
    ]
    
    for url in news_urls:
        print(f"\nAnalyzing: {url}")
        print("-" * 50)
        
        # Scrape with AI analysis
        scraping_result, ai_result = scraper.scrape_with_ai_analysis(url)
        
        if scraping_result.error:
            print(f"❌ Scraping failed: {scraping_result.error}")
            continue
        
        # Display results
        print(f"📄 Title: {scraping_result.title}")
        print(f"🌐 Status: {scraping_result.status_code}")
        print(f"🗣️ Language: {ai_result.language_detected}")
        print(f"📂 Category: {ai_result.content_category}")
        
        if ai_result.sentiment_score is not None:
            sentiment = "Positive" if ai_result.sentiment_score > 0.1 else "Negative" if ai_result.sentiment_score < -0.1 else "Neutral"
            print(f"😊 Sentiment: {sentiment} (Score: {ai_result.sentiment_score:.2f}, Confidence: {ai_result.sentiment_confidence:.2f})")
        
        if ai_result.readability_score is not None:
            print(f"📊 Quality Score: {ai_result.readability_score:.2f}/1.0")
        
        if ai_result.summary:
            print(f"📝 AI Summary: {ai_result.summary}")
        
        # Show extracted entities
        if ai_result.extracted_entities:
            entities = ai_result.extracted_entities
            if entities.get("people"):
                print(f"👥 People mentioned: {', '.join(entities['people'][:3])}")
            if entities.get("places"):
                print(f"🌍 Places mentioned: {', '.join(entities['places'][:3])}")
            if entities.get("organizations"):
                print(f"🏢 Organizations: {', '.join(entities['organizations'][:3])}")
    
    scraper.close()


def example_content_categorization():
    """
    Example: Automatically categorize different types of websites
    """
    print("\n=== AI Content Categorization ===")
    
    scraper = AIEnhancedScraper(ai_provider="anthropic", delay=1.5)
    
    # Mix of different website types
    test_urls = [
        "https://stackoverflow.com",
        "https://github.com",
        "https://www.netflix.com",
        "https://www.amazon.com",
        "https://en.wikipedia.org"
    ]
    
    categories_found = {}
    
    for url in test_urls:
        print(f"\nCategorizing: {url}")
        
        scraping_result, ai_result = scraper.scrape_with_ai_analysis(url)
        
        if not scraping_result.error and ai_result.content_category:
            category = ai_result.content_category
            print(f"📂 Category: {category}")
            
            # Track categories
            if category in categories_found:
                categories_found[category] += 1
            else:
                categories_found[category] = 1
    
    print(f"\n📊 Category Distribution:")
    for category, count in categories_found.items():
        print(f"   {category}: {count} sites")
    
    scraper.close()


def example_multilingual_analysis():
    """
    Example: Analyze content in different languages
    """
    print("\n=== Multilingual Content Analysis ===")
    
    scraper = AIEnhancedScraper(ai_provider="openai", delay=2.0)
    
    # International news sites
    multilingual_urls = [
        "https://www.lemonde.fr",      # French
        "https://www.spiegel.de",      # German  
        "https://elpais.com",          # Spanish
        "https://www.corriere.it",     # Italian
        "https://www.nytimes.com"      # English
    ]
    
    languages_detected = {}
    
    for url in multilingual_urls:
        print(f"\nAnalyzing language for: {url}")
        
        scraping_result, ai_result = scraper.scrape_with_ai_analysis(url)
        
        if not scraping_result.error:
            language = ai_result.language_detected or "Unknown"
            print(f"🗣️ Detected language: {language}")
            
            if ai_result.summary:
                print(f"📝 Summary: {ai_result.summary[:150]}...")
            
            # Track languages
            if language in languages_detected:
                languages_detected[language] += 1
            else:
                languages_detected[language] = 1
    
    print(f"\n🌍 Languages Found:")
    for lang, count in languages_detected.items():
        print(f"   {lang}: {count} sites")
    
    scraper.close()


def example_entity_extraction():
    """
    Example: Extract people, places, and organizations from news content
    """
    print("\n=== Entity Extraction from News ===")
    
    scraper = AIEnhancedScraper(ai_provider="openai", delay=1.5)
    
    # News URLs likely to contain entities
    news_urls = [
        "https://www.reuters.com",
        "https://apnews.com",
        "https://www.bbc.com/news"
    ]
    
    all_entities = {
        "people": set(),
        "places": set(),
        "organizations": set()
    }
    
    for url in news_urls:
        print(f"\nExtracting entities from: {url}")
        
        scraping_result, ai_result = scraper.scrape_with_ai_analysis(url)
        
        if not scraping_result.error and ai_result.extracted_entities:
            entities = ai_result.extracted_entities
            
            print(f"👥 People: {len(entities.get('people', []))} found")
            print(f"🌍 Places: {len(entities.get('places', []))} found")
            print(f"🏢 Organizations: {len(entities.get('organizations', []))} found")
            
            # Collect all entities
            for entity_type in ['people', 'places', 'organizations']:
                if entity_type in entities:
                    all_entities[entity_type].update(entities[entity_type])
    
    print(f"\n📊 Overall Entity Summary:")
    print(f"   Unique people mentioned: {len(all_entities['people'])}")
    print(f"   Unique places mentioned: {len(all_entities['places'])}")
    print(f"   Unique organizations mentioned: {len(all_entities['organizations'])}")
    
    # Show some examples
    if all_entities['people']:
        print(f"   Example people: {', '.join(list(all_entities['people'])[:5])}")
    if all_entities['places']:
        print(f"   Example places: {', '.join(list(all_entities['places'])[:5])}")
    if all_entities['organizations']:
        print(f"   Example organizations: {', '.join(list(all_entities['organizations'])[:5])}")
    
    scraper.close()


def example_sentiment_monitoring():
    """
    Example: Monitor sentiment across different news sources
    """
    print("\n=== News Sentiment Monitoring ===")
    
    scraper = AIEnhancedScraper(ai_provider="anthropic", delay=2.0)
    
    # Different news sources for sentiment comparison
    news_sources = [
        ("BBC News", "https://www.bbc.com/news"),
        ("CNN", "https://www.cnn.com"),
        ("Reuters", "https://www.reuters.com"),
        ("Associated Press", "https://apnews.com")
    ]
    
    sentiment_results = []
    
    for source_name, url in news_sources:
        print(f"\nAnalyzing sentiment for {source_name}...")
        
        scraping_result, ai_result = scraper.scrape_with_ai_analysis(url)
        
        if not scraping_result.error and ai_result.sentiment_score is not None:
            sentiment_results.append({
                "source": source_name,
                "sentiment_score": ai_result.sentiment_score,
                "confidence": ai_result.sentiment_confidence,
                "category": ai_result.content_category
            })
            
            sentiment_label = "Positive" if ai_result.sentiment_score > 0.1 else "Negative" if ai_result.sentiment_score < -0.1 else "Neutral"
            print(f"   Sentiment: {sentiment_label}")
            print(f"   Score: {ai_result.sentiment_score:.3f} (Confidence: {ai_result.sentiment_confidence:.3f})")
    
    # Summary of sentiment analysis
    if sentiment_results:
        avg_sentiment = sum(r["sentiment_score"] for r in sentiment_results) / len(sentiment_results)
        print(f"\n📊 Sentiment Analysis Summary:")
        print(f"   Average sentiment across sources: {avg_sentiment:.3f}")
        print(f"   Most positive source: {max(sentiment_results, key=lambda x: x['sentiment_score'])['source']}")
        print(f"   Most negative source: {min(sentiment_results, key=lambda x: x['sentiment_score'])['source']}")
    
    scraper.close()


def example_content_quality_assessment():
    """
    Example: Assess content quality across different websites
    """
    print("\n=== Content Quality Assessment ===")
    
    scraper = AIEnhancedScraper(ai_provider="openai", delay=1.5)
    
    # Mix of different quality websites
    test_sites = [
        ("Wikipedia", "https://en.wikipedia.org"),
        ("Medium", "https://medium.com"),
        ("Reddit", "https://www.reddit.com"),
        ("Stack Overflow", "https://stackoverflow.com"),
        ("GitHub", "https://github.com")
    ]
    
    quality_scores = []
    
    for site_name, url in test_sites:
        print(f"\nAssessing quality for {site_name}...")
        
        scraping_result, ai_result = scraper.scrape_with_ai_analysis(url)
        
        if not scraping_result.error and ai_result.readability_score is not None:
            quality_scores.append({
                "site": site_name,
                "quality_score": ai_result.readability_score,
                "category": ai_result.content_category,
                "language": ai_result.language_detected
            })
            
            print(f"   Quality Score: {ai_result.readability_score:.2f}/1.0")
            print(f"   Category: {ai_result.content_category}")
    
    # Rank sites by quality
    if quality_scores:
        quality_scores.sort(key=lambda x: x["quality_score"], reverse=True)
        
        print(f"\n🏆 Content Quality Ranking:")
        for i, site in enumerate(quality_scores, 1):
            print(f"   {i}. {site['site']}: {site['quality_score']:.2f}/1.0")
    
    scraper.close()


def example_save_ai_analysis():
    """
    Example: Save comprehensive AI analysis results
    """
    print("\n=== Saving AI Analysis Results ===")
    
    scraper = AIEnhancedScraper(ai_provider="openai", delay=1.0)
    
    # Analyze a comprehensive site
    url = "https://www.bbc.com/news"
    print(f"Performing comprehensive analysis of: {url}")
    
    scraping_result, ai_result = scraper.scrape_with_ai_analysis(url)
    
    if not scraping_result.error:
        # Save detailed results
        filename = "comprehensive_ai_analysis.json"
        scraper.save_ai_results_to_json(scraping_result, ai_result, filename)
        
        print(f"✅ Comprehensive analysis saved to {filename}")
        print(f"📊 Analysis includes:")
        print(f"   - Content summary")
        print(f"   - Sentiment analysis")
        print(f"   - Content categorization")
        print(f"   - Entity extraction")
        print(f"   - Language detection")
        print(f"   - Quality assessment")
    
    scraper.close()


if __name__ == "__main__":
    """
    Run AI-enhanced scraping examples
    """
    print("🤖 AI-Enhanced Web Scraping Examples")
    print("=" * 60)
    print("Note: These examples require valid API keys for OpenAI or Anthropic")
    print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables")
    print()
    
    # Run examples (will need API keys to work)
    try:
        example_news_analysis()
        example_content_categorization()
        example_multilingual_analysis()
        example_entity_extraction()
        example_sentiment_monitoring()
        example_content_quality_assessment()
        example_save_ai_analysis()
        
        print("\n" + "=" * 60)
        print("🎉 All AI examples completed!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("💡 Make sure you have valid API keys set in environment variables")