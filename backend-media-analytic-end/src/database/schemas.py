from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ArticleBase(BaseModel):
    title: str
    content: str
    source: Optional[str] = None
    url: str
    published_date: Optional[datetime] = None
    keywords_flagged: Optional[str] = None
    sentiment: Optional[str] = None
    confidence: Optional[float] = None
    prob_negative: Optional[float] = None
    prob_neutral: Optional[float] = None
    prob_positive: Optional[float] = None
    category: Optional[str] = None
    author: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: int
    crawled_date: datetime

    class Config:
        from_attributes = True

class NewsSourceBase(BaseModel):
    name: str
    base_url: str
    crawl_type: str = "auto"  # 'rss', 'html', 'sitemap', 'auto'
    config: dict
    active: bool = True
    auto_detect: bool = True

class NewsSourceCreate(NewsSourceBase):
    pass

class NewsSourceUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    crawl_type: Optional[str] = None
    config: Optional[dict] = None
    active: Optional[bool] = None
    auto_detect: Optional[bool] = None

class NewsSource(NewsSourceBase):
    id: int
    is_hardcoded: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FavoriteBase(BaseModel):
    article_id: int

class FavoriteCreate(FavoriteBase):
    pass

class Favorite(FavoriteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SearchHistoryBase(BaseModel):
    keyword: str

class SearchHistoryCreate(SearchHistoryBase):
    pass

class SearchHistory(SearchHistoryBase):
    id: int
    search_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Legacy schemas for backward compatibility
class HistoryBase(BaseModel):
    user_id: str
    article_id: int
    action: str

class HistoryCreate(HistoryBase):
    pass

class History(HistoryBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
