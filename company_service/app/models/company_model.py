from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, BigInteger, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Company(Base):
    """
    Bảng lưu thông tin cơ bản của các công ty
    Được populate bởi setup_company.py
    """
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)  # AAPL, MSFT
    company_name = Column(String(200), nullable=False)                    # Apple Inc.
    sector = Column(String(100), nullable=True)                          # Technology
    industry = Column(String(100), nullable=True)                        # Consumer Electronics
    country = Column(String(10), default="US")                           # US, EU, etc.
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)                            # Enable/disable tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship với metrics
    metrics = relationship("CompanyMetrics", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(symbol='{self.symbol}', name='{self.company_name}')>"

class CompanyMetrics(Base):
    """
    Bảng lưu dữ liệu tài chính fetch từ Financial API
    Được populate bởi scheduler
    """
    __tablename__ = "company_metrics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    symbol = Column(String(10), index=True, nullable=False)               # Denormalized for performance
    
    # Valuation metrics từ API
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    price_to_sales_ratio = Column(Float, nullable=True)
    market_cap = Column(BigInteger, nullable=True)
    
    # Profitability metrics từ API  
    eps = Column(Float, nullable=True)
    revenue = Column(BigInteger, nullable=True)                           # TTM revenue
    net_income = Column(BigInteger, nullable=True)                        # TTM net income
    roe = Column(Float, nullable=True)                                    # Return on Equity
    roa = Column(Float, nullable=True)                                    # Return on Assets
    gross_profit = Column(BigInteger, nullable=True)
    operating_income = Column(BigInteger, nullable=True)
    ebitda = Column(BigInteger, nullable=True)
    
    # Financial health metrics từ API
    debt_to_equity = Column(Float, nullable=True)
    current_ratio = Column(Float, nullable=True)
    quick_ratio = Column(Float, nullable=True)
    cash_ratio = Column(Float, nullable=True)
    debt_ratio = Column(Float, nullable=True)
    
    # Profitability ratios từ API
    gross_profit_margin = Column(Float, nullable=True)
    operating_profit_margin = Column(Float, nullable=True)
    net_profit_margin = Column(Float, nullable=True)
    operating_cash_flow_ratio = Column(Float, nullable=True)
    
    # Additional metrics từ API
    shares_outstanding = Column(BigInteger, nullable=True)
    revenue_per_share = Column(Float, nullable=True)
    net_income_per_share = Column(Float, nullable=True)
    
    # Metadata
    data_source = Column(String(50), default="FMP")                      # Financial Modeling Prep
    raw_data = Column(Text, nullable=True)                               # Full API response JSON
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)  # Khi fetch data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship với company
    company = relationship("Company", back_populates="metrics")
    
    def __repr__(self):
        return f"<CompanyMetrics(symbol='{self.symbol}', pe={self.pe_ratio}, recorded_at='{self.recorded_at}')>"