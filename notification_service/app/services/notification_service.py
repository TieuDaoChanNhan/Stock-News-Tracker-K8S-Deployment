import os
import asyncio
import logging
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

def escape_markdown_v2(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2"""
    # Danh sách đầy đủ các ký tự cần escape theo Telegram API docs
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    # Escape từng ký tự
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

async def send_telegram_message_async(message: str, target_chat_id: Optional[str] = None):
    """Gửi tin nhắn Telegram (async)"""
    if not telegram:
        logger.error("❌ python-telegram-bot chưa được cài đặt")
        return False
    
    chat_id = target_chat_id or CHAT_ID
    
    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN không được cấu hình trong .env")
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
                parse_mode='MarkdownV2',
                disable_web_page_preview=False
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
    """Gửi tin nhắn Telegram (sync wrapper) - SỬA LỖI EVENT LOOP"""
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
    """Format tin nhắn thông báo tin tức"""
    # Escape markdown cho title và URL
    escaped_title = escape_markdown_v2(article_title)
    escaped_url = escape_markdown_v2(article_url)
    
    # Tạo danh sách keywords
    keywords_str = ", ".join(matched_keywords)
    escaped_keywords = escape_markdown_v2(keywords_str)
    
    # Format message
    message = f"""🔔 *Tin mới liên quan đến* \\[{escaped_keywords}\\]\\!

*{escaped_title}*

[Đọc ngay]({escaped_url})"""
    
    return message

# Test function
def test_telegram_connection():
    """Test kết nối Telegram"""
    test_message = "🧪 Test kết nối từ Stock News Tracker\\!"
    result = send_telegram_message_sync(test_message)
    if result:
        print("✅ Kết nối Telegram thành công!")
    else:
        print("❌ Kết nối Telegram thất bại!")
    return result

if __name__ == "__main__":
    test_telegram_connection()
