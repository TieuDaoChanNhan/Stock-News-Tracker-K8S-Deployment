from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models import crawl_source_model as models
from app.schemas import crawl_source_schema as schemas

def create_crawl_source(db: Session, source: schemas.CrawlSourceCreate) -> models.CrawlSource:
    """Tạo nguồn crawl mới"""
    db_source = models.CrawlSource(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    print(f"✅ Tạo nguồn crawl mới: {source.name}")
    return db_source

def get_crawl_source(db: Session, source_id: int) -> Optional[models.CrawlSource]:
    """Lấy nguồn crawl theo ID"""
    return db.query(models.CrawlSource).filter(models.CrawlSource.id == source_id).first()

def get_crawl_sources(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[models.CrawlSource]:
    """Lấy danh sách nguồn crawl"""
    query = db.query(models.CrawlSource)
    
    if is_active is not None:
        query = query.filter(models.CrawlSource.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

def get_active_crawl_sources(db: Session) -> List[models.CrawlSource]:
    """Lấy danh sách nguồn crawl đang hoạt động"""
    return db.query(models.CrawlSource).filter(models.CrawlSource.is_active == True).all()

def update_crawl_source(db: Session, source_id: int, source_update: schemas.CrawlSourceUpdate) -> Optional[models.CrawlSource]:
    """Cập nhật nguồn crawl"""
    db_source = get_crawl_source(db, source_id)
    if not db_source:
        return None
    
    update_data = source_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_source, field, value)
    
    db_source.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_source)
    return db_source

def update_crawl_source_last_crawled_at(db: Session, source_id: int, last_crawled_at: datetime) -> Optional[models.CrawlSource]:
    """Cập nhật thời gian crawl cuối"""
    db_source = get_crawl_source(db, source_id)
    if not db_source:
        return None
    
    db_source.last_crawled_at = last_crawled_at
    db_source.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_source)
    return db_source

def delete_crawl_source(db: Session, source_id: int) -> bool:
    """Xóa nguồn crawl"""
    db_source = get_crawl_source(db, source_id)
    if not db_source:
        return False
    
    db.delete(db_source)
    db.commit()
    return True
