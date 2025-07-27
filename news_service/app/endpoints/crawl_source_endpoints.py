from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud import crawl_source_crud as crud
from app.schemas import crawl_source_schema as schemas
from app.database import get_db

router = APIRouter(prefix="/crawl-sources", tags=["crawl-sources"])

@router.post("", response_model=schemas.CrawlSourceInDB, status_code=status.HTTP_201_CREATED)
async def create_crawl_source(
    source: schemas.CrawlSourceCreate, 
    db: Session = Depends(get_db)
):
    """Tạo nguồn crawl mới"""
    try:
        return crud.create_crawl_source(db=db, source=source)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo nguồn crawl: {str(e)}"
        )

@router.get("", response_model=List[schemas.CrawlSourceInDB])
async def read_crawl_sources(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    db: Session = Depends(get_db)
):
    """Lấy danh sách nguồn crawl"""
    try:
        sources = crud.get_crawl_sources(db=db, skip=skip, limit=limit, is_active=is_active)
        return sources
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách nguồn crawl: {str(e)}"
        )

@router.get("/{source_id}", response_model=schemas.CrawlSourceInDB)
async def read_crawl_source(source_id: int, db: Session = Depends(get_db)):
    """Lấy nguồn crawl theo ID"""
    source = crud.get_crawl_source(db=db, source_id=source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nguồn crawl không tồn tại"
        )
    return source

@router.put("/{source_id}", response_model=schemas.CrawlSourceInDB)
async def update_crawl_source(
    source_id: int,
    source_update: schemas.CrawlSourceUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật nguồn crawl"""
    source = crud.update_crawl_source(db=db, source_id=source_id, source_update=source_update)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nguồn crawl không tồn tại"
        )
    return source

@router.delete("/{source_id}")
async def delete_crawl_source(source_id: int, db: Session = Depends(get_db)):
    """Xóa nguồn crawl"""
    success = crud.delete_crawl_source(db=db, source_id=source_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nguồn crawl không tồn tại"
        )
    return {"message": "Đã xóa nguồn crawl thành công"}
