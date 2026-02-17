import requests
from bs4 import BeautifulSoup

url = "https://lampungpro.co"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

links = soup.find_all("a", href=True)
print(f"Total links: {len(links)}")

news_links = 0
non_news_links = 0
external_links = 0

for link in links:
    href = link.get("href", "").strip()
    if not href:
        continue
    
    if "/news/" in href:
        news_links += 1
        if news_links <= 3:
            print(f"News: {href[:70]}")
    elif not href.startswith("http"):
        non_news_links += 1
    else:
        external_links += 1

print(f"\nSummary:")
print(f"  /news/ links: {news_links}")
print(f"  Relative links: {non_news_links}")
print(f"  External links: {external_links}")
