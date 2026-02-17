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

# Get first article
links = soup.find_all("a", href=True)
found = False
for link in links:
    href = link.get("href", "")
    if "/news/" in href and "/kategori/news/" not in href:
        if href.startswith("/"):
            href = "https://lampungpro.co" + href
        
        title = link.get_text(strip=True)
        print(f"Article found:")
        print(f"  Title from link: {title[:60]}")
        print(f"  URL: {href[:60]}...")
        
        # Fetch content
        content = crawler.get_article_content(href, {"name": "Lampung Pro"})
        print(f"  Content length: {len(content)}")
        
        if content:
            print(f"  Content preview: {content[:60]}...")
            
            # Test authentic
            is_auth = crawler._is_authentic_article(title, href, content)
            print(f"  Is authentic: {is_auth}")
            
            if not is_auth:
                # Debug why
                print("\n  Debugging authentication...")
                print(f"    - Title length: {len(title)} (min 5)")
                print(f"    - Content length: {len(content)} (min 80)")
                combined = (title + " " + content).lower()
                sent_count = combined.count(".") + combined.count("!") + combined.count("?")
                print(f"    - Sentence count: {sent_count} (min 1)")
        
        found = True
        break

if not found:
    print("No article link found!")
