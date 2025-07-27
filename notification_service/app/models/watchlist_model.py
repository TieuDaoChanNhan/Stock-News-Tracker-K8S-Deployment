from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True, default='ong_x')  # Tạm thời cố định
    item_type = Column(String, nullable=False)  # 'STOCK_SYMBOL' hoặc 'KEYWORD'
    item_value = Column(String, nullable=False, index=True)  # Mã CK hoặc từ khóa
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<WatchlistItem(id={self.id}, user='{self.user_id}', type='{self.item_type}', value='{self.item_value}')>"
