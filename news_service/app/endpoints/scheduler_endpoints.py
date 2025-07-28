from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime
import asyncio
from app.database import SessionLocal
from app.crud import crawl_source_crud, article_crud
from app.services.generic_crawler import scrape_news_from_website
from app.schemas.article_schema import ArticleCreate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news-scheduler", tags=["scheduler"])

@router.post("/run")
async def trigger_news_scheduler(background_tasks: BackgroundTasks):
    """Manually trigger news crawling scheduler"""
    try:
        logger.info(f"🔄 Manual trigger news scheduler at {datetime.now()}")
        
        # Chạy scheduler trong background để không block request
        background_tasks.add_task(run_news_scheduler)
        
        return {
            "message": "News scheduler triggered successfully",
            "status": "running_in_background", 
            "service": "news_service",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger scheduler: {str(e)}"
        )

@router.get("/status")
async def get_scheduler_status():
    """Get scheduler status"""
    return {
        "service": "news_service",
        "scheduler_status": "ready",
        "description": "Crawls news from active sources and processes with AI",
        "endpoint": "/api/v1/scheduler/run"
    }

async def run_news_scheduler():
    """Function được gọi bởi endpoint để chạy scheduler"""
    logger.info(f"🚀 News Service Scheduler - Manual Run")
    logger.info("=" * 60)
    
    db = SessionLocal()
    total_articles = 0
    
    try:
        # Lấy danh sách nguồn crawl active
        sources = crawl_source_crud.get_active_crawl_sources(db)
        print(f"📊 Tìm thấy {len(sources)} nguồn đang hoạt động.")
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
                    max_articles=1
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
                        
                        # Async create article sẽ tự động trigger AI analysis
                        await article_crud.create_article(db, article_create)
                        total_articles += 1
                        
                    except Exception as e:
                        print(f"   ❌ Lỗi khi lưu article: {e}")
                        continue
                
                # Cập nhật thời gian crawl cuối
                crawl_source_crud.update_crawl_source_last_crawled_at(
                    db, source.id, datetime.now()
                )
                
            except Exception as e:
                print(f"❌ Lỗi khi crawl {source.name}: {e}")
                continue
        
        print(f"✅ Hoàn thành chu kỳ crawl: {total_articles} articles đã được xử lý")
        logger.info(f"✅ Hoàn thành chu kỳ crawl: {total_articles} articles đã được xử lý")
        
    finally:
        db.close()
    
    print("✅ News Service Scheduler completed!")
    logger.info("✅ News Service Scheduler completed!")
    return {"total_articles_processed": total_articles}
