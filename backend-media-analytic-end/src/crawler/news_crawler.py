import re
from datetime import datetime
from typing import Optional, List, Dict, Any

import requests
import feedparser

from bs4 import BeautifulSoup

from config import config
from ..utils.logger import get_logger
from ..utils.keyword_extractor import extract_keywords_high_accuracy, format_keywords_for_db
from ..ml.sentiment_analyzer import SentimentAnalyzer
from ..database.repository import (
    save_articles_bulk,
    cleanup_old_articles,
    get_sources,
    is_link_active,
    mark_link_inactive,
    mark_link_timeout,
    mark_link_active,
)

logger = get_logger(__name__)

class NewsCrawler:
    """
    A crawler for collecting news articles from various sources.

    Supports both database-configured sources and hardcoded sources.
    Handles RSS and HTML-based crawling, sentiment analysis, and keyword extraction.
    """

    def __init__(self, db_session: Optional[Any] = None, max_per_source: Optional[int] = None) -> None:
        self.db_session = db_session
        self.max_per_source = max_per_source or config.MAX_ARTICLES_PER_SOURCE
        self.analyzer = SentimentAnalyzer(model_path="src/ml/model")
        
        # Keywords to exclude (non-authentic articles)
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
        
        # Social media domains to exclude
        self.social_media_domains = [
            "facebook.com", "twitter.com", "instagram.com", "youtube.com",
            "tiktok.com", "linkedin.com", "whatsapp.com", "telegram.org",
            "t.me", "youtu.be", "bit.ly", "tinyurl.com", "linktr.ee",
            "pinterest.com", "snapchat.com", "reddit.com", "weibo.com",
            "viber.com", "line.me", "kakao.com", "wa.me", "whatsa",
        ]

    def _create_article_dict(self, title: str, url: str, source: str, content: str) -> Dict[str, Any]:
        """
        Create a standardized article dictionary with sentiment analysis and high-accuracy keywords.

        Args:
            title: Article title
            url: Article URL
            source: Source name
            content: Article content

        Returns:
            Dictionary containing article data with sentiment and keywords
        """
        # Extract keywords dengan akurasi tinggi (judul + konten)
        keywords = extract_keywords_high_accuracy(title, content, max_keywords=10)
        keywords_str = format_keywords_for_db(keywords)
        
        sentiment_result = self.analyzer.predict(content or title)

        return {
            "title": title,
            "url": url,
            "source": source,
            "content": content,
            "keywords_flagged": keywords_str,  # High-accuracy keywords for search
            "sentiment": sentiment_result["sentiment"],
            "confidence": sentiment_result["confidence"],
            "prob_negative": sentiment_result["prob_negative"],
            "prob_neutral": sentiment_result["prob_neutral"],
            "prob_positive": sentiment_result["prob_positive"],
            "crawled_date": datetime.utcnow(),
        }

    def _is_authentic_article(self, title: str, url: str, content: str) -> bool:
        """
        Filter articles to keep only authentic news articles and exclude non-article pages.
        
        Args:
            title: Article title
            url: Article URL
            content: Article content
            
        Returns:
            True if article is authentic, False otherwise
        """
        # Check content length (articles should have substantial content)
        if not content or len(content) < 200:
            return False
        
        # Check title length
        if not title or len(title.strip()) < 5:
            return False
        
        # For Lampung Pro, URL filtering is already strict (/news/ path, lampungpro.co domain)
        # so we can skip exclude keyword checks to avoid false negatives
        # For Detik, also relax checks since they have good editorial standards
        if "lampungpro.co" not in url.lower() and "detik.com" not in url.lower():
            # Check URL and title for exclude keywords (for other sources)
            combined_text = (title + " " + url).lower()
            for keyword in self.exclude_keywords:
                if keyword in combined_text:
                    return False
            
            # Check if content has article markers (paragraphs, sentences, etc)
            # Articles typically have multiple sentences or significant text
            sentence_count = combined_text.count(".") + combined_text.count("!") + combined_text.count("?")
            if sentence_count < 2:
                return False
        else:
            # For Lampung Pro and Detik, just check that title+content has some punctuation
            combined = (title + " " + content).lower()
            sentence_count = combined.count(".") + combined.count("!") + combined.count("?")
            if sentence_count < 1:
                return False
        
        return True

    def _is_valid_article_url(self, url: str, allowed_domain: str = None) -> bool:
        """
        Validate URL to ensure it's an article link and not external/social media.
        
        Args:
            url: URL to validate
            allowed_domain: Expected domain for the article (optional)
            
        Returns:
            True if URL is valid article link, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        if not url:
            return False
        
        url_lower = url.lower()
        
        # Check for social media domains
        for social_domain in self.social_media_domains:
            if social_domain in url_lower:
                logger.debug(f"Rejected URL - social media domain: {url}")
                return False
        
        # Check for common non-article URL patterns
        invalid_patterns = [
            "/video/", "/videos/", "/gallery/", "/galeri/", "/foto/", "/photos/",
            "/rss", "/feed", "/search", "/page=", "/category", "/tag",
            "/author/", "/author-", "/about", "/contact", "/privacy",
            "/terms", "/sitemap", "/comment", "/login", "/register",
            "/share/", "/amp/", "/print", "/embed", "/popup",
            "#", "javascript:", "data:", "mailto:", "tel:",
        ]
        
        for pattern in invalid_patterns:
            if pattern in url_lower:
                logger.debug(f"Rejected URL - invalid pattern '{pattern}': {url}")
                return False
        
        # If allowed domain is specified, check it matches
        if allowed_domain:
            if allowed_domain.lower() not in url_lower:
                logger.debug(f"Rejected URL - domain mismatch. Expected: {allowed_domain}, Got: {url}")
                return False
        
        return True

    def crawl_all(self):
        from ..database.repository import record_crawl_result
        
        all_articles = []

        # Load sources from database (both hardcoded and user-added)
        if self.db_session:
            sources = get_sources(self.db_session)
            logger.info(f"Found {len(sources)} sources in database")
            
            for source in sources:
                if source.active:
                    try:
                        logger.info(f"Crawling: {source.name} ({source.crawl_type})")
                        
                        # Special handling for sources with custom crawlers
                        if source.name == "Tribun Lampung":
                            source_articles = self.crawl_tribun_lampung()
                        elif source.name == "Detik":
                            source_articles = self.crawl_detik()
                        elif source.name == "Lampung Pro":
                            source_articles = self.crawl_lampung_pro()
                        elif source.name == "Suara":
                            source_articles = self.crawl_suara()
                        else:
                            # Use generic crawler for other sources
                            source_articles = self.crawl_generic(source)
                        
                        # Record crawl result for source health tracking
                        articles_count = len(source_articles)
                        record_crawl_result(self.db_session, source.id, articles_count)
                        
                        all_articles.extend(source_articles)
                    except Exception as e:
                        logger.error(f"Error crawling {source.name}: {e}")
                        # Record failure for source health tracking
                        record_crawl_result(self.db_session, source.id, 0, failure_reason=str(e)[:100])
        else:
            logger.warning("No database session available - crawler cannot run")
            return []

        # logger.info(all_articles)
        save_articles_bulk(all_articles)
        cleanup_old_articles(days=30)  # hapus data lebih dari 7 hari
        logger.info(f"Crawling completed - Total articles: {len(all_articles)}")
        return all_articles

    def crawl_generic(self, source):
        """Generic crawler for RSS or HTML sources based on config"""
        if source.crawl_type == "rss":
            return self._crawl_rss_generic(source)
        elif source.crawl_type == "html":
            return self._crawl_html_generic(source)
        else:
            logger.error(f"Unknown source type: {source.crawl_type}")
            return []

    def _crawl_rss_generic(self, source):
        """Crawl RSS feed with proper error handling and fallback"""
        config = source.config if hasattr(source, 'config') else source.get("config", {})
        source_name = source.name if hasattr(source, 'name') else source.get("name", "Unknown")
        
        # Get RSS URL from config
        rss_url = config.get("rss_url")
        if not rss_url:
            logger.debug(f"No rss_url in config for {source_name}, cannot crawl RSS")
            return []

        headers = config.get("headers", {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        
        try:
            # feedparser.parse() doesn't support timeout parameter, use requests to fetch with timeout
            response = requests.get(rss_url, headers=headers, timeout=15)
            feed = feedparser.parse(response.text)

            if feed.bozo:
                logger.warning(f"{source_name} RSS feed has parsing errors: {feed.bozo_exception}")
                # Continue anyway, some feeds still work despite bozo
            
            if not feed.entries:
                logger.warning(f"{source_name} RSS feed returned no entries from {rss_url}")
                return []

        except Exception as e:
            logger.error(f"Error fetching RSS from {rss_url}: {e}")
            return []

        articles = []
        for entry in feed.entries[:self.max_per_source]:
            try:
                link = entry.get("link")
                title = entry.get("title", "").strip()

                if not link or not title:
                    continue

                content = ""
                if "content" in entry and entry.content:
                    content = entry.content[0].value
                elif "summary" in entry:
                    content = entry.summary

                # Fallback to HTML if content too short
                if len(content) < 200:
                    html_content = self.get_article_content(link, {"name": source_name})
                    if html_content and len(html_content) > len(content):
                        content = html_content

                if len(content) < 150:
                    logger.debug(f"{source_name}: Skipping article with insufficient content: {title[:50]}")
                    continue

                # Filter only authentic articles
                if not self._is_authentic_article(title, link, content):
                    logger.debug(f"{source_name}: Skipping non-authentic article: {title[:50]}")
                    continue

                articles.append(self._create_article_dict(title, link, source_name, content))
            except Exception as e:
                logger.warning(f"{source_name}: Error processing RSS entry: {e}")
                continue

        logger.info(f"{source_name}: extracted {len(articles)} articles from RSS")
        return articles

    def _crawl_html_generic(self, source):
        """Crawl HTML index page with proper config validation"""
        config = source.config if hasattr(source, 'config') else source.get("config", {})
        source_name = source.name if hasattr(source, 'name') else source.get("name", "Unknown")
        base_url = source.base_url if hasattr(source, 'base_url') else source.get("base_url", "")
        
        # Get index URL (can be same as base_url if not specified)
        index_url = config.get("index_url") or base_url
        
        if not index_url:
            logger.error(f"{source_name}: No index_url or base_url in config")
            return []

        link_selector = config.get("link_selector", "a[href]")
        title_selector = config.get("title_selector", "")
        content_selector = config.get("content_selector", "")
        filters = config.get("filters", {})
        headers = config.get("headers", {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

        try:
            r = requests.get(index_url, headers=headers, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            logger.error(f"{source_name}: Failed fetching index from {index_url}: {e}")
            return []

        candidates = soup.select(link_selector)
        seen_urls = set()
        articles = []

        for a in candidates:
            try:
                href = a.get("href", "").strip()
                if not href:
                    continue

                # Make absolute URL
                if href.startswith("/"):
                    href = base_url.rstrip("/") + href
                elif not href.startswith("http"):
                    href = base_url.rstrip("/") + "/" + href.lstrip("/")

                # Check if link is already marked as inactive - skip if it is
                if not is_link_active(href):
                    logger.debug(f"{source_name}: Skipping inactive link: {href}")
                    continue

                # Validate URL is article and from allowed domain
                if not self._is_valid_article_url(href, base_url):
                    continue

                # Additional filter: Skip navigation/UI text
                text = a.get_text(strip=True)
                if self._is_navigation_text(text):
                    logger.debug(f"{source_name}: Skipping navigation link: {text[:50]}")
                    continue

                # Apply filters
                skip = False
                for key, value in filters.items():
                    if key == "href_contains" and value not in href:
                        skip = True
                        break
                    elif key == "href_not_contains" and value in href:
                        skip = True
                        break
                    elif key == "text_contains":
                        link_text = a.get_text(strip=True)
                        if value not in link_text:
                            skip = True
                            break
                if skip:
                    continue

                if href in seen_urls:
                    continue
                seen_urls.add(href)

                # Get title
                title = a.get_text(strip=True)
                if not title and title_selector:
                    title_el = a.select_one(title_selector)
                    if title_el:
                        title = title_el.get_text(strip=True)
                if not title:
                    title = href.split("/")[-1].replace("-", " ").strip()

                if not title:
                    continue

                # Get content
                content = self.get_article_content(href, {"name": source_name})
                if content_selector and content:
                    # Try to extract specific content
                    soup_content = BeautifulSoup(content, "html.parser")
                    content_el = soup_content.select_one(content_selector)
                    if content_el:
                        content = content_el.get_text(" ", strip=True)

                if not content or len(content) < 200:
                    logger.debug(f"{source_name}: Insufficient content for {title[:50]}")
                    continue

                # Filter only authentic articles
                if not self._is_authentic_article(title, href, content):
                    logger.debug(f"{source_name}: Skipping non-authentic article: {title[:50]}")
                    continue

                articles.append(self._create_article_dict(title, href, source_name, content))

                if len(articles) >= self.max_per_source:
                    break
            except Exception as e:
                logger.warning(f"{source_name}: Error processing link: {e}")
                continue

        logger.info(f"{source_name}: extracted {len(articles)} articles from HTML")
        return articles
    
    def crawl_source(self, source):
        """
        Crawl a news source (NewsSource object or dictionary)
        Supports both hardcoded sources and user-defined sources
        Auto-detects optimal crawl method if auto_detect is True
        """
        articles = []
        
        # Handle both NewsSource objects and dictionaries
        if hasattr(source, 'crawl_type'):
            # NewsSource model object
            crawl_type = source.crawl_type
            auto_detect = getattr(source, 'auto_detect', False)
            source_name = source.name
        else:
            # Dictionary
            crawl_type = source.get("parser", source.get("crawl_type", "rss"))
            auto_detect = source.get("auto_detect", False)
            source_name = source.get("name", "Unknown")
        
        # If auto_detect and crawl_type is 'auto', run auto-detection first
        if auto_detect and crawl_type == "auto":
            try:
                from .dynamic_crawler import DynamicCrawler
                base_url = source.base_url if hasattr(source, 'base_url') else source.get("base_url")
                
                if base_url:
                    dynamic = DynamicCrawler()
                    detection = dynamic.detect_crawl_type(base_url)
                    
                    # Update crawl_type and config based on detection
                    crawl_type = detection['type']
                    
                    # Only update if we have a NewsSource model object
                    if hasattr(source, 'crawl_type'):
                        source.crawl_type = crawl_type
                        if 'config' in detection:
                            # Merge detected config with existing config
                            existing_config = source.config or {}
                            existing_config.update(detection['config'])
                            source.config = existing_config
                        if self.db_session:
                            self.db_session.commit()
                        logger.info(f"Auto-detected {source_name}: {crawl_type}")
                    else:
                        # Update dictionary source
                        source['crawl_type'] = crawl_type
                        if isinstance(source.get('config'), dict):
                            source['config'].update(detection.get('config', {}))
            except Exception as e:
                logger.warning(f"Auto-detection failed for {source_name}: {e}, falling back to generic")
                crawl_type = "html"  # Fallback to HTML
        
        # Route to appropriate crawler method based on crawl_type
        if crawl_type == "rss":
            articles = self._crawl_rss_generic(source)
        elif crawl_type in ["sitemap", "html"]:
            articles = self._crawl_html_generic(source)
        elif crawl_type == "auto":
            # Fallback to HTML if auto-detection failed
            logger.warning(f"Auto crawl_type not resolved for {source_name}, using HTML crawler")
            articles = self._crawl_html_generic(source)
        else:
            # Unknown type, try RSS first, then HTML as fallback
            logger.warning(f"Unknown crawl type '{crawl_type}' for {source_name}, trying RSS...")
            articles = self._crawl_rss_generic(source)
            if not articles:
                logger.warning(f"RSS failed for {source_name}, trying HTML fallback...")
                articles = self._crawl_html_generic(source)
        
        return articles[:self.max_per_source]
    
    def crawl_kompas(self):
        """
        Robust Kompas crawler:
        - Ambil semua <a> di area utama (fallback ke seluruh page)
        - Filter URL yang mengandung kompas.com dan kata 'lampung' (lebih luas: ambil artikel yang relevan)
        - Dedupe, lalu fetch content satu-per-satu
        """
        base = "https://www.kompas.com"
        url = "https://www.kompas.com/lampung/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

        try:
            session = requests.Session()
            session.headers.update(headers)
            r = session.get(url, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
        except Exception:
            logger.exception("Kompas: failed fetching index")
            return []

        # collect candidate links from a few sensible containers
        candidates = []
        # target main content blocks if present (best-effort)
        for sel in ["main", ".kp--content", ".container", ".read--list", ".latest__list", ".article__list", ".section--list"]:
            container = soup.select_one(sel)
            if container:
                candidates.extend(container.find_all("a", href=True))

        # fallback all anchors if container picks none
        if not candidates:
            candidates = soup.find_all("a", href=True)

        seen_urls = set()
        articles = []
        for a in candidates:
            href = a["href"].strip()
            if not href:
                continue

            # normalize relative links
            if href.startswith("/"):
                href = base + href

            # Check if link is already marked as inactive - skip if it is
            if not is_link_active(href):
                logger.debug(f"Kompas: Skipping inactive link: {href}")
                continue

            # Validate URL - only Kompas article URLs
            if not self._is_valid_article_url(href, "kompas.com"):
                continue

            # Strict path filter: require Lampung
            if "/lampung" not in href:
                continue

            if href in seen_urls:
                continue
            seen_urls.add(href)

            # title heuristic: text of anchor or parent heading
            title = a.get_text(strip=True)
            if not title:
                # try nearby heading tags
                parent = a.find_parent()
                if parent:
                    for tag in ["h1", "h2", "h3", "h4", "strong"]:
                        ttag = parent.select_one(tag)
                        if ttag and ttag.get_text(strip=True):
                            title = ttag.get_text(strip=True)
                            break
            if not title:
                title = href.split("/")[-1].replace("-", " ").strip()

            # fetch article content (this function is already in your class)
            content = self.get_article_content(href, {"name": "Kompas"})
            
            # Filter only authentic articles
            if not self._is_authentic_article(title, href, content):
                logger.debug(f"Kompas: Skipping non-authentic article: {title}")
                continue
            
            articles.append(self._create_article_dict(title, href, "Kompas", content))

            # break early if reached per-source max
            if len(articles) >= self.max_per_source:
                break

        logger.info(f"Kompas: found {len(articles)} articles")
        return articles


    
    def crawl_detik(self):
        """Detik Sumbagsel crawler - dengan improved title extraction"""
        url = "https://www.detik.com/sumbagsel"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            logger.error(f"Detik: Gagal fetch halaman: {e}")
            return []

        articles = []
        seen_urls = set()
        total_links = 0
        skipped_count = {}

        # Fetch all article links from article elements
        for article_elem in soup.select("article"):
            try:
                # Find link within article
                link_elem = article_elem.find("a", href=True)
                if not link_elem:
                    continue
                
                link = link_elem.get("href")
                total_links += 1
                
                if not link or not link.startswith("https"):
                    continue

                # Check if link is already marked as inactive
                if not is_link_active(link):
                    continue

                # Validate URL is article from detik.com domain
                if not self._is_valid_article_url(link, "detik.com"):
                    continue

                # Deduplicate
                if link in seen_urls:
                    continue
                seen_urls.add(link)

                # === IMPROVED: Get better title from article structure ===
                # Try multiple selectors to find a good title
                title = ""
                
                # Try h2, h3, or strong in article first
                for selector in ["h2", "h3", "strong", "a.title"]:
                    title_elem = article_elem.find(selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if title and len(title) > 5:
                            break
                
                # Fallback to link text if no title found
                if not title or len(title) < 5:
                    title = link_elem.get_text(strip=True)
                
                # Last resort: extract from URL slug
                if not title or len(title) < 5:
                    url_parts = link.split("/")[-1].replace("-", " ")
                    title = url_parts.replace("/", " ").title()
                
                if not title or len(title) < 3:
                    reason = "No valid title"
                    skipped_count[reason] = skipped_count.get(reason, 0) + 1
                    continue
                
                # Fetch content
                content = self.get_article_content(link, {"name": "Detik"})
                
                # Validate content
                if not content or len(content) < 150:
                    reason = "Content too short"
                    skipped_count[reason] = skipped_count.get(reason, 0) + 1
                    continue
                
                # Filter only authentic articles
                if not self._is_authentic_article(title, link, content):
                    reason = "Not authentic"
                    skipped_count[reason] = skipped_count.get(reason, 0) + 1
                    continue
                
                logger.debug(f"Detik: Accepted: {title[:50]}")
                articles.append(self._create_article_dict(title, link, "Detik", content))
                
                # Fetch up to max articles
                if len(articles) >= self.max_per_source:
                    break

            except Exception as e:
                logger.debug(f"Detik: Error processing article: {e}")
                continue

        logger.info(f"Detik: Processed {total_links} links -> {len(articles)} artikel")
        if skipped_count:
            logger.debug(f"Detik skip reasons: {skipped_count}")
        
        return articles
    
    def crawl_radar(self):
        """
        Radar Lampung crawler (Disway CMS compatible)
        - Crawl semua anchor
        - Filter URL artikel valid
        - Dedupe
        - Extract konten spesifik Radar
        """

        base_url = "https://radarlampung.disway.id"
        url = base_url + "/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        try:
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
        except Exception:
            logger.exception("Radar Lampung: gagal fetch halaman utama")
            return []

        articles = []
        seen_urls = set()

        # Radar Lampung (Disway) menyebar link artikel di banyak container
        anchors = soup.find_all("a", href=True)

        for a in anchors:
            try:
                href = a["href"].strip()

                if not href:
                    continue

                # normalisasi link relatif
                if href.startswith("/"):
                    href = base_url + href

                # Check if link is already marked as inactive - skip if it is
                if not is_link_active(href):
                    logger.debug(f"Radar: Skipping inactive link: {href}")
                    continue

                # Validate URL - only Radar domain and valid article path
                if not self._is_valid_article_url(href, "radarlampung.disway.id"):
                    continue

                # filter URL artikel (Disway pattern) - STRICT: hanya /read/
                # contoh valid:
                # https://radarlampung.disway.id/read/xxxxx/judul-berita
                if "/read/" not in href:
                    continue

                if href in seen_urls:
                    continue
                seen_urls.add(href)

                title = a.get_text(strip=True)
                if not title or len(title) < 10:
                    continue

                # ambil konten artikel
                content = self.get_article_content(href, {"name": "Radar"})

                # validasi konten
                if not content or len(content) < 300:
                    continue

                # Apply authentic article filter
                if not self._is_authentic_article(title, href, content):
                    logger.debug(f"Radar: Skipping non-authentic article: {title}")
                    continue

                articles.append(self._create_article_dict(title, href, "Radar Lampung", content))

                if len(articles) >= self.max_per_source:
                    break

            except Exception:
                logger.exception("Radar Lampung: gagal parsing artikel")

        logger.info(f"Radar Lampung: berhasil crawl {len(articles)} artikel")
        return articles

    
    def crawl_suara(self):
        """
        Suara Lampung crawler:
        - URL pattern: lampung.suara.com/read/...
        - Extract dari halaman Lampung Suara
        """
        lampung_url = "https://www.suara.com/lampung"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        articles = []
        seen_urls = set()

        try:
            r = requests.get(lampung_url, headers=headers, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Extract SEMUA links dari halaman
            for link_elem in soup.find_all("a", href=True):
                try:
                    href = link_elem.get("href", "").strip()
                    
                    if not href:
                        continue
                    
                    # PENTING: Suara Lampung URLs ada di lampung.suara.com/read/...
                    if "lampung.suara.com/read/" not in href.lower():
                        continue
                    
                    # Normalize URL ke full URL
                    if not href.startswith("http"):
                        if href.startswith("/"):
                            href = "https://lampung.suara.com" + href
                        else:
                            # Relative URL
                            href = "https://lampung.suara.com" + href if href.startswith("/") else "https://lampung.suara.com/read/" + href
                    
                    # Skip if already processed
                    if href in seen_urls:
                        continue
                    
                    # Check inactive
                    if not is_link_active(href):
                        continue
                    
                    seen_urls.add(href)
                    
                    # Get title dari link text
                    title = link_elem.get_text(strip=True)
                    
                    # If title kosong, extract dari URL slug
                    if not title or len(title) < 5:
                        # Extract dari URL: /read/2026/01/22/205115/[title-slug]
                        url_parts = href.split("/")
                        if len(url_parts) > 0:
                            title_slug = url_parts[-1] if url_parts[-1] else url_parts[-2] if len(url_parts) > 1 else ""
                            title = title_slug.replace("-", " ").title()
                    
                    # Final validation
                    if not title or len(title) < 5:
                        continue
                    
                    # Skip generic titles
                    if any(x in title.lower() for x in ["lampung", "suara", "home", "indeks"]):
                        # Actually Lampung is OK - it's the region
                        pass
                    
                    # Fetch article content
                    content = self.get_article_content(href, {"name": "Suara"})
                    
                    if not content or len(content) < 250:
                        logger.debug(f"Suara: Content too short ({len(content)} chars): {title[:40]}")
                        continue
                    
                    # Validate authentic
                    if not self._is_authentic_article(title, href, content):
                        logger.debug(f"Suara: Not authentic: {title[:40]}")
                        continue
                    
                    logger.debug(f"Suara: Accepted - {title[:50]}")
                    articles.append(self._create_article_dict(title, href, "Suara", content))
                    
                    if len(articles) >= self.max_per_source:
                        break
                        
                except Exception as e:
                    logger.debug(f"Suara: Link error: {str(e)[:100]}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Suara: Crawl failed: {e}")

        logger.info(f"Suara: {len(articles)} artikel")
        return articles
        
        
        
        
        
        
        
    
    def crawl_tribun_lampung(self):
        HEADERS_TRIBUN = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
        }

        
        rss_url = "https://lampung.tribunnews.com/rss"
        feed = feedparser.parse(rss_url, request_headers=HEADERS_TRIBUN)

        if feed.bozo:
            logger.warning("Tribun Lampung RSS bozo error (encoding issue), prioritizing HTML crawling")
            # Don't return empty - try to parse entries despite bozo flag

        articles = []

        for entry in feed.entries[: self.max_per_source]:
            link = entry.get("link")
            title = entry.get("title", "").strip()

            if not link or not title:
                continue

            # === PRIORITAS HTML CRAWLING (RSS summary is low quality) ===
            # Tribun Lampung RSS summary hanya berisi image embed, bukan artikel content
            # Lebih baik fetch HTML langsung untuk content extraction
            content = ""
            
            html_content = self.get_article_content(
                link,
                {"name": "Tribun Lampung"}
            )
            
            if html_content and len(html_content) > 150:
                content = html_content
            else:
                # === FALLBACK ke RSS CONTENT jika HTML gagal ===
                if "content" in entry and entry.content:
                    content = entry.content[0].value
                elif "summary" in entry:
                    content = entry.summary

            # VALIDASI MINIMAL
            if len(content) < 150:
                logger.debug(f"Tribun Lampung: Content too short ({len(content)} chars): {title}")
                continue

            # Apply authentic article filter
            if not self._is_authentic_article(title, link, content):
                logger.debug(f"Tribun Lampung: Skipping non-authentic article: {title}")
                continue

            articles.append(self._create_article_dict(title, link, "Tribun Lampung", content))
            # time.sleep(5)

        logger.info(f"Tribun Lampung: {len(articles)} artikel")
        return articles
    
    def crawl_lampung_pro(self):
        """
        Lampung Pro crawler - crawls category pages to find articles
        """
        base = "https://lampungpro.co"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            r = requests.get(base, headers=headers, timeout=15)
            r.raise_for_status()
            home_soup = BeautifulSoup(r.text, "html.parser")
        except Exception:
            logger.exception("Lampung Pro: gagal fetch")
            return []

        articles = []
        seen = set()

        # Find category page links on homepage
        category_urls = set()
        for link in home_soup.find_all("a", href=True):
            href = link.get("href", "").strip()
            if "/kategori/news/" in href:
                if href.startswith("/"):
                    href = base + href
                category_urls.add(href)
        
        logger.debug(f"Lampung Pro: Found {len(category_urls)} category pages")

        # Crawl articles from each category page
        for cat_url in list(category_urls)[:5]:  # Limit to 5 categories
            try:
                r = requests.get(cat_url, headers=headers, timeout=15)
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")
            except Exception:
                logger.debug(f"Lampung Pro: Failed to fetch category: {cat_url[:50]}")
                continue

            # Extract article links from category page
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if not href:
                    continue
                if href.startswith("/"):
                    href = base + href
                
                if not is_link_active(href):
                    continue
                if "lampungpro.co" not in href.lower():
                    continue
                # Article links: /news/XXX (not /kategori/news/)
                if "/news/" not in href.lower() or "/kategori/news/" in href.lower():
                    continue
                if not self._is_valid_article_url(href, "lampungpro.co"):
                    continue
                if href in seen:
                    continue
                seen.add(href)

                title = a.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                content = self.get_article_content(href, {"name": "Lampung Pro"})
                if not content or len(content) < 150:
                    continue
                if not self._is_authentic_article(title, href, content):
                    continue

                logger.debug(f"Lampung Pro: Accepted - {title[:50]}")
                articles.append(self._create_article_dict(title, href, "Lampung Pro", content))

                if len(articles) >= self.max_per_source:
                    break
            
            if len(articles) >= self.max_per_source:
                break

        logger.info(f"Lampung Pro: {len(articles)} artikel")
        return articles
    
    
    def extract_article(self, element, source):
        """Extract article data dari HTML element"""
        # Implementasi sesuai dengan struktur website
        # Contoh sederhana:
        
        # Penyocokan struktur Kompas
        title_tag = (
            element.select_one('h3.article__title a') or
            element.select_one('h2') or
            element.select_one('a.item__link')['href'] or
            element.select_one('a')['href'] or
            element['href'] or
            element.select_one(".story__title a") or 
            element.select_one(".media__title a") or   # Detik
            element.select_one(".item-title a")
        )

        if not title_tag:
            return None

        title = title_tag.get_text(strip=True)
        link = title_tag['href']

        # Perbaikan untuk link relatif
        if link.startswith('/'):
            if source['name'] == 'Kompas':
                link = "https://kompas.com" + link
            elif source['name'] == 'Detik':
                link = "https://news.detik.com" + link
        
        # Get full content
        article_content = self.get_article_content(link)
        
        return {
            'title': title,
            'content': article_content,
            'url': link,
            'source': source['name'],
            'crawled_date': datetime.utcnow()
        }
    
    def get_article_content(self, url, source=None):
        """
        Fetch article content from a URL with timeout handling and link status tracking.
        
        Args:
            url: Article URL to fetch
            source: Source information (dict with 'name' key)
            
        Returns:
            Article content text, or empty string if fetch fails
        """
        # Check if link is marked as inactive - skip if it is
        if not is_link_active(url):
            logger.debug(f"Skipping inactive link: {url}")
            return ""
        
        source_name = source.get("name", "Unknown") if source else "Unknown"
        
        try:
            r = requests.get(
                url, 
                timeout=20, 
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0 Safari/537.36"
                    ),
                    "Referer": "https://lampung.tribunnews.com"
                }
            )
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "lxml")

            selectors = [
                "div.post-content",          # Radar Lampung (Disway)
                "div.post-body",             # fallback Disway
                "div#article-content",       # Kompas
                "div.read__content",         # Kompas
                "div.detail__body-text",     # Detik
                "div.content-article",       # Suara
                "div.box-content",           # Tribun Lampung (TribunOS)
                "div.col-8",                 # Tribun detail page
                "article"
            ]

            for sel in selectors:
                el = soup.select_one(sel)
                if el:
                    content = el.get_text(" ", strip=True)
                    if content:
                        # Mark link as active on successful fetch
                        mark_link_active(url)
                        return content
            
            # Fallback for Lampung Pro: Find div with multiple paragraphs (content container)
            divs = soup.find_all("div")
            for div in divs:
                direct_paragraphs = div.find_all("p", recursive=False)
                if len(direct_paragraphs) >= 3:  # Article content containers have multiple direct p tags
                    content = div.get_text(" ", strip=True)
                    if content and len(content) > 100:
                        mark_link_active(url)
                        return content

            content = soup.get_text(" ", strip=True)
            if content:
                # Mark link as active on successful fetch
                mark_link_active(url)
            return content
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {source_name} article: {url}")
            mark_link_timeout(url, source_name)
            return ""
            
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error fetching {source_name} article: {url}")
            mark_link_inactive(url, "Connection error", source_name)
            return ""
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logger.warning(f"HTTP {status_code} error fetching {source_name} article: {url}")
            reason = f"HTTP {status_code} Error" if status_code != "Unknown" else "HTTP Error"
            mark_link_inactive(url, reason, source_name)
            return ""
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error fetching {source_name} article: {url} - {str(e)}")
            mark_link_inactive(url, f"Request error: {str(e)[:100]}", source_name)
            return ""
            
        except Exception as e:
            logger.exception(f"Unexpected error fetching {source_name} article: {url}")
            mark_link_inactive(url, f"Error: {str(e)[:100]}", source_name)
            return ""

    def _is_navigation_text(self, text: str) -> bool:
        """
        Check if text is likely navigation/UI text rather than article title
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