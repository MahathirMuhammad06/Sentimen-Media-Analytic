from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(100))
    url = Column(String(500), unique=True)
    published_date = Column(DateTime)
    crawled_date = Column(DateTime, default=datetime.utcnow)
    keywords_flagged = Column(String(512), nullable=True) # coma separated keywords found

    # Sentiment analysis results
    sentiment = Column(String(20))
    confidence = Column(Float)
    prob_negative = Column(Float)
    prob_neutral = Column(Float)
    prob_positive = Column(Float)

    # Metadata
    category = Column(String(100))
    author = Column(String(200))

    # Relationships
    favorites = relationship("Favorite", back_populates="article")

class NewsSource(Base):
    __tablename__ = 'news_sources'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    base_url = Column(String(500), nullable=False)  # Main domain URL
    crawl_type = Column(String(20), nullable=False, default='auto')  # 'rss', 'html', 'sitemap', 'auto'
    config = Column(JSON, nullable=False)  # JSON config for crawling
    active = Column(Boolean, default=True)
    auto_detect = Column(Boolean, default=True)  # Auto-detect RSS/Sitemap/HTML structure
    is_hardcoded = Column(Boolean, default=False)  # Mark if from original hardcoded sources
    
    # Source health tracking
    last_successful_crawl = Column(DateTime, nullable=True)  # Last time articles were extracted
    consecutive_failures = Column(Integer, default=0)  # Count of consecutive failed crawls
    last_crawl_article_count = Column(Integer, default=0)  # Number of articles in last crawl
    failure_reason = Column(String(255), nullable=True)  # Reason why source is inactive
    inactivity_detected_at = Column(DateTime, nullable=True)  # When inactivity was detected
    
    deleted_at = Column(DateTime, nullable=True)  # Soft delete support
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Favorite(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    article = relationship("Article", back_populates="favorites")

class LinkStatus(Base):
    """Track inactive/unreachable links to avoid repeated crawling attempts"""
    __tablename__ = 'link_status'

    id = Column(Integer, primary_key=True)
    url = Column(String(500), unique=True, nullable=False, index=True)
    status = Column(String(50), default='active')  # 'active', 'inactive', 'timeout', 'error'
    reason = Column(String(255), nullable=True)  # Reason for status (e.g., "Connection timeout", "404 Not Found")
    source = Column(String(100), nullable=True)  # Which source this URL came from
    failure_count = Column(Integer, default=0)  # Track how many times it failed
    last_checked = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SearchHistory(Base):
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True)
    keyword = Column(String(500), nullable=False)
    search_count = Column(Integer, default=1)  # Track how many times searched
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CleanupSchedule(Base):
    """Schedule entry for automatic cleanup of old articles"""
    __tablename__ = 'cleanup_schedules'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=True)
    days_threshold = Column(Integer, nullable=False, default=30)  # delete articles older than X days
    interval_minutes = Column(Integer, nullable=False, default=1440)  # run every X minutes (default: 1440 = daily)
    last_run = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
