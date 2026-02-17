import sys
sys.path.insert(0, 'c:/xampp/htdocs/project/backend-media-analytic-final')

import requests
from bs4 import BeautifulSoup
from src.crawler.news_crawler import NewsCrawler

crawler = NewsCrawler()

# Fetch page
url = "https://lampungpro.co"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
soup = BeautifulSoup(r.text, "html.parser")

# Get first article link
first_article = None
for link in soup.find_all("a", href=True):
    href = link.get("href", "")
    if "/news/" in href and "/kategori/news/" not in href:
        if href.startswith("/"):
            href = "https://lampungpro.co" + href
        first_article = href
        break

print(f"First article URL: {first_article}")

# Test title extraction
title = "Test Article Title"
print(f"\nTitle validation:")
print(f"  Title: {title}")
# Skip title validation test

# Test content fetching
if first_article:
    print(f"\nContent extraction:")
    print(f"  URL: {first_article}")
    content = crawler.get_article_content(first_article, {"name": "Lampung Pro"})
    print(f"  Content length: {len(content) if content else 0}")
    if content:
        print(f"  Preview: {content[:100]}...")
        
        # Test authentic
        is_auth = crawler._is_authentic_article(title, first_article, content)
        print(f"  Is authentic: {is_auth}")
