# Hybrid Crawling System - README

## 🎯 Apa itu Hybrid Crawling System?

Sistem **Hybrid Crawling** menggabungkan dua mode crawling yang dapat digunakan secara bersamaan:

1. **Manual Crawling** - Dipicu oleh tombol/button di frontend
2. **Automatic Crawling** - Berjalan secara berkala di background

Sistem ini memungkinkan Anda untuk:
- ✅ Crawl artikel on-demand kapan saja
- ✅ Setup auto-crawl untuk update berkala
- ✅ Menjalankan kedua mode secara bersamaan tanpa conflict
- ✅ Mengontrol interval crawling secara dinamis
- ✅ Monitoring status crawling real-time

---

## 📦 Apa yang Telah Diimplementasikan?

### 1. Core Components

#### `src/crawler/hybrid_manager.py` (NEW)
Kelas utama yang mengelola hybrid crawling:
- Manual crawl trigger
- Auto crawl start/stop
- Status management
- Thread-safe operations
- Graceful shutdown

#### `src/api/crawler_routes.py` (NEW)
FastAPI routes untuk API endpoints:
- POST `/v1/crawler/manual-crawl`
- POST `/v1/crawler/auto-crawl/start`
- POST `/v1/crawler/auto-crawl/stop`
- GET `/v1/crawler/auto-crawl/status`
- PUT `/v1/crawler/auto-crawl/interval`
- GET `/v1/crawler/info`

#### `src/crawler/hybrid_config.py` (NEW)
Optional configuration untuk hybrid crawler

### 2. Integration

#### `src/api/app.py` (MODIFIED)
- Integrated crawler routes
- Initialize manager on startup
- Graceful shutdown on stop
- ✅ **NO BREAKING CHANGES**

### 3. Documentation (NEW)

#### `docs/HYBRID_CRAWLING_SYSTEM.md`
Dokumentasi lengkap sistem hybrid crawling

#### `docs/HYBRID_CRAWLING_API.md`
API reference dengan cURL examples

#### `docs/HYBRID_CRAWLING_QUICKSTART.md`
Quick start guide untuk pemula

#### `docs/HYBRID_CRAWLING_IMPLEMENTATION.md`
Implementation summary dengan checklist

### 4. Testing (NEW)

#### `tests/test_hybrid_crawling.py`
Comprehensive unit dan integration tests

---

## 🚀 Cara Memulai

### 1. Pastikan Dependencies Terinstall

```bash
pip install apscheduler
```

Atau update dari requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Start Server

```bash
python -m src.api.app
```

Server akan berjalan di `http://localhost:5000`

### 3. Test Manual Crawl

```bash
curl -X POST http://localhost:5000/v1/crawler/manual-crawl
```

### 4. Test Auto Crawl

```bash
# Start
curl -X POST http://localhost:5000/v1/crawler/auto-crawl/start

# Check status
curl http://localhost:5000/v1/crawler/auto-crawl/status

# Stop
curl -X POST http://localhost:5000/v1/crawler/auto-crawl/stop
```

---

## 🎮 API Endpoints

### Manual Crawl (Tombol/On-Demand)

```bash
POST /v1/crawler/manual-crawl

# Response:
{
  "status": "success",
  "message": "Manual crawl completed. Found 45 articles.",
  "articles_count": 45,
  "crawl_number": 1,
  "timestamp": "2024-01-19T10:30:00"
}
```

### Start Auto Crawling

```bash
POST /v1/crawler/auto-crawl/start

# Response:
{
  "status": "started",
  "message": "Auto crawling started successfully",
  "interval_seconds": 3600,
  "timestamp": "2024-01-19T10:30:00"
}
```

### Stop Auto Crawling

```bash
POST /v1/crawler/auto-crawl/stop

# Response:
{
  "status": "stopped",
  "message": "Auto crawling stopped successfully",
  "timestamp": "2024-01-19T10:30:00"
}
```

### Get Status

```bash
GET /v1/crawler/auto-crawl/status

# Response:
{
  "auto_running": true,
  "interval_seconds": 3600,
  "last_crawl_time": "2024-01-19T09:30:00",
  "total_crawls": 2,
  "scheduler_running": true,
  "timestamp": "2024-01-19T10:30:00"
}
```

### Update Interval

```bash
PUT /v1/crawler/auto-crawl/interval?interval_seconds=1800

# Response:
{
  "status": "success",
  "message": "Interval updated to 1800 seconds",
  "new_interval": 1800,
  "timestamp": "2024-01-19T10:30:00"
}
```

### Get Info

```bash
GET /v1/crawler/info

# Response:
{
  "configuration": {
    "default_interval": 3600,
    "max_articles_per_source": 100,
    "model_path": "./src/ml/model/model.safetensors"
  },
  "available_endpoints": [...]
}
```

---

## 🔌 Frontend Integration Example

### React Component

```javascript
import { useState } from 'react';

export function CrawlerControl() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  // Manual Crawl
  const handleManualCrawl = async () => {
    setLoading(true);
    try {
      const response = await fetch('/v1/crawler/manual-crawl', {
        method: 'POST'
      });
      const data = await response.json();
      alert(`Found ${data.articles_count} articles`);
      refreshStatus();
    } catch (error) {
      console.error('Crawl failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Start Auto Crawl
  const handleStartAuto = async () => {
    setLoading(true);
    try {
      const response = await fetch('/v1/crawler/auto-crawl/start', {
        method: 'POST'
      });
      const data = await response.json();
      console.log(`Auto crawling ${data.status}`);
      refreshStatus();
    } catch (error) {
      console.error('Failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Stop Auto Crawl
  const handleStopAuto = async () => {
    setLoading(true);
    try {
      const response = await fetch('/v1/crawler/auto-crawl/stop', {
        method: 'POST'
      });
      refreshStatus();
    } catch (error) {
      console.error('Failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get Status
  const refreshStatus = async () => {
    try {
      const response = await fetch('/v1/crawler/auto-crawl/status');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to get status:', error);
    }
  };

  return (
    <div className="crawler-control">
      <button onClick={handleManualCrawl} disabled={loading}>
        🔄 Crawl Now
      </button>

      <button 
        onClick={status?.auto_running ? handleStopAuto : handleStartAuto} 
        disabled={loading}
      >
        {status?.auto_running ? '⏹️ Stop Auto Crawl' : '▶️ Start Auto Crawl'}
      </button>

      <button onClick={refreshStatus} disabled={loading}>
        🔍 Refresh Status
      </button>

      {status && (
        <div className="status-info">
          <p>Auto Running: {status.auto_running ? 'Yes' : 'No'}</p>
          <p>Interval: {status.interval_seconds} seconds</p>
          <p>Total Crawls: {status.total_crawls}</p>
          <p>Last Crawl: {status.last_crawl_time || 'Never'}</p>
        </div>
      )}
    </div>
  );
}
```

---

## ⚙️ Konfigurasi

### Default Configuration

```python
# config.py
CRAWL_INTERVAL = 3600  # 1 hour
MAX_ARTICLES_PER_SOURCE = 100
```

### Runtime Update

```bash
# Change interval ke 30 menit
curl -X PUT "http://localhost:5000/v1/crawler/auto-crawl/interval?interval_seconds=1800"

# Change interval ke 2 jam
curl -X PUT "http://localhost:5000/v1/crawler/auto-crawl/interval?interval_seconds=7200"
```

### Interval Constraints

- **Minimum**: 60 seconds (1 minute)
- **Maximum**: 86400 seconds (24 hours)
- **Default**: 3600 seconds (1 hour)

---

## 📊 Workflow Hybrid System

### Manual Crawling Only

```
User clicks "Crawl Now"
    ↓
POST /v1/crawler/manual-crawl
    ↓
NewsCrawler.crawl_all()
    ↓
Save to Database
    ↓
Return response with article count
```

### Auto Crawling Only

```
User clicks "Start Auto"
    ↓
POST /v1/crawler/auto-crawl/start
    ↓
Background scheduler starts
    ↓
Every N seconds:
  - Run crawl
  - Save articles
  - Update statistics
```

### Hybrid Mode (Both)

```
Auto crawling running every hour
    ↓
User can click "Crawl Now" anytime
    ↓
Manual and auto crawls run concurrent
    ↓
No conflicts (thread-safe)
    ↓
Both save articles independently
```

---

## ✅ Kode Krusial yang Tidak Berubah

✅ **Semua kode berikut TIDAK DIUBAH**:

- `src/crawler/news_crawler.py` - Crawler logic tetap sama
- `src/crawler/scheduler.py` - Bisa tetap digunakan atau deprecated
- `src/api/routes.py` - Semua existing endpoints tetap berfungsi
- `src/database/repository.py` - Database operations tidak berubah
- `src/database/models.py` - Models tidak berubah
- `src/ml/sentiment_analyzer.py` - ML pipeline tidak berubah
- `config.py` - Configuration tetap compatible

**Hanya penambahan**, **tidak ada breaking changes** ✅

---

## 🧪 Testing

### Run Tests

```bash
cd tests
pytest test_hybrid_crawling.py -v
```

### Test Coverage

- ✅ Manual crawl execution
- ✅ Auto crawl start/stop
- ✅ Interval updates
- ✅ Status tracking
- ✅ Thread safety
- ✅ Concurrent operations
- ✅ Edge cases

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `docs/HYBRID_CRAWLING_SYSTEM.md` | Complete system documentation |
| `docs/HYBRID_CRAWLING_API.md` | API endpoint reference |
| `docs/HYBRID_CRAWLING_QUICKSTART.md` | Quick start guide |
| `docs/HYBRID_CRAWLING_IMPLEMENTATION.md` | Implementation summary |

---

## 🔧 Troubleshooting

### Auto crawling tidak jalan?

```bash
# Check status
curl http://localhost:5000/v1/crawler/auto-crawl/status

# Check apakah auto_running = true
# Jika false, start dengan:
curl -X POST http://localhost:5000/v1/crawler/auto-crawl/start
```

### Manual crawl timeout?

Pastikan sources masih valid:
```bash
curl http://localhost:5000/v1/sources
```

### Import error?

Pastikan `apscheduler` terinstall:
```bash
pip install apscheduler
```

---

## 💡 Tips & Best Practices

1. **Manual Crawling** - Gunakan untuk on-demand updates atau testing
2. **Auto Crawling** - Set interval sesuai kebutuhan (jangan terlalu pendek)
3. **Monitoring** - Regularly check status via API
4. **Error Handling** - Implement retry logic di frontend
5. **Logging** - Monitor logs untuk error messages

---

## 🎯 Key Features

✨ **Dual Mode Operation**
- Manual mode untuk on-demand updates
- Automatic mode untuk scheduled updates
- Keduanya berjalan concurrent tanpa conflict

✨ **Thread-Safe**
- Lock mechanism untuk prevent race conditions
- Safe concurrent operations
- Consistent data integrity

✨ **Flexible Configuration**
- Update interval at runtime
- No server restart required
- API-driven configuration

✨ **Production-Ready**
- Comprehensive error handling
- Detailed logging
- Graceful shutdown
- Full test coverage

✨ **Well-Documented**
- System architecture explained
- API reference complete
- Quick start guide included
- Example code provided

---

## 🚀 Next Steps

1. **Integrate Frontend**: Add buttons untuk manual crawl dan auto crawl control
2. **Setup Monitoring**: Monitor logs dan status
3. **Test Thoroughly**: Run test suite dan manual testing
4. **Production Deploy**: Deploy dengan confidence

---

## 📞 Questions?

Refer to:
1. `docs/HYBRID_CRAWLING_SYSTEM.md` - For detailed documentation
2. `docs/HYBRID_CRAWLING_API.md` - For API reference
3. `docs/HYBRID_CRAWLING_QUICKSTART.md` - For quick help
4. `tests/test_hybrid_crawling.py` - For usage examples

---

## ✅ Status

**Fully Implemented & Ready to Use** ✅

- [x] Core functionality
- [x] API endpoints
- [x] Integration
- [x] Documentation
- [x] Tests
- [x] No breaking changes
- [x] Production-ready

---

**Created**: January 19, 2024  
**Version**: 1.0.0  
**Status**: ✅ Active
