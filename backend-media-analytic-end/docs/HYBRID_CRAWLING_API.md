# Hybrid Crawler API Reference

## Base URL
```
http://localhost:5000
```

## Version
```
v1
```

## Content-Type
```
application/json
```

---

## Endpoints

### 1. Manual Crawl (Button/On-Demand)

**SINGLE ENDPOINT for manual crawling:**

#### Request
```http
POST /v1/crawler/manual-crawl HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

#### cURL Example
```bash
curl -X POST http://localhost:5000/v1/crawler/manual-crawl
```

#### Response (Success)
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "message": "Manual crawl completed. Found 45 articles.",
  "articles_count": 45,
  "crawl_number": 5,
  "timestamp": "2024-01-19T10:30:00.000000"
}
```

#### Response (Error)
```json
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "detail": "Manual crawl failed: Connection timeout"
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `success` atau `error` |
| `message` | string | Deskripsi operasi |
| `articles_count` | integer | Jumlah artikel yang ditemukan |
| `crawl_number` | integer | Nomor urut crawl |
| `timestamp` | string | ISO 8601 timestamp |

---

### 2. Start Auto Crawling

#### Request
```http
POST /v1/crawler/auto-crawl/start HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

#### cURL Example
```bash
curl -X POST http://localhost:5000/v1/crawler/auto-crawl/start
```

#### Response (Started)
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "started",
  "message": "Auto crawling started successfully",
  "interval_seconds": 3600,
  "timestamp": "2024-01-19T10:30:00.000000"
}
```

#### Response (Already Running)
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "already_running",
  "message": "Auto crawling is already running",
  "interval_seconds": 3600
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `started`, `already_running`, atau `error` |
| `message` | string | Deskripsi status |
| `interval_seconds` | integer | Interval crawling dalam detik |
| `timestamp` | string | ISO 8601 timestamp |

---

### 3. Stop Auto Crawling

#### Request
```http
POST /v1/crawler/auto-crawl/stop HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

#### cURL Example
```bash
curl -X POST http://localhost:5000/v1/crawler/auto-crawl/stop
```

#### Response (Stopped)
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "stopped",
  "message": "Auto crawling stopped successfully",
  "timestamp": "2024-01-19T10:30:00.000000"
}
```

#### Response (Not Running)
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "not_running",
  "message": "Auto crawling is not running"
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `stopped`, `not_running`, atau `error` |
| `message` | string | Deskripsi status |
| `timestamp` | string | ISO 8601 timestamp |

---

### 4. Get Auto Crawling Status

#### Request
```http
GET /v1/crawler/auto-crawl/status HTTP/1.1
Host: localhost:5000
```

#### cURL Example
```bash
curl http://localhost:5000/v1/crawler/auto-crawl/status
```

#### Response
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "auto_running": true,
  "interval_seconds": 3600,
  "last_crawl_time": "2024-01-19T09:30:00.000000",
  "total_crawls": 5,
  "scheduler_running": true,
  "timestamp": "2024-01-19T10:30:00.000000"
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `auto_running` | boolean | Apakah auto crawling sedang aktif |
| `interval_seconds` | integer | Interval crawling dalam detik |
| `last_crawl_time` | string | ISO 8601 timestamp crawl terakhir (null jika belum pernah) |
| `total_crawls` | integer | Total jumlah crawls yang dilakukan |
| `scheduler_running` | boolean | Apakah scheduler background sedang berjalan |
| `timestamp` | string | ISO 8601 timestamp saat query |

---

### 5. Update Crawl Interval

#### Request
```http
PUT /v1/crawler/auto-crawl/interval?interval_seconds=7200 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

#### Query Parameters
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `interval_seconds` | integer | Yes | 60 <= x <= 86400 | Interval baru dalam detik |

#### cURL Example
```bash
# 2 hours (7200 seconds)
curl -X PUT "http://localhost:5000/v1/crawler/auto-crawl/interval?interval_seconds=7200"

# 30 minutes (1800 seconds)
curl -X PUT "http://localhost:5000/v1/crawler/auto-crawl/interval?interval_seconds=1800"

# 1 hour (3600 seconds - default)
curl -X PUT "http://localhost:5000/v1/crawler/auto-crawl/interval?interval_seconds=3600"
```

#### Response (Success)
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "message": "Interval updated to 7200 seconds",
  "new_interval": 7200,
  "timestamp": "2024-01-19T10:30:00.000000"
}
```

#### Response (Invalid Interval)
```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "detail": "Interval must be at least 60 seconds"
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `success` atau `error` |
| `message` | string | Deskripsi operasi |
| `new_interval` | integer | Interval baru yang sudah diset |
| `timestamp` | string | ISO 8601 timestamp |

#### Recommended Intervals
| Use Case | Seconds | Minutes | Hours |
|----------|---------|---------|-------|
| Testing/Development | 60 | 1 | - |
| High Frequency | 300-600 | 5-10 | - |
| Standard | 1800-3600 | 30-60 | 0.5-1 |
| Low Frequency | 7200-14400 | 120-240 | 2-4 |
| Once Daily | 86400 | - | 24 |

---

### 6. Get Crawler Info

#### Request
```http
GET /v1/crawler/info HTTP/1.1
Host: localhost:5000
```

#### cURL Example
```bash
curl http://localhost:5000/v1/crawler/info
```

#### Response
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "configuration": {
    "default_interval": 3600,
    "max_articles_per_source": 100,
    "model_path": "./src/ml/model/model.safetensors"
  },
  "available_endpoints": [
    "POST /manual-crawl - Trigger manual crawl via button",
    "POST /auto-crawl/start - Start automatic crawling",
    "POST /auto-crawl/stop - Stop automatic crawling",
    "GET /auto-crawl/status - Get crawler status",
    "PUT /auto-crawl/interval - Update crawl interval"
  ]
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `configuration.default_interval` | integer | Default interval dalam detik |
| `configuration.max_articles_per_source` | integer | Max artikel per source per crawl |
| `configuration.model_path` | string | Path ke model sentiment analysis |
| `available_endpoints` | array | Daftar endpoint yang tersedia |

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid parameter"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 409 Conflict
```json
{
  "detail": "Operation cannot be performed - conflict detected"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Status Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Operasi berhasil |
| 400 | Bad Request | Parameter invalid |
| 404 | Not Found | Resource tidak ditemukan |
| 409 | Conflict | Konflik dengan state sekarang |
| 500 | Internal Server Error | Error di server |

---

## Common Use Cases

### Use Case 1: Manual Crawl On Demand
```bash
# User click "Crawl Now" button
curl -X POST http://localhost:5000/v1/crawler/manual-crawl
```

### Use Case 2: Setup Auto Crawling Every Hour
```bash
# Start auto crawling dengan default interval (1 hour)
curl -X POST http://localhost:5000/v1/crawler/auto-crawl/start

# Check status
curl http://localhost:5000/v1/crawler/auto-crawl/status
```

### Use Case 3: Change Crawl Frequency
```bash
# Change ke 30 minutes
curl -X PUT "http://localhost:5000/v1/crawler/auto-crawl/interval?interval_seconds=1800"

# Verify
curl http://localhost:5000/v1/crawler/auto-crawl/status
```

### Use Case 4: Pause and Resume
```bash
# Pause auto crawling
curl -X POST http://localhost:5000/v1/crawler/auto-crawl/stop

# Resume auto crawling
curl -X POST http://localhost:5000/v1/crawler/auto-crawl/start
```

### Use Case 5: Get Full Configuration
```bash
curl http://localhost:5000/v1/crawler/info
```

---

## Request/Response Examples

### Example 1: Complete Manual Crawl Flow
```bash
# 1. Trigger manual crawl
curl -X POST http://localhost:5000/v1/crawler/manual-crawl

# Response:
{
  "status": "success",
  "message": "Manual crawl completed. Found 45 articles.",
  "articles_count": 45,
  "crawl_number": 1,
  "timestamp": "2024-01-19T10:30:00.000000"
}

# 2. Get all articles
curl http://localhost:5000/v1/articles
```

### Example 2: Complete Auto Crawl Flow
```bash
# 1. Start auto crawling
curl -X POST http://localhost:5000/v1/crawler/auto-crawl/start

# Response:
{
  "status": "started",
  "message": "Auto crawling started successfully",
  "interval_seconds": 3600,
  "timestamp": "2024-01-19T10:30:00.000000"
}

# 2. Check status after some time
curl http://localhost:5000/v1/crawler/auto-crawl/status

# Response:
{
  "auto_running": true,
  "interval_seconds": 3600,
  "last_crawl_time": "2024-01-19T10:30:00.000000",
  "total_crawls": 2,
  "scheduler_running": true,
  "timestamp": "2024-01-19T11:35:00.000000"
}

# 3. Stop auto crawling
curl -X POST http://localhost:5000/v1/crawler/auto-crawl/stop

# Response:
{
  "status": "stopped",
  "message": "Auto crawling stopped successfully",
  "timestamp": "2024-01-19T11:35:00.000000"
}
```

---

## Authentication

Saat ini API tidak memerlukan authentication. Dalam production, tambahkan:
- API Key authentication
- JWT tokens
- OAuth2

---

## Rate Limiting

Tidak ada rate limiting saat ini. Untuk production, pertimbangkan:
- Limit manual crawls per user
- Limit API calls
- Implement sliding window rate limiting

---

## CORS

CORS saat ini enabled untuk semua origins (`*`). Untuk production:
- Specify allowed origins
- Restrict methods
- Manage credentials

---

## Headers

### Request Headers
```
Content-Type: application/json
```

### Response Headers
```
Content-Type: application/json
X-Process-Time: 0.123 (optional)
```

---

## Changelog

### v1.0.0 (2024-01-19)
- Initial hybrid crawling API
- Manual crawl endpoint
- Auto crawl start/stop
- Status and interval management
