from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import watchlist_crud as crud
from app.schemas import watchlist_schema as schemas
from app.database import get_db

router = APIRouter(prefix="/users/{user_id}/watchlist", tags=["watchlist"])

@router.post("", response_model=schemas.WatchlistItemInDB, status_code=status.HTTP_201_CREATED)
async def add_watchlist_item(
    user_id: str,
    item: schemas.WatchlistItemCreate,
    db: Session = Depends(get_db)
):
    """Thêm item vào watchlist"""
    try:
        db_item = crud.create_watchlist_item(db=db, item=item, user_id=user_id)
        return db_item
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi thêm vào watchlist: {str(e)}"
        )

@router.get("", response_model=List[schemas.WatchlistItemInDB])
async def get_watchlist(user_id: str, db: Session = Depends(get_db)):
    """Lấy danh sách watchlist của user"""
    try:
        items = crud.get_watchlist_items_by_user(db=db, user_id=user_id)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy watchlist: {str(e)}"
        )

@router.delete("/{item_id}", response_model=schemas.WatchlistItemInDB)
async def remove_watchlist_item(
    user_id: str,
    item_id: int,
    db: Session = Depends(get_db)
):
    """Xóa item khỏi watchlist"""
    item = crud.delete_watchlist_item(db=db, item_id=item_id, user_id=user_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item không tồn tại hoặc không thuộc về user này"
        )
    return item
