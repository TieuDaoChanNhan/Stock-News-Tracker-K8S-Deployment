from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CrawlSourceBase(BaseModel):
    name: str
    url: str
    article_container_selector: str
    title_selector: str
    link_selector: str
    summary_selector: Optional[str] = None
    date_selector: Optional[str] = None
    is_active: bool = True

class CrawlSourceCreate(CrawlSourceBase):
    pass

class CrawlSourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    article_container_selector: Optional[str] = None
    title_selector: Optional[str] = None
    link_selector: Optional[str] = None
    summary_selector: Optional[str] = None
    date_selector: Optional[str] = None
    is_active: Optional[bool] = None
    last_crawled_at: Optional[datetime] = None

class CrawlSourceInDB(CrawlSourceBase):
    id: int
    last_crawled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
