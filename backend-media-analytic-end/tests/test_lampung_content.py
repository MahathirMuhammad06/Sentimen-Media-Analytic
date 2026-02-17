import requests
from bs4 import BeautifulSoup
import re

url = "https://lampungpro.co/news/musrenbang-rkpd-2027-tanjung-bintang-usulkan-bangun-jalan-patok-besi-hingga-jembatan-ke-pemkab-lampung-selatan"

r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

# Find main content container - look for large text blocks
paragraphs = soup.find_all("p")
print(f"Found {len(paragraphs)} paragraphs")

# Group consecutive paragraphs
article_content = ""
for p in paragraphs:
    text = p.get_text(strip=True)
    if len(text) > 20:  # Skip very short paragraphs
        article_content += text + " "
        if len(article_content) > 200:
            break

print(f"Grouped content: {len(article_content)} chars")
print(f"Preview: {article_content[:100]}...")

# Try to find divs that contain lots of paragraphs
print("\nLooking for containers with paragraphs...")
divs = soup.find_all("div")
for div in divs[:100]:
    ps_count = len(div.find_all("p", recursive=False))
    if ps_count >= 3:
        text = div.get_text()[:150]
        print(f"  Div with {ps_count} direct paragraphs: {len(div.get_text())} chars")
        break
