# Crawling Strategy Documentation

## Overview

The Media Analytics Backend uses a two-tier crawling system:

1. **Hardcoded Crawler** - Pre-configured sources
2. **Dynamic Crawler** - User-submitted URLs with auto-detection

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│         News Crawler Entry Point                │
│    (src/crawler/news_crawler.py::crawl_all)    │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┴───────────┐
        │                      │
        ▼                      ▼
    ┌────────────┐      ┌──────────────────┐
    │ Hardcoded  │      │  Dynamic Crawler │
    │  Sources   │      │  (User URLs)     │
    └────────────┘      └──────────────────┘
        │                      │
        ├─ Kompas            ├─ Auto-detect
        ├─ Detik             ├─ RSS Detection
        ├─ Radar Lampung     ├─ Sitemap Detection
        ├─ Suara             └─ HTML Heuristics
        ├─ Tribun Lampung
        └─ Lampung Pro
```

---

## Hardcoded Crawler

### Overview

Pre-configured crawlers for known news sources. Each source has specific HTML parsing logic adapted to its structure.

### Source Configuration

Located in `src/crawler/news_crawler.py`, each source has its own crawling method:

#### 1. Kompas (`crawl_kompas`)

**URL:** https://www.kompas.com/lampung/

**Strategy:** HTML-based crawling with CSS selectors

```python
- Target: Kompas Lampung news section
- Link Selection: Main content containers
- Filtering: URLs containing /lampung or /read
- Content Extraction: Main article text
- Article Count: Up to 100 per run
```

**Key Features:**
- Fallback to all page anchors if containers don't match
- Loose URL filtering to avoid missing articles
- Robust title extraction from anchor text

#### 2. Detik

**URL:** https://rss.detik.com/index.php/detikcom

**Strategy:** RSS feed parsing

```python
- Type: RSS Feed
- Content Fallback: Fetches full HTML if RSS content too short
- Article Count: Up to 100 per run
```

#### 3. Radar Lampung

**Strategy:** HTML-based crawling

```python
- Adaptive selector detection
- Container-based article finding
- URL pattern matching
```

#### 4. Suara

**Strategy:** RSS feed parsing

```python
- Reliable RSS implementation
- Meta tag extraction
- Link normalization
```

#### 5. Tribun Lampung

**Strategy:** HTML-based crawling with regex patterns

```python
- Pattern-based link detection
- Resilient to HTML changes
- Content normalization
```

#### 6. Lampung Pro

**Strategy:** Adaptive HTML crawling

```python
- Multiple selector fallbacks
- Dynamic content handling
- Clean text extraction
```

### Processing Pipeline

```
1. Fetch HTML/RSS
   ↓
2. Parse content
   ↓
3. Extract articles (links, titles)
   ↓
4. De-duplicate URLs
   ↓
5. Fetch full article content
   ↓
6. Sentiment Analysis
   ↓
7. Extract Keywords
   ↓
8. Store in Database
```

### Resilience Mechanisms

1. **Fallback Selectors**: Try multiple CSS selectors if primary fails
2. **Timeout Handling**: 15-second timeout per request
3. **Exception Catching**: Continues crawling other sources on error
4. **Content Validation**: Minimum 200 characters required
5. **URL Filtering**: Avoids navigation/tag pages

---

## Dynamic Crawler

### Overview

Automatically discovers and crawls user-provided URLs without manual configuration.

**Location:** `src/crawler/dynamic_crawler.py`

### Crawl Type Detection

The system automatically detects the best crawling method:

```
User provides URL
   ↓
┌──────────────────────────────┐
│  1. Check for RSS Feeds      │ ← Priority 1
│     - Common paths (/rss, /feed, etc.)
│     - HTML meta tags
└──────────────────────────────┘
   ↓ Not found
┌──────────────────────────────┐
│  2. Check for Sitemap        │ ← Priority 2
│     - /sitemap.xml
│     - robots.txt reference
└──────────────────────────────┘
   ↓ Not found
┌──────────────────────────────┐
│  3. HTML Heuristic Detection │ ← Fallback
│     - DOM density analysis
│     - Common patterns
│     - Link heuristics
└──────────────────────────────┘
```

### RSS Detection

**Process:**

1. Check common paths:
   - `/rss`
   - `/rss.xml`
   - `/feed`
   - `/feed.xml`
   - `/feeds`
   - `/feeds/rss`
   - `/index.php/rss`

2. Parse HTML for meta tags:
   ```html
   <link rel="alternate" type="application/rss+xml" href="/rss" />
   <link rel="feed" href="/feed" />
   ```

3. Return first working RSS URL

**Advantages:**
- Most reliable method
- Structured content
- Metadata available
- Efficient parsing

### Sitemap Detection

**Process:**

1. Try `/sitemap.xml`
2. Check `robots.txt` for sitemap location
3. Validate URL accessibility

**Use Case:**
- Large websites with proper sitemap
- Efficient URL discovery
- Periodic crawling

### HTML Heuristic Crawling

**Strategy:** When RSS/Sitemap not available, use intelligent HTML parsing

#### 1. Article Link Discovery

```python
Heuristics applied:
- URL pattern matching (/article/, /news/, /post/, /read/, /story/)
- Numeric ID detection (/2024/01/123)
- URL length (longer = more specific)
- Title length (longer = more informative)
- Common URL segments

Skip patterns:
- Navigation links (/tag/, /category/, /page/)
- Utility links (/search, /help, /about, /contact)
- Admin/login pages (/admin, /login, /register)
- Feed links (/rss, /feed)
```

#### 2. Title Extraction

```
Priority order:
1. Anchor tag text (most reliable)
2. Parent heading tag (h1, h2, h3, h4)
3. URL slug transformation (camelCase/slug → Title Case)
```

#### 3. Content Extraction

**Method 1: CSS Selector Detection** (Fastest)
```
Common selectors tried in order:
- article
- main
- [role="main"]
- .post-content
- .article-content
- .entry-content
- .content-body
- .isi-artikel (Indonesian)
- .story-body
- .article__body
- .news-content
- div[class*="content"]
- div[class*="artikel"] (Indonesian)
- div[class*="article"]
- div[class*="post"]
```

**Method 2: DOM Density Heuristic** (Fallback)
```
Formula: text_length / (number_of_tags + 1)

Process:
1. Calculate density for all major containers
2. Find element with highest density
3. Extract text from that element
```

#### 4. Content Validation

```python
Filters:
- Minimum 150 characters required
- Remove scripts, styles, navigation
- Clean HTML tags
- Limit to 5000 characters
```

### Processing Flow

```
Dynamic Crawl Request (URL)
   ↓
Detect Crawl Type
   ├─ RSS → RSS Parser
   ├─ Sitemap → Sitemap Parser
   └─ HTML → Heuristic Parser
   ↓
Find Article Links
   ├─ URL pattern heuristics
   ├─ Link ranking by relevance
   └─ De-duplication
   ↓
For each article:
   ├─ Fetch content
   ├─ Extract text (selector or density)
   ├─ Validate content length
   └─ Sentiment analysis
   ↓
Return articles
```

---

## Sentiment Analysis

### Overview

All articles are analyzed for sentiment (positive, negative, neutral).

**Location:** `src/ml/sentiment_analyzer.py`

### Model Details

- **Model**: DistilBERT fine-tuned for sentiment
- **Languages**: Indonesian (primary), English
- **Output**: 
  - Sentiment label (positive/negative/neutral)
  - Confidence score (0-1)
  - Per-label probabilities

### Processing

```
Article Text
   ↓
Preprocessing
   ├─ Lowercasing
   ├─ Text cleaning
   └─ Tokenization
   ↓
DistilBERT Model
   ├─ Input: Article content or title
   ├─ Output: Logits per sentiment class
   └─ Softmax: Convert to probabilities
   ↓
Result
   ├─ sentiment: negative/neutral/positive
   ├─ confidence: 0.0-1.0
   ├─ prob_negative: 0.0-1.0
   ├─ prob_neutral: 0.0-1.0
   └─ prob_positive: 0.0-1.0
```

---

## Keyword Extraction

### Overview

Flags articles containing specific keywords relevant to news monitoring.

**Location:** `src/database/repository.py::extract_keywords_flagged`

### Flagged Keywords

```python
{
    "korupsi",        # Corruption
    "kriminal",       # Crime
    "demo",           # Protest/Demonstration
    "kecelakaan",     # Accident
    "bencana",        # Disaster
    "pembunuhan",     # Murder
    "narkoba",        # Drugs
    "olahraga",       # Sports
    "hukum"           # Law
}
```

### Processing

```python
1. Convert text to lowercase
2. Check each keyword presence
3. Store comma-separated list
4. Example output: "korupsi,bencana,hukum"
```

---

## Database Storage

### Article Storage

```
Article data flow:
1. Create article dict with:
   - title, url, source, content
   - sentiment, confidence, probabilities
   - keywords_flagged
   - crawled_date

2. Check for duplicates (by URL)

3. If exists:
   - Update sentiment analysis
   - Preserve original metadata

4. If new:
   - Insert into database
   - Commit transaction
```

### Bulk Insert

```python
# Multiple articles from same source
articles = [article1, article2, ...]
save_articles_bulk(articles)

# Internally:
- Opens single DB session
- De-duplicates URLs
- Upserts each article
- Single commit
```

---

## Crawl Scheduling

### Manual Crawling

**API Endpoint:** `POST /v1/crawler/run`

Triggers all active sources immediately.

### Scheduled Crawling (Optional)

Can be enabled in `src/api/app.py`:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()
scheduler.add_job(
    crawl_periodically, 
    IntervalTrigger(hours=config.CRAWL_INTERVAL)
)
scheduler.start()
```

### Configuration

```python
# config.py
CRAWL_INTERVAL = 3600  # 1 hour
MAX_ARTICLES_PER_SOURCE = 100
```

---

## Error Handling

### Graceful Degradation

```
If source fails:
1. Log error with source name
2. Continue with next source
3. Don't abort entire crawl
4. Report successful sources
```

### Common Errors

1. **Connection Timeout**
   - Action: Skip source, continue
   - Retry: Not implemented (prevent rate limiting)

2. **Invalid HTML**
   - Action: Use fallback selectors
   - Last Resort: Skip article

3. **Content Too Short**
   - Action: Skip article (< 150 chars)
   - Reason: Likely navigation/teaser

4. **Duplicate URL**
   - Action: Skip (ignore insert)
   - Reason: Prevent duplicates

5. **Missing Required Fields**
   - Action: Skip article
   - Validation: title, url, content

---

## Performance Optimization

### Techniques

1. **Connection Pooling**
   - Reuse HTTP session within crawler
   - Faster DNS resolution

2. **Timeout Settings**
   - Request timeout: 15 seconds
   - RSS parsing: Default feedparser

3. **Batch Operations**
   - Bulk inserts (multiple articles)
   - Single DB transaction

4. **Caching** (Future)
   - Cache RSS feeds
   - Cache parsed content

### Typical Performance

```
Hardcoded Sources (6 sources):
- Total articles: 400-600
- Duration: 5-15 minutes
- DB size growth: ~50-100 KB

Dynamic URL Crawl:
- Single site: 20-50 articles
- Duration: 30 seconds - 2 minutes
- Size: ~100-200 KB
```

---

## Future Enhancements

### Planned Features

1. **Intelligent Caching**
   - Cache RSS feeds to reduce requests
   - Check ETags/Last-Modified

2. **JavaScript Rendering**
   - Support dynamic content
   - Use Playwright/Puppeteer

3. **Computer Vision**
   - Extract article images
   - Image-based duplicate detection

4. **Multi-language Support**
   - Language detection
   - Source-specific parsing

5. **Proxy Support**
   - Rotate proxies
   - Avoid IP bans

### Configuration for Extensions

```python
# Dynamic crawler config example
config = {
    'rss_url': 'https://example.com/rss',
    'timeout': 10,
    'max_articles': 50,
    'proxy': 'http://proxy.example.com:8080',
    'user_agent': 'Mozilla/5.0...'
}
```

---

## Testing & Validation

### Unit Tests

Located in `tests/test_crawler.py`:

```python
- Test hardcoded crawlers
- Test dynamic crawler
- Test sentiment analysis
- Test keyword extraction
```

### Integration Tests

```python
- Full crawl pipeline
- Database storage
- API endpoints
```

### Manual Testing

```bash
# Run crawler
curl -X POST http://localhost:5000/v1/crawler/run

# Crawl custom URL
curl -X POST "http://localhost:5000/v1/crawler/crawl-url?url=https://example.com"

# Check results
curl http://localhost:5000/v1/articles
```

---

## Monitoring & Maintenance

### Logs

Check `logs/` directory for crawler activity:
```
[2024-01-14 10:30:00] INFO: Kompas: found 50 articles
[2024-01-14 10:35:00] INFO: Detik: found 45 articles
[2024-01-14 10:40:00] INFO: Crawl completed successfully
```

### Database Maintenance

```python
# Auto cleanup old articles (every crawl)
cleanup_old_articles(days=30)

# Backup database
cp database/media_analytics.db database/media_analytics.db.backup
```

### Troubleshooting

1. **No articles found**
   - Check source is active
   - Verify URL accessibility
   - Check network connectivity

2. **Timeout errors**
   - Increase timeout setting
   - Check source responsiveness
   - Review network issues

3. **Duplicate articles**
   - Check URL uniqueness constraint
   - Verify dedupe logic

4. **Missing content**
   - Check CSS selectors
   - Verify DOM density heuristic
   - Review content filters
