from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
import hashlib
import json

from app.models import article_model as models
from app.schemas import article_schema as schemas
from app.models import ai_analysis_model
from app.crud import ai_analysis_crud  
from app.services import gemini_service
from app.services.event_publisher import event_publisher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_article_by_url(db: Session, url: str) -> Optional[models.Article]:
    """Lấy article theo URL"""
    return db.query(models.Article).filter(models.Article.url == url).first()

def get_article_by_content_hash(db: Session, content_hash: str) -> Optional[models.Article]:
    """Lấy article theo content hash"""
    return db.query(models.Article).filter(models.Article.content_hash == content_hash).first()

async def create_article(db: Session, article: schemas.ArticleCreate) -> models.Article:
    """Tạo article mới và publish event"""
    
    # Tính content hash
    content_to_hash = (article.title or "") + (article.summary or "")
    content_hash = hashlib.md5(content_to_hash.encode('utf-8')).hexdigest()
    
    # Kiểm tra trùng lặp
    existing_article_by_url = get_article_by_url(db, url=article.url)
    if existing_article_by_url:
        logger.info(f"📄 Article đã tồn tại (URL): {article.title[:50]}...")
        return existing_article_by_url
    
    existing_article_by_hash = get_article_by_content_hash(db, content_hash=content_hash)
    if existing_article_by_hash:
        logger.info(f"📄 Article đã tồn tại (Content): {article.title[:50]}...")
        return existing_article_by_hash
    
    # Tạo article mới
    article_dict = article.dict()
    article_dict['content_hash'] = content_hash
    
    db_article = models.Article(**article_dict)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    
    logger.info(f"✅ Tạo article mới: {article.title[:50]}...")
    
    # **PHÂN TÍCH AI VỚI GEMINI**
    ai_analysis_data = None
    try:
        logger.info(f"🤖 Đang phân tích bài viết bằng Gemini...")
        
        # 1. Tóm tắt
        ai_summary = gemini_service.summarize_article_with_gemini(
            title=db_article.title,
            content=db_article.summary or ""
        )

        # 2. Phân tích toàn diện
        full_analysis = gemini_service.analyze_article_with_gemini(
            title=db_article.title,
            content=db_article.summary or ""
        )

        #Tạo rỗng data trước
        db_ai_analysis = ai_analysis_model.ArticleAIAnalysis(
                article_id=db_article.id,
                summary="",                 # Chuỗi rỗng thay vì None
                category="Không rõ",                   # Không có phân loại
                sentiment_score=0.0,           # Mặc định trung lập
                impact_score=0.0,              # Mặc định 0
                keywords_extracted="[]",       # JSON rỗng
                analysis_metadata="{}"         # Metadata rỗng
            )
        
        if ai_summary:
            db_ai_analysis = ai_analysis_model.ArticleAIAnalysis(
                article_id=db_article.id,
                summary=ai_summary or "",  # Nếu None thì rỗng
            )

        if full_analysis:
            db_ai_analysis.category = full_analysis.get("category", "")
            sentiment_map = {"Tích cực": 1.0, "Trung tính": 0.0, "Tiêu cực": -1.0}
            db_ai_analysis.sentiment_score = sentiment_map.get(full_analysis.get("sentiment"), 0.0)
            impact_map = {"Cao": 1.0, "Trung bình": 0.5, "Thấp": 0.1}
            db_ai_analysis.impact_score = impact_map.get(full_analysis.get("impact_level"), 0.0)
            db_ai_analysis.keywords_extracted = json.dumps(full_analysis.get("key_entities", []), ensure_ascii=False)
            db_ai_analysis.analysis_metadata = json.dumps(full_analysis, ensure_ascii=False)

        # 5. Lưu AI analysis
        db.add(db_ai_analysis)
        db.commit()
        db.refresh(db_ai_analysis)
        
        # Prepare data cho event
        ai_analysis_data = {
            "category": db_ai_analysis.category,
            "sentiment_score": db_ai_analysis.sentiment_score,
            "impact_score": db_ai_analysis.impact_score,
            "keywords": full_analysis.get("key_entities", []) if full_analysis else [],
            "analysis_summary": full_analysis.get("analysis_summary", "") if full_analysis else "",
            "sentiment_text": full_analysis.get("sentiment", "") if full_analysis else "",
            "impact_text": full_analysis.get("impact_level", "") if full_analysis else ""
        }
        
        logger.info(f"✅ Đã lưu AI analysis với ID: {db_ai_analysis.id}")
        
    except Exception as e:
        logger.info(f"⚠️ Lỗi khi phân tích AI: {e}")
        ai_analysis_data = None
    
    # **PUBLISH EVENT THAY VÌ DIRECT CALL**
    try:
        event_data = {
            "event_type": "article_created",
            "article_id": db_article.id,
            "title": db_article.title,
            "url": db_article.url,
            "summary": db_article.summary,
            "source_url": db_article.source_url,
            "created_at": db_article.created_at.isoformat(),
            "ai_analysis": ai_analysis_data,
            "timestamp": datetime.now().isoformat(),
            "service_name": "news_service"
        }
        
        # Publish event async
        await event_publisher.publish_article_created(event_data)
        logger.info(f"📤 Đã publish event cho article: {db_article.title[:50]}...")
        
    except Exception as e:
        logger.info(f"⚠️ Lỗi khi publish event: {e}")
        # Vẫn return article dù publish event thất bại
    
    return db_article

def get_articles(db: Session, skip: int = 0, limit: int = 20) -> List[models.Article]:
    """Lấy danh sách articles với phân trang"""
    return db.query(models.Article)\
             .order_by(models.Article.created_at.desc())\
             .offset(skip)\
             .limit(limit)\
             .all()

def get_articles_count(db: Session) -> int:
    """Đếm tổng số articles"""
    return db.query(models.Article).count()

def get_articles_with_ai_analysis(db: Session, skip: int = 0, limit: int = 20):
    """Lấy articles kèm AI analysis"""
    return ai_analysis_crud.get_articles_with_ai_analysis(db, skip, limit)

def get_articles_by_category(db: Session, category: str):
    """Lấy articles theo category AI"""
    return ai_analysis_crud.get_articles_by_category(db, category)

def get_high_impact_articles(db: Session, min_impact: float = 0.7):
    """Lấy articles có impact cao"""
    return ai_analysis_crud.get_high_impact_articles(db, min_impact)
