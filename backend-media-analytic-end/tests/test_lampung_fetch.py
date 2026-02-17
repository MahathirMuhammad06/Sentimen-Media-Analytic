import requests
from bs4 import BeautifulSoup

url = "https://lampungpro.co/news/musrenbang-rkpd-2027-tanjung-bintang-usulkan-bangun-jalan-patok-besi-hingga-jembatan-ke-pemkab-lampung-selatan"

try:
    r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    print(f"Status: {r.status_code}")
    
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Try various selectors
    selectors = [
        "article",
        "main",
        "div.article-body",
        "div.entry-content",
        "div.content",
        "div.post-content",
    ]
    
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            text = el.get_text(" ", strip=True)
            print(f"\n{sel}: {len(text)} chars")
            print(f"  Preview: {text[:100]}...")
    
    # Try full text
    full_text = soup.get_text(" ", strip=True)
    print(f"\nFull text: {len(full_text)} chars")
    print(f"  Preview: {full_text[:100]}...")
    
except Exception as e:
    print(f"Error: {e}")
