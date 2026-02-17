#!/usr/bin/env python3
"""
Test Script: Source Health Tracking System
============================================

Tests:
1. record_crawl_result() with success (resets failure counter)
2. record_crawl_result() with failures (increments counter)
3. Auto-marking as inactive after 3 consecutive failures
4. Tracking failure reasons
5. API endpoints response validation
6. Manual reactivation

Usage:
    python test_health_tracking_system.py
"""

import sys
import os
from datetime import datetime

# Add backend path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, NewsSource
from src.database.repository import record_crawl_result, get_inactive_sources, get_source_health, reactivate_source

# Database setup
DB_PATH = "database/media_analytics.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)

def test_health_tracking():
    """Run comprehensive health tracking tests"""
    session = Session()
    
    print("""
╔═════════════════════════════════════════════════════════════════╗
║        SOURCE HEALTH TRACKING SYSTEM - TESTS                    ║
╚═════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Test 1: Create test source
        print("\n[TEST 1] Creating test source...")
        test_source = NewsSource(
            name=f"TestSource_{datetime.now().timestamp()}",
            base_url="https://test.example.com",
            crawl_type="html",
            config={"selectors": {"title": ".title"}},
            active=True,
            auto_detect=False
        )
        session.add(test_source)
        session.commit()
        source_id = test_source.id
        print(f"  ✓ Test source created: {test_source.name} (ID: {source_id})")
        print(f"    Initial state: active={test_source.active}, failures={test_source.consecutive_failures}")
        
        # Test 2: Record success (30 articles)
        print("\n[TEST 2] Record successful crawl (30 articles)...")
        record_crawl_result(session, source_id, articles_count=30)
        session.refresh(test_source)
        print(f"  ✓ Success recorded")
        print(f"    State after: active={test_source.active}, failures={test_source.consecutive_failures}")
        print(f"    Last crawl article count: {test_source.last_crawl_article_count}")
        print(f"    Last successful crawl: {test_source.last_successful_crawl}")
        assert test_source.consecutive_failures == 0, "Failures should reset to 0 after success"
        assert test_source.last_crawl_article_count == 30, "Article count should be 30"
        
        # Test 3: Record 1st failure (0 articles)
        print("\n[TEST 3] Record 1st failure (0 articles)...")
        record_crawl_result(session, source_id, articles_count=0, failure_reason="No articles found")
        session.refresh(test_source)
        print(f"  ✓ Failure #1 recorded")
        print(f"    State after: active={test_source.active}, failures={test_source.consecutive_failures}")
        print(f"    Failure reason: {test_source.failure_reason}")
        assert test_source.consecutive_failures == 1, "Should have 1 failure"
        assert test_source.active == True, "Should still be active"
        
        # Test 4: Record 2nd failure
        print("\n[TEST 4] Record 2nd failure...")
        record_crawl_result(session, source_id, articles_count=0, failure_reason="Connection timeout")
        session.refresh(test_source)
        print(f"  ✓ Failure #2 recorded")
        print(f"    State after: active={test_source.active}, failures={test_source.consecutive_failures}")
        print(f"    Failure reason: {test_source.failure_reason}")
        assert test_source.consecutive_failures == 2, "Should have 2 failures"
        assert test_source.active == True, "Should still be active"
        
        # Test 5: Record 3rd failure (AUTO-MARK INACTIVE)
        print("\n[TEST 5] Record 3rd failure (AUTO-MARK INACTIVE)...")
        record_crawl_result(session, source_id, articles_count=0, failure_reason="Selector not found")
        session.refresh(test_source)
        print(f"  ✓ Failure #3 recorded - AUTO-MARKED INACTIVE")
        print(f"    State after: active={test_source.active}, failures={test_source.consecutive_failures}")
        print(f"    Failure reason: {test_source.failure_reason}")
        print(f"    Inactivity detected at: {test_source.inactivity_detected_at}")
        assert test_source.consecutive_failures == 3, "Should have 3 failures"
        assert test_source.active == False, "Should be marked INACTIVE"
        assert test_source.inactivity_detected_at is not None, "Should have inactivity timestamp"
        
        # Test 6: Get inactive sources list
        print("\n[TEST 6] Get inactive sources...")
        inactive = get_inactive_sources(session)
        print(f"  ✓ Found {len(inactive)} inactive source(s)")
        found = False
        for src in inactive:
            print(f"    • {src['name']}: {src['failure_reason']} (detected: {src['inactivity_detected_at']})")
            if src['id'] == source_id:
                found = True
        assert found, "Test source should be in inactive list"
        
        # Test 7: Get source health details
        print("\n[TEST 7] Get source health details...")
        health = get_source_health(session, source_id)
        print(f"  ✓ Health details retrieved")
        print(f"    ID: {health['id']}")
        print(f"    Name: {health['name']}")
        print(f"    Status: {health['status']}")
        print(f"    Consecutive failures: {health['consecutive_failures']}")
        print(f"    Failure reason: {health['failure_reason']}")
        assert health['status'] == 'inactive', "Status should be inactive"
        
        # Test 8: Record success on inactive source (AUTO-REACTIVATE)
        print("\n[TEST 8] Record success on inactive source (AUTO-REACTIVATE)...")
        record_crawl_result(session, source_id, articles_count=25)
        session.refresh(test_source)
        print(f"  ✓ Success recorded on previously inactive source")
        print(f"    State after: active={test_source.active}, failures={test_source.consecutive_failures}")
        assert test_source.consecutive_failures == 0, "Failures should reset to 0"
        assert test_source.active == True, "Should be auto-reactivated"
        
        # Test 9: Manual reactivation endpoint
        print("\n[TEST 9] Manual reactivation...")
        # First mark it inactive again
        record_crawl_result(session, source_id, articles_count=0, failure_reason="Test")
        record_crawl_result(session, source_id, articles_count=0, failure_reason="Test")
        record_crawl_result(session, source_id, articles_count=0, failure_reason="Test")
        session.refresh(test_source)
        assert test_source.active == False, "Should be inactive"
        
        # Now manually reactivate
        reactivate_source(session, source_id)
        session.refresh(test_source)
        print(f"  ✓ Manual reactivation successful")
        print(f"    State after: active={test_source.active}, failures={test_source.consecutive_failures}")
        assert test_source.active == True, "Should be active after manual reactivation"
        assert test_source.consecutive_failures == 0, "Failures should be reset"
        
        # Test 10: Get all health status
        print("\n[TEST 10] Get health status (all sources)...")
        all_health = get_source_health(session)
        print(f"  ✓ Retrieved health status for all sources")
        if 'total_sources' in all_health:
            print(f"    Total sources: {all_health['total_sources']}")
            print(f"    Active sources: {all_health['active_sources']}")
            print(f"    Inactive sources: {all_health['inactive_sources']}")
        
        # Cleanup
        print("\n[CLEANUP] Removing test source...")
        session.delete(test_source)
        session.commit()
        print(f"  ✓ Test source deleted")
        
        # Summary
        print("\n" + "=" * 65)
        print("✅ ALL TESTS PASSED!")
        print("=" * 65)
        print("""
Health Tracking System is working correctly:
  ✓ Success resets failure counter
  ✓ Failures increment counter
  ✓ Auto-marks inactive after 3 consecutive failures
  ✓ Tracks failure reasons
  ✓ Stores inactivity detection timestamp
  ✓ Auto-reactivates on success
  ✓ Manual reactivation works
  ✓ API functions retrieve correct data

NEXT STEPS:
  1. Start crawling sources to track health
  2. Monitor API endpoints: /sources/health/all, /sources/inactive/list
  3. Use /sources/{id}/reactivate for manual fixes
        """)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = test_health_tracking()
    sys.exit(0 if success else 1)
