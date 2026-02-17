# SOURCE HEALTH TRACKING - QUICK REFERENCE GUIDE

**TL;DR**: System automatically marks news sources as inactive when they fail to extract articles 3 times in a row.

---

## What Changed?

### Database (5 new columns)
```
news_sources table now has:
✓ last_successful_crawl         (when articles were last found)
✓ consecutive_failures          (counter: 0-3, resets on success)
✓ last_crawl_article_count      (how many articles last time)
✓ failure_reason                (why it's not working)
✓ inactivity_detected_at        (when marked inactive)
```

### Behavior
- **On Success** (articles found): Failure counter resets to 0 ✓
- **On Failure** (0 articles): Failure counter increments +1
- **After 3 Failures**: Source auto-marked `inactive` ❌
- **Inactive Sources**: Not crawled until manually reactivated

### Code Integration
```python
# When crawling sources:
record_crawl_result(
    session_id, 
    articles_count,      # 0 = failure, >0 = success
    failure_reason       # e.g., "No articles found"
)
```

---

## API Quick Start

### 1. Check All Sources Health
```bash
curl http://localhost:8000/v1/sources/health/all
```

Response shows: total/active/inactive counts + each source's status

### 2. Check Specific Source
```bash
curl http://localhost:8000/v1/sources/{id}/health
```

Shows: status, failure count, last successful crawl, etc.

### 3. List Inactive Sources
```bash
curl http://localhost:8000/v1/sources/inactive/list
```

Shows: all inactive sources with failure reasons (why they're not working)

### 4. Reactivate a Source
```bash
curl -X POST http://localhost:8000/v1/sources/{id}/reactivate
```

Resets counter to 0, marks as active again (you must fix the underlying issue first!)

---

## Examples

### Example 1: Healthy Source
```
Source: "Kompas"
Status: active
Failures: 0
Last crawl: 2026-02-04 09:00:00 (33 articles)
Action: Keep crawling ✓
```

### Example 2: Temporary Failure
```
Source: "Old News"
Status: active (still trying)
Failures: 2/3
Last reason: "Selector not found"
Action: Will auto-mark inactive on next failure
```

### Example 3: Inactive Source
```
Source: "Broken Site"
Status: inactive
Failures: 3
Reason: "Connection timeout"
Detected: 2026-02-04 08:00:00
Last success: 2026-01-30 10:00:00
Action: Fix site, then POST /sources/5/reactivate
```

---

## Common Tasks

### Monitor Source Health (Dashboard)
```bash
# Run this daily
curl http://localhost:8000/v1/sources/health/all \
  | jq '.sources[] | select(.active == false)'
```

### Find Why a Source Failed
```bash
curl http://localhost:8000/v1/sources/5/health \
  | jq '.failure_reason'
# Output: "No articles found", "Selector mismatch", etc.
```

### Reactivate All Inactive Sources
```bash
# Get list
curl http://localhost:8000/v1/sources/inactive/list \
  | jq '.[].id' \
  | xargs -I {} curl -X POST http://localhost:8000/v1/sources/{}/reactivate
```

### Test Source Configuration
```bash
# Manually run crawler for one source
# Then check if articles were extracted
curl http://localhost:8000/v1/sources/{id}/health
# If last_crawl_article_count > 0, it's working!
```

---

## Automatic Behavior

### Success Flow
```
crawl_source() → 30 articles found
                    ↓
          record_crawl_result()
                    ↓
        failures = 0 ✓
        last_successful_crawl = now
        active = true
```

### Failure Flow (First 2 Attempts)
```
crawl_source() → 0 articles found
                    ↓
          record_crawl_result()
                    ↓
        failures + 1
        failure_reason = "No articles found"
        active = true (still trying!)
```

### Auto-Inactive (3rd Failure)
```
crawl_source() → 0 articles found
                    ↓
          record_crawl_result()
                    ↓
        failures = 3
        active = false ❌ (MARKED INACTIVE)
        inactivity_detected_at = now
        ⚠️  Log: "Source marked INACTIVE"
                    ↓
      Next crawl: SKIP (won't even try)
```

### Recovery (Reactivation)
```
Manual reactivate via API
            ↓
failures = 0 ✓
active = true
inactivity_detected_at = NULL
            ↓
Next crawl: RESUME
```

---

## Files Changed

```
Modified:
  ✓ src/database/models.py       (+8 lines: 5 new fields)
  ✓ src/database/repository.py   (+140 lines: 4 functions)
  ✓ src/crawler/news_crawler.py  (+8 lines: call record_crawl_result)
  ✓ src/api/routes.py            (+60 lines: 4 endpoints)

Created:
  ✓ migrate_add_source_health_tracking.py (migration script)
  ✓ test_health_tracking_system.py (test suite - 10/10 passed ✅)
  ✓ SOURCE_HEALTH_TRACKING.md (detailed docs)
  ✓ IMPLEMENTATION_COMPLETE.md (full report)
```

---

## Before/After

### Before (No Health Tracking)
- ❌ Don't know which sources are broken
- ❌ Keep crawling broken sources (waste resources)
- ❌ No record of failures
- ❌ Manual inspection needed

### After (With Health Tracking)
- ✅ Automatically detect broken sources
- ✅ Skip broken sources (save resources)
- ✅ Full failure history & reasons
- ✅ API to check & fix sources

---

## Key Numbers

- **Failure Threshold**: 3 consecutive failures = inactive
- **Reset Trigger**: 1 successful crawl = counter resets
- **Auto-Reactivate**: YES, when success after being inactive
- **Manual Reactivate**: YES, via POST /sources/{id}/reactivate
- **Backward Compatible**: YES, no breaking changes

---

## Testing Status

```
✅ Migration:        5/5 columns added successfully
✅ Unit Tests:       10/10 test cases passed
✅ Integration:      With existing crawler code
✅ API Endpoints:    4 endpoints working
✅ Logging:          All events logged properly
✅ Backward Compat:  No breaking changes
```

---

## Deployment

1. **Run Migration**:
   ```bash
   python migrate_add_source_health_tracking.py
   ```

2. **Run Tests** (optional):
   ```bash
   python test_health_tracking_system.py
   ```

3. **Start Using**:
   - Crawler auto-uses health tracking
   - Check endpoints for status
   - Monitor logs for inactivity messages

---

## Support

- **Full Docs**: See `SOURCE_HEALTH_TRACKING.md`
- **Implementation Details**: See `IMPLEMENTATION_COMPLETE.md`
- **Test Results**: Run `test_health_tracking_system.py`
- **Quick Troubleshoot**: Section below

---

## Quick Troubleshoot

### Q: Source marked inactive but it's working now
**A**: Run `/sources/{id}/reactivate` to reset

### Q: How do I prevent auto-inactivity?
**A**: Keep failing → keep trying (default: 3 failures threshold)

### Q: Can I manually mark inactive?
**A**: Yes, set `active = false` in database directly

### Q: Do I lose articles if source goes inactive?
**A**: No! All past articles stay in database. Only future crawls are skipped.

### Q: How do I know why a source failed?
**A**: Check `failure_reason` field via health API

---

**Status**: ✅ READY TO USE  
**Version**: 1.2.0  
**Date**: 2026-02-04
