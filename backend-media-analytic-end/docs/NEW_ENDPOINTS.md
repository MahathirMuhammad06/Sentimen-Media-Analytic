# New Endpoints Documentation

## Overview
Tiga endpoint baru telah ditambahkan untuk monitoring crawler status dan source management:

### 1. GET `/v1/crawler/last-crawl-status`
**Purpose**: Mendapatkan status dan informasi crawl terakhir

**Response**:
```json
{
  "last_crawl_time": "2026-02-03T14:00:59.156112",
  "articles_in_last_crawl": 120,
  "status": "success"
}
```

**Details**:
- `last_crawl_time`: ISO format timestamp dari crawl terakhir
- `articles_in_last_crawl`: Jumlah artikel yang dikumpulkan dalam window 30 menit sekitar waktu crawl
- `status`: "success", "no_crawl_history", atau "error"

---

### 2. GET `/v1/crawler/sources-summary`
**Purpose**: Mendapatkan ringkasan sumber berita (total dan active)

**Response**:
```json
{
  "total_sources": 6,
  "active_sources": 6,
  "inactive_sources": 0
}
```

**Details**:
- `total_sources`: Total semua sumber (active + inactive)
- `active_sources`: Sumber yang aktif dan belum di-delete
- `inactive_sources`: Sumber yang non-active atau di-delete

---

## Implementation Details

### Repository Functions
Dua fungsi baru ditambahkan di `src/database/repository.py`:

1. **`get_last_crawl_status(session: Session) -> dict`**
   - Query artikel terakhir berdasarkan `crawled_date`
   - Menghitung jumlah artikel dalam window 30 menit
   - Return status dengan error handling

2. **`get_sources_summary(session: Session) -> dict`**
   - Count total sources dari database
   - Count active sources (filter by `active=True` dan `deleted_at=None`)
   - Return summary dengan error handling

### API Routes
Dua endpoint baru ditambahkan di `src/api/routes.py` (dalam section DASHBOARD API):

1. **`@router.get("/crawler/last-crawl-status")`**
   - Memanggil `get_last_crawl_status()` dengan dependency injection database
   - Error handling dengan HTTPException

2. **`@router.get("/crawler/sources-summary")`**
   - Memanggil `get_sources_summary()` dengan dependency injection database
   - Error handling dengan HTTPException

---

## Testing

Endpoints dapat ditest dengan curl:

```bash
# Test last crawl status
curl http://localhost:5000/v1/crawler/last-crawl-status

# Test sources summary
curl http://localhost:5000/v1/crawler/sources-summary
```

---

## Integration Notes

- Tidak ada perubahan pada existing endpoints
- Minimal changes ke codebase yang tidak berkaitan
- Menggunakan pattern yang sama dengan endpoint existing lainnya
- Database queries optimized dan lightweight
- Full error handling dan logging implemented
