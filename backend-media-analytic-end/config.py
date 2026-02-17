# News sources
from pathlib import Path

class Config:
    # Base directory
    BASE_DIR = Path(__file__).parent

    # Model paths
    MODEL_PATH: str = "./src/ml/model/model.safetensors"

    # API settings
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    DEBUG = False
    
    # ML settings
    BATCH_SIZE = 32
    MAX_LENGTH = 512
    USE_GPU = True

    ENV: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./database/media_analytics.db"
    
    # Crawler settings
    CRAWL_INTERVAL = 86400  # 1 Day
    MAX_ARTICLES_PER_SOURCE = 10
    LOG_LEVEL: str = "INFO"
    
    # News Sources
    NEWS_SOURCES = [
        {
            "name": "Kompas",
            "url": "https://indeks.kompas.com/rss",
            "parser": "rss",
            "base_url": "https://www.kompas.com"
        },
        {
            "name": "Detik",
            "url": "https://rss.detik.com/index.php/detikcom",
            "parser": "rss",
            "base_url": "https://news.detik.com"
        },
        {
            "name": "Suara",
            "url": "https://www.suara.com/lampung",
            "parser": "html",
            "base_url": "https://www.suara.com"
        }
    ]
    
    # Sosmed
    TWITTER_SOURCES = [
        "kompas",
        "detik",
        "suara",
        "lampungpro",
        "tribunlampung",
        "radarlampung"
    ]

    # Cache
    CACHE_TYPE = 'redis'
    REDIS_URL = 'redis://localhost:6379/0'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    USE_GPU = True


config = Config()