import requests
from bs4 import BeautifulSoup

url = "https://lampungpro.co/news/musrenbang-rkpd-2027-tanjung-bintang-usulkan-bangun-jalan-patok-besi-hingga-jembatan-ke-pemkab-lampung-selatan"

r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

# Find divs with class
divs = soup.find_all("div", class_=True)
print("Div classes found:")
for div in divs[:15]:
    classes = " ".join(div.get("class", []))
    text_len = len(div.get_text())
    if text_len > 100:
        print(f"  {classes[:60]:60} ({text_len} chars)")

# Try to find article container
print("\nLooking for article containers...")
for selector in ["div.detail-content", "div.entry", "div.post", "div.article"]:
    el = soup.select_one(selector)
    if el:
        text = el.get_text()[:100]
        print(f"  {selector}: Found {len(el.get_text())} chars")
