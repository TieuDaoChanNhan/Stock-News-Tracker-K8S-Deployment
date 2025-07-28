import os
import asyncio
import logging
import html
from typing import Optional, List
from dotenv import load_dotenv
import concurrent.futures

# Load environment variables
load_dotenv()

# Telegram imports
try:
    import telegram
    from telegram.error import TelegramError
except ImportError:
    print("⚠️ Cần cài đặt: pip install python-telegram-bot")
    telegram = None

# Cấu hình
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID_DEFAULT")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log configuration status (không expose sensitive data)
if BOT_TOKEN:
    logger.info(f"🔧 Telegram bot token configured (length: {len(BOT_TOKEN)})")
else:
    logger.error("❌ TELEGRAM_BOT_TOKEN not configured")

if CHAT_ID:
    logger.info(f"🔧 Telegram chat ID configured: {CHAT_ID}")
else:
    logger.error("❌ TELEGRAM_CHAT_ID_DEFAULT not configured")


def escape_html(text: str) -> str:
    """Escape HTML special characters for Telegram HTML parsing"""
    if not text:
        return ""
    
    # HTML escape để tránh conflict với HTML tags
    return html.escape(text)


async def send_telegram_message_async(message: str, target_chat_id: Optional[str] = None):
    """Gửi tin nhắn Telegram (async) - HTML Format"""
    if not telegram:
        logger.error("❌ python-telegram-bot chưa được cài đặt")
        return False
    
    chat_id = target_chat_id or CHAT_ID
    
    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN không được cấu hình")
        return False
    
    if not chat_id:
        logger.error("❌ TELEGRAM_CHAT_ID không được cấu hình")
        return False
    
    try:
        bot = telegram.Bot(token=BOT_TOKEN)
        async with bot:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML',  # 🔄 CHUYỂN SANG HTML
                disable_web_page_preview=False,
                disable_notification=False
            )
        
        logger.info(f"✅ Đã gửi thông báo Telegram đến {chat_id}")
        return True
        
    except TelegramError as e:
        logger.error(f"❌ Lỗi Telegram: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Lỗi không xác định: {e}")
        return False


def send_telegram_message_sync(message: str, target_chat_id: Optional[str] = None):
    """Gửi tin nhắn Telegram (sync wrapper) - Fixed Event Loop"""
    try:
        # Kiểm tra xem có event loop đang chạy không
        try:
            loop = asyncio.get_running_loop()
            # Nếu có event loop đang chạy, sử dụng thread pool
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(send_telegram_message_async(message, target_chat_id))
                )
                return future.result(timeout=30)  # Timeout 30 giây
        except RuntimeError:
            # Không có event loop đang chạy, có thể dùng asyncio.run()
            return asyncio.run(send_telegram_message_async(message, target_chat_id))
            
    except Exception as e:
        logger.error(f"❌ Lỗi khi gửi tin nhắn sync: {e}")
        return False


def format_news_notification(article_title: str, article_url: str, matched_keywords: List[str]) -> str:
    """Format tin nhắn thông báo tin tức - HTML Beautiful Format"""
    
    # HTML escape cho title và keywords (URL không cần escape)
    escaped_title = escape_html(article_title)
    keywords_str = ", ".join(matched_keywords)
    escaped_keywords = escape_html(keywords_str)
    
    # 🎨 Beautiful HTML Format
    message = f"""📢 <b>TIN TỨC MỚI</b>

🎯 <b>Từ khóa quan tâm:</b> <code>{escaped_keywords}</code>

📰 <b>{escaped_title}</b>

<a href="{article_url}">📖 Đọc chi tiết →</a>

<i>🤖 Stock News Tracker Bot</i>"""
    
    return message


def format_test_message() -> str:
    """Format test message - HTML Beautiful Format"""
    message = f"""🧪 <b>TEST CONNECTION</b>

✅ <i>Kết nối thành công từ Stock News Tracker Bot!</i>

🤖 <code>System Status: Online</code>"""
    
    return message


def test_telegram_connection():
    """Test kết nối Telegram với HTML format"""
    test_message = format_test_message()
    result = send_telegram_message_sync(test_message)
    if result:
        print("✅ Kết nối Telegram thành công!")
    else:
        print("❌ Kết nối Telegram thất bại!")
    return result


if __name__ == "__main__":
    test_telegram_connection()
