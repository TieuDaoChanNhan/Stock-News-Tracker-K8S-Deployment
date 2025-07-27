import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_news_from_website(
    page_url: str,
    article_container_selector: str,
    title_selector: str,
    link_selector: str,
    summary_selector: Optional[str] = None,
    date_selector: Optional[str] = None,
    source_name: str = "Unknown",
    max_articles: int = 1
) -> List[Dict[str, str]]:
    """
    Generic crawler function để crawl từ bất kỳ website nào
    """
    articles = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
        }
        
        response = requests.get(page_url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tìm các container chứa bài viết
        article_containers = soup.select(article_container_selector)
        logger.info(f"Tìm thấy {len(article_containers)} containers từ {source_name}")
        
        # Giới hạn số lượng bài viết
        article_containers = article_containers[:max_articles]
        
        for idx, container in enumerate(article_containers):
            try:
                # Trích xuất tiêu đề
                title_element = container.select_one(title_selector)
                title = title_element.get_text(strip=True) if title_element else ""
                
                if not title:
                    logger.info(f"Bỏ qua container {idx+1}: Không có tiêu đề")
                    continue
                
                # Trích xuất link
                link_element = container.select_one(link_selector)
                if link_element:
                    url = link_element.get('href', '')
                    if url.startswith('/'):
                        from urllib.parse import urljoin
                        url = urljoin(page_url, url)
                else:
                    url = ""
                
                # Trích xuất tóm tắt
                summary = ""
                if summary_selector:
                    summary_element = container.select_one(summary_selector)
                    summary = summary_element.get_text(strip=True) if summary_element else ""
                
                # Trích xuất ngày tháng
                published_date = ""
                if date_selector:
                    date_element = container.select_one(date_selector)
                    published_date = date_element.get_text(strip=True) if date_element else ""
                
                article_data = {
                    'title': title,
                    'url': url,
                    'summary': summary,
                    'published_date_str': published_date,
                    'source_page': source_name,
                    'collected_at_iso': datetime.now().isoformat()
                }
                
                articles.append(article_data)
                logger.info(f"✅ Crawled: {title[:50]}...")
                
            except Exception as e:
                logger.error(f"Lỗi khi xử lý container {idx+1}: {str(e)}")
                continue
        
        time.sleep(1)  # Delay để tránh bị block
        
    except requests.RequestException as e:
        logger.error(f"Lỗi kết nối khi crawl {source_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Lỗi không xác định khi crawl {source_name}: {str(e)}")
    
    return articles