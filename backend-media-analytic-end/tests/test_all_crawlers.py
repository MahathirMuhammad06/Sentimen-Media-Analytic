#!/usr/bin/env python3
import sys
sys.path.insert(0, 'c:/xampp/htdocs/project/backend-media-analytic-final')

from src.crawler.news_crawler import NewsCrawler

print("[TEST] Starting crawler tests...")

crawler = NewsCrawler()

print("\n[SUARA] Crawling...")
suara_articles = crawler.crawl_suara()
print(f"[SUARA] {len(suara_articles)} articles found")

print("\n[DETIK] Crawling...")
detik_articles = crawler.crawl_detik()
print(f"[DETIK] {len(detik_articles)} articles found")

print("\n[LAMPUNG PRO] Crawling...")
lampung_articles = crawler.crawl_lampung_pro()
print(f"[LAMPUNG PRO] {len(lampung_articles)} articles found")

print("\n[RESULT]")
print(f"Total: {len(suara_articles) + len(detik_articles) + len(lampung_articles)} articles")
print(f"  Suara: {len(suara_articles)}")
print(f"  Detik: {len(detik_articles)}")
print(f"  Lampung Pro: {len(lampung_articles)}")
