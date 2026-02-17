"""
Dynamic crawler for user-submitted URLs
Automatically detects article links, titles, and content using heuristics
Falls back to RSS/Sitemap if detected
"""

import re
import feedparser
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin, urlparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup, NavigableString

from config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DynamicCrawler:
    """
    Crawls user-submitted URLs to extract articles
    Uses heuristic-based detection for article links, titles, and content
    Automatically detects RSS feeds and sitemaps
    """

    def __init__(self, max_articles: Optional[int] = None) -> None:
        self.max_articles = max_articles or config.MAX_ARTICLES_PER_SOURCE
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        }
        
        # Exclude keywords - matching news_crawler standards
        self.exclude_keywords = [
            "tentang kami", "about us", "about", "kontak kami", "contact us",
            "kebijakan privasi", "privacy policy", "syarat dan ketentuan", "terms",
            "sitemap", "bantuan", "help", "faq", "frequently asked",
            "redaksi", "editorial", "advertise", "iklan", "advertising",
            "berlangganan", "subscribe", "newsletter", "login", "sign up",
            "register", "registrasi", "profile", "profil", "setting",
            "lupa password", "forgot password", "hubungi admin", "hubungi kami",
            "beranda", "home page", "homepage", "halaman utama", "main page",
            "kategori", "category", "tag", "tags", "archive", "arsip",
            "powered by", "copyright", "hak cipta", "designed by",
            "404", "error", "not found", "page not found",
            "video", "videos", "foto", "photos", "gallery", "galeri",
            "facebook", "twitter", "instagram", "youtube", "tiktok",
            "instagram.com", "facebook.com", "twitter.com", "youtube.com",
            "whatsapp", "telegram", "linktr.ee", "bit.ly",
            "live streaming", "livestream", "lihat",
        ]
        
        # Social media domains to exclude - matching news_crawler standards
        self.social_media_domains = [
            "facebook.com", "twitter.com", "instagram.com", "youtube.com",
            "tiktok.com", "linkedin.com", "whatsapp.com", "telegram.org",
            "t.me", "youtu.be", "bit.ly", "tinyurl.com", "linktr.ee",
            "pinterest.com", "snapchat.com", "reddit.com", "weibo.com",
            "viber.com", "line.me", "kakao.com", "wa.me", "whatsa",
        ]

    def detect_crawl_type(self, url: str) -> Dict[str, Any]:
        """
        Detect the best crawling method for a URL
        Priority: RSS Feed > Sitemap > HTML Structure Analysis
        Returns: {'type': 'rss'|'sitemap'|'html', 'config': {...}}
        """
        try:
            # Check for RSS feeds in common locations
            rss_feeds = self._detect_rss_feeds(url)
            if rss_feeds:
                logger.info(f"Detected RSS feed at {url}: {rss_feeds[0]}")
                return {
                    'type': 'rss',
                    'config': {'rss_url': rss_feeds[0]},
                    'detected': True
                }

            # Check for sitemap
            sitemap_url = self._detect_sitemap(url)
            if sitemap_url:
                logger.info(f"Detected Sitemap at {url}: {sitemap_url}")
                return {
                    'type': 'sitemap',
                    'config': {'sitemap_url': sitemap_url},
                    'detected': True
                }

            # Fallback to HTML structure analysis
            logger.info(f"Using heuristic HTML crawling for {url}")
            return {
                'type': 'html',
                'config': {'base_url': url},
                'detected': False
            }
        except Exception as e:
            logger.error(f"Error detecting crawl type for {url}: {e}")
            return {
                'type': 'html',
                'config': {'base_url': url},
                'detected': False
            }

    def _detect_rss_feeds(self, url: str) -> List[str]:
        """
        Detect RSS feeds by checking common paths and HTML meta tags
        """
        rss_urls = []
        base_domain = self._get_base_domain(url)

        # Common RSS feed paths
        common_paths = [
            '/rss',
            '/rss.xml',
            '/feed',
            '/feed.xml',
            '/feeds',
            '/feeds/rss',
            '/index.php/rss',
        ]

        for path in common_paths:
            test_url = base_domain + path
            if self._url_exists(test_url):
                rss_urls.append(test_url)

        # Check for RSS links in HTML meta tags
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for RSS/Atom links
            for link in soup.find_all('link', {'rel': ['alternate', 'feed']}):
                href = link.get('href')
                if href and ('rss' in href.lower() or 'feed' in href.lower() or 'atom' in href.lower()):
                    full_url = urljoin(url, href)
                    if full_url not in rss_urls:
                        rss_urls.append(full_url)
        except Exception as e:
            logger.warning(f"Could not parse HTML for RSS detection at {url}: {e}")

        return rss_urls[:3]  # Return up to 3 feeds

    def _detect_sitemap(self, url: str) -> Optional[str]:
        """
        Detect sitemap.xml location
        """
        base_domain = self._get_base_domain(url)
        sitemap_url = base_domain + '/sitemap.xml'

        if self._url_exists(sitemap_url):
            return sitemap_url

        # Check robots.txt for sitemap location
        try:
            robots_url = base_domain + '/robots.txt'
            response = requests.get(robots_url, headers=self.headers, timeout=10)
            for line in response.text.split('\n'):
                if line.lower().startswith('sitemap:'):
                    sitemap = line.split(':', 1)[1].strip()
                    if self._url_exists(sitemap):
                        return sitemap
        except Exception as e:
            logger.debug(f"Could not check robots.txt: {e}")

        return None

    def _url_exists(self, url: str) -> bool:
        """
        Check if a URL is accessible
        """
        try:
            response = requests.head(url, headers=self.headers, timeout=5, allow_redirects=True)
            return response.status_code < 400
        except Exception:
            # Try GET if HEAD fails
            try:
                response = requests.get(url, headers=self.headers, timeout=5)
                return response.status_code < 400
            except Exception:
                return False

    def _get_base_domain(self, url: str) -> str:
        """
        Extract base domain from URL
        """
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def crawl_rss_feed(self, rss_url: str) -> List[Dict[str, Any]]:
        """
        Crawl RSS feed and extract articles
        """
        articles = []
        try:
            feed = feedparser.parse(rss_url, request_headers=self.headers)

            if feed.bozo:
                logger.warning(f"RSS feed parsing issue: {feed.bozo_exception}")

            for entry in feed.entries[:self.max_articles]:
                link = entry.get('link', '').strip()
                title = entry.get('title', '').strip()

                if not link or not title:
                    continue

                # Extract content
                content = ''
                if 'content' in entry and entry.content:
                    content = entry.content[0].value
                elif 'summary' in entry:
                    content = entry.summary

                # Clean HTML from content
                content = self._clean_html(content)

                # Fallback to fetching full article if content too short
                if len(content) < 200:
                    fetched_content = self._fetch_article_content(link)
                    if fetched_content and len(fetched_content) > len(content):
                        content = fetched_content

                if len(content) < 150:
                    continue

                articles.append({
                    'title': title,
                    'url': link,
                    'content': content,
                    'source': self._extract_domain_name(rss_url)
                })

                if len(articles) >= self.max_articles:
                    break

        except Exception as e:
            logger.error(f"Error crawling RSS feed {rss_url}: {e}")

        return articles

    def crawl_html_dynamic(self, base_url: str) -> List[Dict[str, Any]]:
        """
        Crawl HTML page using heuristic-based detection
        Identifies article links, titles, and content
        """
        articles = []
        try:
            response = requests.get(base_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {base_url}: {e}")
            return articles

        # Find potential article links using heuristics
        article_links = self._find_article_links(soup, base_url)

        seen_urls = set()
        for link_data in article_links[:self.max_articles]:
            url = link_data['url']

            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Fetch and parse article
            content = self._fetch_article_content(url)
            if not content or len(content) < 150:
                continue

            title = link_data.get('title') or self._extract_title_from_url(url)

            articles.append({
                'title': title,
                'url': url,
                'content': content,
                'source': self._extract_domain_name(base_url)
            })

        logger.info(f"Found {len(articles)} articles at {base_url}")
        return articles

    def _find_article_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """
        Use heuristics to find article links on a page
        Looks for common patterns and link density
        Filters out navigation/footer/sidebar links and content container links
        Aligned with news_crawler standards
        """
        article_links = []

        # Remove script, style, and navigation elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()

        # Remove common non-article containers with expanded patterns
        exclude_patterns = re.compile(
            r'(sidebar|footer|header|nav|menu|breadcrumb|comment|related|'
            r'advertisement|ads|social|widget|slide|banner|popover|modal|'
            r'pagination|pager|next-|prev-|share-|follow-|subscribe-)',
            re.IGNORECASE
        )
        
        for container in soup.find_all(class_=exclude_patterns):
            container.decompose()

        # Also remove by id patterns
        exclude_id_patterns = re.compile(
            r'(sidebar|footer|header|nav|menu|ads|comment|related|social)',
            re.IGNORECASE
        )
        for container in soup.find_all(id=exclude_id_patterns):
            container.decompose()

        # Find all anchor tags
        all_links = soup.find_all('a', href=True)

        for link in all_links:
            href = link.get('href', '').strip()
            if not href:
                continue

            # Skip common non-article URLs
            if self._is_article_link(href, base_url):
                full_url = urljoin(base_url, href)

                # Extract title heuristics
                title = link.get_text(strip=True)

                # If title is too short, try parent heading elements
                if len(title) < 10:
                    parent = link.find_parent(['h1', 'h2', 'h3', 'h4'])
                    if parent:
                        title = parent.get_text(strip=True)

                # Filter out very short titles and obvious non-article text
                if len(title) > 10 and not self._is_navigation_text(title):
                    article_links.append({
                        'url': full_url,
                        'title': title
                    })

        # Rank links by likelihood of being articles
        article_links = self._rank_article_links(article_links)
        return article_links

    def _is_navigation_text(self, text: str) -> bool:
        """
        Check if text is likely navigation/UI text rather than article title
        Aligned with news_crawler standards
        """
        nav_patterns = [
            'read more', 'read next', 'continue reading', 'lihat selengkapnya',
            'baca selengkapnya', 'back to', 'previous', 'next', 'home', 'menu',
            'search', 'sign in', 'sign up', 'login', 'register', 'subscribe',
            'follow', 'share', 'print', 'email', 'comment', 'like', 'download',
            'posted', 'published', 'category', 'tag', 'author'
        ]
        text_lower = text.lower().strip()
        for pattern in nav_patterns:
            if pattern in text_lower:
                return True
        
        # Also filter very short text (likely not article title)
        if len(text.strip()) < 10:
            return True
        
        return False

    def _is_article_link(self, href: str, base_url: str) -> bool:
        """
        Heuristic to detect if a link is likely to be an article
        Filters out navigation, UI elements, inline content links, and social media
        Aligned with news_crawler standards
        """
        href_lower = href.lower()

        # Check for social media domains
        for social_domain in self.social_media_domains:
            if social_domain in href_lower:
                return False

        # Check for exclude keywords in URL
        for keyword in self.exclude_keywords:
            if keyword.lower() in href_lower:
                return False

        # Skip navigation and utility links
        skip_patterns = [
            'javascript:', '#', 'mailto:', 'tel:', '/search', '/tag/',
            '/category/', '/archive/', '/page/', '/wp-admin', '/admin',
            '/login', '/register', '/cart', '/checkout', '/help', '/about',
            '/contact', '/privacy', '/terms', '/rss', '/feed', '/sitemap',
            '/galleries', '/videos', '/photo', '/picture', '/image',
            '/?', '&utm_', '.pdf', '.doc', '.xls', '#!', '/share',
            '/comment', '/discussion', '/forum', '/user/', '/profile',
            '/notification', '/preference', '/setting', '/subscribe',
            '/gallery', '/galeri', '/video', '/foto',
        ]

        for pattern in skip_patterns:
            if pattern in href_lower:
                return False

        # Common article URL patterns - must match at least one
        article_patterns = [
            '/artikel/', '/article/', '/news/', '/post/', '/read/',
            '/story/', '/berita/', '/2024/', '/2025/', '/2023/', '/2022/', 
            '/2021/', '/2020/', '/blog/',
            '/content/', '/entry/', '-lampung', '-news', '-article',
            '/news-', '/artikel-', '/berita-'
        ]

        has_article_pattern = False
        for pattern in article_patterns:
            if pattern in href_lower:
                has_article_pattern = True
                break

        if not has_article_pattern:
            # If no article pattern, require numeric ID or date pattern
            if not re.search(r'/\d{4,}(-\d{2})?(-\d{2})?', href_lower):
                if not re.search(r'-\d{2,}[a-z-]*$', href_lower):
                    # Also check for date patterns like 2024/01/23
                    if not re.search(r'\d{4}/\d{2}/\d{2}', href_lower):
                        return False

        # Check base URL to avoid leaving domain
        try:
            if base_url not in href and urlparse(href).netloc and urlparse(href).netloc != urlparse(base_url).netloc:
                return False
        except Exception:
            pass

        return True

    def _rank_article_links(self, links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank article links by relevance/likelihood with improved scoring
        Prioritizes links with longer titles, proper article patterns, and recent dates
        """
        def score_link(link_data):
            score = 0
            url = link_data['url'].lower()
            title = link_data.get('title', '').lower()

            # 1. Title quality (max 5 points)
            title_length = len(title.strip())
            if title_length > 50:
                score += 5
            elif title_length > 30:
                score += 4
            elif title_length > 20:
                score += 3
            elif title_length > 10:
                score += 1

            # 2. Date patterns (prefer recent articles) (max 4 points)
            # Match YYYY/MM/DD pattern
            if re.search(r'202[4-9]/\d{2}/\d{2}', url):
                score += 4
            # Match YYYY/MM pattern
            elif re.search(r'202[4-9]/\d{2}', url):
                score += 3
            # Match older year patterns
            elif re.search(r'202[0-3]/\d{2}', url):
                score += 2

            # 3. Article keywords in URL (max 3 points)
            high_priority_patterns = ['artikel/', 'berita/', 'news/', 'post/']
            medium_priority_patterns = ['article/', 'story/', 'read/', 'content/']
            
            for pattern in high_priority_patterns:
                if pattern in url:
                    score += 3
                    break
            else:
                for pattern in medium_priority_patterns:
                    if pattern in url:
                        score += 2
                        break

            # 4. URL specificity - longer paths usually mean more specific articles (max 3 points)
            path_depth = len(url.split('/')) - 3
            if path_depth >= 5:
                score += 3
            elif path_depth >= 3:
                score += 2
            elif path_depth >= 2:
                score += 1

            # 5. URL length quality (max 2 points)
            if 50 < len(url) < 200:
                score += 2

            return score

        return sorted(links, key=score_link, reverse=True)

    def _fetch_article_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch and extract main content from an article URL
        Uses DOM density heuristic and common content selectors
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove non-content elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', '.sidebar', '.ads', '.advertisement']):
                element.decompose()

            # Try common content selectors first
            content_selectors = [
                'article',
                'main',
                '[role="main"]',
                '.post-content',
                '.article-content',
                '.entry-content',
                '.content-body',
                '.isi-artikel',
                '.story-body',
                '.article__body',
                '.news-content',
                'div[class*="content"]',
                'div[class*="artikel"]',
                'div[class*="article"]',
                'div[class*="post"]',
            ]

            content = None
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(' ', strip=True)
                    if len(content) > 200:
                        return content[:5000]  # Limit content length

            # Fallback: Use DOM density heuristic
            if not content or len(content) < 200:
                content = self._extract_by_dom_density(soup)

            return content[:5000] if content else None

        except Exception as e:
            logger.warning(f"Error fetching content from {url}: {e}")
            return None

    def _extract_by_dom_density(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract main content using DOM density analysis
        Find the element with highest text-to-tag ratio
        """
        best_element = None
        best_score = 0

        for element in soup.find_all(['div', 'section', 'article', 'main']):
            text_length = len(element.get_text())
            tag_count = len(element.find_all())

            if tag_count == 0:
                continue

            # DOM density = text length / number of tags
            density = text_length / (tag_count + 1)

            if density > best_score and text_length > 200:
                best_score = density
                best_element = element

        if best_element:
            return best_element.get_text(' ', strip=True)[:5000]

        return None

    def _clean_html(self, html_text: str) -> str:
        """
        Remove HTML tags from text
        """
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.get_text(' ', strip=True)

    def _extract_domain_name(self, url: str) -> str:
        """
        Extract domain name from URL for source attribution
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            # Capitalize first letters
            return ' '.join(word.capitalize() for word in domain.split('.')[0].split('-'))
        except Exception:
            return 'Unknown'

    def _extract_title_from_url(self, url: str) -> str:
        """
        Extract potential title from URL slug
        """
        try:
            path = urlparse(url).path
            slug = path.split('/')[-1].replace('-', ' ').replace('_', ' ')
            return slug.title()[:100]
        except Exception:
            return 'Article'

    def crawl_url(self, url: str) -> List[Dict[str, Any]]:
        """
        Main entry point: crawl a user-provided URL
        Detects best crawling method and extracts articles
        """
        detection = self.detect_crawl_type(url)
        crawl_type = detection['type']

        logger.info(f"Crawling {url} using method: {crawl_type}")

        articles = []
        if crawl_type == 'rss':
            articles = self.crawl_rss_feed(detection['config']['rss_url'])
        elif crawl_type == 'html':
            articles = self.crawl_html_dynamic(url)

        return articles
