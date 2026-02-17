# Panduan Menambahkan News Sources Baru

## Ringkasan Perbaikan

Sistem telah diperbaiki untuk mendukung penambahan news sources baru dengan auto-detection otomatis dan error handling yang lebih baik.

## Fitur Baru

### 1. Auto-Detection Otomatis
Ketika menambahkan source baru, sistem akan **otomatis mendeteksi**:
- Apakah situs memiliki feed RSS
- Apakah situs memiliki sitemap
- Fallback ke HTML crawling jika tidak ada RSS/sitemap

### 2. Validasi Config
Sistem sekarang **memvalidasi config** sebelum menyimpan:
- Untuk RSS: memastikan `rss_url` ada (auto-detect jika tidak ada)
- Untuk HTML: memastikan `index_url` dan `base_url` ada
- Normalisasi URL (tambah https:// jika tidak ada)

### 3. Better Error Handling
- Log terperinci untuk setiap langkah
- Pesan error yang informatif
- Fallback otomatis jika gagal

## Cara Menambahkan News Source Baru

### Metode 1: Melalui API (Otomatis)

```bash
POST /v1/sources
Content-Type: application/json

{
  "name": "Nama Situs Berita",
  "base_url": "https://example.com",
  "crawl_type": "auto",
  "config": {},
  "active": true,
  "auto_detect": true
}
```

**Respon:**
```json
{
  "id": 1,
  "name": "Nama Situs Berita",
  "base_url": "https://example.com",
  "crawl_type": "rss",  // atau html atau sitemap
  "config": {
    "rss_url": "https://example.com/rss",
    "base_url": "https://example.com"
  },
  "active": true,
  "created_at": "2024-02-04T10:00:00",
  "message": "Source created with rss crawler"
}
```

### Metode 2: Melalui API (Manual - RSS)

```bash
POST /v1/sources

{
  "name": "Radar Banten",
  "base_url": "https://radarbanten.id",
  "crawl_type": "rss",
  "config": {
    "rss_url": "https://radarbanten.id/rss"
  },
  "active": true,
  "auto_detect": false
}
```

### Metode 3: Melalui API (Manual - HTML)

```bash
POST /v1/sources

{
  "name": "Situs Berita Lokal",
  "base_url": "https://lokalnews.com",
  "crawl_type": "html",
  "config": {
    "index_url": "https://lokalnews.com/news",
    "link_selector": "a.article-link",
    "filters": {
      "href_contains": "/article/"
    }
  },
  "active": true,
  "auto_detect": false
}
```

## Testing Source Baru

Setelah menambahkan source, test dengan:

```bash
POST /v1/sources/{source_id}/test-crawl
```

**Respon:**
```json
{
  "message": "Crawl test completed for Nama Situs Berita",
  "source_id": 1,
  "source_name": "Nama Situs Berita",
  "crawl_type": "rss",
  "config": {...},
  "articles_found": 15,
  "sample_articles": [
    {
      "title": "Judul Berita",
      "url": "https://example.com/article/...",
      "source": "Nama Situs Berita",
      "sentiment": "positive",
      "confidence": 0.85
    }
  ],
  "status": "success"
}
```

## Auto-Crawling dengan Source Baru

Source baru akan otomatis di-crawl ketika:

1. **Manual crawl** dipicu:
```bash
POST /v1/crawler/manual-crawl
```

2. **Auto-crawl** berjalan (jika diaktifkan):
```bash
POST /v1/crawler/auto-crawl/start
```

3. **Per-source crawl**:
```bash
POST /v1/crawler/crawl-url?url=https://example.com
```

## Troubleshooting

### Source tidak menemukan artikel

**Kemungkinan penyebab:**
1. URL salah atau situs tidak accessible
2. Config selector CSS tidak sesuai dengan struktur HTML
3. Artikel terlalu pendek (minimum 200 karakter)
4. Artikel terfilter (navigation links, social media, dll)

**Solusi:**
1. Cek log untuk error message:
```bash
# Lihat log
tail -f app.log | grep "source_name"
```

2. Update config dengan selector yang benar:
```bash
PUT /v1/sources/{source_id}

{
  "config": {
    "link_selector": "a.article-title",
    "title_selector": "h2.title",
    "content_selector": "article.content"
  }
}
```

3. Test ulang crawling

### Kesalahan "Auto-detection failed"

Sistem akan fallback ke HTML crawling. Jika tidak ada artikel:
- Cek apakah situs memiliki RSS feed
- Jika ada, update manual: `"crawl_type": "rss"` dan sertakan `"rss_url"`
- Jika tidak ada, provide selector CSS yang akurat

## Config Parameter Lengkap

### Untuk RSS
```json
{
  "rss_url": "https://example.com/rss",
  "base_url": "https://example.com",
  "headers": {
    "User-Agent": "Mozilla/5.0..."
  }
}
```

### Untuk HTML
```json
{
  "index_url": "https://example.com/news",
  "base_url": "https://example.com",
  "link_selector": "a[href]",
  "title_selector": "h2.title",
  "content_selector": "article.content",
  "filters": {
    "href_contains": "/article/",
    "text_contains": "berita"
  },
  "headers": {
    "User-Agent": "Mozilla/5.0..."
  }
}
```

## Monitoring

Cek status auto-crawling:
```bash
GET /v1/crawler/auto-crawl/status
```

Cek dashboard:
```bash
GET /v1/dashboard/stats
```

## Best Practices

1. **Gunakan auto-detect dulu**: Biarkan sistem mendeteksi tipe crawling
2. **Test sebelum go live**: Gunakan endpoint `/test-crawl` 
3. **Monitor log**: Perhatikan warning dan error messages
4. **Update config jika perlu**: Sesuaikan selector CSS untuk hasil optimal
5. **Cleanup periodically**: Hapus source yang tidak aktif atau tidak berhasil

---

Untuk bantuan lebih lanjut, lihat:
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Master Documentation](docs/MASTER_DOCUMENTATION.md)
- [Crawling Strategy](docs/CRAWLING_STRATEGY.md)
