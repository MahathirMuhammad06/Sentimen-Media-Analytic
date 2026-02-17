"""
Hybrid Crawler API Routes
Provides endpoints for manual and automatic crawling control
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ..database.repository import get_session, get_session as get_db_session
from ..crawler.news_crawler import NewsCrawler

from ..utils.logger import get_logger
from ..crawler.hybrid_manager import get_crawler_manager

logger = get_logger(__name__)
router = APIRouter(prefix="/v1/crawler", tags=["crawler"])

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

# Endpoint: Real-time manual crawling sesuai keyword pencarian
@router.post("/search-crawl")
async def search_crawl_endpoint(
    keyword: str = Body(..., embed=True, description="Keyword/topik pencarian berita"),
    db: Session = Depends(get_db)
):
    """
    Real-time crawling sesuai keyword/topik pencarian user (manual search)
    - Melakukan crawling ke semua sumber aktif
    - Memfilter hasil sesuai keyword
    - Hasil tidak langsung masuk ke tabel utama artikel, hanya dikembalikan ke frontend
    - (Opsional) Simpan ke tabel sementara/manual jika ingin history
    """
    try:
        # Inisialisasi NewsCrawler manual (bisa tanpa auto-crawler manager)
        crawler = NewsCrawler(db_session=db)
        all_articles = crawler.crawl_all()
        # Filter hasil sesuai keyword (judul/konten mengandung keyword, case-insensitive)
        filtered = [
            a for a in all_articles
            if keyword.lower() in (a["title"].lower() + " " + (a["content"] or "").lower())
        ]

        # (Opsional) Simpan ke tabel/manual_search jika ingin history pencarian
        # Contoh: simpan ke SearchHistory (sudah ada), atau buat tabel baru jika ingin
        # from ..database.repository import add_search_history
        # add_search_history(db, keyword)

        return {
            "status": "success",
            "message": f"Crawling manual sesuai keyword '{keyword}' selesai. Ditemukan {len(filtered)} artikel.",
            "keyword": keyword,
            "articles_count": len(filtered),
            "articles": filtered,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in search-crawl endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Search crawl failed: {str(e)}")


@router.post("/manual-crawl")
async def manual_crawl_endpoint(db: Session = Depends(get_db)):
    """
    Manually trigger crawling via button/API call
    
    Returns:
        - status: success/error
        - message: operation details
        - articles_count: number of articles found
        - crawl_number: sequential crawl number
        - timestamp: when crawl was performed
    
    Example:
        POST /v1/crawler/manual-crawl
        Response: {
            "status": "success",
            "message": "Manual crawl completed. Found 45 articles.",
            "articles_count": 45,
            "crawl_number": 5,
            "timestamp": "2024-01-19T10:30:00.000000"
        }
    """
    try:
        manager = get_crawler_manager()
        result = manager.run_manual_crawl()
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in manual crawl endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Manual crawl failed: {str(e)}")


@router.post("/auto-crawl/start")
async def start_auto_crawl_endpoint(db: Session = Depends(get_db)):
    """
    Start automatic crawling
    
    Automatically crawls at configured interval (default: every hour)
    Can be stopped with /auto-crawl/stop endpoint
    
    Returns:
        - status: started/already_running/error
        - message: operation details
        - interval_seconds: crawling interval
        - timestamp: when operation was performed
    
    Example:
        POST /v1/crawler/auto-crawl/start
        Response: {
            "status": "started",
            "message": "Auto crawling started successfully",
            "interval_seconds": 3600,
            "timestamp": "2024-01-19T10:30:00.000000"
        }
    """
    try:
        manager = get_crawler_manager()
        result = manager.start_auto_crawling()
        return result
        
    except Exception as e:
        logger.error(f"Error starting auto crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-crawl/stop")
async def stop_auto_crawl_endpoint(db: Session = Depends(get_db)):
    """
    Stop automatic crawling
    
    Stops the background scheduler
    Can be restarted with /auto-crawl/start endpoint
    
    Returns:
        - status: stopped/not_running/error
        - message: operation details
        - timestamp: when operation was performed
    
    Example:
        POST /v1/crawler/auto-crawl/stop
        Response: {
            "status": "stopped",
            "message": "Auto crawling stopped successfully",
            "timestamp": "2024-01-19T10:30:00.000000"
        }
    """
    try:
        manager = get_crawler_manager()
        result = manager.stop_auto_crawling()
        return result
        
    except Exception as e:
        logger.error(f"Error stopping auto crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto-crawl/status")
async def get_auto_crawl_status_endpoint(db: Session = Depends(get_db)):
    """
    Get current status of automatic crawling
    
    Returns:
        - auto_running: whether auto crawling is active
        - interval_seconds: current crawling interval
        - last_crawl_time: timestamp of last crawl
        - total_crawls: total number of crawls performed
        - scheduler_running: whether scheduler is running
        - timestamp: when status was queried
    
    Example:
        GET /v1/crawler/auto-crawl/status
        Response: {
            "auto_running": true,
            "interval_seconds": 3600,
            "last_crawl_time": "2024-01-19T09:30:00.000000",
            "total_crawls": 5,
            "scheduler_running": true,
            "timestamp": "2024-01-19T10:30:00.000000"
        }
    """
    try:
        manager = get_crawler_manager()
        status = manager.get_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting crawler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/auto-crawl/interval")
async def update_crawl_interval_endpoint(
    interval_seconds: int = Query(..., ge=60, le=86400),
    db: Session = Depends(get_db)
):
    """
    Update the automatic crawling interval
    
    Parameters:
        - interval_seconds: new interval in seconds (minimum: 60, maximum: 86400)
    
    Returns:
        - status: success/error
        - message: operation details
        - new_interval: the updated interval
        - timestamp: when operation was performed
    
    Example:
        PUT /v1/crawler/auto-crawl/interval?interval_seconds=7200
        Response: {
            "status": "success",
            "message": "Interval updated to 7200 seconds",
            "new_interval": 7200,
            "timestamp": "2024-01-19T10:30:00.000000"
        }
    """
    try:
        manager = get_crawler_manager()
        result = manager.update_interval(interval_seconds)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating crawl interval: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_crawler_info_endpoint(db: Session = Depends(get_db)):
    """
    Get crawler configuration information
    
    Returns:
        - configuration: current crawler settings
        - max_articles_per_source: maximum articles to crawl per source
        - available_endpoints: list of available crawler endpoints
    
    Example:
        GET /v1/crawler/info
        Response: {
            "configuration": {
                "default_interval": 3600,
                "max_articles_per_source": 100
            },
            "available_endpoints": [
                "POST /manual-crawl",
                "POST /auto-crawl/start",
                "POST /auto-crawl/stop",
                "GET /auto-crawl/status",
                "PUT /auto-crawl/interval"
            ]
        }
    """
    try:
        from config import config
        
        return {
            "configuration": {
                "default_interval": config.CRAWL_INTERVAL,
                "max_articles_per_source": config.MAX_ARTICLES_PER_SOURCE,
                "model_path": config.MODEL_PATH
            },
            "available_endpoints": [
                "POST /manual-crawl - Trigger manual crawl via button",
                "POST /auto-crawl/start - Start automatic crawling",
                "POST /auto-crawl/stop - Stop automatic crawling",
                "GET /auto-crawl/status - Get crawler status",
                "PUT /auto-crawl/interval - Update crawl interval"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting crawler info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
