from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CompanyBase(BaseModel):
    symbol: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: str = "US"
    website: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class CompanyInDB(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CompanyMetricsBase(BaseModel):
    symbol: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    price_to_sales_ratio: Optional[float] = None
    market_cap: Optional[int] = None
    eps: Optional[float] = None
    revenue: Optional[int] = None
    net_income: Optional[int] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    gross_profit: Optional[int] = None
    operating_income: Optional[int] = None
    ebitda: Optional[int] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None
    debt_ratio: Optional[float] = None
    gross_profit_margin: Optional[float] = None
    operating_profit_margin: Optional[float] = None
    net_profit_margin: Optional[float] = None
    operating_cash_flow_ratio: Optional[float] = None
    shares_outstanding: Optional[int] = None
    revenue_per_share: Optional[float] = None
    net_income_per_share: Optional[float] = None

class CompanyMetricsCreate(CompanyMetricsBase):
    company_id: int

class CompanyMetricsInDB(CompanyMetricsBase):
    id: int
    company_id: int
    data_source: str
    recorded_at: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CompanyWithLatestMetrics(CompanyInDB):
    latest_metrics: Optional[CompanyMetricsInDB] = None
    