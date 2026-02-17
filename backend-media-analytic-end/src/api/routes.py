from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from ..database.repository import (
    get_session, get_sources, add_source, delete_source, update_source, 
    get_dashboard_stats, get_recent_articles, get_articles,
    add_favorite, remove_favorite, get_favorites, is_favorite,
    add_search_history, get_search_history, delete_search_history,
    clear_all_search_history, get_active_sources, get_all_sources_including_deleted,
    get_source_by_id, get_favorite_articles_detailed, get_favorite_by_article_id,
    remove_favorite_by_article_id, get_last_crawl_status, get_sources_summary,
    get_inactive_sources, get_source_health, reactivate_source
)
from ..database.repository import (
    create_cleanup_schedule, get_cleanup_schedules, delete_cleanup_schedule,
    run_cleanup_for_schedule, run_due_schedules, cleanup_old_articles
)
from ..database.models import Article, NewsSource, SearchHistory
from ..database.schemas import NewsSourceCreate, NewsSourceUpdate
from ..utils.logger import get_logger
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

logger = get_logger(__name__)
router = APIRouter(prefix="/v1")

# Start background cleanup scheduler (poll every 60 seconds)
try:
    from ..utils.scheduler import start_scheduler
    # start scheduler in background when routes module is imported
    start_scheduler(poll_interval_seconds=60)
except Exception:
    logger.exception("Failed to start cleanup scheduler")

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/articles", response_model=List[dict])
def list_articles(
    q: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        # ✅ FIX KE-3: SIMPAN SEARCH HISTORY
        if q and q.strip():
            add_search_history(db, q.strip())

        query = db.query(Article)

        if q:
            like = f"%{q}%"
            query = query.filter(
                (Article.title.ilike(like)) | 
                (Article.content.ilike(like)) |
                (Article.keywords_flagged.ilike(like))
            )

        if source:
            query = query.filter(Article.source == source)

        items = query.order_by(Article.crawled_date.desc()).all()

        results = []
        for a in items:
            results.append({
                "id": a.id,
                "title": a.title,
                "url": a.url,
                "source": a.source,
                "sentiment": a.sentiment,
                "crawled_date": a.crawled_date,
                "keywords_flagged": a.keywords_flagged,
            })

        return results

    except Exception:
        logger.exception("Failed listing articles")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/article/{article_id}", response_model=dict)
def get_article(article_id: int, db: Session = Depends(get_db)):
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Check if article is in favorites
    is_fav = is_favorite(db, article_id)
    
    return {
        "id": a.id,
        "title": a.title,
        "url": a.url,
        "source": a.source,
        "content": a.content,
        "sentiment": a.sentiment,
        "keywords_flagged": a.keywords_flagged,
        "crawled_date": a.crawled_date,
        "is_favorite": is_fav,
    }

# ============= NEWS SOURCES API =============

@router.get("/sources", response_model=List[dict])
def list_sources(db: Session = Depends(get_db)):
    """Get all active news sources"""
    try:
        sources = get_active_sources(db)
        return sources
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sources", response_model=dict)
def create_source(source: NewsSourceCreate, db: Session = Depends(get_db)):
    """Add a new news source with auto-detection"""
    try:
        # Add source with auto-detection
        new_source = add_source(db, source.dict())
        logger.info(f"Created source: {new_source.name} (type: {new_source.crawl_type})")
        return {
            "id": new_source.id,
            "name": new_source.name,
            "base_url": new_source.base_url,
            "crawl_type": new_source.crawl_type,
            "config": new_source.config,
            "active": new_source.active,
            "auto_detect": new_source.auto_detect,
            "created_at": new_source.created_at.isoformat(),
            "message": f"Source created with {new_source.crawl_type} crawler"
        }
    except ValueError as e:
        logger.error(f"Validation error adding source: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding source: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources/{source_id}", response_model=dict)
def get_source_detail(source_id: int, db: Session = Depends(get_db)):
    """Get a specific news source"""
    try:
        source = get_source_by_id(db, source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        return source
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sources/{source_id}", response_model=dict)
def update_source_detail(source_id: int, source_update: NewsSourceUpdate, db: Session = Depends(get_db)):
    """Update a news source"""
    try:
        source = db.query(NewsSource).filter_by(id=source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        for key, value in source_update.dict(exclude_unset=True).items():
            if hasattr(source, key):
                setattr(source, key, value)

        source.updated_at = datetime.utcnow()
        db.commit()
        return get_source_by_id(db, source_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sources/{source_id}")
def delete_source_detail(source_id: int, soft_delete: bool = False, db: Session = Depends(get_db)):
    """
    Delete a news source
    
    Parameters:
    - source_id: ID of the source to delete
    - soft_delete: If True, soft delete only (mark as deleted); if False, permanently delete from database (default: False - hard delete)
    
    Returns:
    - Dictionary with message and source_id
    """
    try:
        source = db.query(NewsSource).filter_by(id=source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        if soft_delete:
            # Soft delete - just mark as deleted
            success = delete_source(db, source_id)
            if not success:
                raise HTTPException(status_code=404, detail="Source not found")
            logger.info(f"Soft deleted source: {source.name} (ID: {source_id})")
            return {
                "message": "Source soft deleted (data preserved)",
                "source_id": source_id,
                "type": "soft_delete"
            }
        else:
            # Hard delete - remove from database completely (DEFAULT)
            db.delete(source)
            db.commit()
            logger.info(f"Hard deleted source: {source.name} (ID: {source_id})")
            return {
                "message": "Source permanently deleted from database",
                "source_id": source_id,
                "type": "hard_delete"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sources/{source_id}/test-crawl")
def test_crawl_source(source_id: int, db: Session = Depends(get_db)):
    """
    Test crawling on a source and fetch sample articles
    Useful for verifying that source configuration works correctly
    
    Returns:
    - source details
    - articles_found: number of articles extracted
    - sample_articles: up to 5 sample articles from crawl
    - message: status message
    """
    try:
        from ..crawler.news_crawler import NewsCrawler
        
        # Get source from database
        source = db.query(NewsSource).filter_by(id=source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Crawl the source
        logger.info(f"Testing crawl for {source.name}...")
        crawler = NewsCrawler(db_session=db)
        articles = crawler.crawl_source(source)
        
        # Format articles for response
        sample_articles = []
        for article in articles[:5]:
            sample_articles.append({
                "title": article.get("title"),
                "url": article.get("url"),
                "source": article.get("source"),
                "sentiment": article.get("sentiment"),
                "confidence": article.get("confidence")
            })
        
        return {
            "message": f"Crawl test completed for {source.name}",
            "source_id": source_id,
            "source_name": source.name,
            "crawl_type": source.crawl_type,
            "config": source.config,
            "articles_found": len(articles),
            "sample_articles": sample_articles,
            "status": "success" if articles else "no_articles"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing crawl for source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= SOURCE HEALTH API =============

@router.get("/sources/health/all", response_model=dict)
def get_all_sources_health(db: Session = Depends(get_db)):
    """Get health status of all sources"""
    try:
        health = get_source_health(db)
        return health
    except Exception as e:
        logger.error(f"Error getting sources health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources/{source_id}/health", response_model=dict)
def get_source_health_detail(source_id: int, db: Session = Depends(get_db)):
    """Get health status of a specific source"""
    try:
        health = get_source_health(db, source_id)
        if not health:
            raise HTTPException(status_code=404, detail="Source not found")
        return health
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting source {source_id} health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources/inactive/list", response_model=list)
def list_inactive_sources(db: Session = Depends(get_db)):
    """Get all inactive sources with reason for inactivity"""
    try:
        inactive = get_inactive_sources(db)
        return inactive
    except Exception as e:
        logger.error(f"Error getting inactive sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sources/{source_id}/reactivate", response_model=dict)
def reactivate_source_endpoint(source_id: int, db: Session = Depends(get_db)):
    """Manually reactivate an inactive source (reset failure counter)"""
    try:
        success = reactivate_source(db, source_id)
        if not success:
            raise HTTPException(status_code=404, detail="Source not found")
        
        source = get_source_by_id(db, source_id)
        return {
            "message": f"Source {source['name']} reactivated successfully",
            "source_id": source_id,
            "active": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reactivating source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= CRAWLER API =============
# Note: Manual crawl endpoint moved to crawler_routes.py (/v1/crawler/manual-crawl)
# This provides unified hybrid crawling system with auto and manual modes

@router.post("/crawler/crawl-url")
def crawl_custom_url(url: str = Query(...), db: Session = Depends(get_db)):
    """Crawl a custom URL (user-provided) using dynamic crawler"""
    try:
        from ..crawler.dynamic_crawler import DynamicCrawler
        crawler = DynamicCrawler()
        articles = crawler.crawl_url(url)
        return {
            "message": f"Crawled {url} successfully. Found {len(articles)} articles.",
            "articles_count": len(articles),
            "articles": articles
        }
    except Exception as e:
        logger.error(f"Error crawling URL {url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= FAVORITES API =============

@router.post("/favorites/{article_id}")
def add_to_favorites(article_id: int, db: Session = Depends(get_db)):
    """
    Add article to favorites (IDEMPOTENT)
    """
    try:
        article = db.query(Article).filter_by(id=article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Jika sudah favorite → tetap sukses
        if is_favorite(db, article_id):
            return {
                "success": True,
                "is_favorite": True,
                "article_id": article_id
            }

        add_favorite(db, article_id)

        return {
            "success": True,
            "is_favorite": True,
            "article_id": article_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding favorite: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/favorites/{article_id}")
def remove_from_favorite(article_id: int, db: Session = Depends(get_db)):
    """
    Remove article from favorites (IDEMPOTENT)
    """
    try:
        # Tidak masalah jika data tidak ada
        remove_favorite_by_article_id(db, article_id)

        return {
            "success": True,
            "is_favorite": False,
            "article_id": article_id
        }

    except Exception as e:
        logger.error(f"Error removing favorite: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/favorites", response_model=List[dict])
def list_favorites(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all favorite articles (SAFE)
    """
    try:
        return get_favorite_articles_detailed(db, limit=limit)
    except Exception as e:
        logger.error(f"Error getting favorites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/favorites/{article_id}/check")
def check_is_favorite(article_id: int, db: Session = Depends(get_db)):
    """
    Check if article is favorite
    """
    try:
        favorite = get_favorite_by_article_id(db, article_id)
        return {
            "success": True,
            "is_favorite": favorite is not None,
            "article_id": article_id,
            "favorite_id": favorite["id"] if favorite else None
        }
    except Exception as e:
        logger.error(f"Error checking favorite: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ============= SEARCH HISTORY API =============

@router.post("/search-history")
def save_search(keyword: str = Query(..., min_length=1, max_length=500), db: Session = Depends(get_db)):
    """Save search keyword to history"""
    try:
        history = add_search_history(db, keyword.strip())
        return {
            "id": history.id,
            "keyword": history.keyword,
            "search_count": history.search_count,
            "message": "Search saved to history"
        }
    except Exception as e:
        logger.error(f"Error saving search history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-history", response_model=List[dict])
def get_search_history_list(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    """Get search history"""
    try:
        history = get_search_history(db, limit=limit)
        return history
    except Exception as e:
        logger.error(f"Error getting search history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-history/{history_id}", response_model=dict)
def get_search_history_by_id(history_id: int, db: Session = Depends(get_db)):
    """
    Get search history details by ID with related articles
    
    Parameters:
    - history_id: ID of the search history entry
    
    Returns:
    - Search history entry with id, keyword, search_count, timestamps, and related articles
    """
    try:
        history = db.query(SearchHistory).filter_by(id=history_id).first()
        if not history:
            raise HTTPException(status_code=404, detail="Search history entry not found")
        
        # Search for articles related to the keyword
        keyword_filter = f"%{history.keyword}%"
        related_articles = db.query(Article)\
            .filter((Article.title.ilike(keyword_filter)) | (Article.content.ilike(keyword_filter)))\
            .order_by(Article.crawled_date.desc())\
            .limit(10)\
            .all()
        
        return {
            'id': history.id,
            'keyword': history.keyword,
            'search_count': history.search_count,
            'created_at': history.created_at.isoformat(),
            'updated_at': history.updated_at.isoformat(),
            'related_articles': [{
                'id': a.id,
                'title': a.title,
                'url': a.url,
                'source': a.source,
                'sentiment': a.sentiment,
                'confidence': a.confidence,
                'keywords': a.keywords_flagged,
                'crawled_date': a.crawled_date.isoformat() if a.crawled_date else None
            } for a in related_articles]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting search history by id {history_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/search-history/{history_id}")
def delete_search_history_item(history_id: int, db: Session = Depends(get_db)):
    """Delete a search history entry"""
    try:
        success = delete_search_history(db, history_id)
        if not success:
            raise HTTPException(status_code=404, detail="Search history entry not found")
        return {"message": "Search history deleted", "history_id": history_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting search history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/search-history")
def clear_search_history_all(db: Session = Depends(get_db)):
    """Clear all search history"""
    try:
        success = clear_all_search_history(db)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear search history")
        return {"message": "All search history cleared"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing search history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= DASHBOARD API =============

@router.get("/dashboard/stats")
def get_dashboard_stats_api():
    """Get dashboard statistics"""
    try:
        stats = get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/articles/recent")
def get_recent_articles_dashboard(limit: int = Query(10, ge=1, le=50)):
    """Get recent articles for dashboard"""
    try:
        articles = get_recent_articles(limit)
        return articles
    except Exception as e:
        logger.error(f"Error getting recent articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crawler/last-crawl-status")
def get_last_crawl_status_api(db: Session = Depends(get_db)):
    """Get the status of the last crawl operation"""
    try:
        status = get_last_crawl_status(db)
        return status
    except Exception as e:
        logger.error(f"Error getting last crawl status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crawler/sources-summary")
def get_sources_summary_api(db: Session = Depends(get_db)):
    """Get summary of total and active news sources"""
    try:
        summary = get_sources_summary(db)
        return summary
    except Exception as e:
        logger.error(f"Error getting sources summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= CLEANUP SCHEDULE API =============


class CleanupScheduleCreate(BaseModel):
    name: Optional[str] = None
    days_threshold: int = 30
    interval_minutes: int = 1440


@router.post("/cleanup/schedules", response_model=dict)
def create_cleanup_schedule_endpoint(payload: CleanupScheduleCreate, db: Session = Depends(get_db)):
    """Create a cleanup schedule that will delete articles older than `days_threshold` every `interval_minutes`."""
    try:
        sched = create_cleanup_schedule(db, payload.name, payload.days_threshold, payload.interval_minutes)
        return {
            "id": sched.id,
            "name": sched.name,
            "days_threshold": sched.days_threshold,
            "interval_minutes": sched.interval_minutes,
            "active": sched.active,
            "created_at": sched.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating cleanup schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cleanup/schedules", response_model=List[dict])
def list_cleanup_schedules(db: Session = Depends(get_db)):
    """List all cleanup schedules"""
    try:
        schedules = get_cleanup_schedules(db)
        return [{
            "id": s.id,
            "name": s.name,
            "days_threshold": s.days_threshold,
            "interval_minutes": s.interval_minutes,
            "last_run": s.last_run.isoformat() if s.last_run else None,
            "active": s.active,
            "created_at": s.created_at.isoformat()
        } for s in schedules]
    except Exception as e:
        logger.error(f"Error listing cleanup schedules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cleanup/schedules/{schedule_id}")
def delete_cleanup_schedule_endpoint(schedule_id: int, db: Session = Depends(get_db)):
    """Delete a cleanup schedule by id"""
    try:
        success = delete_cleanup_schedule(db, schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return {"message": "Schedule deleted", "schedule_id": schedule_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting cleanup schedule {schedule_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup/schedules/{schedule_id}/run", response_model=dict)
def run_cleanup_schedule_now(schedule_id: int, db: Session = Depends(get_db)):
    """Trigger a specific cleanup schedule immediately"""
    try:
        result = run_cleanup_for_schedule(db, schedule_id)
        return {"message": "Cleanup executed", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error running cleanup schedule {schedule_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup/run-now", response_model=dict)
def run_cleanup_immediate(days: int = Query(30, ge=1), db: Session = Depends(get_db)):
    """Immediately run cleanup deleting articles older than `days` days."""
    try:
        cleanup_old_articles(days=days)
        return {"message": f"Cleanup executed: deleted articles older than {days} days"}
    except Exception as e:
        logger.error(f"Error running immediate cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= HEALTH CHECK =============
# Note: Health check endpoint moved to app.py (/health)
# Only one health check endpoint is used across the application

#         return {"is_favorite": is_fav}
#     except Exception as e:
#         logger.error(f"Error checking favorite: {e}")
#         raise HTTPException(status_code=500, detail=str(e))




