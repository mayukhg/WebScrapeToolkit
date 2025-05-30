"""
Database models for the web scraping application

This module defines the database schema for storing scraped data,
user sessions, and scraping history using SQLAlchemy.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import json


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class ScrapingSession(db.Model):
    """
    Stores information about user scraping sessions
    """
    __tablename__ = 'scraping_sessions'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    pages_scraped = db.Column(db.Integer, default=0)
    total_links_found = db.Column(db.Integer, default=0)
    total_content_analyzed = db.Column(db.Integer, default=0)
    
    # Relationship to scraped pages
    scraped_pages = db.relationship('ScrapedPage', backref='session', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'pages_scraped': self.pages_scraped,
            'total_links_found': self.total_links_found,
            'total_content_analyzed': self.total_content_analyzed
        }


class ScrapedPage(db.Model):
    """
    Stores information about individual scraped pages
    """
    __tablename__ = 'scraped_pages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('scraping_sessions.id'), nullable=False)
    url = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    title = db.Column(db.Text)
    status_code = db.Column(db.Integer)
    content_length = db.Column(db.Integer)
    links_count = db.Column(db.Integer)
    images_count = db.Column(db.Integer)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI Analysis results
    ai_summary = db.Column(db.Text)
    content_category = db.Column(db.String(100))
    sentiment_score = db.Column(db.Float)
    sentiment_confidence = db.Column(db.Float)
    language_detected = db.Column(db.String(50))
    quality_score = db.Column(db.Float)
    
    # Raw content and metadata stored as JSON
    text_content = db.Column(db.Text)
    page_metadata = db.Column(db.Text)  # JSON string
    error_message = db.Column(db.Text)
    
    # Relationships
    links = db.relationship('ExtractedLink', backref='page', lazy=True, cascade='all, delete-orphan')
    entities = db.relationship('ExtractedEntity', backref='page', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'domain': self.domain,
            'title': self.title,
            'status_code': self.status_code,
            'content_length': self.content_length,
            'links_count': self.links_count,
            'images_count': self.images_count,
            'scraped_at': self.scraped_at.isoformat(),
            'ai_summary': self.ai_summary,
            'content_category': self.content_category,
            'sentiment_score': self.sentiment_score,
            'language_detected': self.language_detected,
            'quality_score': self.quality_score,
            'metadata': json.loads(self.page_metadata) if self.page_metadata else None,
            'error_message': self.error_message
        }


class ExtractedLink(db.Model):
    """
    Stores links extracted from scraped pages
    """
    __tablename__ = 'extracted_links'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('scraped_pages.id'), nullable=False)
    url = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text)
    title = db.Column(db.Text)
    is_internal = db.Column(db.Boolean, default=False)
    is_external = db.Column(db.Boolean, default=False)
    link_type = db.Column(db.String(50))  # 'navigation', 'content', 'image', etc.
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'text': self.text,
            'title': self.title,
            'is_internal': self.is_internal,
            'is_external': self.is_external,
            'link_type': self.link_type
        }


class ExtractedEntity(db.Model):
    """
    Stores named entities extracted from page content
    """
    __tablename__ = 'extracted_entities'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('scraped_pages.id'), nullable=False)
    entity_text = db.Column(db.String(255), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # 'person', 'place', 'organization', etc.
    confidence = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'entity_text': self.entity_text,
            'entity_type': self.entity_type,
            'confidence': self.confidence
        }


class ScrapingStatistics(db.Model):
    """
    Stores aggregated statistics about scraping activity
    """
    __tablename__ = 'scraping_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    total_sessions = db.Column(db.Integer, default=0)
    total_pages_scraped = db.Column(db.Integer, default=0)
    total_links_found = db.Column(db.Integer, default=0)
    total_content_analyzed = db.Column(db.Integer, default=0)
    unique_domains = db.Column(db.Integer, default=0)
    avg_content_length = db.Column(db.Float, default=0.0)
    avg_links_per_page = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        return {
            'date': self.date.isoformat(),
            'total_sessions': self.total_sessions,
            'total_pages_scraped': self.total_pages_scraped,
            'total_links_found': self.total_links_found,
            'total_content_analyzed': self.total_content_analyzed,
            'unique_domains': self.unique_domains,
            'avg_content_length': self.avg_content_length,
            'avg_links_per_page': self.avg_links_per_page
        }


class PopularDomain(db.Model):
    """
    Tracks most frequently scraped domains
    """
    __tablename__ = 'popular_domains'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    scrape_count = db.Column(db.Integer, default=1)
    last_scraped = db.Column(db.DateTime, default=datetime.utcnow)
    avg_content_length = db.Column(db.Float, default=0.0)
    avg_links_count = db.Column(db.Float, default=0.0)
    success_rate = db.Column(db.Float, default=1.0)
    
    def to_dict(self):
        return {
            'domain': self.domain,
            'scrape_count': self.scrape_count,
            'last_scraped': self.last_scraped.isoformat(),
            'avg_content_length': self.avg_content_length,
            'avg_links_count': self.avg_links_count,
            'success_rate': self.success_rate
        }