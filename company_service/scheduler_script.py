from datetime import datetime
from app.services.financial_api_service import fetch_all_active_company_metrics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function để chạy một lần"""
    logger.info("🚀 Company Service Scheduler - Single Run")
    logger.info("=" * 60)
    
    # Fetch metrics cho tất cả active companies
    result = fetch_all_active_company_metrics()
    
    logger.info(f"📊 Kết quả:")
    logger.info(f"   ✅ Thành công: {result.get('success_count', 0)} companies")
    logger.info(f"   ❌ Lỗi: {result.get('error_count', 0)} companies")
    logger.info(f"   🔧 API usage: {result.get('api_requests_used', 0)}/{result.get('api_limit', 0)}")
    
    logger.info("✅ Company Service Scheduler completed!")

if __name__ == "__main__":
    main()
