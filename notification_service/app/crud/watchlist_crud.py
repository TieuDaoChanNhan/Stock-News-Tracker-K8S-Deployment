from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import watchlist_model as models
from app.schemas import watchlist_schema as schemas

def create_watchlist_item(db: Session, item: schemas.WatchlistItemCreate, user_id: str) -> models.WatchlistItem:
    """Tạo item watchlist mới"""
    # Kiểm tra trùng lặp
    existing_item = db.query(models.WatchlistItem).filter(
        models.WatchlistItem.user_id == user_id,
        models.WatchlistItem.item_type == item.item_type,
        models.WatchlistItem.item_value == item.item_value
    ).first()
    
    if existing_item:
        print(f"⚠️ Item đã tồn tại: {item.item_value}")
        return existing_item
    
    db_item = models.WatchlistItem(
        user_id=user_id,
        item_type=item.item_type,
        item_value=item.item_value
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    print(f"✅ Đã thêm vào watchlist: {item.item_value} ({item.item_type})")
    return db_item

def get_watchlist_items_by_user(db: Session, user_id: str) -> List[models.WatchlistItem]:
    """Lấy danh sách watchlist của user"""
    return db.query(models.WatchlistItem).filter(models.WatchlistItem.user_id == user_id).all()

def delete_watchlist_item(db: Session, item_id: int, user_id: str) -> Optional[models.WatchlistItem]:
    """Xóa item khỏi watchlist"""
    item = db.query(models.WatchlistItem).filter(
        models.WatchlistItem.id == item_id,
        models.WatchlistItem.user_id == user_id
    ).first()
    
    if item:
        db.delete(item)
        db.commit()
        print(f"✅ Đã xóa khỏi watchlist: {item.item_value}")
        return item
    
    return None

def get_watchlist_item_by_id(db: Session, item_id: int) -> Optional[models.WatchlistItem]:
    """Lấy watchlist item theo ID"""
    return db.query(models.WatchlistItem).filter(models.WatchlistItem.id == item_id).first()
