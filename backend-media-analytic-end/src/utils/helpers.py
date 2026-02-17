from urllib.parse import urljoin

def safe_join(base, link):
    if not link:
        return ""
    if link.startswitch("http"):
        return link
    return urljoin(base, link)