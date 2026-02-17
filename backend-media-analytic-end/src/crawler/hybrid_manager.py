"""
Hybrid Crawler Manager
Manages both manual (button-triggered) and automatic crawling
Provides centralized control for crawling operations
"""

import threading
from typing import Optional, Dict, Any
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import config
from ..utils.logger import get_logger
from .news_crawler import NewsCrawler
from ..database.repository import get_session

logger = get_logger(__name__)


class HybridCrawlerManager:
    """
    Manages both automatic and manual crawling operations.
    
    Features:
    - Manual crawling triggered via API endpoint
    - Automatic crawling based on configurable interval
    - Start/Stop auto crawling
    - Get crawler status
    - Thread-safe operations
    """

    def __init__(self):
        self.scheduler: Optional[BackgroundScheduler] = None
        self.crawler: Optional[NewsCrawler] = None
        self.is_auto_running: bool = False
        self.last_crawl_time: Optional[datetime] = None
        self.crawl_count: int = 0
        self.lock = threading.Lock()
        self.crawl_interval: int = config.CRAWL_INTERVAL
        
        logger.info("HybridCrawlerManager initialized")

    def initialize_crawler(self) -> None:
        """Initialize the news crawler instance"""
        try:
            session = get_session()
            self.crawler = NewsCrawler(db_session=session)
            logger.info("Crawler instance initialized")
        except Exception as e:
            logger.error(f"Failed to initialize crawler: {e}")
            raise

    def start_auto_crawling(self) -> Dict[str, Any]:
        """
        Start automatic crawling with configured interval
        
        Returns:
            Dictionary with status and details
        """
        with self.lock:
            if self.is_auto_running:
                return {
                    "status": "already_running",
                    "message": "Auto crawling is already running",
                    "interval_seconds": self.crawl_interval
                }

            try:
                if self.crawler is None:
                    self.initialize_crawler()

                if self.scheduler is None:
                    self.scheduler = BackgroundScheduler()

                # Add job if not already added
                existing_jobs = self.scheduler.get_jobs()
                if not any(job.name == 'auto_crawl' for job in existing_jobs):
                    self.scheduler.add_job(
                        self._auto_crawl_job,
                        'interval',
                        seconds=self.crawl_interval,
                        id='auto_crawl',
                        name='auto_crawl',
                        replace_existing=True
                    )

                if not self.scheduler.running:
                    self.scheduler.start()

                self.is_auto_running = True
                logger.info(f"Auto crawling started with interval {self.crawl_interval}s")

                return {
                    "status": "started",
                    "message": "Auto crawling started successfully",
                    "interval_seconds": self.crawl_interval,
                    "timestamp": datetime.utcnow().isoformat()
                }

            except Exception as e:
                logger.error(f"Error starting auto crawling: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to start auto crawling: {str(e)}"
                }

    def stop_auto_crawling(self) -> Dict[str, Any]:
        """
        Stop automatic crawling
        
        Returns:
            Dictionary with status and details
        """
        with self.lock:
            if not self.is_auto_running:
                return {
                    "status": "not_running",
                    "message": "Auto crawling is not running"
                }

            try:
                if self.scheduler and self.scheduler.running:
                    self.scheduler.shutdown(wait=False)
                    self.is_auto_running = False
                    logger.info("Auto crawling stopped")

                return {
                    "status": "stopped",
                    "message": "Auto crawling stopped successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }

            except Exception as e:
                logger.error(f"Error stopping auto crawling: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to stop auto crawling: {str(e)}"
                }

    def run_manual_crawl(self) -> Dict[str, Any]:
        """
        Manually trigger crawling (button action)
        
        Returns:
            Dictionary with crawl results and details
        """
        with self.lock:
            try:
                if self.crawler is None:
                    self.initialize_crawler()

                logger.info("Manual crawl triggered")
                articles = self._perform_crawl()

                self.last_crawl_time = datetime.utcnow()
                self.crawl_count += 1

                return {
                    "status": "success",
                    "message": f"Manual crawl completed. Found {len(articles)} articles.",
                    "articles_count": len(articles),
                    "crawl_number": self.crawl_count,
                    "timestamp": self.last_crawl_time.isoformat()
                }

            except Exception as e:
                logger.error(f"Error in manual crawl: {e}")
                return {
                    "status": "error",
                    "message": f"Manual crawl failed: {str(e)}"
                }

    def _auto_crawl_job(self) -> None:
        """
        Background job for automatic crawling
        Called by scheduler at configured intervals
        """
        try:
            logger.info("Auto crawl job started")
            articles = self._perform_crawl()
            self.last_crawl_time = datetime.utcnow()
            self.crawl_count += 1
            logger.info(f"Auto crawl completed. Found {len(articles)} articles")

        except Exception as e:
            logger.error(f"Error in auto crawl job: {e}")

    def _perform_crawl(self) -> list:
        """
        Perform the actual crawling operation
        
        Returns:
            List of articles found
        """
        try:
            if self.crawler is None:
                self.initialize_crawler()

            # Perform crawl
            articles = self.crawler.crawl_all()
            logger.info(f"Crawl operation completed: {len(articles)} articles found")
            return articles

        except Exception as e:
            logger.error(f"Error performing crawl: {e}")
            raise

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the hybrid crawler
        
        Returns:
            Dictionary containing crawler status information
        """
        with self.lock:
            return {
                "auto_running": self.is_auto_running,
                "interval_seconds": self.crawl_interval,
                "last_crawl_time": self.last_crawl_time.isoformat() if self.last_crawl_time else None,
                "total_crawls": self.crawl_count,
                "scheduler_running": self.scheduler.running if self.scheduler else False,
                "timestamp": datetime.utcnow().isoformat()
            }

    def update_interval(self, interval_seconds: int) -> Dict[str, Any]:
        """
        Update the crawling interval for auto crawling
        
        Args:
            interval_seconds: New interval in seconds
            
        Returns:
            Dictionary with update status
        """
        with self.lock:
            try:
                if interval_seconds < 60:
                    return {
                        "status": "error",
                        "message": "Interval must be at least 60 seconds"
                    }

                self.crawl_interval = interval_seconds

                # If scheduler is running, update the job
                if self.scheduler and self.is_auto_running:
                    self.scheduler.reschedule_job(
                        'auto_crawl',
                        trigger=IntervalTrigger(seconds=interval_seconds)
                    )

                logger.info(f"Crawl interval updated to {interval_seconds}s")

                return {
                    "status": "success",
                    "message": f"Interval updated to {interval_seconds} seconds",
                    "new_interval": interval_seconds,
                    "timestamp": datetime.utcnow().isoformat()
                }

            except Exception as e:
                logger.error(f"Error updating interval: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to update interval: {str(e)}"
                }

    def shutdown(self) -> None:
        """Gracefully shutdown the crawler and scheduler"""
        with self.lock:
            try:
                if self.scheduler and self.scheduler.running:
                    self.scheduler.shutdown(wait=True)
                self.is_auto_running = False
                logger.info("HybridCrawlerManager shut down gracefully")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")


# Global instance
_manager: Optional[HybridCrawlerManager] = None


def get_crawler_manager() -> HybridCrawlerManager:
    """Get or create the global crawler manager instance"""
    global _manager
    if _manager is None:
        _manager = HybridCrawlerManager()
    return _manager
