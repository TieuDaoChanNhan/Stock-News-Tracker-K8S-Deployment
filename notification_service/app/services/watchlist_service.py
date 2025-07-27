from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud.watchlist_crud import get_watchlist_items_by_user
from app.services.notification_service import (
    send_telegram_message_sync, 
    escape_markdown_v2
)

async def check_and_process_article_notification(event_data: Dict[str, Any]):
    """Kiểm tra watchlist và gửi thông báo dựa trên event data"""
    
    db = SessionLocal()
    
    try:
        print(f"🔍 Processing notification for article: {event_data['title']}")
        
        # Lấy watchlist của user
        watchlist_items = get_watchlist_items_by_user(db, user_id='ong_x')
        
        if not watchlist_items:
            print("🔍 No watchlist items found")
            return
        
        triggered_keywords = set()
        
        # Chuẩn bị text để kiểm tra
        article_title_lower = event_data['title'].lower()
        article_summary_lower = (event_data.get('summary') or "").lower()
        
        # Kiểm tra từng item trong watchlist
        for item in watchlist_items:
            keyword_to_check = item.item_value.lower()
            
            if (keyword_to_check in article_title_lower or 
                keyword_to_check in article_summary_lower):
                triggered_keywords.add(item.item_value)
        
        # Lấy AI analysis data
        ai_analysis = event_data.get('ai_analysis', {})
        impact_score = ai_analysis.get('impact_score', 0.0) if ai_analysis else 0.0
        
        # **ĐIỀU KIỆN 1: CÓ TRIGGERED KEYWORDS**
        if triggered_keywords:
            matched_keywords_list = list(triggered_keywords)
            print(f"🔔 Found match with watchlist: {matched_keywords_list}")
            
            message = create_keyword_notification_message(
                event_data, ai_analysis, matched_keywords_list
            )
            
            success = send_telegram_message_sync(message=message)
            
            if success:
                print(f"✅ Sent KEYWORD notification for: {matched_keywords_list}")
            else:
                print(f"❌ Failed to send KEYWORD notification")
        
        # **ĐIỀU KIỆN 2: HIGH IMPACT (0.5+)**
        elif impact_score >= 0.5:
            print(f"📊 High impact article: {ai_analysis.get('impact_text', 'N/A')} (score: {impact_score})")
            
            message = create_impact_notification_message(event_data, ai_analysis)
            
            success = send_telegram_message_sync(message=message)
            
            if success:
                print(f"✅ Sent HIGH IMPACT notification")
            else:
                print(f"❌ Failed to send HIGH IMPACT notification")
        
        else:
            print("🔍 No notification criteria met")
            
    except Exception as e:
        print(f"❌ Error processing notification: {e}")
    finally:
        db.close()

def create_keyword_notification_message(
    event_data: Dict[str, Any], 
    ai_analysis: Dict[str, Any], 
    matched_keywords_list: List[str]
) -> str:
    """Tạo message cho thông báo triggered keywords"""
    
    # Extract data
    category = ai_analysis.get('category', 'Tin tức') if ai_analysis else 'Tin tức'
    sentiment_text = ai_analysis.get('sentiment_text', 'N/A') if ai_analysis else 'N/A'
    impact_text = ai_analysis.get('impact_text', 'N/A') if ai_analysis else 'N/A'
    analysis_summary = ai_analysis.get('analysis_summary', '') if ai_analysis else ''
    
    # Escape markdown
    escaped_category = escape_markdown_v2(category.upper())
    escaped_impact = escape_markdown_v2(impact_text)
    escaped_sentiment = escape_markdown_v2(sentiment_text)
    escaped_keywords = escape_markdown_v2(', '.join(matched_keywords_list))
    escaped_title = escape_markdown_v2(event_data['title'])
    escaped_analysis = escape_markdown_v2(analysis_summary)
    escaped_url = escape_markdown_v2(event_data['url'])
    
    # Format message
    message_parts = [
        f"🎯 *WATCHLIST ALERT*",
        f"📂 {escaped_category} \\| 📊 {escaped_impact} \\| 💭 {escaped_sentiment}",
        f"🔍 Từ khóa: *{escaped_keywords}*",
        "\\-\\-\\-",
        f"*{escaped_title}*",
        f"_{escaped_analysis}_",
        "",
        f"[Đọc ngay]({escaped_url})"
    ]
    
    return "\n".join(message_parts)

def create_impact_notification_message(
    event_data: Dict[str, Any], 
    ai_analysis: Dict[str, Any]
) -> str:
    """Tạo message cho thông báo high impact"""
    
    # Extract data
    category = ai_analysis.get('category', 'Tin tức') if ai_analysis else 'Tin tức'
    sentiment_text = ai_analysis.get('sentiment_text', 'N/A') if ai_analysis else 'N/A'
    impact_text = ai_analysis.get('impact_text', 'N/A') if ai_analysis else 'N/A'
    analysis_summary = ai_analysis.get('analysis_summary', '') if ai_analysis else ''
    
    # Escape markdown
    escaped_category = escape_markdown_v2(category.upper())
    escaped_impact = escape_markdown_v2(impact_text)
    escaped_sentiment = escape_markdown_v2(sentiment_text)
    escaped_title = escape_markdown_v2(event_data['title'])
    escaped_analysis = escape_markdown_v2(analysis_summary)
    escaped_url = escape_markdown_v2(event_data['url'])
    
    # Chọn emoji theo impact level
    impact_emoji = "🔥" if impact_text == "Cao" else "⚡"
    
    # Format message
    message_parts = [
        f"{impact_emoji} *TIN TỨC TÁC ĐỘNG {escaped_impact.upper()}*",
        f"📂 {escaped_category} \\| 💭 {escaped_sentiment}",
        "\\-\\-\\-",
        f"*{escaped_title}*",
        f"_{escaped_analysis}_",
        "",
        f"[Đọc ngay]({escaped_url})"
    ]
    
    return "\n".join(message_parts)
