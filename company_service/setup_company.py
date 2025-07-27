import os
import sys
from datetime import datetime
from typing import List

from app.database import SessionLocal, init_db
from app.crud import company_crud as crud
from app.schemas import company_schema as schemas

def setup_popular_companies() -> List[str]:
    """Setup initial companies for company service"""
    
    popular_companies = [
        {"symbol": "AAPL", "company_name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
        {"symbol": "MSFT", "company_name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"},
        {"symbol": "GOOGL", "company_name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Services"},
        {"symbol": "TSLA", "company_name": "Tesla Inc.", "sector": "Technology", "industry": "Electric Vehicles"},
        {"symbol": "NVDA", "company_name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
        # {"symbol": "META", "company_name": "Meta Platforms Inc.", "sector": "Technology", "industry": "Social Media"},
        # {"symbol": "JPM", "company_name": "JPMorgan Chase & Co.", "sector": "Financial", "industry": "Banking"},
        # {"symbol": "BAC", "company_name": "Bank of America Corp", "sector": "Financial", "industry": "Banking"},
        # {"symbol": "JNJ", "company_name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Pharmaceuticals"},
        # {"symbol": "PFE", "company_name": "Pfizer Inc.", "sector": "Healthcare", "industry": "Pharmaceuticals"},
        # {"symbol": "KO", "company_name": "The Coca-Cola Company", "sector": "Consumer", "industry": "Beverages"},
        # {"symbol": "PG", "company_name": "Procter & Gamble Co", "sector": "Consumer", "industry": "Consumer Goods"},
        # {"symbol": "XOM", "company_name": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Oil & Gas"},
        # {"symbol": "CVX", "company_name": "Chevron Corporation", "sector": "Energy", "industry": "Oil & Gas"},
        # {"symbol": "WMT", "company_name": "Walmart Inc.", "sector": "Retail", "industry": "Discount Stores"},
        # {"symbol": "AMZN", "company_name": "Amazon.com Inc.", "sector": "Retail", "industry": "E-commerce"},
    ]
    
    db = SessionLocal()
    added_symbols = []
    
    try:
        print("🏢 COMPANY SERVICE: Setting up initial companies...")
        
        for company_data in popular_companies:
            try:
                existing = crud.get_company_by_symbol(db, company_data['symbol'])
                if existing:
                    print(f"   ⚠️ {company_data['symbol']} already exists, skipping...")
                    continue
                
                company_create = schemas.CompanyCreate(**company_data)
                db_company = crud.create_company(db, company_create)
                added_symbols.append(company_data['symbol'])
                print(f"   ✅ Added {company_data['symbol']} - {company_data['company_name']}")
                
            except Exception as e:
                print(f"   ❌ Error adding {company_data['symbol']}: {e}")
                continue
        
        print(f"🎉 Company setup completed: {len(added_symbols)} companies added")
        return added_symbols
        
    finally:
        db.close()

def main():
    """Main setup function for company service"""
    print("🚀 Company Service - Initial Setup")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    # Setup companies
    added_symbols = setup_popular_companies()
    
    # Set environment variable to mark setup as complete
    os.environ['COMPANY_SETUP_COMPLETE'] = 'true'
    
    print("✅ Company Service setup completed successfully!")

if __name__ == "__main__":
    main()
    sys.exit(0)
