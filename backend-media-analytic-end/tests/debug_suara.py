import sys
sys.path.insert(0, 'c:/xampp/htdocs/project/backend-media-analytic-final')

from src.crawler.news_crawler import NewsCrawler
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

crawler = NewsCrawler()

print("=== TESTING SUARA CRAWLER ===\n")
print("[1] Testing URL fetch...")

import requests
from bs4 import BeautifulSoup

url = "https://lampung.suara.com"
try:
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    print(f"OK - URL accessible: {r.status_code}")
    
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a", href=True)
    article_links = [l.get("href") for l in links if "/read/" in l.get("href", "")]
    print(f"OK - Found {len(article_links)} /read/ links")
    
    if article_links:
        print(f"  Sample: {article_links[0][:70]}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n[2] Running actual crawler...")
suara_articles = crawler.crawl_suara()
print(f"OK - Crawler returned {len(suara_articles)} articles")

if suara_articles:
    print("\nFirst 3 articles:")
    for i, article in enumerate(suara_articles[:3], 1):
        print(f"\n  {i}. Title: {article['title'][:60]}")
        print(f"     URL: {article['url'][:60]}...")
        print(f"     Content: {len(article['content'])} chars")
        print(f"     Sentiment: {article.get('sentiment', 'N/A')}")
else:
    print("\nERROR - No articles returned!")
