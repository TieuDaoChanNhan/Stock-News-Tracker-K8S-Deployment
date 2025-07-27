# backend/app/schemas/ai_analysis_schema.py
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Union
from datetime import datetime
import json

class AIAnalysisBase(BaseModel):
    summary: Optional[str] = None
    category: Optional[str] = None
    sentiment_score: Optional[float] = None
    impact_score: Optional[float] = None
    keywords_extracted: Optional[List[str]] = None
    analysis_metadata: Optional[str] = None

class AIAnalysisCreate(AIAnalysisBase):
    article_id: int

class AIAnalysisResponse(AIAnalysisBase):
    id: int
    article_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('keywords_extracted', mode='before')
    @classmethod
    def parse_keywords_extracted(cls, v):
        """Parse JSON string thành list nếu cần"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                # Parse JSON string thành list
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else None
            except (json.JSONDecodeError, TypeError):
                return None
        if isinstance(v, list):
            return v
        return None
    
    @field_validator('analysis_metadata', mode='before')
    @classmethod
    def parse_analysis_metadata(cls, v):
        """Parse JSON string cho analysis_metadata nếu cần"""
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, dict):
            try:
                return json.dumps(v, ensure_ascii=False)
            except (TypeError, ValueError):
                return str(v)
        return str(v)

class ArticleWithAIResponse(BaseModel):
    # Article fields
    id: int
    title: str
    url: str
    summary: Optional[str]
    
    # AI Analysis
    ai_analysis: Optional[AIAnalysisResponse] = None
    
    model_config = ConfigDict(from_attributes=True)
