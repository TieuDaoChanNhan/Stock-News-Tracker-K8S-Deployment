import requests
import os
import time
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialAPIService:
    """Service for Financial Modeling Prep API integration"""
    
    def __init__(self):
        self.api_key = os.getenv("FMP_API_KEY")
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.request_count = 0
        self.daily_limit = 250
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = 3600  # 1 hour in seconds
        
        if not self.api_key:
            logger.error("❌ FMP_API_KEY không được tìm thấy trong environment variables")
    
    def _make_request(self, endpoint: str, retries: int = 3) -> Optional[Dict]:
        """Make API request with retry logic and rate limiting"""
        
        if self.request_count >= self.daily_limit:
            logger.error("❌ Đã vượt quá rate limit hàng ngày (250 requests)")
            return None
        
        # Check cache first
        cache_key = f"{endpoint}_{datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                logger.info(f"✅ Sử dụng cached data cho {endpoint}")
                return cached_data
        
        url = f"{self.base_url}/{endpoint}"
        params = {"apikey": self.api_key}
        
        for attempt in range(retries):
            try:
                logger.info(f"🔄 API Request [{attempt+1}/{retries}]: {endpoint}")
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                self.request_count += 1
                data = response.json()
                
                # Cache the response
                self.cache[cache_key] = (time.time(), data)
                
                logger.info(f"✅ API Request successful: {endpoint}")
                return data
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Attempt {attempt+1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"❌ All {retries} attempts failed for {endpoint}")
                    return None
        
        return None
    
    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """
        Fetch company basic info từ /profile/{symbol}
        Return: company_name, sector, industry, market_cap, country
        """
        data = self._make_request(f"profile/{symbol.upper()}")
        
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        profile = data[0]
        
        return {
            'symbol': symbol.upper(),
            'company_name': profile.get('companyName', ''),
            'sector': profile.get('sector', ''),
            'industry': profile.get('industry', ''),
            'market_cap': profile.get('mktCap', 0),
            'country': profile.get('country', 'US'),
            'website': profile.get('website', ''),
            'description': profile.get('description', '')
        }
    
    def get_key_metrics(self, symbol: str) -> Optional[Dict]:
        """
        Fetch key metrics từ /key-metrics/{symbol}?limit=1
        Return: pe_ratio, pb_ratio, price_to_sales_ratio, debt_to_equity, roe, roa
        """
        data = self._make_request(f"key-metrics/{symbol.upper()}?limit=1")
        
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        metrics = data[0]
        
        return {
            'pe_ratio': metrics.get('peRatio'),
            'pb_ratio': metrics.get('pbRatio'),
            'price_to_sales_ratio': metrics.get('priceToSalesRatio'),
            'debt_to_equity': metrics.get('debtToEquity'),
            'roe': metrics.get('roe'),
            'roa': metrics.get('roa'),
            'revenue_per_share': metrics.get('revenuePerShare'),
            'net_income_per_share': metrics.get('netIncomePerShare')
        }
    
    def get_financial_ratios(self, symbol: str) -> Optional[Dict]:
        """
        Fetch financial ratios từ /ratios/{symbol}?limit=1
        Return: current_ratio, quick_ratio, cash_ratio, operating_cash_flow_ratio
        """
        data = self._make_request(f"ratios/{symbol.upper()}?limit=1")
        
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        ratios = data[0]
        
        return {
            'current_ratio': ratios.get('currentRatio'),
            'quick_ratio': ratios.get('quickRatio'),
            'cash_ratio': ratios.get('cashRatio'),
            'operating_cash_flow_ratio': ratios.get('operatingCashFlowRatio'),
            'debt_ratio': ratios.get('debtRatio'),
            'gross_profit_margin': ratios.get('grossProfitMargin'),
            'operating_profit_margin': ratios.get('operatingProfitMargin'),
            'net_profit_margin': ratios.get('netProfitMargin')
        }
    
    def get_income_statement(self, symbol: str) -> Optional[Dict]:
        """
        Fetch latest income statement từ /income-statement/{symbol}?limit=1
        Return: revenue, net_income, eps, shares_outstanding
        """
        data = self._make_request(f"income-statement/{symbol.upper()}?limit=1")
        
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        income = data[0]
        
        return {
            'revenue': income.get('revenue'),
            'net_income': income.get('netIncome'),
            'eps': income.get('eps'),
            'shares_outstanding': income.get('weightedAverageShsOut'),
            'gross_profit': income.get('grossProfit'),
            'operating_income': income.get('operatingIncome'),
            'ebitda': income.get('ebitda')
        }
    
    def fetch_all_company_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        Combine tất cả APIs thành một comprehensive metrics dict
        """
        logger.info(f"🔍 Fetching comprehensive metrics for {symbol}")
        
        result = {
            'symbol': symbol.upper(),
            'last_updated': datetime.now().isoformat(),
            'errors': []
        }
        
        # Fetch company profile
        try:
            profile = self.get_company_profile(symbol)
            if profile:
                result.update(profile)
            else:
                result['errors'].append("Failed to fetch company profile")
        except Exception as e:
            result['errors'].append(f"Profile error: {str(e)}")
        
        # Fetch key metrics
        try:
            key_metrics = self.get_key_metrics(symbol)
            if key_metrics:
                result.update(key_metrics)
            else:
                result['errors'].append("Failed to fetch key metrics")
        except Exception as e:
            result['errors'].append(f"Key metrics error: {str(e)}")
        
        # Fetch financial ratios
        try:
            ratios = self.get_financial_ratios(symbol)
            if ratios:
                result.update(ratios)
            else:
                result['errors'].append("Failed to fetch financial ratios")
        except Exception as e:
            result['errors'].append(f"Ratios error: {str(e)}")
        
        # Fetch income statement
        try:
            income = self.get_income_statement(symbol)
            if income:
                result.update(income)
            else:
                result['errors'].append("Failed to fetch income statement")
        except Exception as e:
            result['errors'].append(f"Income statement error: {str(e)}")
        
        logger.info(f"✅ Completed fetching metrics for {symbol}: {len(result)} fields")
        
        return result
    
    def test_api_connection(self) -> bool:
        """Test API connection"""
        try:
            test_data = self.get_company_profile("AAPL")
            if test_data and test_data.get('company_name'):
                logger.info("✅ FMP API connection successful")
                return True
            else:
                logger.error("❌ FMP API test failed - no data returned")
                return False
        except Exception as e:
            logger.error(f"❌ FMP API test failed: {e}")
            return False

# Global instance
financial_api = FinancialAPIService()

# 🚀 MAIN SERVICE FUNCTION CHO SCHEDULER
def fetch_all_active_company_metrics() -> Dict[str, Any]:
    """
    🎯 HÀM CHÍNH: Fetch metrics cho tất cả active companies
    Function này được gọi bởi SCHEDULER
    """
    
    # Import ở đây để tránh circular import
    from app.database import SessionLocal
    from app.crud import company_crud as crud
    
    db = SessionLocal()
    
    try:
        print(f"\n📊 🔄 FINANCIAL SERVICE: Fetching metrics cho tất cả active companies...")
        print(f"🕐 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Lấy tất cả active companies từ bảng 'companies'
        active_companies = crud.get_active_companies(db)
        print(f"🔍 Tìm thấy {len(active_companies)} active companies trong database")
        
        if not active_companies:
            return {
                "message": "Không có active companies trong database", 
                "success_count": 0, 
                "error_count": 0
            }
        
        # Check API usage
        if financial_api.request_count >= financial_api.daily_limit:
            print(f"⚠️ API daily limit đã đạt ({financial_api.daily_limit}), skipping fetch")
            return {
                "message": "API daily limit reached", 
                "success_count": 0, 
                "error_count": 0
            }
        
        success_count = 0
        error_count = 0
        errors = []
        
        for i, company in enumerate(active_companies, 1):
            try:
                print(f"📈 [{i}/{len(active_companies)}] Fetching metrics cho {company.symbol} ({company.company_name})...")
                
                # Check if we're approaching rate limit
                if financial_api.request_count >= financial_api.daily_limit - 5:
                    print(f"⚠️ Sắp đạt API limit, dừng tại {company.symbol}")
                    break
                
                # 🔥 FETCH METRICS TỪ FINANCIAL API SERVICE
                print(f"   🔄 Calling Financial Modeling Prep API via service...")
                metrics_data = financial_api.fetch_all_company_metrics(company.symbol)
                
                if not metrics_data or 'symbol' not in metrics_data:
                    error_count += 1
                    error_msg = f"Không có data từ API cho {company.symbol}"
                    errors.append(error_msg)
                    print(f"   ❌ {error_msg}")
                    continue
                
                # LƯU VÀO BẢNG 'company_metrics' QUA CRUD
                print(f"   💾 Lưu metrics vào database...")
                db_metrics = crud.create_company_metrics(db, company.id, metrics_data)
                
                success_count += 1
                print(f"   ✅ Đã lưu metrics cho {company.symbol}")
                print(f"      📊 PE: {metrics_data.get('pe_ratio')}, Market Cap: {metrics_data.get('market_cap')}")
                print(f"      🆔 Metrics ID: {db_metrics.id}")
                
                # Brief delay để respect rate limits
                time.sleep(1)
                
            except Exception as e:
                error_count += 1
                error_msg = f"Lỗi khi xử lý {company.symbol}: {str(e)}"
                errors.append(error_msg)
                print(f"   ❌ {error_msg}")
                continue
        
        # Summary
        summary = {
            "message": "Hoàn thành fetch company metrics từ Financial API Service",
            "total_companies": len(active_companies),
            "success_count": success_count,
            "error_count": error_count,
            "api_requests_used": financial_api.request_count,
            "api_limit": financial_api.daily_limit,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"\n📊 KẾT QUẢ FINANCIAL SERVICE:")
        print(f"   ✅ Thành công: {success_count} companies")
        print(f"   ❌ Lỗi: {error_count} companies")
        print(f"   🔧 API usage: {financial_api.request_count}/{financial_api.daily_limit}")
        
        return summary
        
    finally:
        db.close()

# Test function
def test_financial_api():
    """Test function"""
    print("🧪 Testing Financial Modeling Prep API...")
    
    if not financial_api.test_api_connection():
        print("❌ API connection failed")
        return
    
    # Test with AAPL
    test_symbol = "AAPL"
    print(f"\n📊 Testing comprehensive fetch for {test_symbol}...")
    
    metrics = financial_api.fetch_all_company_metrics(test_symbol)
    
    print(f"\n📈 Results for {test_symbol}:")
    for key, value in metrics.items():
        if key not in ['errors', 'description', 'last_updated']:
            print(f"   {key}: {value}")
    
    if metrics.get('errors'):
        print(f"\n⚠️ Errors: {metrics['errors']}")

if __name__ == "__main__":
    test_financial_api()
