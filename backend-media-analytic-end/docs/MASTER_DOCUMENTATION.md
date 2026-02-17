# Media Analytics Backend - Master Documentation
**Last Updated**: January 23, 2026
**Status**: Production Ready ✅

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [API Reference](#api-reference)
4. [Database Schema](#database-schema)
5. [Crawling System](#crawling-system)
6. [Link Status Tracking](#link-status-tracking)
7. [Recent Improvements](#recent-improvements)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation
```bash
cd medal-backend
pip install -r requirements.txt
python -c "from src.database.repository import init_db; init_db()"
python -m uvicorn src.api.app:app --reload
```

### First API Call
```bash
# Get all articles
curl http://localhost:8000/v1/articles

# Crawl a URL
curl -X POST "http://localhost:8000/v1/crawler/crawl-url?url=https://example.com"

# Get sources
curl http://localhost:8000/v1/sources
```

---

## System Overview

### Architecture
```
Frontend (Web App)
    ↓
FastAPI Backend (API Routes)
    ↓
Services (Crawler, ML Analysis)
    ↓
Database (SQLite/PostgreSQL)
    ↓
File Storage (Articles, Models)
```

### Components

| Component | Purpose | Status |
|-----------|---------|--------|
| **Hardcoded Crawlers** | Pre-configured crawlers for 6 news sources | ✅ Active |
| **Dynamic Crawler** | Auto-detect and crawl any URL | ✅ Active |
| **Sentiment Analysis** | ML-based sentiment classification | ✅ Active |
| **Link Status Tracking** | Monitor article link health | ✅ Active |
| **News Source Management** | CRUD operations for crawl sources | ✅ Active |
| **Favorites System** | User favorite articles | ✅ Active |
| **Search History** | Track user searches | ✅ Active |

### Hardcoded News Sources
1. **Kompas** - RSS + HTML hybrid crawling
2. **Detik** - RSS feed parsing
3. **Radar Lampung** - HTML crawling with link filters
4. **Suara** - RSS feed parsing
5. **Tribun Lampung** - HTML + RSS fallback
6. **Lampung Pro** - HTML crawling with advanced selectors

---

## API Reference

### Authentication
Currently no authentication. Configure in future versions.

### Base URL
- Development: `http://localhost:8000`
- Production: `https://api.example.com`

### API Version
`/v1/` - Version 1

---

### Articles Endpoints

#### GET /v1/articles
List all articles with pagination and filters.

**Query Parameters:**
- `limit`: Number of articles (default: 100)
- `offset`: Starting position (default: 0)
- `source`: Filter by source name (optional)
- `sentiment`: Filter by sentiment - 'positive', 'negative', 'neutral' (optional)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Article Title",
    "content": "Article content...",
    "source": "Kompas",
    "url": "https://example.com/article",
    "sentiment": "positive",
    "confidence": 0.95,
    "crawled_date": "2024-01-23T10:30:00",
    "keywords_flagged": ["keyword1", "keyword2"]
  }
]
```

#### GET /v1/article/{id}
Get single article by ID.

**Response:** Single article object (same format as above)

#### GET /v1/dashboard/stats
Get dashboard statistics.

**Response:**
```json
{
  "total_sources": 6,
  "active_sources": 6,
  "total_articles": 1250,
  "recent_articles": 45,
  "avg_sentiment": 0.35,
  "last_crawl_time": "2024-01-23T10:30:00"
}
```

---

### News Sources Endpoints

#### GET /v1/sources
List all active news sources.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Kompas",
    "base_url": "https://www.kompas.com",
    "crawl_type": "rss",
    "active": true,
    "auto_detect": true,
    "is_hardcoded": true,
    "config": {"rss_url": "https://indeks.kompas.com/rss"}
  }
]
```

#### POST /v1/sources
Create a new news source.

**Request Body:**
```json
{
  "name": "My News Site",
  "base_url": "https://example.com",
  "crawl_type": "auto",
  "config": {},
  "active": true,
  "auto_detect": true
}
```

**Query Parameters:**
- `crawl_type`: 'auto' (auto-detect), 'rss', 'html', 'sitemap'
- `auto_detect`: true to auto-detect crawl type

#### GET /v1/sources/{id}
Get specific source details.

#### PUT /v1/sources/{id}
Update a news source.

**Request Body:** Same as POST (partial fields)

#### DELETE /v1/sources/{id}
Delete a news source.

**Query Parameters:**
- `hard_delete=true`: Permanent delete from database (default: false)
- `hard_delete=false`: Soft delete (data preserved)

#### POST /v1/sources/{id}/test-auto-detect
Test auto-detection on a source and return sample articles.

**Response:**
```json
{
  "message": "Auto-detect test successful",
  "source_id": 1,
  "detected_type": "rss",
  "config": {"rss_url": "https://..."},
  "articles_found": 25,
  "sample_articles": [...]
}
```

---

### Crawler Endpoints

#### POST /v1/crawler/manual-crawl
Manually trigger crawling of all active sources.

**Response:**
```json
{
  "status": "success",
  "message": "Manual crawl completed. Found 145 articles.",
  "articles_count": 145,
  "crawl_number": 5,
  "timestamp": "2024-01-23T10:30:00"
}
```

#### POST /v1/crawler/crawl-url
Crawl a user-provided URL with auto-detection.

**Query Parameters:**
- `url` (required): URL to crawl

**Response:**
```json
{
  "message": "Crawled URL successfully. Found 12 articles.",
  "articles_count": 12,
  "articles": [...]
}
```

#### POST /v1/crawler/auto-crawl/start
Start automatic background crawling.

**Response:**
```json
{
  "status": "started",
  "message": "Auto crawling started successfully",
  "interval_seconds": 3600,
  "timestamp": "2024-01-23T10:30:00"
}
```

#### POST /v1/crawler/auto-crawl/stop
Stop automatic background crawling.

#### GET /v1/crawler/auto-crawl/status
Get auto-crawl status.

**Response:**
```json
{
  "status": "running",
  "is_running": true,
  "interval_seconds": 3600,
  "last_crawl": "2024-01-23T09:30:00",
  "total_crawls": 15
}
```

#### PUT /v1/crawler/auto-crawl/interval
Update crawling interval.

**Request Body:**
```json
{
  "interval_seconds": 1800
}
```

---

### Favorites Endpoints

#### POST /v1/favorites/{article_id}
Add article to favorites.

**Response:**
```json
{
  "message": "Article added to favorites",
  "favorite_id": 5,
  "article_id": 42
}
```

#### DELETE /v1/favorites/{article_id}
Remove article from favorites.

#### GET /v1/favorites
List all favorite articles.

**Response:**
```json
[
  {
    "favorite_id": 5,
    "article": { ... },
    "added_at": "2024-01-20T15:45:00"
  }
]
```

#### GET /v1/favorites/{article_id}/check
Check if article is favorited.

**Response:**
```json
{
  "is_favorite": true,
  "favorite_id": 5
}
```

---

### Search History Endpoints

#### POST /v1/search-history
Save search keyword.

**Request Body:**
```json
{
  "keyword": "lampung"
}
```

#### GET /v1/search-history
Get search history with frequency and related articles.

**Query Parameters:**
- `limit`: Number of records (default: 50)

#### DELETE /v1/search-history/{history_id}
Delete specific search history entry.

#### POST /v1/search-history/clear
Clear all search history.

---

## Database Schema

### Articles Table
```
id (INTEGER PRIMARY KEY)
title (VARCHAR)
content (TEXT)
source (VARCHAR)
url (VARCHAR UNIQUE)
published_date (DATETIME)
crawled_date (DATETIME)
keywords_flagged (VARCHAR)
sentiment (VARCHAR: 'positive', 'negative', 'neutral')
confidence (FLOAT: 0-1)
prob_positive (FLOAT)
prob_neutral (FLOAT)
prob_negative (FLOAT)
category (VARCHAR)
author (VARCHAR)
```

### News Sources Table
```
id (INTEGER PRIMARY KEY)
name (VARCHAR UNIQUE)
base_url (VARCHAR)
crawl_type (VARCHAR: 'rss', 'html', 'sitemap', 'auto')
config (JSON)
active (BOOLEAN)
auto_detect (BOOLEAN)
is_hardcoded (BOOLEAN)
deleted_at (DATETIME - NULL unless soft deleted)
created_at (DATETIME)
updated_at (DATETIME)
```

### Link Status Table
```
id (INTEGER PRIMARY KEY)
url (VARCHAR UNIQUE)
status (VARCHAR: 'active', 'inactive')
reason (VARCHAR)
source (VARCHAR)
failure_count (INTEGER)
last_checked (DATETIME)
created_at (DATETIME)
```

### Favorites Table
```
id (INTEGER PRIMARY KEY)
article_id (INTEGER FOREIGN KEY)
created_at (DATETIME)
```

### Search History Table
```
id (INTEGER PRIMARY KEY)
keyword (VARCHAR UNIQUE)
search_count (INTEGER)
created_at (DATETIME)
updated_at (DATETIME)
```

---

## Crawling System

### Crawl Types

#### RSS Crawling
- Detects RSS/Atom feeds from common paths
- Parses feed entries
- Extracts title, link, content
- Automatic content fallback to HTML if needed

**Detection Paths:**
- `/rss`, `/rss.xml`, `/feed`, `/feed.xml`
- Meta tag detection in HTML

#### HTML Crawling
- Uses CSS selectors to find article links
- Applies URL pattern filters
- Extracts article content via selectors or heuristics
- Validates minimum content length (150+ chars)

**Common Selectors:**
- `article` - HTML5 semantic tag
- `.article-link`, `.post-link` - Common classes
- `a[href*="/article/"]` - Article URL patterns

#### Sitemap Crawling
- Discovers `sitemap.xml` files
- Parses XML for article URLs
- Follows standard sitemap protocol
- Fallback to robots.txt references

#### Auto-Detection
Priority order:
1. **RSS** - Check common RSS paths and meta tags
2. **Sitemap** - Look for sitemap.xml
3. **HTML** - Use heuristic-based detection

### Heuristic-Based Detection

When no structured feeds found, the crawler uses heuristics:

1. **Link Discovery**
   - Removes navigation/footer/sidebar containers
   - Scans for article-like links (by URL pattern)
   - Ranks links by relevance

2. **Content Extraction**
   - Tries common CSS selectors first
   - Falls back to DOM density analysis
   - Validates minimum 150 character content

3. **Title Extraction**
   - From link text
   - From parent heading elements
   - Generated from URL slug

### Link Status Tracking

Automatic timeout and error detection:

- **Timeout Detection**: Links taking >20 seconds marked as inactive
- **Connection Error**: Failed connections recorded
- **HTTP Errors**: 404, 500, etc. tracked
- **Auto Recovery**: Successful fetches clear error status
- **Skip Inactive**: Already-down links skipped without waiting

#### Usage
```python
from src.database.repository import (
    is_link_active,
    mark_link_inactive,
    get_inactive_links_count
)

# Check before processing
if is_link_active(url):
    content = fetch_content(url)

# Monitor health
inactive = get_inactive_links_count()
print(f"Inactive links: {inactive}")
```

---

## Recent Improvements (January 23, 2026)

### Fix 1: Improved Article Link Extraction
**Problem**: Backend history pulling content links and navigation elements
**Solution**: 
- Enhanced `_find_article_links()` to remove sidebar/footer/header containers
- Added `_is_navigation_text()` to filter UI elements
- Improved `_is_article_link()` with stricter URL pattern matching

**Files Changed:**
- `src/crawler/dynamic_crawler.py` - Better container removal and link filtering
- `src/crawler/news_crawler.py` - Added navigation text detection

### Fix 2: Hard Delete Support
**Problem**: Deleting Master Data from frontend only soft deletes (preserves data)
**Solution**: 
- Added `hard_delete` query parameter to DELETE endpoint
- `hard_delete=true`: Permanently removes from database
- `hard_delete=false` (default): Soft delete only

**Files Changed:**
- `src/api/routes.py` - Updated delete endpoint

**Usage:**
```bash
# Soft delete (default)
DELETE /v1/sources/{id}

# Hard delete
DELETE /v1/sources/{id}?hard_delete=true
```

### Fix 3: Auto-Detect Selector Support
**Problem**: Auto-detect feature not actually crawling with detected configuration
**Solution**: 
- Added `POST /v1/sources/{id}/test-auto-detect` endpoint
- Runs auto-detection and returns sample articles
- Updates source configuration with detected type
- Enhanced `crawl_source()` to handle both NewsSource objects and dictionaries

**Files Changed:**
- `src/api/routes.py` - New test endpoint
- `src/crawler/news_crawler.py` - Improved crawl_source() method

**Usage:**
```bash
# Test auto-detect on a source
POST /v1/sources/1/test-auto-detect

# Response includes detected type and sample articles
```

---

## Troubleshooting

### Issue: Crawler not finding articles
**Diagnosis:**
1. Check if source is active: `GET /v1/sources/{id}`
2. Test with auto-detect: `POST /v1/sources/{id}/test-auto-detect`
3. Check crawl logs in stderr

**Solutions:**
- Update CSS selectors in source config
- Switch crawl_type to 'auto' for auto-detection
- For hardcoded sources, verify URL hasn't changed

### Issue: Timeout errors
**Diagnosis:**
1. Check link status: `GET /v1/dashboard/stats`
2. Identify inactive links: Source-specific query

**Solutions:**
- Links are automatically skipped after first timeout
- Use `reset_link_status()` to retry marked links
- Increase timeout (default 20s) if needed

### Issue: Low sentiment accuracy
**Diagnosis:**
1. Model may need retraining
2. Non-Indonesian text may not classify well
3. Very short articles (<100 chars) less accurate

**Solutions:**
- Ensure articles are proper Lampung/Indonesia news
- Train model with more examples
- Use pre-processing to clean text

### Issue: Duplicate articles
**Diagnosis:**
1. URLs not normalized (trailing slashes, parameters)
2. Same content published across sources

**Solutions:**
- Check URL normalization in crawler
- Review URL filters in source config
- Consider content-based de-duplication

---

## Configuration

### config.py
```python
class Config:
    DATABASE_URL = "sqlite:///database/media_analytics.db"
    MAX_ARTICLES_PER_SOURCE = 100
    ARTICLE_CONTENT_MIN_LENGTH = 150
    CRAWLER_TIMEOUT = 20  # seconds
    CRAWL_INTERVAL = 3600  # seconds
```

### Environment Variables
```bash
ENVIRONMENT=development|production
DEBUG=true|false
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
```

---

## Development Notes

### Adding New Hardcoded Source
1. Create method in `NewsCrawler`: `crawl_new_source()`
2. Add to `hardcoded_sources` in `repository.py`
3. Update documentation

### Extending Dynamic Crawler
1. Modify heuristics in `DynamicCrawler._find_article_links()`
2. Add new CSS selector patterns
3. Test with `POST /v1/crawler/crawl-url`

### ML Model Updates
1. Retrain sentiment model with new data
2. Update model path in config
3. Restart API server

---

## Support & Contact

For issues or questions:
1. Check this documentation
2. Review test files in `tests/` directory
3. Check logs in `*.log` files
4. Consult developer team

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Jan 23, 2026 | Improved link extraction, hard delete, auto-detect test endpoint |
| 0.9.0 | Jan 22, 2026 | Link status tracking implementation |
| 0.8.0 | Jan 19, 2026 | Hybrid crawling system |
| 0.7.0 | Jan 14, 2026 | Dynamic crawler addition |
| 0.1.0 | Dec 2025 | Initial release |

---

**Document Version**: 2.0
**Last Updated**: January 23, 2026
**Status**: Production Ready ✅
