# AI Coding Agent Instructions - Media Analytics Backend

## Project Overview
**Dual-stack media analytics platform**: Python FastAPI backend for news crawling, sentiment analysis, and ML inference + Laravel frontend for UI/reporting.

### Core Responsibilities
- **News crawling**: RSS feeds and HTML parsing from Indonesian news sources (Kompas, Detik, Tribun Lampung, Radar, Suara, Lampung Pro)
- **Sentiment analysis**: Binary classification (positive/negative) using transformers ML model
- **Keyword extraction**: High-accuracy keyword detection from title + content
- **Link tracking**: Manages link status (active/inactive/timeout) to avoid re-crawling broken URLs
- **API serving**: FastAPI REST endpoints for article retrieval, source management, and analytics

---

## Architecture & Key Patterns

### Monolithic Backend Structure
```
src/
├── api/              # FastAPI routes (app.py, routes.py, crawler_routes.py)
├── crawler/          # News crawling logic (news_crawler.py + individual source crawlers)
├── database/         # SQLAlchemy models (Article, NewsSource, LinkStatus, Favorite)
├── ml/              # Sentiment analyzer + text preprocessing
├── services/        # High-level business logic (not just DB access)
├── tasks/           # Background/scheduled tasks
└── utils/           # Logger, keyword extractor, helpers
```

### Critical Data Flow
1. **Crawl Initiation**: `crawl_all()` → loads sources from DB + hardcoded defaults
2. **Content Fetching**: `get_article_content(url)` → HTTP fetch → HTML parsing → `_extract_article_body(soup)` (uses CSS selectors)
3. **Validation Pipeline**:
   - `_is_valid_article_url()`: Rejects social media, non-article patterns
   - `_is_authentic_article()`: Filters exclude_keywords, checks content length (200+ chars)
   - Link status check: Skips if marked inactive by prior failure
4. **Enrichment**: Each article gets sentiment score + keywords before saving
5. **Persistence**: Bulk insert to SQLite via SQLAlchemy ORM

### Content Extraction Pattern (Critical!)
**All HTML parsing follows CSS selector priority order** in `_extract_article_body()`:
```python
selectors = [
    "div.post-content",       # Radar Lampung (Disway CMS)
    "div#article-content",    # Kompas
    "div.detail__body-text",  # Detik
    # ... others
    "article"                 # Generic fallback
]
```
✅ Uses `.get_text(" ", strip=True)` to preserve word spacing  
✅ Tries each selector in order; returns first match  
✅ Falls back to `soup.get_text()` if no selector matches

---

## Project-Specific Conventions

### Article Dictionary Schema
Every crawler returns articles as:
```python
{
    "title": str,
    "url": str,
    "source": str,              # Source name (e.g., "Kompas")
    "content": str,             # Plain text only (no HTML)
    "keywords_flagged": str,    # Comma-separated keyword list
    "sentiment": str,           # "positive", "negative", "neutral"
    "confidence": float,        # 0.0-1.0
    "prob_positive": float,
    "prob_negative": float,
    "prob_neutral": float,
    "crawled_date": datetime,
}
```

### Error Handling Convention
**Link Status Tracking** (not just exceptions):
```python
# After successful fetch:
mark_link_active(url)

# After HTTP 404/403/5xx:
mark_link_inactive(url, "HTTP 404", source_name)

# After timeout:
mark_link_timeout(url, source_name)
```
Links marked inactive are skipped in future crawls (`if not is_link_active(url): return ""`).

### Source Configuration Pattern
**Hardcoded sources** (in `config.py`) vs **DB sources** (`NewsSource` model):
```python
# Hardcoded (NEWS_SOURCES list in config.py)
{"name": "Kompas", "url": "https://...", "parser": "rss"}

# DB-sourced with custom crawler method:
source.crawl_type in ["rss", "html", "sitemap"]
source.config = {"rss_url": "...", "content_selector": "..."}
```
Special crawlers (`crawl_kompas()`, `crawl_detik()`, etc.) route via `crawl_all()` → check source name.

### Sentiment Analysis Integration
```python
self.analyzer = SentimentAnalyzer(model_path="src/ml/model")
result = self.analyzer.predict(content or title)
# Returns: {"sentiment": str, "confidence": float, "prob_*": float}
```
**Always use content first; fallback to title only if content empty.**

---

## Testing & Development Workflows

### Running Tests
```bash
cd c:\xampp\htdocs\project\backend-media-analytic-final
python -m pytest tests/ -v                    # Run all tests
python -m pytest tests/test_content_extraction.py -v  # Specific test
```

### Local API Development
```bash
# Activate venv
.venv\Scripts\activate

# Start FastAPI with auto-reload
python -m uvicorn src.api.app:app --reload

# API runs on http://localhost:8000
# Docs at http://localhost:8000/docs (Swagger)
```

### Database Operations
```bash
# Initialize fresh DB
python -c "from src.database.repository import init_db; init_db()"

# Access session in scripts
from src.database.repository import get_session
session = get_session()
```

### Debugging Crawlers
```python
# Test single source crawling
from src.crawler.news_crawler import NewsCrawler
crawler = NewsCrawler()
articles = crawler.crawl_kompas()  # or crawl_detik(), crawl_radar(), etc.
```

---

## Common Tasks & Code Locations

| Task | File | Pattern |
|------|------|---------|
| Add new news source | `src/crawler/news_crawler.py` | Add `crawl_sourcename()` method; register in `crawl_all()` |
| Modify content extraction | `src/crawler/news_crawler.py:_extract_article_body()` | Add CSS selector to priority list |
| Add API endpoint | `src/api/routes.py` | Use FastAPI `@router.get()` decorator |
| Change sentiment threshold | `src/ml/sentiment_analyzer.py` | Modify confidence/probability thresholds |
| Add link status tracking | `src/database/repository.py` | Use `mark_link_*()` functions in crawler |
| Exclude more keywords | `src/crawler/news_crawler.py:__init__()` | Update `self.exclude_keywords` list |

---

## Critical "Gotchas" & Conventions

1. **Content Length Validation**: Articles under 200 chars are filtered as non-authentic. HTML parsing must return meaningful text.

2. **Link Status Check FIRST**: Always check `if not is_link_active(url)` before making HTTP requests; saves bandwidth.

3. **Relative URL Normalization**: Crawlers must normalize relative paths:
   ```python
   if href.startswith("/"): href = base_url + href
   ```

4. **Deduplication**: Use `seen_urls` set to avoid duplicate articles within single crawl run.

5. **Source Name Consistency**: Article's `source` field must exactly match registered source name for proper filtering.

6. **HTML Parsing Library**: All HTML parsing uses **BeautifulSoup with lxml parser**:
   ```python
   soup = BeautifulSoup(r.content, "lxml")  # Never use "html.parser"
   ```

7. **Timeout Value**: All HTTP requests use `timeout=20` (or `timeout=15` for index pages).

8. **Sentiment Analysis Fallback**: If ML model fails, sentiment defaults to "neutral" with confidence 0.0.

---

## Dependencies & Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| API Framework | FastAPI | 0.115.6 |
| Web Server | Uvicorn | 0.32.1 |
| Database ORM | SQLAlchemy | 2.0.44 |
| Database | SQLite | (file-based) |
| HTML Parsing | BeautifulSoup4 | 4.14.3 |
| ML Model | Transformers/Torch | 4.57.3 / 2.9.1 |
| RSS Parsing | feedparser | 6.0.12 |
| HTTP | requests | 2.32.3 |
| Task Scheduling | APScheduler | 3.11.2 |

---

## Key Documentation Files

**Must Read First**:
- `docs/MASTER_DOCUMENTATION.md` - Complete system reference
- `docs/PROJECT_STRUCTURE.md` - Code organization details
- `docs/CRAWLING_STRATEGY.md` - Detailed crawler algorithms

**Implementation Details**:
- `docs/DATABASE_SCHEMA.md` - Table definitions & relationships
- `docs/API_DOCUMENTATION.md` - REST endpoint reference
- `docs/LINK_STATUS_TRACKING.md` - Link status state machine

**Recent Fixes**:
- `docs/FIX_REPORT_LAMPUNG_PRO_TRIBUN.md` - Domain validation improvements
- `docs/TRIBUN_FIX_COMPLETE.md` - Tribun Lampung RSS parsing

---

## Writing New Crawlers

Template for adding a new news source crawler:

```python
def crawl_newsource(self):
    """Crawl NewsSource articles."""
    base_url = "https://newsource.com"
    url = f"{base_url}/news"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception:
        logger.exception("NewsSource: failed fetching")
        return []
    
    articles = []
    seen_urls = set()
    
    for link_elem in soup.find_all("a", href=True):
        href = link_elem.get("href", "").strip()
        if not href or href in seen_urls:
            continue
        
        if href.startswith("/"): href = base_url + href
        if not is_link_active(href): continue
        if not self._is_valid_article_url(href, "newsource.com"): continue
        
        seen_urls.add(href)
        title = link_elem.get_text(strip=True)
        if not title or len(title) < 5: continue
        
        content = self.get_article_content(href, {"name": "NewsSource"})
        if not content or len(content) < 200: continue
        if not self._is_authentic_article(title, href, content): continue
        
        articles.append(self._create_article_dict(title, href, "NewsSource", content))
        if len(articles) >= self.max_per_source: break
    
    logger.info(f"NewsSource: {len(articles)} articles")
    return articles
```

---

## Integration with Frontend (Laravel)

Frontend at `c:\xampp\htdocs\project\frontend-media-analytic` consumes:
- **GET `/v1/articles`** - List articles with filters (sentiment, source, keyword)
- **GET `/v1/articles/{id}`** - Article detail + sentiment breakdown
- **POST `/v1/sources`** - Add custom news source
- **POST `/v1/crawl`** - Trigger manual crawl

Full API spec: `docs/API_DOCUMENTATION.md`
