import requests
from bs4 import BeautifulSoup

url = "https://lampungpro.co"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
soup = BeautifulSoup(r.text, "html.parser")

# Find /news/ links
links = soup.find_all("a", href=True)
news_links = {}
for link in links:
    href = link.get("href", "")
    if "/news/" in href.lower():
        category = "kategori" if "/kategori/news/" in href else "regular"
        if category not in news_links:
            news_links[category] = []
        news_links[category].append(href[:80])

for cat, hrefs in news_links.items():
    print(f"\n{cat.upper()}: {len(hrefs)} links")
    for h in hrefs[:3]:
        print(f"  {h}")
