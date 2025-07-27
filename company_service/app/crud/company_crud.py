from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from app.models import company_model as models
from app.schemas import company_schema as schemas

# Company CRUD operations
def create_company(db: Session, company: schemas.CompanyCreate) -> models.Company:
    """Tạo company mới"""
    # Check if already exists
    existing = get_company_by_symbol(db, company.symbol)
    if existing:
        return existing
    
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_companies(db: Session, skip: int = 0, limit: int = 50, active_only: bool = True) -> List[models.Company]:
    """Lấy danh sách companies"""
    query = db.query(models.Company)
    
    if active_only:
        query = query.filter(models.Company.is_active == True)
    
    return query.offset(skip).limit(limit).all()

def get_company_by_symbol(db: Session, symbol: str) -> Optional[models.Company]:
    """Lấy company theo symbol"""
    return db.query(models.Company).filter(models.Company.symbol == symbol.upper()).first()

def get_active_companies(db: Session) -> List[models.Company]:
    """Lấy tất cả companies đang active"""
    return db.query(models.Company).filter(models.Company.is_active == True).all()

def update_company(db: Session, symbol: str, company_update: schemas.CompanyUpdate) -> Optional[models.Company]:
    """Cập nhật company"""
    db_company = get_company_by_symbol(db, symbol)
    if not db_company:
        return None
    
    update_data = company_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_company, field, value)
    
    db_company.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_company)
    return db_company

def delete_company(db: Session, symbol: str) -> bool:
    """Xóa company"""
    db_company = get_company_by_symbol(db, symbol)
    if not db_company:
        return False
    
    db.delete(db_company)
    db.commit()
    return True

# Company Metrics CRUD operations
def create_company_metrics(db: Session, company_id: int, metrics_data: Dict[str, Any]) -> models.CompanyMetrics:
    """Tạo company metrics mới"""
    
    # Prepare metrics data
    db_metrics = models.CompanyMetrics(
        company_id=company_id,
        symbol=metrics_data.get('symbol', '').upper(),
        pe_ratio=metrics_data.get('pe_ratio'),
        pb_ratio=metrics_data.get('pb_ratio'),
        price_to_sales_ratio=metrics_data.get('price_to_sales_ratio'),
        market_cap=metrics_data.get('market_cap'),
        eps=metrics_data.get('eps'),
        revenue=metrics_data.get('revenue'),
        net_income=metrics_data.get('net_income'),
        roe=metrics_data.get('roe'),
        roa=metrics_data.get('roa'),
        gross_profit=metrics_data.get('gross_profit'),
        operating_income=metrics_data.get('operating_income'),
        ebitda=metrics_data.get('ebitda'),
        debt_to_equity=metrics_data.get('debt_to_equity'),
        current_ratio=metrics_data.get('current_ratio'),
        quick_ratio=metrics_data.get('quick_ratio'),
        cash_ratio=metrics_data.get('cash_ratio'),
        debt_ratio=metrics_data.get('debt_ratio'),
        gross_profit_margin=metrics_data.get('gross_profit_margin'),
        operating_profit_margin=metrics_data.get('operating_profit_margin'),
        net_profit_margin=metrics_data.get('net_profit_margin'),
        operating_cash_flow_ratio=metrics_data.get('operating_cash_flow_ratio'),
        shares_outstanding=metrics_data.get('shares_outstanding'),
        revenue_per_share=metrics_data.get('revenue_per_share'),
        net_income_per_share=metrics_data.get('net_income_per_share'),
        raw_data=json.dumps(metrics_data, ensure_ascii=False)
    )
    
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

def get_latest_metrics_by_symbol(db: Session, symbol: str) -> Optional[models.CompanyMetrics]:
    """Lấy metrics mới nhất của company"""
    return db.query(models.CompanyMetrics).filter(
        models.CompanyMetrics.symbol == symbol.upper()
    ).order_by(models.CompanyMetrics.recorded_at.desc()).first()

def get_metrics_history(db: Session, symbol: str, limit: int = 10) -> List[models.CompanyMetrics]:
    """Lấy lịch sử metrics của company"""
    return db.query(models.CompanyMetrics).filter(
        models.CompanyMetrics.symbol == symbol.upper()
    ).order_by(models.CompanyMetrics.recorded_at.desc()).limit(limit).all()

def get_companies_with_latest_metrics(db: Session, active_only: bool = True) -> List[Dict[str, Any]]:
    """Lấy companies kèm metrics mới nhất"""
    companies = get_companies(db, active_only=active_only)
    
    result = []
    for company in companies:
        latest_metrics = get_latest_metrics_by_symbol(db, company.symbol)
        
        company_dict = {
            'company': company,
            'latest_metrics': latest_metrics
        }
        
        result.append(company_dict)
    
    return result
