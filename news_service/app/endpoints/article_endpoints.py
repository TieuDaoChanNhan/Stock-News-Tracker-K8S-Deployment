from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import article_crud as crud
from app.schemas import article_schema as schemas
from app.database import get_db

# Tạo router
router = APIRouter(prefix="/articles", tags=["articles"])

@router.post("", response_model=schemas.ArticleInDB, status_code=status.HTTP_201_CREATED)
async def create_new_article(
    article: schemas.ArticleCreate, 
    db: Session = Depends(get_db)
):
    """Tạo article mới"""
    try:
        db_article = crud.create_article(db=db, article=article)
        return db_article
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo article: {str(e)}"
        )

@router.get("", response_model=List[schemas.ArticleInDB])
async def read_articles(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """Lấy danh sách articles"""
    try:
        articles = crud.get_articles(db=db, skip=skip, limit=limit)
        return articles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách articles: {str(e)}"
        )

@router.get("/count")
async def get_articles_count(db: Session = Depends(get_db)):
    """Đếm tổng số articles"""
    try:
        count = crud.get_articles_count(db=db)
        return {"total_articles": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi đếm articles: {str(e)}"
        )

@router.get("/{article_id}", response_model=schemas.ArticleInDB)
async def read_article(article_id: int, db: Session = Depends(get_db)):
    """Lấy article theo ID"""
    try:
        article = db.query(crud.models.Article).filter(crud.models.Article.id == article_id).first()
        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article không tồn tại"
            )
        return article
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy article: {str(e)}"
        )
