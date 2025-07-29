import os
import sys
from app.database import SessionLocal, init_db
from app.crud import watchlist_crud as crud
from app.schemas import watchlist_schema as schemas
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_default_watchlist():
    """Setup default watchlist for notification service"""
    
    USER_ID = "ong_x"
    
    sample_watchlist = [
        # Keywords quan trọng
        {"item_type": "KEYWORD", "item_value": "lãi suất"},
        {"item_type": "KEYWORD", "item_value": "bất động sản"},
        {"item_type": "KEYWORD", "item_value": "chứng khoán"},
        {"item_type": "KEYWORD", "item_value": "ngân hàng"},
        {"item_type": "KEYWORD", "item_value": "kinh tế"},
        {"item_type": "KEYWORD", "item_value": "Mỹ"},
        {"item_type": "KEYWORD", "item_value": "Fed"},
        {"item_type": "KEYWORD", "item_value": "inflation"},
        {"item_type": "KEYWORD", "item_value": "GDP"},
        {"item_type": "KEYWORD", "item_value": "vàng"},
        
        # # Stock symbols
        # {"item_type": "STOCK_SYMBOL", "item_value": "AAPL"},
        # {"item_type": "STOCK_SYMBOL", "item_value": "MSFT"},
        # {"item_type": "STOCK_SYMBOL", "item_value": "GOOGL"},
        # {"item_type": "STOCK_SYMBOL", "item_value": "TSLA"},
        # {"item_type": "STOCK_SYMBOL", "item_value": "NVDA"},
    ]
    
    db = SessionLocal()
    added_items = []
    
    try:
        logger.info("🔔 NOTIFICATION SERVICE: Setting up default watchlist...")
        
        # Check if user already has watchlist
        existing_items = crud.get_watchlist_items_by_user(db, USER_ID)
        if existing_items:
            logger.info(f"   ⚠️ User {USER_ID} already has {len(existing_items)} watchlist items, skipping...")
            return [item.item_value for item in existing_items]
        
        for item_data in sample_watchlist:
            try:
                item_create = schemas.WatchlistItemCreate(**item_data)
                db_item = crud.create_watchlist_item(db, item_create, USER_ID)
                added_items.append(item_data['item_value'])
                logger.info(f"   ✅ Added {item_data['item_value']} ({item_data['item_type']})")
                
            except Exception as e:
                logger.info(f"   ❌ Error adding {item_data['item_value']}: {e}")
                continue
        
        logger.info(f"🎉 Watchlist setup completed: {len(added_items)} items added for user {USER_ID}")
        return added_items
        
    finally:
        db.close()

def main():
    """Main setup function for notification service"""
    logger.info("🚀 Notification Service - Initial Setup")
    logger.info("=" * 50)
    
    # Initialize database
    init_db()
    
    # Setup watchlist
    added_items = setup_default_watchlist()
    
    # Set environment variable to mark setup as complete
    os.environ['NOTIFICATION_SETUP_COMPLETE'] = 'true'
    
    logger.info("✅ Notification Service setup completed successfully!")
    return len(added_items) > 0

if __name__ == "__main__":
    main()
    sys.exit(0)
