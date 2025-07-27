from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ArticleCreatedEvent(BaseModel):
    event_type: str = "article_created"
    article_id: int
    title: str
    url: str
    summary: Optional[str] = None
    source_url: str
    created_at: datetime
    
    # AI Analysis data (nếu có)
    ai_analysis: Optional[Dict[str, Any]] = None
    
    # Metadata
    timestamp: datetime = datetime.now()
    service_name: str = "news_service"
