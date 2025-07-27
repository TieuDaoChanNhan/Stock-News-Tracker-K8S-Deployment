from datetime import datetime
from app.services.financial_api_service import fetch_all_active_company_metrics

def main():
    """Main function để chạy một lần"""
    print("🚀 Company Service Scheduler - Single Run")
    print("=" * 60)
    
    # Fetch metrics cho tất cả active companies
    result = fetch_all_active_company_metrics()
    
    print(f"📊 Kết quả:")
    print(f"   ✅ Thành công: {result.get('success_count', 0)} companies")
    print(f"   ❌ Lỗi: {result.get('error_count', 0)} companies")
    print(f"   🔧 API usage: {result.get('api_requests_used', 0)}/{result.get('api_limit', 0)}")
    
    print("✅ Company Service Scheduler completed!")

if __name__ == "__main__":
    main()
