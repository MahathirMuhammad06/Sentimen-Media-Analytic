import sys
sys.path.insert(0, 'c:/xampp/htdocs/project/backend-media-analytic-final')

from src.crawler.news_crawler import NewsCrawler

crawler = NewsCrawler()

# Test URLs
test_urls = [
    "https://lampungpro.co/news/musrenbang-rkpd-2027-tanjung-bintang-usulkan-bangun",
    "https://lampungpro.co/kategori/news/News%20Update/",
]

for url in test_urls:
    is_valid = crawler._is_valid_article_url(url, "lampungpro.co")
    print(f"URL: {url[:60]}...")
    print(f"  _is_valid_article_url: {is_valid}\n")
