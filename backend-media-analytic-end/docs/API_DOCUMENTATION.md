# Media Analytics Backend - API Documentation

## Overview

The Media Analytics Backend provides REST APIs for:
- News article management and search
- Dynamic news source crawling
- Sentiment analysis
- Favorites management
- Search history tracking
- Dashboard statistics

**Base URL:** `http://localhost:5000/v1`

**API Version:** 1.0.0

---

## Table of Contents

1. [Articles](#articles)
2. [News Sources](#news-sources)
3. [Crawler](#crawler)
4. [Favorites](#favorites)
5. [Search History](#search-history)
6. [Dashboard](#dashboard)
7. [Health Check](#health-check)

---

## Articles

### List Articles

Get a paginated list of articles with optional filters.

**Endpoint:** `GET /articles`

**Query Parameters:**
- `q` (optional, string): Search query (searches title and content)
- `source` (optional, string): Filter by source name

**Response:**
```json
[
  {
    "id": 1,
    "title": "Article Title",
    "url": "https://example.com/article",
    "source": "Kompas",
    "sentiment": "positive",
    "crawled_date": "2024-01-14T10:30:00"
  }
]
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

### Get Single Article

Retrieve full details of a specific article.

**Endpoint:** `GET /article/{article_id}`

**Path Parameters:**
- `article_id` (required, integer): Article ID

**Response:**
```json
{
  "id": 1,
  "title": "Article Title",
  "url": "https://example.com/article",
  "source": "Kompas",
  "content": "Full article content...",
  "sentiment": "positive",
  "keywords_flagged": "korupsi,hukum",
  "crawled_date": "2024-01-14T10:30:00"
}
```

**Status Codes:**
- `200`: Success
- `404`: Article not found
- `500`: Internal server error

---

## News Sources

### List News Sources

Get all active news sources.

**Endpoint:** `GET /sources`

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
    "created_at": "2024-01-14T10:00:00",
    "updated_at": "2024-01-14T10:00:00"
  }
]
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

### Create News Source

Add a new news source.

**Endpoint:** `POST /sources`

**Request Body:**
```json
{
  "name": "My News Source",
  "base_url": "https://mynewssite.com",
  "crawl_type": "auto",
  "config": {
    "rss_url": "https://mynewssite.com/rss"
  },
  "active": true,
  "auto_detect": true
}
```

**Request Parameters:**
- `name` (required, string): Source name (must be unique)
- `base_url` (required, string): Base URL of the news source
- `crawl_type` (optional, string): `"rss"`, `"html"`, `"sitemap"`, or `"auto"` (default: `"auto"`)
- `config` (required, object): Crawling configuration
- `active` (optional, boolean): Enable/disable source (default: `true`)
- `auto_detect` (optional, boolean): Auto-detect RSS/Sitemap (default: `true`)

**Response:**
```json
{
  "id": 2,
  "name": "My News Source",
  "base_url": "https://mynewssite.com",
  "crawl_type": "auto",
  "active": true,
  "auto_detect": true,
  "is_hardcoded": false,
  "created_at": "2024-01-14T10:30:00",
  "updated_at": "2024-01-14T10:30:00"
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

### Get News Source Details

Get a specific news source.

**Endpoint:** `GET /sources/{source_id}`

**Path Parameters:**
- `source_id` (required, integer): Source ID

**Response:**
```json
{
  "id": 1,
  "name": "Kompas",
  "base_url": "https://www.kompas.com",
  "crawl_type": "rss",
  "active": true,
  "auto_detect": true,
  "is_hardcoded": true,
  "created_at": "2024-01-14T10:00:00",
  "updated_at": "2024-01-14T10:00:00"
}
```

**Status Codes:**
- `200`: Success
- `404`: Source not found
- `500`: Internal server error

---

### Update News Source

Update a news source.

**Endpoint:** `PUT /sources/{source_id}`

**Path Parameters:**
- `source_id` (required, integer): Source ID

**Request Body (all fields optional):**
```json
{
  "name": "Updated Name",
  "base_url": "https://updated-url.com",
  "crawl_type": "html",
  "active": false,
  "auto_detect": false
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Updated Name",
  "base_url": "https://updated-url.com",
  "crawl_type": "html",
  "active": false,
  "auto_detect": false,
  "is_hardcoded": true,
  "created_at": "2024-01-14T10:00:00",
  "updated_at": "2024-01-14T11:00:00"
}
```

**Status Codes:**
- `200`: Success
- `404`: Source not found
- `500`: Internal server error

---

### Delete News Source

Soft delete a news source (marks as deleted, doesn't remove from DB).

**Endpoint:** `DELETE /sources/{source_id}`

**Path Parameters:**
- `source_id` (required, integer): Source ID

**Response:**
```json
{
  "message": "Source deleted successfully",
  "source_id": 1
}
```

**Status Codes:**
- `200`: Success
- `404`: Source not found
- `500`: Internal server error

---

## Crawler

### Run Main Crawler

Run the crawler for all active sources (hardcoded + user-defined).

**Endpoint:** `POST /crawler/run`

**Response:**
```json
{
  "message": "Crawler completed successfully. Found 150 articles.",
  "articles_count": 150
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

### Crawl Custom URL (Dynamic Crawler)

Crawl a user-provided URL with automatic detection of articles.

**Endpoint:** `POST /crawler/crawl-url`

**Query Parameters:**
- `url` (required, string): URL to crawl

**Response:**
```json
{
  "message": "Crawled https://example.com successfully. Found 25 articles.",
  "articles_count": 25,
  "articles": [
    {
      "title": "Article Title",
      "url": "https://example.com/article1",
      "content": "Article content...",
      "source": "Example"
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

## Favorites

### Add to Favorites

Add an article to favorites.

**Endpoint:** `POST /favorites/{article_id}`

**Path Parameters:**
- `article_id` (required, integer): Article ID

**Response:**
```json
{
  "message": "Article added to favorites",
  "favorite_id": 5,
  "article_id": 1
}
```

**Status Codes:**
- `200`: Success
- `404`: Article not found
- `409`: Article already in favorites
- `500`: Internal server error

---

### Remove from Favorites

Remove an article from favorites.

**Endpoint:** `DELETE /favorites/{article_id}`

**Path Parameters:**
- `article_id` (required, integer): Article ID

**Response:**
```json
{
  "message": "Article removed from favorites",
  "article_id": 1
}
```

**Status Codes:**
- `200`: Success
- `404`: Favorite not found
- `500`: Internal server error

---

### List Favorites

Get all favorite articles.

**Endpoint:** `GET /favorites`

**Query Parameters:**
- `limit` (optional, integer): Maximum results (default: 100, max: 1000)

**Response:**
```json
[
  {
    "favorite_id": 5,
    "article": {
      "id": 1,
      "title": "Article Title",
      "url": "https://example.com/article",
      "source": "Kompas",
      "sentiment": "positive",
      "confidence": 0.95,
      "crawled_date": "2024-01-14T10:30:00"
    },
    "added_at": "2024-01-14T11:00:00"
  }
]
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

### Check if Article is Favorite

Check if a specific article is in favorites.

**Endpoint:** `GET /favorites/{article_id}/check`

**Path Parameters:**
- `article_id` (required, integer): Article ID

**Response:**
```json
{
  "is_favorite": true,
  "article_id": 1,
  "favorite_id": 5
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

## Search History

### Save Search

Save a search keyword to history.

**Endpoint:** `POST /search-history`

**Query Parameters:**
- `keyword` (required, string): Search keyword (1-500 characters)

**Response:**
```json
{
  "id": 3,
  "keyword": "lampung news",
  "search_count": 2,
  "message": "Search saved to history"
}
```

**Status Codes:**
- `200`: Success
- `422`: Invalid input
- `500`: Internal server error

---

### Get Search History

Retrieve search history.

**Endpoint:** `GET /search-history`

**Query Parameters:**
- `limit` (optional, integer): Maximum results (default: 50, max: 500)

**Response:**
```json
[
  {
    "id": 3,
    "keyword": "lampung news",
    "search_count": 5,
    "created_at": "2024-01-14T09:00:00",
    "updated_at": "2024-01-14T11:00:00"
  },
  {
    "id": 2,
    "keyword": "disaster",
    "search_count": 2,
    "created_at": "2024-01-14T10:00:00",
    "updated_at": "2024-01-14T10:00:00"
  }
]
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

### Delete Search History Entry

Delete a single search history entry.

**Endpoint:** `DELETE /search-history/{history_id}`

**Path Parameters:**
- `history_id` (required, integer): History entry ID

**Response:**
```json
{
  "message": "Search history deleted",
  "history_id": 3
}
```

**Status Codes:**
- `200`: Success
- `404`: History entry not found
- `500`: Internal server error

---

### Clear All Search History

Clear all search history.

**Endpoint:** `DELETE /search-history`

**Response:**
```json
{
  "message": "All search history cleared"
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

## Dashboard

### Get Dashboard Statistics

Get aggregated statistics for the dashboard.

**Endpoint:** `GET /dashboard/stats`

**Response:**
```json
{
  "total_sources": 8,
  "active_sources": 6,
  "total_articles": 2500,
  "recent_articles": 45,
  "avg_sentiment": 0.42,
  "last_crawl_time": "2024-01-14T11:30:00"
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

### Get Recent Articles

Get recent articles for dashboard.

**Endpoint:** `GET /dashboard/articles/recent`

**Query Parameters:**
- `limit` (optional, integer): Maximum results (default: 10, max: 50)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Latest News",
    "url": "https://example.com/article",
    "source": "Kompas",
    "sentiment": "neutral",
    "confidence": 0.88,
    "crawled_date": "2024-01-14T11:30:00",
    "keywords_flagged": "news"
  }
]
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

## Health Check

### Health Check

Check if the backend is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "message": "Media Analytics Backend is running"
}
```

**Status Codes:**
- `200`: Success

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid input
- `404`: Not Found - Resource doesn't exist
- `409`: Conflict - Duplicate entry or invalid state
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Backend error

---

## Authentication & Security

Currently, the API has **no authentication**. In production, implement:
- JWT token-based authentication
- API key validation
- Rate limiting

---

## Rate Limiting

Not currently implemented. Consider adding:
- Request throttling per IP
- User-based rate limits
- Crawler frequency limits

---

## Example Usage

### Using cURL

```bash
# Get articles
curl http://localhost:5000/v1/articles

# Add to favorites
curl -X POST http://localhost:5000/v1/favorites/1

# Save search
curl -X POST "http://localhost:5000/v1/search-history?keyword=lampung"

# Crawl custom URL
curl -X POST "http://localhost:5000/v1/crawler/crawl-url?url=https://example.com"
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:5000/v1"

# Get articles
response = requests.get(f"{BASE_URL}/articles", params={"q": "lampung"})
articles = response.json()

# Add favorite
response = requests.post(f"{BASE_URL}/favorites/1")

# Save search
response = requests.post(f"{BASE_URL}/search-history", params={"keyword": "news"})

# Get dashboard stats
response = requests.get(f"{BASE_URL}/dashboard/stats")
stats = response.json()
```

---

## API Versioning

The API uses URL-based versioning (`/v1`). Future versions will be available as `/v2`, etc.

---

## Contact & Support

For issues or questions about the API, refer to the project documentation in `/docs`.
