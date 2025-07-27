from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class WatchlistItemBase(BaseModel):
    item_type: str  # 'STOCK_SYMBOL' hoặc 'KEYWORD'
    item_value: str  # Mã cổ phiếu hoặc từ khóa

class WatchlistItemCreate(WatchlistItemBase):
    pass

class WatchlistItemInDB(WatchlistItemBase):
    id: int
    user_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
