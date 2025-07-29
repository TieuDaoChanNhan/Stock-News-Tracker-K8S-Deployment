import requests
from datetime import datetime
import asyncio
from app.database import SessionLocal
from app.crud import crawl_source_crud, article_crud
from app.services.generic_crawler import scrape_news_from_website
from app.schemas.article_schema import ArticleCreate

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_and_process_all_active_sources():
    """Fetch và process tin tức từ các nguồn đang hoạt động"""
    logger.info(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Bắt đầu chu kỳ crawl tin tức...")
    
    db = SessionLocal()
    total_articles = 0
    
    try:
        # Lấy danh sách nguồn crawl active
        sources = crawl_source_crud.get_active_crawl_sources(db)
        logger.info(f"📊 Tìm thấy {len(sources)} nguồn đang hoạt động.")
        
        for source in sources:
            try:
                logger.info(f"🔄 Crawling: {source.name}")
                
                # Crawl articles từ nguồn
                articles_data = scrape_news_from_website(
                    page_url=source.url,
                    article_container_selector=source.article_container_selector,
                    title_selector=source.title_selector,
                    link_selector=source.link_selector,
                    summary_selector=source.summary_selector,
                    date_selector=source.date_selector,
                    source_name=source.name,
                    max_articles=5
                )
                
                # Lưu articles vào database
                for article_data in articles_data:
                    try:
                        article_create = ArticleCreate(
                            title=article_data['title'],
                            url=article_data['url'],
                            summary=article_data['summary'],
                            published_date_str=article_data['published_date_str'],
                            source_url=source.url
                        )
                        
                        # Async create article sẽ tự động trigger AI analysis và publish event
                        await article_crud.create_article(db, article_create)
                        total_articles += 1
                        
                    except Exception as e:
                        logger.info(f"   ❌ Lỗi khi lưu article: {e}")
                        continue
                
                # Cập nhật thời gian crawl cuối
                crawl_source_crud.update_crawl_source_last_crawled_at(
                    db, source.id, datetime.now()
                )
                
            except Exception as e:
                logger.info(f"❌ Lỗi khi crawl {source.name}: {e}")
                continue
        
        logger.info(f"✅ Hoàn thành chu kỳ crawl: {total_articles} articles đã được xử lý")
        
    finally:
        db.close()

def main():
    """Main function để chạy một lần"""
    logger.info("🚀 News Service Scheduler - Single Run")
    logger.info("=" * 60)
    
    # Chạy async function
    asyncio.run(fetch_and_process_all_active_sources())
    
    logger.info("✅ News Service Scheduler completed!")

if __name__ == "__main__":
    main()
