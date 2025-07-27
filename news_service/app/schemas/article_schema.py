from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    published_date_str: Optional[str] = None
    source_url: str

class ArticleCreate(ArticleBase):
    pass

class ArticleInDB(ArticleBase):
    id: int
    content_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
