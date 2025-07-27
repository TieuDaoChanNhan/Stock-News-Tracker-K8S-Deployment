import os
import sys
from app.database import SessionLocal, init_db
from app.crud import crawl_source_crud as crud
from app.schemas import crawl_source_schema as schemas

def setup_sample_sources():
    """Setup initial crawl sources for news service"""
    
    sample_sources = [
        {
        "name": "VnExpress - Doanh nghiệp",
        "url": "https://vnexpress.net/kinh-doanh/doanh-nghiep",
        "article_container_selector": ".item-news",
        "title_selector": "h3 a, h2 a",
        "link_selector": "h3 a, h2 a",
        "summary_selector": ".description",
        "date_selector": ".time",
        "is_active": True
        },
        {
        "name": "VnExpress - Chính trị",
        "url": "https://vnexpress.net/thoi-su/chinh-tri",
        "article_container_selector": ".item-news",
        "title_selector": "h3 a, h2 a",
        "link_selector": "h3 a, h2 a",
        "summary_selector": ".description",
        "date_selector": ".time",
        "is_active": True
        },
        {
        "name": "VnExpress - Luật doanh nghiệp",
        "url": "https://vnexpress.net/chu-de/luat-doanh-nghiep-7163",
        "article_container_selector": ".item-news",
        "title_selector": "h3 a, h2 a",
        "link_selector": "h3 a, h2 a",
        "summary_selector": ".description",
        "date_selector": ".time",
        "is_active": True
        },
        {
        "name": "VnExpress - Kinh doanh",
        "url": "https://vnexpress.net/kinh-doanh",
        "article_container_selector": ".item-news",
        "title_selector": "h3 a, h2 a",
        "link_selector": "h3 a, h2 a",
        "summary_selector": ".description",
        "date_selector": ".time",
        "is_active": True
        },
        {
        "name": "VnExpress - Giá vàng",
        "url": "https://vnexpress.net/chu-de/gia-vang-1403",
        "article_container_selector": ".item-news",
        "title_selector": "h3 a, h2 a",
        "link_selector": "h3 a, h2 a",
        "summary_selector": ".description",
        "date_selector": ".time",
        "is_active": True
        },
        {
        "name": "VnExpress - Giá USD",
        "url": "https://vnexpress.net/tag/gia-usd-267904",
        "article_container_selector": ".item-news",
        "title_selector": "h3 a, h2 a",
        "link_selector": "h3 a, h2 a",
        "summary_selector": ".description",
        "date_selector": ".time",
        "is_active": True
        },
        {
        "name": "VnExpress - Kinh doanh",
        "url": "https://vnexpress.net/kinh-doanh",
        "article_container_selector": ".item-news",
        "title_selector": "h3 a, h2 a",
        "link_selector": "h3 a, h2 a",
        "summary_selector": ".description",
        "date_selector": ".time",
        "is_active": True
        },
        {
        "name": "VnExpress - Khoa học công nghệ",
        "url": "https://vnexpress.net/khoa-hoc-cong-nghe",
        "article_container_selector": ".item-news",
        "title_selector": "h3 a, h2 a",
        "link_selector": "h3 a, h2 a",
        "summary_selector": ".description",
        "date_selector": ".time",
        "is_active": True
        },
    ]
    
    db = SessionLocal()
    added_sources = []
    
    try:
        print("📰 NEWS SERVICE: Setting up crawl sources...")
        
        for source_data in sample_sources:
            try:
                # Check if source already exists
                existing_sources = crud.get_crawl_sources(db, limit=1000)
                if any(s.name == source_data['name'] for s in existing_sources):
                    print(f"   ⚠️ {source_data['name']} already exists, skipping...")
                    continue
                
                source_create = schemas.CrawlSourceCreate(**source_data)
                db_source = crud.create_crawl_source(db, source_create)
                added_sources.append(source_data['name'])
                print(f"   ✅ Added {source_data['name']}")
                
            except Exception as e:
                print(f"   ❌ Error adding {source_data['name']}: {e}")
                continue
        
        print(f"🎉 News sources setup completed: {len(added_sources)} sources added")
        return added_sources
        
    finally:
        db.close()

def main():
    """Main setup function for news service"""
    print("🚀 News Service - Initial Setup")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    # Setup crawl sources
    added_sources = setup_sample_sources()
    
    # Set environment variable to mark setup as complete
    os.environ['NEWS_SETUP_COMPLETE'] = 'true'
    
    print("✅ News Service setup completed successfully!")

if __name__ == "__main__":
    main()
    sys.exit(0)
