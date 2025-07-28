import html
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud.watchlist_crud import get_watchlist_items_by_user
from app.services.notification_service import send_telegram_message_sync


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
    """Tạo message cho thông báo triggered keywords - Beautiful HTML Format"""
    
    # Extract data
    category = ai_analysis.get('category', 'Tin tức') if ai_analysis else 'Tin tức'
    sentiment_text = ai_analysis.get('sentiment_text', 'Trung tính') if ai_analysis else 'Trung tính'
    impact_text = ai_analysis.get('impact_text', 'Thấp') if ai_analysis else 'Thấp'
    analysis_summary = ai_analysis.get('analysis_summary', 'Không có phân tích') if ai_analysis else 'Không có phân tích'
    
    # HTML escape
    escaped_category = html.escape(category)
    escaped_impact = html.escape(impact_text)
    escaped_sentiment = html.escape(sentiment_text)
    escaped_keywords = html.escape(', '.join(matched_keywords_list))
    escaped_title = html.escape(event_data['title'])
    escaped_analysis = html.escape(analysis_summary)
    
    # Chọn emoji theo sentiment
    sentiment_emoji = {
        'Tích cực': '📈',
        'Tiêu cực': '📉', 
        'Trung tính': '📊'
    }.get(sentiment_text, '📊')
    
    # Chọn emoji theo impact
    impact_emoji = {
        'Cao': '🔥',
        'Trung bình': '⚡',
        'Thấp': '💡'
    }.get(impact_text, '💡')
    
    # 🎨 Beautiful HTML Format
    message = f"""🎯 <b>WATCHLIST ALERT</b>

🏷️ <b>Từ khóa:</b> <code>{escaped_keywords}</code>
📂 <b>Danh mục:</b> {escaped_category}
{impact_emoji} <b>Tác động:</b> {escaped_impact}
{sentiment_emoji} <b>Tâm lý:</b> {escaped_sentiment}

━━━━━━━━━━━━━━━━━━━━

📰 <b>{escaped_title}</b>

🤖 <i>{escaped_analysis}</i>

<a href="{event_data['url']}">📖 Đọc chi tiết →</a>

<i>⏰ Stock News Tracker Bot</i>"""
    
    return message


def create_impact_notification_message(
    event_data: Dict[str, Any], 
    ai_analysis: Dict[str, Any]
) -> str:
    """Tạo message cho thông báo high impact - Beautiful HTML Format"""
    
    # Extract data
    category = ai_analysis.get('category', 'Tin tức') if ai_analysis else 'Tin tức'
    sentiment_text = ai_analysis.get('sentiment_text', 'Trung tính') if ai_analysis else 'Trung tính'
    impact_text = ai_analysis.get('impact_text', 'Cao') if ai_analysis else 'Cao'
    analysis_summary = ai_analysis.get('analysis_summary', 'Không có phân tích') if ai_analysis else 'Không có phân tích'
    impact_score = ai_analysis.get('impact_score', 0.0) if ai_analysis else 0.0
    
    # HTML escape
    escaped_category = html.escape(category)
    escaped_impact = html.escape(impact_text)
    escaped_sentiment = html.escape(sentiment_text)
    escaped_title = html.escape(event_data['title'])
    escaped_analysis = html.escape(analysis_summary)
    
    # Chọn emoji theo impact level
    if impact_score >= 0.8:
        impact_emoji = "🚨"
        alert_level = "KHẨN CẤP"
    elif impact_score >= 0.7:
        impact_emoji = "🔥"
        alert_level = "CAO"
    else:
        impact_emoji = "⚡"
        alert_level = "TRUNG BÌNH"
    
    # Chọn emoji theo sentiment
    sentiment_emoji = {
        'Tích cực': '📈',
        'Tiêu cực': '📉', 
        'Trung tính': '📊'
    }.get(sentiment_text, '📊')
    
    # 🎨 Beautiful HTML Format
    message = f"""{impact_emoji} <b>TIN TỨC TÁC ĐỘNG {alert_level}</b>

📊 <b>Điểm ảnh hưởng:</b> <code>{impact_score:.2f}/1.0</code>
📂 <b>Danh mục:</b> {escaped_category}
{sentiment_emoji} <b>Tâm lý thị trường:</b> {escaped_sentiment}

━━━━━━━━━━━━━━━━━━━━

📰 <b>{escaped_title}</b>

🔍 <i>Phân tích AI:</i>
<i>{escaped_analysis}</i>

<a href="{event_data['url']}">📖 Đọc ngay để cập nhật thông tin →</a>

<i>🤖 Stock News AI Analysis Bot</i>"""
    
    return message
