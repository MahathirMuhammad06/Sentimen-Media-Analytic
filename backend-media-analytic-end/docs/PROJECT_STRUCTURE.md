# Project Structure Documentation

## Overview

This document explains the folder structure and purpose of each component in the Media Analytics Backend.

```
medal-backend/
├── config.py                          # Configuration settings
├── requirements.txt                   # Python dependencies
├── README.md                          # Project overview
│
├── database/                          # Database files
│   └── media_analytics.db            # SQLite database (auto-created)
│
├── docs/                              # Documentation (THIS FOLDER)
│   ├── API_DOCUMENTATION.md           # REST API reference
│   ├── DATABASE_SCHEMA.md             # Database table definitions
│   ├── CRAWLING_STRATEGY.md           # Crawling implementation details
│   └── PROJECT_STRUCTURE.md           # This file
│
├── src/                               # Source code
│   ├── __init__.py                   # Package marker
│   │
│   ├── api/                           # REST API layer
│   │   ├── __init__.py
│   │   ├── app.py                     # FastAPI application setup
│   │   ├── routes.py                  # API endpoint definitions
│   │   ├── middleware.py              # Request/response middleware
│   │   ├── crawler_routes.py          # Crawler-specific routes
│   │   └── routes/                    # Additional route modules
│   │
│   ├── crawler/                       # News crawling modules
│   │   ├── __init__.py
│   │   ├── news_crawler.py            # Hardcoded crawler for known sources
│   │   ├── dynamic_crawler.py         # Dynamic crawler for user URLs
│   │   ├── scheduler.py               # Crawl scheduling (optional)
│   │   └── engines/                   # Specialized crawlers (future)
│   │
│   ├── database/                      # Data persistence layer
│   │   ├── __init__.py
│   │   ├── db.py                      # Database connection utilities
│   │   ├── models.py                  # SQLAlchemy ORM models
│   │   ├── repository.py              # Data access functions
│   │   ├── schemas.py                 # Pydantic validation schemas
│   │   └── migrations/                # Database migrations (future)
│   │
│   ├── ml/                            # Machine learning components
│   │   ├── __init__.py
│   │   ├── sentiment_analyzer.py      # Sentiment analysis model
│   │   ├── text_preprocessor.py       # Text preprocessing utilities
│   │   │
│   │   ├── model/                     # Primary ML model
│   │   │   ├── config.json
│   │   │   ├── model_info.json
│   │   │   ├── model.safetensors
│   │   │   ├── special_tokens_map.json
│   │   │   ├── tokenizer_config.json
│   │   │   ├── tokenizer.json
│   │   │   └── vocab.txt
│   │   │
│   │   └── modelV1/                   # Alternative/legacy model
│   │       ├── config.json
│   │       ├── model_info.json
│   │       ├── model.safetensors
│   │       ├── special_tokens_map.json
│   │       ├── tokenizer_config.json
│   │       ├── tokenizer.json
│   │       └── vocab.txt
│   │
│   ├── services/                      # Business logic layer
│   │   ├── __init__.py
│   │   └── article_service.py         # Article-related operations
│   │
│   ├── tasks/                         # Background jobs (Celery)
│   │   ├── __init__.py
│   │   └── celery_app.py              # Celery configuration
│   │
│   ├── utils/                         # Utility functions
│   │   ├── __init__.py
│   │   ├── helpers.py                 # Helper functions
│   │   ├── logger.py                  # Logging configuration
│   │   └── __pycache__/
│   │
│   └── core/                          # Core functionality
│       └── __pycache__/
│
└── tests/                             # Unit & integration tests
    ├── conftest.py                    # Pytest configuration
    ├── test_api.py                    # API endpoint tests
    ├── test_crawler.py                # Crawler tests
    ├── test_db_storage.py             # Database tests
    ├── test_sentiment.py              # ML model tests
    ├── fixtures/                      # Test data
    └── __pycache__/
```

---

## Component Details

### 1. Root Level Files

#### `config.py`
- **Purpose**: Centralized configuration
- **Contains**:
  - API settings (host, port, debug mode)
  - Database URL
  - ML model paths
  - Crawler settings (interval, max articles)
  - News source definitions
  - Cache settings
- **Usage**: `from config import config`

#### `requirements.txt`
- **Purpose**: Python package dependencies
- **Key packages**:
  - `fastapi`: Web framework
  - `sqlalchemy`: ORM
  - `beautifulsoup4`: HTML parsing
  - `transformers`: ML models
  - `feedparser`: RSS parsing
  - `requests`: HTTP client
  - `pydantic`: Data validation

#### `README.md`
- **Purpose**: Project overview and setup instructions

---

### 2. API Module (`src/api/`)

#### `app.py`
- **Purpose**: FastAPI application factory
- **Responsibilities**:
  - Initialize FastAPI app
  - Configure CORS middleware
  - Register API routes
  - Handle startup/shutdown events
  - Setup logging middleware

**Key Functions**:
```python
app = FastAPI(...)           # Create app
app.add_middleware(...)      # Add CORS
app.include_router(router)   # Register routes
@app.on_event("startup")     # Initialization
```

#### `routes.py`
- **Purpose**: API endpoint definitions
- **Endpoints** (organized by resource):

**Articles:**
- `GET /articles` - List articles with filters
- `GET /article/{id}` - Get single article

**News Sources:**
- `GET /sources` - List sources
- `POST /sources` - Create source
- `GET /sources/{id}` - Get source
- `PUT /sources/{id}` - Update source
- `DELETE /sources/{id}` - Delete source

**Crawler:**
- `POST /crawler/run` - Run hardcoded crawler
- `POST /crawler/crawl-url` - Crawl user URL

**Favorites:**
- `POST /favorites/{id}` - Add to favorites
- `DELETE /favorites/{id}` - Remove from favorites
- `GET /favorites` - List favorites
- `GET /favorites/{id}/check` - Check if favorite

**Search History:**
- `POST /search-history` - Save search
- `GET /search-history` - Get history
- `DELETE /search-history/{id}` - Delete entry
- `DELETE /search-history` - Clear all

**Dashboard:**
- `GET /dashboard/stats` - Get statistics
- `GET /dashboard/articles/recent` - Recent articles

**Health:**
- `GET /health` - Health check

#### `middleware.py`
- **Purpose**: Request/response processing
- **Features**:
  - Request logging
  - Error handling
  - Header management

#### `crawler_routes.py`
- **Purpose**: Crawler-specific endpoints (optional)
- **May contain**: Crawler scheduling, advanced options

---

### 3. Crawler Module (`src/crawler/`)

#### `news_crawler.py`
- **Purpose**: Hardcoded crawlers for known sources
- **Sources**: Kompas, Detik, Radar Lampung, Suara, Tribun Lampung, Lampung Pro
- **Key Class**: `NewsCrawler`

**Main Methods**:
```python
crawl_all()                 # Crawl all active sources
crawl_generic(source)       # Generic crawler for DB sources
crawl_kompas()              # Kompas-specific logic
crawl_detik()               # Detik-specific logic
_crawl_rss_generic()        # Generic RSS parsing
_crawl_html_generic()       # Generic HTML crawling
get_article_content()       # Fetch article content
```

#### `dynamic_crawler.py` ⭐ (NEW)
- **Purpose**: User-submitted URL crawling
- **Features**:
  - Automatic detection (RSS → Sitemap → HTML)
  - Heuristic-based article discovery
  - DOM density analysis
  - Smart content extraction

**Key Methods**:
```python
crawl_url(url)              # Main entry point
detect_crawl_type(url)      # Auto-detect method
_detect_rss_feeds(url)      # Check for RSS
_detect_sitemap(url)        # Check for sitemap
crawl_html_dynamic(url)     # Heuristic crawling
_find_article_links()       # Discover articles
_fetch_article_content()    # Extract content
```

#### `scheduler.py`
- **Purpose**: Background crawl scheduling (optional)
- **Framework**: APScheduler (optional implementation)

---

### 4. Database Module (`src/database/`)

#### `models.py`
- **Purpose**: SQLAlchemy ORM models
- **Tables**:
  - `Article` - News articles
  - `NewsSource` - Crawl sources
  - `Favorite` - User favorites
  - `SearchHistory` - Search tracking (NEW)

**Key Features**:
- Relationships between tables
- Default values
- Constraints

#### `schemas.py`
- **Purpose**: Pydantic validation schemas
- **Schemas**:
  - `ArticleCreate`, `Article`
  - `NewsSourceCreate`, `NewsSourceUpdate`, `NewsSource`
  - `FavoriteCreate`, `Favorite`
  - `SearchHistoryCreate`, `SearchHistory`

**Features**:
- Request validation
- Response serialization
- Config for ORM conversion

#### `repository.py`
- **Purpose**: Data access layer
- **Functions** (organized by resource):

**Articles:**
- `save_articles_bulk()` - Batch insert
- `upsert_article()` - Insert or update
- `extract_keywords_flagged()` - Keyword extraction
- `cleanup_old_articles()` - Data retention

**News Sources:**
- `get_sources()` - List all sources
- `add_source()` - Create source
- `update_source()` - Update source
- `delete_source()` - Soft delete source
- `get_active_sources()` - Active only
- `get_source_by_id()` - Get specific

**Favorites:**
- `add_favorite()` - Add favorite
- `remove_favorite()` - Remove favorite
- `get_favorites()` - List favorites
- `is_favorite()` - Check status
- `get_favorite_articles_detailed()` - Full details

**Search History:** (NEW)
- `add_search_history()` - Track search
- `get_search_history()` - List searches
- `delete_search_history()` - Delete entry
- `clear_all_search_history()` - Clear all

**Dashboard:**
- `get_dashboard_stats()` - Statistics
- `get_recent_articles()` - Recent items

#### `db.py`
- **Purpose**: Database connection utilities
- **Provides**:
  - Connection string handling
  - Session management
  - Connection pooling

---

### 5. ML Module (`src/ml/`)

#### `sentiment_analyzer.py`
- **Purpose**: Sentiment analysis using DistilBERT
- **Key Class**: `SentimentAnalyzer`
- **Output**: Sentiment + confidence scores

**Methods**:
```python
predict(text)      # Analyze text
preprocess(text)   # Clean text
```

#### `text_preprocessor.py`
- **Purpose**: Text preparation utilities
- **Functions**:
  - Lowercasing
  - HTML removal
  - Tokenization
  - Special character handling

#### `model/` & `modelV1/`
- **Contents**: Pre-trained model files
  - `model.safetensors` - Model weights
  - `config.json` - Model config
  - `tokenizer.json` - Vocabulary
  - `vocab.txt` - Token mappings

---

### 6. Services Module (`src/services/`)

#### `article_service.py`
- **Purpose**: Business logic for articles
- **May contain**:
  - Complex queries
  - Data transformations
  - Domain logic

---

### 7. Tasks Module (`src/tasks/`)

#### `celery_app.py`
- **Purpose**: Background job queue (optional)
- **Use Cases**:
  - Async crawling
  - Scheduled tasks
  - Notification delivery

---

### 8. Utils Module (`src/utils/`)

#### `logger.py`
- **Purpose**: Centralized logging
- **Features**:
  - File & console output
  - Log levels
  - Formatted output

**Usage**:
```python
from ..utils.logger import get_logger
logger = get_logger(__name__)
logger.info("Message")
```

#### `helpers.py`
- **Purpose**: Utility functions
- **Current**: URL joining, basic helpers
- **Extensible**: Add common functions

---

### 9. Tests Module (`tests/`)

#### `conftest.py`
- **Purpose**: Pytest configuration
- **Contains**: Fixtures, setup/teardown

#### `test_api.py`
- **Purpose**: API endpoint tests
- **Tests**: All REST endpoints

#### `test_crawler.py`
- **Purpose**: Crawler functionality tests
- **Tests**: Hardcoded & dynamic crawlers

#### `test_sentiment.py`
- **Purpose**: ML model tests
- **Tests**: Sentiment analysis accuracy

#### `test_db_storage.py`
- **Purpose**: Database tests
- **Tests**: CRUD operations

#### `fixtures/`
- **Purpose**: Test data
- **Contains**: Sample articles, sources, etc.

---

## Data Flow Diagrams

### Crawling Flow

```
Crawler Request
    ↓
Choose Sources (hardcoded or user-defined)
    ↓
For each source:
    ├─ Fetch HTML/RSS
    ├─ Parse & extract links
    ├─ Fetch article content
    ├─ Sentiment analysis
    ├─ Keyword extraction
    └─ Store in database
    ↓
Return results
```

### API Request Flow

```
HTTP Request
    ↓
FastAPI Router
    ↓
Route Handler
    ↓
Repository Functions (DB access)
    ↓
SQLAlchemy ORM
    ↓
SQLite Database
    ↓
Response JSON
```

### ML Processing

```
Article Text
    ↓
Preprocessing (clean, lowercase)
    ↓
Tokenization
    ↓
DistilBERT Model
    ↓
Sentiment Probabilities
    ↓
Store in Database
```

---

## Configuration Files

### Environment-Specific Config

```python
# config.py structure
class Config:
    # Base settings
    DATABASE_URL = "sqlite:///..."
    LOG_LEVEL = "INFO"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    USE_GPU = True
```

---

## Adding New Features

### Adding a New API Endpoint

1. Create route in `src/api/routes.py`:
```python
@router.post("/new-endpoint")
def new_endpoint(param: Type, db: Session = Depends(get_db)):
    # Implementation
    pass
```

2. Add repository function in `src/database/repository.py`

3. Add schema if needed in `src/database/schemas.py`

4. Add test in `tests/test_api.py`

### Adding a New Data Model

1. Define model in `src/database/models.py`
2. Create schema in `src/database/schemas.py`
3. Add repository functions in `src/database/repository.py`
4. Run `init_db()` to create table

### Adding a New Crawler Source

1. Add hardcoded method to `news_crawler.py`:
```python
def crawl_new_source(self):
    # Implementation
    pass
```

2. Add to `crawl_all()` method

3. Or add via API to dynamic sources:
```
POST /sources
{
  "name": "New Source",
  "base_url": "https://...",
  "crawl_type": "auto"
}
```

---

## Dependencies Between Modules

```
api/routes.py
    ├─ imports database/repository
    ├─ imports database/schemas
    ├─ imports crawler/news_crawler
    ├─ imports crawler/dynamic_crawler
    └─ imports utils/logger

crawler/news_crawler.py
    ├─ imports database/repository
    ├─ imports ml/sentiment_analyzer
    └─ imports utils/logger

database/repository.py
    ├─ imports database/models
    ├─ imports database/db
    └─ imports utils/logger

ml/sentiment_analyzer.py
    └─ imports ml/text_preprocessor
```

---

## Key Architectural Patterns

### 1. Layered Architecture
```
API Layer (routes.py)
    ↓
Service Layer (services/)
    ↓
Repository Layer (repository.py)
    ↓
ORM Layer (SQLAlchemy)
    ↓
Database (SQLite)
```

### 2. Dependency Injection
```python
# FastAPI automatic dependency injection
def endpoint(db: Session = Depends(get_db)):
    # db is automatically provided
    pass
```

### 3. Factory Pattern
```python
# SentimentAnalyzer initialization
analyzer = SentimentAnalyzer(model_path="...")
```

### 4. Repository Pattern
```python
# Data access abstraction
result = get_articles(limit=10)
add_favorite(db, article_id)
```

---

## Performance Considerations

### Database Indexes
Recommended in `database/models.py`:
- `articles.url` (unique, prevents duplicates)
- `articles.source` (filtering)
- `articles.crawled_date` (sorting)
- `news_sources.active` (filtering)
- `favorites.article_id` (lookup)

### Caching Opportunities
- Cache recent articles (1 minute)
- Cache dashboard stats (5 minutes)
- Cache source list (30 minutes)

### Query Optimization
- Use pagination for large result sets
- Filter at DB level (not in app)
- Use indexes for WHERE/ORDER BY clauses

---

## Security Considerations

### Current Gaps
- ⚠️ No authentication
- ⚠️ No authorization
- ⚠️ No rate limiting
- ⚠️ CORS allows all origins

### Recommended Implementations
1. **Authentication**: JWT tokens
2. **Authorization**: Role-based access
3. **Rate Limiting**: Per-IP or per-user
4. **CORS**: Restrict to specific origins
5. **Input Validation**: Pydantic schemas (done)
6. **SQL Injection**: SQLAlchemy parameterized queries (done)

---

## Deployment Structure

### Development
```
medal-backend/
├── .env (development settings)
├── database/media_analytics.db (local)
└── logs/ (application logs)
```

### Production
```
/app/medal-backend/
├── .env (production settings, encrypted)
├── /data/media_analytics.db (persistent volume)
├── /logs/ (persistent volume)
└── requirements.txt (frozen versions)
```

---

## Summary

The architecture separates concerns into:
- **API Layer**: REST endpoints and validation
- **Service Layer**: Business logic
- **Data Layer**: Database operations
- **ML Layer**: Model inference
- **Crawler Layer**: Data collection
- **Utils Layer**: Shared utilities

This design allows easy testing, maintenance, and extension of features.
