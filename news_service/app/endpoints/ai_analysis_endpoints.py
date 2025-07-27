# backend/app/api/endpoints/ai_analysis_endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import ai_analysis_crud as crud
from app.schemas import ai_analysis_schema as schemas
from app.database import get_db

router = APIRouter(prefix="/ai-analysis", tags=["ai-analysis"])

@router.get("/article/{article_id}", response_model=schemas.AIAnalysisResponse)
async def get_ai_analysis(article_id: int, db: Session = Depends(get_db)):
    """Lấy AI analysis của bài báo"""
    try:
        # Sử dụng function đã sửa để trả về parsed data
        ai_analysis = crud.get_ai_analysis_by_article_id(db, article_id)
        
        if not ai_analysis:
            raise HTTPException(
                status_code=404, 
                detail=f"AI analysis not found for article {article_id}"
            )
        
        return ai_analysis  # Đã được parse trong CRUD
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching AI analysis: {str(e)}"
        )

@router.get("/category/{category}", response_model=List[schemas.ArticleWithAIResponse])
async def get_articles_by_category(category: str, db: Session = Depends(get_db)):
    """Lấy articles theo category"""
    return crud.get_articles_by_category(db, category)

@router.get("/high-impact", response_model=List[schemas.ArticleWithAIResponse])
async def get_high_impact_articles(min_impact: float = 0.7, db: Session = Depends(get_db)):
    """Lấy articles có impact cao"""
    return crud.get_high_impact_articles(db, min_impact)
