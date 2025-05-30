"""
Database service for web scraping application

This module provides functions to interact with the database,
storing scraped data and managing sessions.
"""

import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from models import (
    db, ScrapingSession, ScrapedPage, ExtractedLink, 
    ExtractedEntity, ScrapingStatistics, PopularDomain
)
from utils import extract_domain


class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    def create_session(session_id: str) -> ScrapingSession:
        """Create a new scraping session"""
        session = ScrapingSession(id=session_id)
        db.session.add(session)
        db.session.commit()
        return session
    
    @staticmethod
    def get_session(session_id: str) -> Optional[ScrapingSession]:
        """Get existing session or create new one"""
        session = ScrapingSession.query.filter_by(id=session_id).first()
        if not session:
            session = DatabaseService.create_session(session_id)
        return session
    
    @staticmethod
    def update_session_activity(session_id: str):
        """Update session last activity timestamp"""
        session = ScrapingSession.query.filter_by(id=session_id).first()
        if session:
            session.last_activity = datetime.utcnow()
            db.session.commit()
    
    @staticmethod
    def save_scraped_page(session_id: str, scraping_result: Dict[str, Any], 
                         ai_result: Optional[Dict[str, Any]] = None) -> ScrapedPage:
        """Save scraped page data to database"""
        
        # Ensure session exists
        session = DatabaseService.get_session(session_id)
        
        # Extract basic information
        url = scraping_result.get('url', '')
        domain = extract_domain(url)
        
        # Create scraped page record
        page = ScrapedPage(
            session_id=session_id,
            url=url,
            domain=domain,
            title=scraping_result.get('title'),
            status_code=scraping_result.get('status_code'),
            content_length=scraping_result.get('content_length', 0),
            links_count=scraping_result.get('links_count', 0),
            text_content=scraping_result.get('text_content', '')[:50000],  # Limit size
            error_message=scraping_result.get('error_message')
        )
        
        # Add AI analysis if available
        if ai_result:
            page.ai_summary = ai_result.get('ai_summary')
            page.content_category = ai_result.get('content_category')
            page.sentiment_score = ai_result.get('sentiment_score')
            page.sentiment_confidence = ai_result.get('sentiment_confidence')
            page.language_detected = ai_result.get('language_detected')
            page.quality_score = ai_result.get('quality_score')
        
        # Store metadata as JSON
        metadata = scraping_result.get('metadata', {})
        if metadata:
            page.page_metadata = json.dumps(metadata)
        
        db.session.add(page)
        db.session.commit()
        
        # Update session statistics
        session.pages_scraped += 1
        if scraping_result.get('links_count'):
            session.total_links_found += scraping_result['links_count']
        if scraping_result.get('content_length'):
            session.total_content_analyzed += scraping_result['content_length']
        
        DatabaseService.update_session_activity(session_id)
        db.session.commit()
        
        # Update domain statistics
        DatabaseService.update_domain_stats(domain, scraping_result)
        
        return page
    
    @staticmethod
    def save_extracted_links(page_id: int, links: List[Dict[str, str]]):
        """Save extracted links for a page"""
        if not links:
            return
        
        page = ScrapedPage.query.get(page_id)
        if not page:
            return
        
        base_domain = page.domain
        
        for link_data in links[:100]:  # Limit to 100 links
            link = ExtractedLink(
                page_id=page_id,
                url=link_data.get('url', ''),
                text=link_data.get('text', '')[:500],  # Limit length
                title=link_data.get('title', '')[:200],
                is_internal=extract_domain(link_data.get('url', '')) == base_domain,
                is_external=extract_domain(link_data.get('url', '')) != base_domain
            )
            db.session.add(link)
        
        db.session.commit()
    
    @staticmethod
    def save_extracted_entities(page_id: int, entities: Dict[str, List[str]]):
        """Save extracted entities for a page"""
        if not entities:
            return
        
        for entity_type, entity_list in entities.items():
            for entity_text in entity_list[:20]:  # Limit per type
                entity = ExtractedEntity(
                    page_id=page_id,
                    entity_text=entity_text[:255],
                    entity_type=entity_type
                )
                db.session.add(entity)
        
        db.session.commit()
    
    @staticmethod
    def update_domain_stats(domain: str, scraping_result: Dict[str, Any]):
        """Update statistics for a domain"""
        popular_domain = PopularDomain.query.filter_by(domain=domain).first()
        
        if popular_domain:
            # Update existing record
            popular_domain.scrape_count += 1
            popular_domain.last_scraped = datetime.utcnow()
            
            # Update averages
            content_length = scraping_result.get('content_length', 0)
            links_count = scraping_result.get('links_count', 0)
            
            # Simple moving average
            total_scrapes = popular_domain.scrape_count
            popular_domain.avg_content_length = (
                (popular_domain.avg_content_length * (total_scrapes - 1) + content_length) / total_scrapes
            )
            popular_domain.avg_links_count = (
                (popular_domain.avg_links_count * (total_scrapes - 1) + links_count) / total_scrapes
            )
            
        else:
            # Create new record
            popular_domain = PopularDomain(
                domain=domain,
                scrape_count=1,
                avg_content_length=scraping_result.get('content_length', 0),
                avg_links_count=scraping_result.get('links_count', 0)
            )
            db.session.add(popular_domain)
        
        db.session.commit()
    
    @staticmethod
    def get_session_history(session_id: str) -> List[Dict[str, Any]]:
        """Get scraping history for a session"""
        pages = ScrapedPage.query.filter_by(session_id=session_id).order_by(
            ScrapedPage.scraped_at.desc()
        ).all()
        
        return [page.to_dict() for page in pages]
    
    @staticmethod
    def get_popular_domains(limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular scraped domains"""
        domains = PopularDomain.query.order_by(
            PopularDomain.scrape_count.desc()
        ).limit(limit).all()
        
        return [domain.to_dict() for domain in domains]
    
    @staticmethod
    def get_recent_pages(limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently scraped pages across all sessions"""
        pages = ScrapedPage.query.order_by(
            ScrapedPage.scraped_at.desc()
        ).limit(limit).all()
        
        return [page.to_dict() for page in pages]
    
    @staticmethod
    def search_pages(query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search scraped pages by title or domain"""
        pages = ScrapedPage.query.filter(
            db.or_(
                ScrapedPage.title.ilike(f'%{query}%'),
                ScrapedPage.domain.ilike(f'%{query}%'),
                ScrapedPage.url.ilike(f'%{query}%')
            )
        ).order_by(ScrapedPage.scraped_at.desc()).limit(limit).all()
        
        return [page.to_dict() for page in pages]
    
    @staticmethod
    def get_page_details(page_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a scraped page"""
        page = ScrapedPage.query.get(page_id)
        if not page:
            return None
        
        page_data = page.to_dict()
        
        # Add links and entities
        links = [link.to_dict() for link in page.links]
        entities = [entity.to_dict() for entity in page.entities]
        
        page_data['links'] = links
        page_data['entities'] = entities
        
        return page_data
    
    @staticmethod
    def get_analytics_data() -> Dict[str, Any]:
        """Get analytics data for dashboard"""
        from sqlalchemy import func
        
        # Total statistics
        total_sessions = ScrapingSession.query.count()
        total_pages = ScrapedPage.query.count()
        total_domains = PopularDomain.query.count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_pages = ScrapedPage.query.filter(
            ScrapedPage.scraped_at >= week_ago
        ).count()
        
        # Most active domains
        popular_domains = DatabaseService.get_popular_domains(5)
        
        # Content categories distribution
        category_stats = db.session.query(
            ScrapedPage.content_category,
            func.count(ScrapedPage.id).label('count')
        ).filter(
            ScrapedPage.content_category.isnot(None)
        ).group_by(ScrapedPage.content_category).all()
        
        # Language distribution
        language_stats = db.session.query(
            ScrapedPage.language_detected,
            func.count(ScrapedPage.id).label('count')
        ).filter(
            ScrapedPage.language_detected.isnot(None)
        ).group_by(ScrapedPage.language_detected).all()
        
        return {
            'total_sessions': total_sessions,
            'total_pages': total_pages,
            'total_domains': total_domains,
            'recent_pages': recent_pages,
            'popular_domains': popular_domains,
            'content_categories': [{'category': cat, 'count': count} for cat, count in category_stats],
            'languages': [{'language': lang, 'count': count} for lang, count in language_stats]
        }
    
    @staticmethod
    def cleanup_old_sessions(days_old: int = 7):
        """Clean up old sessions and their data"""
        cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
        
        # Delete old sessions (cascades to pages and related data)
        old_sessions = ScrapingSession.query.filter(
            ScrapingSession.last_activity < cutoff_date
        ).all()
        
        for session in old_sessions:
            db.session.delete(session)
        
        db.session.commit()
        return len(old_sessions)