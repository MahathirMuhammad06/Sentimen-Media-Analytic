"""
Optional configuration for hybrid crawling
Can be used to customize hybrid crawler behavior
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HybridCrawlerConfig:
    """Configuration for hybrid crawler manager"""
    
    # Default interval untuk auto crawling (seconds)
    default_interval: int = 86400  # 1 day
    
    # Minimum interval allowed (seconds)
    min_interval: int = 3600  # 1 hour
    
    # Maximum interval allowed (seconds)
    max_interval: int = 604800  # 1 week
    
    # Enable auto crawling on startup
    auto_start: bool = False
    
    # Max articles per source per crawl
    max_articles_per_source: int = 100
    
    # Enable logging untuk hybrid crawler
    enable_logging: bool = True
    
    # Timeout untuk individual crawl (seconds)
    crawl_timeout: Optional[int] = None
    
    # Retry policy untuk failed crawls
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    
    # Thread pool size untuk concurrent crawling (future feature)
    max_workers: int = 5
    
    # Enable metrics collection
    collect_metrics: bool = True
    
    # Webhook URL untuk crawl completion (optional)
    webhook_url: Optional[str] = None


# Default configuration
DEFAULT_HYBRID_CONFIG = HybridCrawlerConfig()


# Development configuration
DEV_HYBRID_CONFIG = HybridCrawlerConfig(
    default_interval=300,  # 5 minutes
    auto_start=False,
    enable_logging=True,
    collect_metrics=True
)


# Production configuration
PROD_HYBRID_CONFIG = HybridCrawlerConfig(
    default_interval=3600,  # 1 hour
    auto_start=True,
    enable_logging=True,
    collect_metrics=True,
    max_retries=5,
    retry_delay=120
)
