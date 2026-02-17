import requests
from bs4 import BeautifulSoup

url = "https://lampungpro.co/news/musrenbang-rkpd-2027-tanjung-bintang-usulkan-bangun-jalan-patok-besi-hingga-jembatan-ke-pemkab-lampung-selatan"

r = requests.get(url, timeout=20, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://lampung.tribunnews.com"
})
soup = BeautifulSoup(r.content, "lxml")

# Test selectors
selectors = [
    "div.post-content",
    "div.post-body",
    "div#article-content",
    "div.read__content",
    "div.detail__body-text",
    "div.content-article",
    "div.box-content",
    "div.col-8",
    "article"
]

print("Testing selectors...")
for sel in selectors:
    el = soup.select_one(sel)
    if el:
        text = el.get_text(" ", strip=True)
        print(f"  {sel}: Found {len(text)} chars")
        break
else:
    print("  No selector matched")

# Test fallback
print("\nTesting fallback (divs with 3+ paragraphs)...")
divs = soup.find_all("div")
for i, div in enumerate(divs):
    direct_paragraphs = div.find_all("p", recursive=False)
    if len(direct_paragraphs) >= 3:
        text = div.get_text(" ", strip=True)
        print(f"  Found at div #{i}: {len(direct_paragraphs)} paragraphs, {len(text)} chars")
        if len(text) > 100:
            print(f"    Content: {text[:100]}...")
            break

# Test full text
print("\nFull text length:", len(soup.get_text(" ", strip=True)))
