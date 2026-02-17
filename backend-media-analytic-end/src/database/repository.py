import os
from sqlalchemy import create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Article, NewsSource, Favorite, SearchHistory, LinkStatus, CleanupSchedule
from config import config
from ..utils.logger import get_logger
from .db import get_connection
from datetime import datetime, timedelta

logger = get_logger(__name__)

# Use the database URL from config, but ensure the directory exists for SQLite
if "sqlite" in config.DATABASE_URL:
    # Extract the path from the SQLite URL (sqlite:///path/to/db.db)
    db_path = config.DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")

def get_session() -> Session:
    return SessionLocal()


def upsert_article(db: Session, article_data: dict) -> Article | None:
    url = article_data.get("url")
    if not url:
        return None

    obj = db.query(Article).filter(Article.url == url).first()

    if obj:
        for k, v in article_data.items():
            if hasattr(obj, k) and v is not None:
                setattr(obj, k, v)
        return obj

    obj = Article(**article_data)
    db.add(obj)

    try:
        db.flush()  # 🔥 PENTING: force insert sekarang
    except IntegrityError:
        db.rollback()
        return None

    return obj

def save_article(article: dict):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR IGNORE INTO articles (title, content, source, url, published_date, crawled_date, keywords_flagged, sentiment, confidence, prob_negative, prob_neutral, prob_positive, category, author)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        article.get("title"),
        article.get("content"),
        article.get("source"),
        article.get("url"),
        article.get("published_date"),
        article.get("crawled_date"),
        article.get("keywords_flagged"),
        article.get("sentiment"),
        article.get("confidence"),
        article.get("prob_negative"),
        article.get("prob_neutral"),
        article.get("prob_positive"),
        article.get("category"),
        article.get("author")
    ))

    conn.commit()
    conn.close()


def save_articles_bulk(articles: list):
    session = get_session()
    try:
        seen_urls = set()
        for article in articles:
            url = article.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            upsert_article(session, article)

        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def extract_keywords_flagged(text: str) -> list[str]:
    keywords = {
        "korupsi", "kriminal", "demo",
        "kecelakaan", "bencana",
        "pembunuhan", "narkoba", "olahraga", "hukum"
    }

    text = text.lower()
    found = [k for k in keywords if k in text]
    return found


def cleanup_old_articles(days: int = 30):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM articles WHERE crawled_date < datetime('now', ?);",
        (f"-{days} days",)
    )
    conn.commit()
    conn.close()


def create_cleanup_schedule(session: Session, name: str | None, days_threshold: int = 30, interval_minutes: int = 1440) -> CleanupSchedule:
    """Create a new cleanup schedule (default daily, 30 days threshold)."""
    schedule = CleanupSchedule(
        name=name,
        days_threshold=days_threshold,
        interval_minutes=interval_minutes,
        active=True
    )
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    logger.info(f"Created cleanup schedule: id={schedule.id}, days={days_threshold}, interval_min={interval_minutes}")
    return schedule


def get_cleanup_schedules(session: Session) -> list:
    """Return all cleanup schedules."""
    return session.query(CleanupSchedule).order_by(CleanupSchedule.created_at.desc()).all()


def delete_cleanup_schedule(session: Session, schedule_id: int) -> bool:
    """Delete a cleanup schedule by id."""
    schedule = session.query(CleanupSchedule).filter_by(id=schedule_id).first()
    if not schedule:
        return False
    session.delete(schedule)
    session.commit()
    logger.info(f"Deleted cleanup schedule: id={schedule_id}")
    return True


def run_cleanup_for_schedule(session: Session, schedule_id: int) -> dict:
    """Execute cleanup for a specific schedule and update last_run."""
    schedule = session.query(CleanupSchedule).filter_by(id=schedule_id, active=True).first()
    if not schedule:
        raise ValueError("Schedule not found or not active")

    # Perform cleanup (uses low-level function)
    cleanup_old_articles(days=schedule.days_threshold)

    schedule.last_run = datetime.utcnow()
    session.commit()
    logger.info(f"Executed cleanup schedule id={schedule.id}, days={schedule.days_threshold}")
    return {
        'schedule_id': schedule.id,
        'days_threshold': schedule.days_threshold,
        'last_run': schedule.last_run.isoformat()
    }


def run_due_schedules(session: Session):
    """Find schedules due to run and execute cleanup. Returns list of executed schedule ids."""
    now = datetime.utcnow()
    executed = []
    schedules = session.query(CleanupSchedule).filter_by(active=True).all()
    for s in schedules:
        run = False
        if not s.last_run:
            run = True
        else:
            delta = now - s.last_run
            if delta.total_seconds() >= s.interval_minutes * 60:
                run = True

        if run:
            try:
                cleanup_old_articles(days=s.days_threshold)
                s.last_run = now
                session.commit()
                executed.append(s.id)
                logger.info(f"Scheduled cleanup executed for schedule id={s.id}")
            except Exception as e:
                session.rollback()
                logger.exception(f"Failed running scheduled cleanup for id={s.id}: {e}")
    return executed

def get_dashboard_stats():
    """Get dashboard statistics"""
    session = get_session()
    try:
        # Total sources
        total_sources = session.query(NewsSource).count()

        # Active sources
        active_sources = session.query(NewsSource).filter_by(active=True).count()

        # Total articles
        total_articles = session.query(Article).count()

        # Recent articles (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_articles = session.query(Article).filter(Article.crawled_date >= yesterday).count()

        # Average sentiment (weighted: positive=1, neutral=0, negative=-1)
        # Formula: (prob_positive - prob_negative)
        result = session.query(
            func.avg(Article.prob_positive - Article.prob_negative).label('avg_sentiment')
        ).first()
        avg_sentiment = float(result.avg_sentiment) if result.avg_sentiment else 0

        # Last crawl time
        last_crawl = session.query(Article).order_by(Article.crawled_date.desc()).first()
        last_crawl_time = last_crawl.crawled_date.isoformat() if last_crawl else None

        return {
            'total_sources': total_sources,
            'active_sources': active_sources,
            'total_articles': total_articles,
            'recent_articles': recent_articles,
            'avg_sentiment': round(avg_sentiment, 2),
            'last_crawl_time': last_crawl_time
        }
    finally:
        session.close()

def get_recent_articles(limit=10):
    """Get recent articles for dashboard"""
    session = get_session()
    try:
        articles = session.query(Article).order_by(Article.crawled_date.desc()).limit(limit).all()
        return [{
            'id': a.id,
            'title': a.title,
            'url': a.url,
            'source': a.source,
            'sentiment': a.sentiment,
            'confidence': a.confidence,
            'crawled_date': a.crawled_date.isoformat(),
            'keywords_flagged': a.keywords_flagged
        } for a in articles]
    finally:
        session.close()

def get_articles(limit: int = 100, offset: int = 0):
    """Get articles with pagination"""
    session = get_session()
    try:
        articles = session.query(Article).order_by(Article.crawled_date.desc()).limit(limit).offset(offset).all()
        return [{
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'source': a.source,
            'url': a.url,
            'published_date': a.published_date.isoformat() if a.published_date else None,
            'crawled_date': a.crawled_date.isoformat(),
            'keywords_flagged': a.keywords_flagged,
            'sentiment': a.sentiment,
            'confidence': a.confidence,
            'prob_negative': a.prob_negative,
            'prob_neutral': a.prob_neutral,
            'prob_positive': a.prob_positive,
            'category': a.category,
            'author': a.author
        } for a in articles]
    finally:
        session.close()

def get_sources(session: Session):
    """Get all news sources"""
    return session.query(NewsSource).order_by(NewsSource.created_at.desc()).all()

def add_source(session: Session, source_data: dict):
    """Add a new news source with auto-detection support"""
    from ..crawler.dynamic_crawler import DynamicCrawler
    
    base_url = source_data.get('base_url', '').strip()
    if not base_url:
        raise ValueError("base_url is required")
    
    # Normalize base_url
    if not base_url.startswith('http'):
        base_url = 'https://' + base_url
    
    # Get crawl_type and config
    crawl_type = source_data.get('crawl_type', 'auto').lower()
    config = source_data.get('config', {})
    
    # If crawl_type is auto, run auto-detection
    if crawl_type == 'auto' or source_data.get('auto_detect', True):
        try:
            logger.info(f"Auto-detecting crawl type for {base_url}...")
            dynamic = DynamicCrawler()
            detection = dynamic.detect_crawl_type(base_url)
            
            crawl_type = detection['type']
            # Merge detected config with provided config
            if isinstance(config, dict):
                config.update(detection.get('config', {}))
            else:
                config = detection.get('config', {})
            
            logger.info(f"Auto-detected: {crawl_type} for {base_url}")
        except Exception as e:
            logger.warning(f"Auto-detection failed for {base_url}: {e}, using html fallback")
            crawl_type = 'html'
            if 'index_url' not in config:
                config['index_url'] = base_url
    
    # Ensure config has required fields based on crawl_type
    if isinstance(config, dict):
        if crawl_type == 'rss' and 'rss_url' not in config:
            # Try to find RSS URL if not provided
            try:
                dynamic = DynamicCrawler()
                rss_feeds = dynamic._detect_rss_feeds(base_url)
                if rss_feeds:
                    config['rss_url'] = rss_feeds[0]
                    logger.info(f"Found RSS: {config['rss_url']}")
            except:
                pass
            
            if 'rss_url' not in config:
                raise ValueError(f"RSS type selected but no rss_url found or provided for {base_url}")
        
        elif crawl_type == 'html':
            if 'index_url' not in config:
                config['index_url'] = base_url
            if 'base_url' not in config:
                config['base_url'] = base_url
        
        # Ensure base_url is always in config
        if 'base_url' not in config:
            config['base_url'] = base_url
    
    # Create source
    source = NewsSource(
        name=source_data['name'],
        base_url=base_url,
        crawl_type=crawl_type,
        config=config,
        active=source_data.get('active', True),
        auto_detect=source_data.get('auto_detect', True),
        is_hardcoded=source_data.get('is_hardcoded', False)
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return source

def update_source(session: Session, source_id: int, source_data: dict):
    """Update a news source"""
    source = session.query(NewsSource).filter_by(id=source_id).first()
    if not source:
        return None

    for key, value in source_data.items():
        if hasattr(source, key):
            setattr(source, key, value)

    session.commit()
    session.refresh(source)
    return source

def delete_source(session: Session, source_id: int):
    """Soft delete a news source"""
    source = session.query(NewsSource).filter_by(id=source_id).first()
    if not source:
        return False

    source.deleted_at = datetime.utcnow()
    session.commit()
    return True

def add_favorite(session: Session, article_id: int):
    """Add an article to favorites"""
    favorite = Favorite(article_id=article_id)
    session.add(favorite)
    session.commit()
    session.refresh(favorite)
    return favorite

def remove_favorite(session: Session, favorite_id: int):
    """Remove an article from favorites"""
    favorite = session.query(Favorite).filter_by(id=favorite_id).first()
    if not favorite:
        return False

    session.delete(favorite)
    session.commit()
    return True

def get_favorites(session: Session):
    """Get all favorite articles"""
    favorites = session.query(Favorite).order_by(Favorite.created_at.desc()).all()
    return [f.article for f in favorites]

def is_favorite(session: Session, article_id: int):
    """Check if an article is favorited"""
    favorite = session.query(Favorite).filter_by(article_id=article_id).first()
    return favorite is not None

# ============= SEARCH HISTORY FUNCTIONS =============

def add_search_history(session: Session, keyword: str) -> SearchHistory:
    """
    Always insert new search history entry.
    Same keyword is allowed multiple times.
    """
    history = SearchHistory(
        keyword=keyword.strip()
    )
    session.add(history)
    session.commit()
    session.refresh(history)
    return history

def get_search_history(session: Session, limit: int = 50) -> list:
    """Get search history sorted by recency and frequency with related articles"""
    histories = session.query(SearchHistory)\
        .order_by(SearchHistory.created_at.desc())\
        .limit(limit)\
        .all()
    
    results = []
    for h in histories:
        # Search for articles related to the keyword
        keyword_filter = f"%{h.keyword}%"
        related_articles = session.query(Article)\
            .filter((Article.title.ilike(keyword_filter)) | (Article.content.ilike(keyword_filter)))\
            .order_by(Article.crawled_date.desc())\
            .limit(10)\
            .all()
        
        results.append({
            'id': h.id,
            'keyword': h.keyword,
            'search_count': h.search_count,
            'created_at': h.created_at.isoformat(),
            'updated_at': h.updated_at.isoformat(),
            'related_articles': [{
                'id': a.id,
                'title': a.title,
                'url': a.url,
                'source': a.source,
                'sentiment': a.sentiment,
                'crawled_date': a.crawled_date.isoformat() if a.crawled_date else None
            } for a in related_articles]
        })
    
    return results

def delete_search_history(session: Session, history_id: int) -> bool:
    """Delete a search history entry"""
    history = session.query(SearchHistory).filter_by(id=history_id).first()
    if not history:
        return False
    
    session.delete(history)
    session.commit()
    return True

def clear_all_search_history(session: Session) -> bool:
    """Clear all search history"""
    try:
        session.query(SearchHistory).delete()
        session.commit()
        return True
    except Exception as e:
        logger.error(f"Error clearing search history: {e}")
        session.rollback()
        return False

# ============= NEWS SOURCE LISTING FUNCTIONS =============

def get_active_sources(session: Session) -> list:
    """Get all active news sources (non-deleted)"""
    sources = session.query(NewsSource)\
        .filter(NewsSource.active == True, NewsSource.deleted_at == None)\
        .order_by(NewsSource.created_at.desc())\
        .all()
    
    return [{
        'id': s.id,
        'name': s.name,
        'base_url': s.base_url,
        'crawl_type': s.crawl_type,
        'config': s.config,
        'active': s.active,
        'auto_detect': s.auto_detect,
        'is_hardcoded': s.is_hardcoded,
        'created_at': s.created_at.isoformat(),
        'updated_at': s.updated_at.isoformat()
    } for s in sources]

def get_all_sources_including_deleted(session: Session) -> list:
    """Get all sources including soft-deleted ones"""
    sources = session.query(NewsSource).order_by(NewsSource.created_at.desc()).all()
    
    return [{
        'id': s.id,
        'name': s.name,
        'base_url': s.base_url,
        'crawl_type': s.crawl_type,
        'config': s.config,
        'active': s.active,
        'auto_detect': s.auto_detect,
        'is_hardcoded': s.is_hardcoded,
        'deleted_at': s.deleted_at.isoformat() if s.deleted_at else None,
        'created_at': s.created_at.isoformat(),
        'updated_at': s.updated_at.isoformat()
    } for s in sources]

# ============= SOURCE HEALTH TRACKING =============

def record_crawl_result(session: Session, source_id: int, articles_count: int, failure_reason: str = None) -> bool:
    """
    Record crawl result for a source.
    Auto-mark as inactive if no articles found on consecutive crawls.
    
    Args:
        source_id: ID of the source
        articles_count: Number of articles found (0 if none)
        failure_reason: Reason for failure (if any)
    
    Returns:
        True if source is still active, False if marked inactive
    """
    try:
        source = session.query(NewsSource).filter_by(id=source_id).first()
        if not source:
            return False
        
        if articles_count > 0:
            # Successful crawl - reset failure counter
            source.last_successful_crawl = datetime.utcnow()
            source.consecutive_failures = 0
            source.last_crawl_article_count = articles_count
            source.failure_reason = None
            source.inactivity_detected_at = None
            source.active = True  # Re-activate if it was inactive
            logger.info(f"Crawl success for {source.name}: {articles_count} articles")
        else:
            # No articles found - increment failure counter
            source.consecutive_failures += 1
            source.last_crawl_article_count = 0
            source.failure_reason = failure_reason or "No articles found"
            logger.warning(f"Crawl failed for {source.name}: {source.consecutive_failures} consecutive failures")
            
            # Mark as inactive after 3 consecutive failures
            if source.consecutive_failures >= 3:
                source.active = False
                source.inactivity_detected_at = datetime.utcnow()
                logger.warning(f"Source marked INACTIVE: {source.name} ({source.failure_reason})")
        
        session.commit()
        return source.active
        
    except Exception as e:
        logger.error(f"Error recording crawl result for source {source_id}: {e}")
        session.rollback()
        return False

def get_inactive_sources(session: Session) -> list:
    """Get all inactive sources with reason for inactivity"""
    sources = session.query(NewsSource)\
        .filter(NewsSource.active == False, NewsSource.deleted_at == None)\
        .order_by(NewsSource.inactivity_detected_at.desc())\
        .all()
    
    return [{
        'id': s.id,
        'name': s.name,
        'base_url': s.base_url,
        'crawl_type': s.crawl_type,
        'active': s.active,
        'consecutive_failures': s.consecutive_failures,
        'failure_reason': s.failure_reason,
        'last_successful_crawl': s.last_successful_crawl.isoformat() if s.last_successful_crawl else None,
        'inactivity_detected_at': s.inactivity_detected_at.isoformat() if s.inactivity_detected_at else None,
        'created_at': s.created_at.isoformat(),
        'updated_at': s.updated_at.isoformat()
    } for s in sources]

def get_source_health(session: Session, source_id: int = None) -> dict:
    """
    Get health status of one or all sources.
    
    Args:
        source_id: If provided, get health of specific source. Otherwise get all.
    
    Returns:
        Dict with source health information
    """
    if source_id:
        source = session.query(NewsSource).filter_by(id=source_id).first()
        if not source:
            return {}
        
        return {
            'id': source.id,
            'name': source.name,
            'active': source.active,
            'consecutive_failures': source.consecutive_failures,
            'failure_reason': source.failure_reason,
            'last_successful_crawl': source.last_successful_crawl.isoformat() if source.last_successful_crawl else None,
            'last_crawl_article_count': source.last_crawl_article_count,
            'inactivity_detected_at': source.inactivity_detected_at.isoformat() if source.inactivity_detected_at else None,
            'status': 'active' if source.active else 'inactive'
        }
    else:
        # Get health of all sources
        sources = session.query(NewsSource).filter(NewsSource.deleted_at == None).all()
        
        active_count = sum(1 for s in sources if s.active)
        inactive_count = len(sources) - active_count
        
        sources_health = []
        for source in sources:
            sources_health.append({
                'id': source.id,
                'name': source.name,
                'active': source.active,
                'consecutive_failures': source.consecutive_failures,
                'failure_reason': source.failure_reason,
                'last_successful_crawl': source.last_successful_crawl.isoformat() if source.last_successful_crawl else None,
                'last_crawl_article_count': source.last_crawl_article_count,
                'inactivity_detected_at': source.inactivity_detected_at.isoformat() if source.inactivity_detected_at else None,
                'status': 'active' if source.active else 'inactive'
            })
        
        return {
            'total_sources': len(sources),
            'active_sources': active_count,
            'inactive_sources': inactive_count,
            'sources': sources_health
        }

def reactivate_source(session: Session, source_id: int) -> bool:
    """
    Manually reactivate an inactive source (reset failure counter).
    Useful for sources that had temporary issues.
    """
    try:
        source = session.query(NewsSource).filter_by(id=source_id).first()
        if not source:
            return False
        
        source.active = True
        source.consecutive_failures = 0
        source.failure_reason = None
        source.inactivity_detected_at = None
        session.commit()
        
        logger.info(f"Source reactivated: {source.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error reactivating source {source_id}: {e}")
        session.rollback()
        return False

def get_source_by_id(session: Session, source_id: int) -> dict | None:
    """Get a specific source by ID"""
    source = session.query(NewsSource).filter_by(id=source_id).first()
    
    if not source:
        return None
    
    return {
        'id': source.id,
        'name': source.name,
        'base_url': source.base_url,
        'crawl_type': source.crawl_type,
        'config': source.config,
        'active': source.active,
        'auto_detect': source.auto_detect,
        'is_hardcoded': source.is_hardcoded,
        'deleted_at': source.deleted_at.isoformat() if source.deleted_at else None,
        'created_at': source.created_at.isoformat(),
        'updated_at': source.updated_at.isoformat()
    }

# ============= FAVORITE ARTICLES FUNCTIONS =============

def get_favorite_articles_detailed(session: Session, limit: int = 100) -> list:
    favorites = (
        session.query(Favorite)
        .join(Article)
        .order_by(Favorite.created_at.desc())
        .limit(limit)
        .all()
    )

    results = []

    for f in favorites:
        results.append({
            'favorite_id': f.id,
            'article': {
                'id': f.article.id,
                'title': f.article.title,
                'url': f.article.url,
                'source': f.article.source,
                'sentiment': f.article.sentiment,
                'confidence': f.article.confidence,
                'crawled_date': f.article.crawled_date.isoformat()
                    if f.article.crawled_date else None,
            },
            'added_at': f.created_at.isoformat()
                if f.created_at else None,
        })

    return results

def get_favorite_by_article_id(session: Session, article_id: int) -> dict | None:
    """Get favorite record by article ID"""
    favorite = session.query(Favorite).filter_by(article_id=article_id).first()
    
    if not favorite:
        return None
    
    return {
        'id': favorite.id,
        'article_id': favorite.article_id,
        'created_at': favorite.created_at.isoformat() if favorite.created_at else None
    }

def remove_favorite_by_article_id(session: Session, article_id: int) -> bool:
    favorite = session.query(Favorite).filter_by(article_id=article_id).first()
    if not favorite:
        return False

    session.delete(favorite)
    session.commit()
    return True

def initialize_hardcoded_sources(session: Session) -> None:
    """Initialize hardcoded news sources in database if they don't exist"""
    hardcoded_sources = [
        {
            "name": "Kompas",
            "base_url": "https://www.kompas.com",
            "crawl_type": "rss",
            "config": {"rss_url": "https://indeks.kompas.com/rss"},
            "active": True,
            "auto_detect": True,
            "is_hardcoded": True,
        },
        {
            "name": "Detik",
            "base_url": "https://news.detik.com",
            "crawl_type": "html",
            "config": {
                "index_url": "https://www.detik.com/sumbagsel",
                "link_selector": "article a",
            },
            "active": True,
            "auto_detect": True,
            "is_hardcoded": True,
        },
        {
            "name": "Radar Lampung",
            "base_url": "https://radarlampung.disway.id",
            "crawl_type": "html",
            "config": {
                "index_url": "https://radarlampung.disway.id/",
                "link_filter": "/read/",
            },
            "active": True,
            "auto_detect": True,
            "is_hardcoded": True,
        },
        {
            "name": "Suara",
            "base_url": "https://www.suara.com",
            "crawl_type": "rss",
            "config": {"rss_url": "https://www.suara.com/rss"},
            "active": True,
            "auto_detect": True,
            "is_hardcoded": True,
        },
        {
            "name": "Tribun Lampung",
            "base_url": "https://lampung.tribunnews.com",
            "crawl_type": "rss",
            "config": {"rss_url": "https://lampung.tribunnews.com/rss"},
            "active": True,
            "auto_detect": True,
            "is_hardcoded": True,
        },
        {
            "name": "Lampung Pro",
            "base_url": "https://lampungpro.co",
            "crawl_type": "html",
            "config": {
                "index_url": "https://lampungpro.co",
                "link_filter": "/news/",
            },
            "active": True,
            "auto_detect": True,
            "is_hardcoded": True,
        },
    ]

    for source_data in hardcoded_sources:
        # Check if source already exists
        existing = session.query(NewsSource).filter_by(name=source_data["name"]).first()
        if not existing:
            new_source = NewsSource(
                name=source_data["name"],
                base_url=source_data["base_url"],
                crawl_type=source_data["crawl_type"],
                config=source_data["config"],
                active=source_data["active"],
                auto_detect=source_data["auto_detect"],
                is_hardcoded=source_data["is_hardcoded"],
            )
            session.add(new_source)
            logger.info(f"Added hardcoded source: {source_data['name']}")
        else:
            logger.info(f"Hardcoded source already exists: {source_data['name']}")

    session.commit()
    logger.info("Hardcoded sources initialization completed")


# ==================== LINK STATUS MANAGEMENT ====================

def is_link_active(url: str) -> bool:
    """
    Check if a link is marked as active in the database.
    
    Args:
        url: The URL to check
        
    Returns:
        True if link is active, False if inactive or not found
    """
    session = get_session()
    try:
        link_status = session.query(LinkStatus).filter(LinkStatus.url == url).first()
        if not link_status:
            return True  # Default to active if not in database
        return link_status.status == 'active'
    except Exception:
        # If table doesn't exist or other error, default to active
        return True
    finally:
        session.close()


def mark_link_inactive(url: str, reason: str = "Connection timeout", source: str = None) -> None:
    """
    Mark a link as inactive due to connection error or timeout.
    
    Args:
        url: The URL to mark as inactive
        reason: Reason for marking as inactive (e.g., "Connection timeout", "404 Not Found")
        source: The news source this URL came from
    """
    session = get_session()
    try:
        link_status = session.query(LinkStatus).filter(LinkStatus.url == url).first()
        
        if link_status:
            link_status.status = 'inactive'
            link_status.reason = reason
            link_status.failure_count += 1
            link_status.last_checked = datetime.utcnow()
        else:
            link_status = LinkStatus(
                url=url,
                status='inactive',
                reason=reason,
                source=source,
                failure_count=1
            )
            session.add(link_status)
        
        session.commit()
        logger.debug(f"Marked link as inactive: {url} - Reason: {reason}")
    except Exception as e:
        session.rollback()
        logger.error(f"Error marking link inactive: {e}")
    finally:
        session.close()


def mark_link_timeout(url: str, source: str = None) -> None:
    """
    Mark a link as having a timeout error.
    
    Args:
        url: The URL that timed out
        source: The news source this URL came from
    """
    mark_link_inactive(url, "Connection timeout", source)


def mark_link_active(url: str) -> None:
    """
    Mark a link as active (successful fetch).
    
    Args:
        url: The URL to mark as active
    """
    session = get_session()
    try:
        link_status = session.query(LinkStatus).filter(LinkStatus.url == url).first()
        
        if link_status:
            link_status.status = 'active'
            link_status.failure_count = 0
            link_status.last_checked = datetime.utcnow()
            session.commit()
            logger.debug(f"Marked link as active: {url}")
    except Exception as e:
        session.rollback()
        logger.error(f"Error marking link active: {e}")
    finally:
        session.close()


def get_inactive_links_count() -> int:
    """Get total count of inactive links."""
    session = get_session()
    try:
        return session.query(LinkStatus).filter(LinkStatus.status == 'inactive').count()
    finally:
        session.close()


def get_inactive_links_by_source(source: str) -> list:
    """Get all inactive links for a specific source."""
    session = get_session()
    try:
        results = session.query(LinkStatus).filter(
            LinkStatus.status == 'inactive',
            LinkStatus.source == source
        ).all()
        return [{"url": r.url, "reason": r.reason, "failures": r.failure_count} for r in results]
    finally:
        session.close()


def reset_link_status(url: str = None) -> None:
    """
    Reset link status(es). If url is None, reset all links.
    
    Args:
        url: Specific URL to reset, or None to reset all
    """
    session = get_session()
    try:
        if url:
            link_status = session.query(LinkStatus).filter(LinkStatus.url == url).first()
            if link_status:
                session.delete(link_status)
        else:
            session.query(LinkStatus).delete()
        
        session.commit()
        logger.info(f"Reset link status for: {url if url else 'all links'}")
    except Exception as e:
        session.rollback()
        logger.error(f"Error resetting link status: {e}")
    finally:
        session.close()

def get_last_crawl_status(session: Session) -> dict:
    """Get the last crawl status with timestamp and article count"""
    try:
        last_crawl = session.query(Article).order_by(Article.crawled_date.desc()).first()
        if not last_crawl:
            return {
                'last_crawl_time': None,
                'articles_in_last_crawl': 0,
                'status': 'no_crawl_history'
            }
        
        # Get articles from the same crawl (within a reasonable time window)
        crawl_window = timedelta(minutes=30)
        articles_in_crawl = session.query(Article).filter(
            Article.crawled_date >= last_crawl.crawled_date - crawl_window,
            Article.crawled_date <= last_crawl.crawled_date + crawl_window
        ).count()
        
        return {
            'last_crawl_time': last_crawl.crawled_date.isoformat() if last_crawl.crawled_date else None,
            'articles_in_last_crawl': articles_in_crawl,
            'status': 'success'
        }
    except Exception as e:
        logger.error(f"Error getting last crawl status: {e}")
        return {
            'last_crawl_time': None,
            'articles_in_last_crawl': 0,
            'status': 'error',
            'error': str(e)
        }

def get_sources_summary(session: Session) -> dict:
    """Get summary of total and active sources"""
    try:
        total_sources = session.query(NewsSource).count()
        active_sources = session.query(NewsSource).filter(
            NewsSource.active == True,
            NewsSource.deleted_at == None
        ).count()
        
        return {
            'total_sources': total_sources,
            'active_sources': active_sources,
            'inactive_sources': total_sources - active_sources
        }
    except Exception as e:
        logger.error(f"Error getting sources summary: {e}")
        return {
            'total_sources': 0,
            'active_sources': 0,
            'inactive_sources': 0,
            'error': str(e)
        }
