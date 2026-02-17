# Database Schema Documentation

## Overview

The Media Analytics Backend uses SQLite as the database. All tables are defined in `src/database/models.py`.

---

## Table of Contents

1. [Articles](#articles)
2. [News Sources](#news-sources)
3. [Favorites](#favorites)
4. [Search History](#search-history)
5. [Relationships](#relationships)

---

## Articles

Stores all crawled news articles with sentiment analysis results.

**Table Name:** `articles`

### Columns

| Column | Type | Nullable | Unique | Default | Description |
|--------|------|----------|--------|---------|-------------|
| `id` | INTEGER | NO | YES | auto-increment | Primary key |
| `title` | VARCHAR(500) | NO | NO | - | Article title |
| `content` | TEXT | NO | NO | - | Full article content |
| `source` | VARCHAR(100) | YES | NO | - | News source name |
| `url` | VARCHAR(500) | YES | YES | - | Article URL |
| `published_date` | DATETIME | YES | NO | - | Original publication date |
| `crawled_date` | DATETIME | NO | NO | UTC now | When article was crawled |
| `keywords_flagged` | VARCHAR(512) | YES | NO | - | Comma-separated flagged keywords |
| `sentiment` | VARCHAR(20) | YES | NO | - | Sentiment: positive/negative/neutral |
| `confidence` | FLOAT | YES | NO | - | Sentiment confidence score (0-1) |
| `prob_negative` | FLOAT | YES | NO | - | Probability of negative sentiment |
| `prob_neutral` | FLOAT | YES | NO | - | Probability of neutral sentiment |
| `prob_positive` | FLOAT | YES | NO | - | Probability of positive sentiment |
| `category` | VARCHAR(100) | YES | NO | - | Article category |
| `author` | VARCHAR(200) | YES | NO | - | Article author |

### Example Record

```sql
INSERT INTO articles VALUES (
  1, 
  'Lampung Banjir Parah',
  'Wilayah Lampung mengalami banjir...',
  'Kompas',
  'https://kompas.com/article-1',
  '2024-01-14 10:00:00',
  '2024-01-14 10:30:00',
  'bencana,kecelakaan',
  'negative',
  0.92,
  0.92,
  0.05,
  0.03,
  'Bencana Alam',
  'Roni'
);
```

---

## News Sources

Stores news sources for crawling (both hardcoded and user-defined).

**Table Name:** `news_sources`

### Columns

| Column | Type | Nullable | Unique | Default | Description |
|--------|------|----------|--------|---------|-------------|
| `id` | INTEGER | NO | YES | auto-increment | Primary key |
| `name` | VARCHAR(100) | NO | YES | - | Source name (unique) |
| `base_url` | VARCHAR(500) | NO | NO | - | Base domain URL |
| `crawl_type` | VARCHAR(20) | NO | NO | 'auto' | Crawling method: rss/html/sitemap/auto |
| `config` | JSON | NO | NO | - | Crawling configuration |
| `active` | BOOLEAN | NO | NO | TRUE | Enable/disable source |
| `auto_detect` | BOOLEAN | NO | NO | TRUE | Auto-detect RSS/Sitemap |
| `is_hardcoded` | BOOLEAN | NO | NO | FALSE | Originally from hardcoded sources |
| `deleted_at` | DATETIME | YES | NO | NULL | Soft delete timestamp |
| `created_at` | DATETIME | NO | NO | UTC now | Creation timestamp |
| `updated_at` | DATETIME | NO | NO | UTC now | Last update timestamp |

### Crawl Type Values

- `rss`: RSS/Atom feed
- `html`: HTML scraping
- `sitemap`: Sitemap-based crawling
- `auto`: Auto-detect (tries RSS → Sitemap → HTML)

### Config JSON Schema

#### For RSS Sources
```json
{
  "rss_url": "https://example.com/rss"
}
```

#### For HTML Sources
```json
{
  "base_url": "https://example.com",
  "index_url": "https://example.com/news",
  "link_selector": "a.article-link",
  "title_selector": "h2.article-title",
  "content_selector": ".article-content",
  "filters": {
    "href_contains": "/article/",
    "href_not_contains": "/tag/"
  }
}
```

### Example Records

```sql
-- Hardcoded RSS source
INSERT INTO news_sources VALUES (
  1,
  'Kompas',
  'https://www.kompas.com',
  'rss',
  '{"rss_url": "https://indeks.kompas.com/rss"}',
  1,
  1,
  1,
  NULL,
  '2024-01-14 10:00:00',
  '2024-01-14 10:00:00'
);

-- User-defined HTML source
INSERT INTO news_sources VALUES (
  7,
  'My News Site',
  'https://mynewssite.com',
  'html',
  '{"base_url": "https://mynewssite.com", "link_selector": "a.news"}',
  1,
  1,
  0,
  NULL,
  '2024-01-14 11:00:00',
  '2024-01-14 11:00:00'
);
```

---

## Favorites

Stores user's favorite articles.

**Table Name:** `favorites`

### Columns

| Column | Type | Nullable | Unique | Default | Description |
|--------|------|----------|--------|---------|-------------|
| `id` | INTEGER | NO | YES | auto-increment | Primary key |
| `article_id` | INTEGER | NO | NO | - | Foreign key to articles table |
| `created_at` | DATETIME | NO | NO | UTC now | When article was favorited |

### Foreign Keys

- `article_id` → `articles.id` (CASCADE)

### Example Record

```sql
INSERT INTO favorites VALUES (1, 5, '2024-01-14 11:30:00');
```

---

## Search History

Tracks search keywords used on the dashboard.

**Table Name:** `search_history`

### Columns

| Column | Type | Nullable | Unique | Default | Description |
|--------|------|----------|--------|---------|-------------|
| `id` | INTEGER | NO | YES | auto-increment | Primary key |
| `keyword` | VARCHAR(500) | NO | NO | - | Search keyword |
| `search_count` | INTEGER | NO | NO | 1 | Number of times searched |
| `created_at` | DATETIME | NO | NO | UTC now | First search time |
| `updated_at` | DATETIME | NO | NO | UTC now | Last search time |

### Example Record

```sql
INSERT INTO search_history VALUES (
  1,
  'lampung disaster',
  5,
  '2024-01-14 09:00:00',
  '2024-01-14 11:30:00'
);
```

---

## Relationships

```
Articles ─ 1 ──── N ── Favorites
  (id)            (article_id)
```

### One-to-Many Relationship

**Articles → Favorites**

- Each article can have multiple favorite entries
- Deleting an article cascades to its favorites
- Used to track which articles users have favorited

---

## Indexes

The following indexes should be created for optimal performance:

```sql
-- Articles indexes
CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_articles_crawled_date ON articles(crawled_date DESC);
CREATE INDEX idx_articles_sentiment ON articles(sentiment);
CREATE INDEX idx_articles_search ON articles(title, content);

-- News Sources indexes
CREATE INDEX idx_news_sources_name ON news_sources(name);
CREATE INDEX idx_news_sources_active ON news_sources(active);
CREATE INDEX idx_news_sources_deleted_at ON news_sources(deleted_at);

-- Favorites indexes
CREATE INDEX idx_favorites_article_id ON favorites(article_id);
CREATE INDEX idx_favorites_created_at ON favorites(created_at DESC);

-- Search History indexes
CREATE INDEX idx_search_history_keyword ON search_history(keyword);
CREATE INDEX idx_search_history_updated_at ON search_history(updated_at DESC);
```

---

## Data Types

- **INTEGER**: Whole numbers
- **VARCHAR(n)**: Variable-length text (max n characters)
- **TEXT**: Large text blocks
- **DATETIME**: Date and time (ISO format)
- **BOOLEAN**: True/False (stored as 0/1 in SQLite)
- **FLOAT**: Decimal numbers
- **JSON**: JSON objects (stored as text in SQLite)

---

## Constraints

### Primary Keys
- All tables have an `id` primary key

### Unique Constraints
- `articles.url`: URLs must be unique (prevents duplicates)
- `news_sources.name`: Source names must be unique

### Foreign Keys
- `favorites.article_id` → `articles.id`

### Not Null Constraints
- See column definitions above

---

## Data Retention Policy

### Current Implementation
- Articles are automatically cleaned up after 30 days via `cleanup_old_articles(days=30)`
- This can be configured via the `CRAWL_INTERVAL` setting

### Soft Deletes
- News sources use soft deletes (set `deleted_at` timestamp)
- Allows recovery and historical tracking
- Set `deleted_at IS NULL` to filter active sources

---

## Typical Queries

### Get Recent Articles
```sql
SELECT * FROM articles 
WHERE crawled_date >= datetime('now', '-1 day')
ORDER BY crawled_date DESC
LIMIT 20;
```

### Get Active Sources
```sql
SELECT * FROM news_sources 
WHERE active = 1 AND deleted_at IS NULL
ORDER BY created_at DESC;
```

### Get Favorite Articles
```sql
SELECT a.* FROM articles a
JOIN favorites f ON a.id = f.article_id
ORDER BY f.created_at DESC
LIMIT 50;
```

### Get Search Statistics
```sql
SELECT keyword, search_count, updated_at 
FROM search_history 
ORDER BY search_count DESC, updated_at DESC
LIMIT 10;
```

### Find Articles by Sentiment
```sql
SELECT * FROM articles
WHERE sentiment = 'negative'
ORDER BY confidence DESC, crawled_date DESC
LIMIT 100;
```

---

## Migration Notes

### From Previous Versions
If upgrading from older versions:

1. **New Tables**: `search_history` table will be created automatically
2. **Schema Changes**: `news_sources` table has new columns:
   - `base_url`
   - `crawl_type` (replaces `type`)
   - `auto_detect`
   - `is_hardcoded`
   - `deleted_at`
   - `updated_at`

3. **Migration Steps**:
   ```python
   # Run this to initialize/migrate database
   from src.database.repository import init_db
   init_db()
   ```

---

## Backup & Recovery

### Backup Database
```bash
cp database/media_analytics.db database/media_analytics.db.backup
```

### Database Size
- Typical database size: ~5-50 MB per 100,000 articles
- Monitor: `database/media_analytics.db` file size

### Performance Tips
- Regular cleanup of old articles
- Create indexes on frequently queried columns
- Use pagination for large result sets
- Archive old articles if needed
