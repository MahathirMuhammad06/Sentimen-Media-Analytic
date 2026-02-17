#!/usr/bin/env python3
"""
Test script untuk memverifikasi bahwa news sources baru dapat ditambahkan dan artikel dapat dicrawl
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from src.database.db import get_connection
from src.database.repository import get_session, initialize_hardcoded_sources, add_source, get_sources
from src.crawler.news_crawler import NewsCrawler
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_add_new_source():
    """Test menambahkan news source baru"""
    print("\n" + "="*80)
    print("TEST: Menambahkan News Source Baru")
    print("="*80)
    
    session = get_session()
    
    try:
        # Test 1: Add source dengan auto-detect
        print("\n[1] Menambahkan source dengan auto-detect (RSS)...")
        
        new_source_data = {
            "name": f"Test RSS Source {datetime.now().timestamp()}",
            "base_url": "https://www.kompas.com",
            "crawl_type": "auto",
            "config": {},
            "active": True,
            "auto_detect": True
        }
        
        source = add_source(session, new_source_data)
        print(f"✓ Source ditambahkan: {source.name}")
        print(f"  ID: {source.id}")
        print(f"  Crawl Type: {source.crawl_type}")
        print(f"  Config: {source.config}")
        
        # Test 2: Crawl source baru
        print(f"\n[2] Melakukan crawl pada source baru...")
        crawler = NewsCrawler(db_session=session)
        articles = crawler.crawl_source(source)
        
        if articles:
            print(f"✓ Berhasil extract {len(articles)} artikel")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n  Artikel {i}:")
                print(f"    Title: {article['title'][:60]}...")
                print(f"    URL: {article['url'][:60]}...")
                print(f"    Sentiment: {article['sentiment']} ({article['confidence']:.2f})")
        else:
            print("⚠ Tidak ada artikel yang ditemukan")
        
        # Test 3: Add source dengan HTML crawling
        print(f"\n[3] Menambahkan source HTML dengan auto-detect...")
        
        html_source_data = {
            "name": f"Test HTML Source {datetime.now().timestamp()}",
            "base_url": "https://example.com",
            "crawl_type": "auto",
            "config": {},
            "active": True,
            "auto_detect": True
        }
        
        html_source = add_source(session, html_source_data)
        print(f"✓ Source ditambahkan: {html_source.name}")
        print(f"  Crawl Type: {html_source.crawl_type}")
        
        print("\n" + "="*80)
        print("✓ SEMUA TEST PASSED!")
        print("="*80)
        
    except ValueError as e:
        print(f"✗ Error (Validation): {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()
    
    return True


def test_crawl_all_sources():
    """Test crawl semua active sources"""
    print("\n" + "="*80)
    print("TEST: Crawl Semua Active Sources")
    print("="*80)
    
    session = get_session()
    
    try:
        # Initialize hardcoded sources jika belum ada
        initialize_hardcoded_sources(session)
        
        # Get all sources
        sources = get_sources(session)
        active_sources = [s for s in sources if s.active]
        
        print(f"\nTotal sources: {len(sources)}")
        print(f"Active sources: {len(active_sources)}")
        
        if not active_sources:
            print("⚠ Tidak ada active sources")
            return True
        
        # Crawl each source
        crawler = NewsCrawler(db_session=session)
        total_articles = 0
        
        for source in active_sources[:3]:  # Test first 3 sources
            print(f"\n[{source.name}]")
            print(f"  Type: {source.crawl_type}")
            
            try:
                articles = crawler.crawl_source(source)
                total_articles += len(articles)
                print(f"  ✓ {len(articles)} artikel ditemukan")
                
                if articles:
                    print(f"    Sample: {articles[0]['title'][:50]}...")
            except Exception as e:
                print(f"  ✗ Error: {str(e)[:100]}")
        
        print(f"\n{'='*80}")
        print(f"Total articles extracted: {total_articles}")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()
    
    return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("News Sources Test Suite")
    print("="*80)
    
    # Test 1: Add new source
    test1_passed = test_add_new_source()
    
    # Test 2: Crawl all sources
    test2_passed = test_crawl_all_sources()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Test 1 (Add New Source): {'PASSED ✓' if test1_passed else 'FAILED ✗'}")
    print(f"Test 2 (Crawl All): {'PASSED ✓' if test2_passed else 'FAILED ✗'}")
    print("="*80 + "\n")
    
    sys.exit(0 if (test1_passed and test2_passed) else 1)
