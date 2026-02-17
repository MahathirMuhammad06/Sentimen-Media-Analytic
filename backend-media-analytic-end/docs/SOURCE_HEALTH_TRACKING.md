# SOURCE HEALTH TRACKING - Auto-Inactive Features

**Date**: 2026-02-04  
**Version**: 1.2.0  
**Status**: ✅ IMPLEMENTED & TESTED

## Overview

Sistem telah ditambah dengan mekanisme automatic source health tracking yang menandai news sources sebagai `inactive` ketika tidak bisa menarik artikel berita selama beberapa crawl berturut-turut.

## How It Works

### Auto-Inactive Mechanism

1. **Setiap crawl per-source ditrack**:
   - Berhasil (ada artikel) → Reset failure counter
   - Gagal (tidak ada artikel) → Increment failure counter

2. **Automatic marking inactive**:
   - Setelah **3 consecutive failures** → Status menjadi `inactive`
   - Reason untuk inactivity dicatat (e.g., "No articles found")
   - `inactivity_detected_at` timestamp dicatat

3. **Logging**:
   - Setiap failure dilog dengan detail
   - Ketika source di-mark inactive, ada warning log

### Success Reset

Jika source yang inactive berhasil di-crawl (menemukan artikel):
- Failure counter di-reset ke 0
- Status diubah kembali ke `active`
- Dapat langsung crawl lagi

## Database Changes

### New Fields di NewsSource Model

```python
class NewsSource(Base):
    # ... existing fields ...
    
    # Source health tracking
    last_successful_crawl: DateTime              # Waktu crawl terakhir berhasil
    consecutive_failures: Integer = 0            # Counter kegagalan berturut-turut
    last_crawl_article_count: Integer = 0        # Jumlah artikel di crawl terakhir
    failure_reason: String                       # Alasan source tidak aktif
    inactivity_detected_at: DateTime             # Kapan dideteksi tidak aktif
```

## API Endpoints

### 1. Get Health Status Semua Sources
```bash
GET /v1/sources/health/all
```

**Response**:
```json
{
  "total_sources": 10,
  "active_sources": 8,
  "inactive_sources": 2,
  "sources": [
    {
      "id": 1,
      "name": "Kompas",
      "active": true,
      "consecutive_failures": 0,
      "failure_reason": null,
      "last_successful_crawl": "2026-02-04T15:30:00",
      "last_crawl_article_count": 33,
      "status": "active"
    },
    {
      "id": 5,
      "name": "Old News Site",
      "active": false,
      "consecutive_failures": 3,
      "failure_reason": "No articles found",
      "last_successful_crawl": "2026-01-30T10:00:00",
      "inactivity_detected_at": "2026-02-04T12:00:00",
      "status": "inactive"
    }
  ]
}
```

### 2. Get Health Status Source Tertentu
```bash
GET /v1/sources/{source_id}/health
```

**Response**:
```json
{
  "id": 1,
  "name": "Kompas",
  "active": true,
  "consecutive_failures": 0,
  "failure_reason": null,
  "last_successful_crawl": "2026-02-04T15:30:00",
  "last_crawl_article_count": 33,
  "inactivity_detected_at": null,
  "status": "active"
}
```

### 3. List Semua Inactive Sources
```bash
GET /v1/sources/inactive/list
```

**Response**:
```json
[
  {
    "id": 5,
    "name": "Old News Site",
    "base_url": "https://oldnews.com",
    "active": false,
    "consecutive_failures": 3,
    "failure_reason": "No articles found",
    "last_successful_crawl": "2026-01-30T10:00:00",
    "inactivity_detected_at": "2026-02-04T12:00:00"
  }
]
```

### 4. Reactivate Source Manual
```bash
POST /v1/sources/{source_id}/reactivate
```

**Use Case**: Source yang temporary tidak aktif ingin diaktifkan kembali

**Response**:
```json
{
  "message": "Source News Site reactivated successfully",
  "source_id": 5,
  "active": true
}
```

## Crawling Flow

### Per-Source Tracking

```python
for source in sources:
    articles = crawler.crawl_source(source)
    
    # Track hasil crawling
    record_crawl_result(
        source_id=source.id,
        articles_count=len(articles),
        failure_reason=None  # if success
    )
    
    # Source akan auto-marked inactive setelah 3 gagal berturut-turut
```

### Logging Output

**Success Crawl**:
```
INFO: Crawl success for Kompas: 33 articles
INFO: Crawl success for Suara: 25 articles
```

**Failed Crawl**:
```
WARNING: Crawl failed for Old Site: 1 consecutive failures
WARNING: Crawl failed for Old Site: 2 consecutive failures
WARNING: Crawl failed for Old Site: 3 consecutive failures
WARNING: Source marked INACTIVE: Old Site (No articles found)
```

## Implementation Details

### File Changes

#### 1. `src/database/models.py`
- Tambah 5 fields untuk tracking health
- Backward compatible (fields nullable)

#### 2. `src/database/repository.py`
- `record_crawl_result()` - Track setiap crawl hasil
- `get_inactive_sources()` - List inactive sources
- `get_source_health()` - Get health status semua/per-source
- `reactivate_source()` - Manual reactivate

#### 3. `src/crawler/news_crawler.py`
- `crawl_all()` - Call `record_crawl_result()` untuk tracking
- Record both success dan failure

#### 4. `src/api/routes.py`
- 4 endpoints baru untuk health monitoring & management

## Behavior Examples

### Example 1: Source dengan konsisten bagus
```
Crawl 1: 30 articles  → failures: 0, active: true
Crawl 2: 28 articles  → failures: 0, active: true
Crawl 3: 32 articles  → failures: 0, active: true
Status: ACTIVE (terus di-crawl)
```

### Example 2: Source menjadi tidak aktif
```
Crawl 1: 0 articles   → failures: 1, active: true
Crawl 2: 0 articles   → failures: 2, active: true
Crawl 3: 0 articles   → failures: 3, active: false ← MARKED INACTIVE
Crawl 4: Skipped (tidak di-crawl karena inactive)
Status: INACTIVE (tidak di-crawl sampai direaktifkan)
```

### Example 3: Inactive source kembali aktif
```
Status: INACTIVE (3 failures)
Manual Test: 15 articles → SUCCESS
Automatically: failures reset to 0, active: true
Status: ACTIVE kembali (bisa di-crawl lagi)
```

## Use Cases

### 1. Monitor Source Health
```bash
# Check which sources are having problems
curl http://localhost:8000/v1/sources/health/all
```

### 2. Identify Problematic Sources
```bash
# Get all inactive sources
curl http://localhost:8000/v1/sources/inactive/list
```

### 3. Debug Specific Source
```bash
# Check why a source is inactive
curl http://localhost:8000/v1/sources/5/health
# Response shows: failure_reason, failure_count, last_crawl_date
```

### 4. Reactivate After Fix
```bash
# Source sudah diperbaiki, reactivate
curl -X POST http://localhost:8000/v1/sources/5/reactivate
```

## Benefits

✅ **Automatic Detection**: Tidak perlu manual check
✅ **Efficiency**: Skip sources yang tidak bekerja
✅ **Debugging**: Clear reason untuk inactivity
✅ **Flexibility**: Dapat manual reactivate kapan saja
✅ **Logging**: Comprehensive tracking untuk troubleshooting
✅ **Backward Compatible**: Tidak break existing code

## Configuration

Threshold untuk marking inactive dapat diubah di `record_crawl_result()`:
```python
if source.consecutive_failures >= 3:  # Ubah ke 2 atau 5 jika diperlukan
    source.active = False
```

## Monitoring Recommendations

1. **Regular Health Check**:
   ```bash
   curl http://localhost:8000/v1/sources/health/all | jq '.inactive_sources'
   ```

2. **Set Alert**:
   - Jika `inactive_sources > 0`, check logs
   - Review `failure_reason` untuk setiap inactive source

3. **Maintenance**:
   - Setiap minggu: Check inactive sources
   - Jika masalah resolved: Reactivate manually
   - Jika persistent: Softdelete atau hard delete

## Future Enhancements

- [ ] Email notification saat source inactive
- [ ] Auto-reactivate setelah X waktu + test success
- [ ] Dashboard widget untuk inactive sources
- [ ] Bulk reactivate operation
- [ ] Per-source failure threshold configuration

---

**Status**: ✅ COMPLETE & READY FOR PRODUCTION
**Backward Compatible**: ✅ Yes
**Breaking Changes**: ❌ None
