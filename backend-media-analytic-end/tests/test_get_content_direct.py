import sys
sys.path.insert(0, 'c:/xampp/htdocs/project/backend-media-analytic-final')

# Bypass data model imports to just test crawler
from src.crawler.news_crawler import NewsCrawler

crawler = NewsCrawler()

# Test single article
url = "https://lampungpro.co/news/musrenbang-rkpd-2027-tanjung-bintang-usulkan-bangun-jalan-patok-besi-hingga-jembatan-ke-pemkab-lampung-selatan"

print("Testing get_article_content directly...")
try:
    result = crawler.get_article_content(url, {"name": "Lampung Pro"})
    print(f"Result: {len(result)} chars")
    if result:
        print(f"Content: {result[:100]}...")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
