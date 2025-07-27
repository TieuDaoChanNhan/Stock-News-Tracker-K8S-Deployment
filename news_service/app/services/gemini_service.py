import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import json
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    logger.info("CẢNH BÁO: GOOGLE_API_KEY không được tìm thấy trong file .env")

def call_gemini(prompt: str, model_name: str = "gemini-1.5-flash") -> Optional[str]:
    """
    Gửi một prompt đến Gemini API và nhận về text response.
    """
    if not GOOGLE_API_KEY:
        logger.info("Lỗi: Không thể gọi Gemini API vì thiếu API Key.")
        return None
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.info(f"Lỗi khi gọi Gemini API: {e}")
        return None

def extract_json_from_markdown(text: str) -> str:
    """
    Trích xuất JSON từ markdown code block hoặc text thuần túy.
    Xử lý các trường hợp:
    - ``````
    - ``````  
    - {...} (JSON thuần túy)
    """
    # Loại bỏ whitespace đầu cuối
    text = text.strip()
    
    # Pattern 1: ``````
    pattern1 = r'``````'
    match1 = re.search(pattern1, text, re.DOTALL)
    if match1:
        return match1.group(1).strip()
    
    # Pattern 2: ``````
    pattern2 = r'``````'
    match2 = re.search(pattern2, text, re.DOTALL)
    if match2:
        return match2.group(1).strip()
    
    # Pattern 3: Tìm JSON object đầu tiên trong text
    pattern3 = r'\{.*\}'
    match3 = re.search(pattern3, text, re.DOTALL)
    if match3:
        return match3.group(0).strip()
    
    # Fallback: trả về text gốc
    return text

def summarize_article_with_gemini(title: str, content: str) -> Optional[str]:
    """
    Tóm tắt một bài báo bằng cách sử dụng Gemini API.
    """
    if not content or len(content.strip()) < 100:
        return content

    prompt = f"""
    Bạn là một trợ lý phân tích tài chính chuyên nghiệp. Nhiệm vụ của bạn là đọc tiêu đề và đoạn trích của một bài báo kinh tế bằng tiếng Việt và tóm tắt lại các ý chính một cách ngắn gọn, súc tích, tập trung vào những thông tin có thể ảnh hưởng đến thị trường chứng khoán.

    **Yêu cầu:**
    1.  Tóm tắt trong khoảng 6-7 câu (khoảng 175 từ).
    2.  Giữ giọng văn trung lập, khách quan.
    3.  Loại bỏ các thông tin không cần thiết, chỉ giữ lại những gì quan trọng nhất.
    4.  Trả lời chỉ bằng nội dung tóm tắt, không thêm lời chào hay câu dẫn.

    **Tiêu đề bài báo:**
    "{title}"

    **Nội dung trích dẫn:**
    "{content}"

    **Bản tóm tắt của bạn:**
    """
    summary = call_gemini(prompt)
    return summary

def analyze_article_with_gemini(title: str, content: str) -> Optional[Dict[str, Any]]:
    """
    Phân tích một bài báo toàn diện bằng Gemini API, bao gồm phân loại,
    đánh giá sentiment, tác động và trích xuất thông tin.
    """
    if not content or len(content.strip()) < 50:
        return None

    prompt = f"""
    Bạn là một chuyên gia phân tích tài chính vĩ mô cho thị trường chứng khoán Việt Nam.
    Hãy phân tích bài báo sau đây và trả về kết quả dưới dạng một JSON object.

    **Bài báo:**
    - Tiêu đề: "{title}"
    - Nội dung: "{content}"

    **Yêu cầu phân tích (trả về dưới dạng JSON object với các key sau):**

    1.  "category": Phân loại bài báo vào một trong các danh mục sau: "Địa chính trị", "Chính sách tiền tệ", "Chính sách tài khóa", "Giá vàng", "Tỷ giá USD", "Tin tức doanh nghiệp", "Thị trường chung", "Không liên quan".
    2.  "sentiment": Đánh giá cảm xúc của tin tức đối với thị trường chứng khoán Việt Nam. Chỉ trả về một trong ba giá trị: "Tích cực", "Tiêu cực", "Trung tính".
    3.  "impact_level": Đánh giá mức độ tác động dự kiến của tin tức này đến thị trường. Chỉ trả về một trong ba giá trị: "Cao", "Trung bình", "Thấp".
    4.  "key_entities": Trích xuất một danh sách (array) các thực thể quan trọng nhất được đề cập, ví dụ như tên quốc gia, tổ chức, công ty, hoặc các chỉ số kinh tế (tối đa 5 thực thể).
    5.  "analysis_summary": Viết một câu phân tích ngắn gọn (tối đa 25 từ) giải thích TẠI SAO tin tức này lại có sentiment và mức độ tác động như vậy.

    **Ví dụ định dạng JSON output mong muốn:**
    {{
      "category": "Chính sách tiền tệ",
      "sentiment": "Tiêu cực",
      "impact_level": "Cao",
      "key_entities": ["FED", "Lãi suất", "Lạm phát"],
      "analysis_summary": "Việc FED tăng lãi suất có thể gây áp lực rút vốn ngoại và ảnh hưởng tiêu cực đến tỷ giá."
    }}

    **QUAN TRỌNG: Chỉ trả về JSON object thuần túy, không bao bọc trong markdown code block. Không sử dụng backticks. Bắt đầu trực tiếp bằng dấu {{ và kết thúc bằng dấu }}.**

    **JSON object kết quả phân tích của bạn:**
    """

    analysis_str = call_gemini(prompt)
    if not analysis_str:
        return None

    try:
        # Sử dụng hàm extract_json_from_markdown để parse JSON
        clean_json_str = extract_json_from_markdown(analysis_str)
        analysis_json = json.loads(clean_json_str)
        return analysis_json
    except json.JSONDecodeError as e:
        logger.info(f"Lỗi khi parse JSON từ Gemini: {e}\nResponse gốc: {analysis_str}")
        return None

# ===== CÁC MODULE PHÂN TÍCH CHUYÊN BIỆT =====

def analyze_geopolitics_with_gemini(title: str, content: str) -> Optional[Dict[str, Any]]:
    """Module phân tích địa chính trị"""
    prompt = f"""
    Bạn là chuyên gia phân tích địa chính trị. Hãy đọc bài báo sau và trả về kết quả dưới dạng JSON với các trường:
    - "risk_level": "Cao", "Trung bình", "Thấp"
    - "main_countries": danh sách các quốc gia liên quan (tối đa 3)
    - "summary": tóm tắt 1-2 câu về rủi ro địa chính trị

    Tiêu đề: "{title}"
    Nội dung: "{content}"

    Chỉ trả về JSON object thuần túy:
    """
    result = call_gemini(prompt)
    if not result:
        return None
    try:
        clean_json_str = extract_json_from_markdown(result)
        return json.loads(clean_json_str)
    except Exception as e:
        logger.info(f"Lỗi parse JSON Geopolitics: {e}\n{result}")
        return None

def analyze_policy_with_gemini(title: str, content: str) -> Optional[Dict[str, Any]]:
    """Module phân tích chính sách"""
    prompt = f"""
    Bạn là chuyên gia phân tích chính sách kinh tế. Hãy đọc bài báo sau và trả về JSON với:
    - "policy_type": "Tiền tệ", "Tài khóa", "Khác"
    - "sentiment": "Tích cực", "Trung tính", "Tiêu cực"
    - "impact": "Cao", "Trung bình", "Thấp"
    - "summary": 1 câu giải thích

    Tiêu đề: "{title}"
    Nội dung: "{content}"

    Chỉ trả về JSON object thuần túy:
    """
    result = call_gemini(prompt)
    if not result:
        return None
    try:
        clean_json_str = extract_json_from_markdown(result)
        return json.loads(clean_json_str)
    except Exception as e:
        logger.info(f"Lỗi parse JSON Policy: {e}\n{result}")
        return None

def analyze_gold_with_gemini(title: str, content: str) -> Optional[Dict[str, Any]]:
    """Module phân tích giá vàng"""
    prompt = f"""
    Bạn là chuyên gia phân tích thị trường vàng. Đọc bài báo sau và trả về JSON với:
    - "trend": "Tăng", "Giảm", "Ổn định"
    - "impact_reason": giải thích ngắn gọn
    - "summary": 1 câu tổng kết

    Tiêu đề: "{title}"
    Nội dung: "{content}"

    Chỉ trả về JSON object thuần túy:
    """
    result = call_gemini(prompt)
    if not result:
        return None
    try:
        clean_json_str = extract_json_from_markdown(result)
        return json.loads(clean_json_str)
    except Exception as e:
        logger.info(f"Lỗi parse JSON Gold: {e}\n{result}")
        return None

def analyze_usd_index_with_gemini(title: str, content: str) -> Optional[Dict[str, Any]]:
    """Module phân tích giá Dollar Index"""
    prompt = f"""
    Bạn là chuyên gia phân tích chỉ số Dollar Index. Đọc bài báo sau và trả về JSON với:
    - "trend": "Tăng", "Giảm", "Ổn định"
    - "impact_reason": giải thích ngắn gọn
    - "summary": 1 câu tổng kết

    Tiêu đề: "{title}"
    Nội dung: "{content}"

    Chỉ trả về JSON object thuần túy:
    """
    result = call_gemini(prompt)
    if not result:
        return None
    try:
        clean_json_str = extract_json_from_markdown(result)
        return json.loads(clean_json_str)
    except Exception as e:
        logger.info(f"Lỗi parse JSON USD Index: {e}\n{result}")
        return None

def analyze_article_all_with_gemini(title: str, content: str) -> Dict[str, Any]:
    """
    Module tổng hợp - gọi tất cả các module phân tích chuyên biệt
    """
    result = {
        "summary": summarize_article_with_gemini(title, content),
        "general_analysis": analyze_article_with_gemini(title, content),
        "geopolitics": analyze_geopolitics_with_gemini(title, content),
        "policy": analyze_policy_with_gemini(title, content),
        "gold": analyze_gold_with_gemini(title, content),
        "usd_index": analyze_usd_index_with_gemini(title, content)
    }
    return result
