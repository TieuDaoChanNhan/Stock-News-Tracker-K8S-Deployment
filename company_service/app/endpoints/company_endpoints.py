from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.crud import company_crud as crud
from app.schemas import company_schema as schemas
from app.database import get_db
from app.services.financial_api_service import financial_api

router = APIRouter(prefix="/companies", tags=["companies"])

@router.post("", response_model=schemas.CompanyInDB, status_code=status.HTTP_201_CREATED)
async def create_company(
    company: schemas.CompanyCreate, 
    db: Session = Depends(get_db)
):
    """Add new company to tracking list"""
    try:
        # Check if company already exists
        existing = crud.get_company_by_symbol(db, company.symbol)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Company with symbol {company.symbol} already exists"
            )
        
        db_company = crud.create_company(db=db, company=company)
        return db_company
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating company: {str(e)}"
        )

@router.get("", response_model=List[schemas.CompanyInDB])
async def list_companies(
    skip: int = 0, 
    limit: int = 50, 
    active_only: bool = True, 
    db: Session = Depends(get_db)
):
    """List all companies with optional filtering"""
    try:
        companies = crud.get_companies(db=db, skip=skip, limit=limit, active_only=active_only)
        return companies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching companies: {str(e)}"
        )

@router.get("/{symbol}", response_model=schemas.CompanyInDB)
async def get_company(symbol: str, db: Session = Depends(get_db)):
    """Get specific company by symbol"""
    try:
        company = crud.get_company_by_symbol(db, symbol)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with symbol {symbol} not found"
            )
        return company
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching company: {str(e)}"
        )

@router.put("/{symbol}", response_model=schemas.CompanyInDB)
async def update_company(
    symbol: str, 
    company_update: schemas.CompanyUpdate, 
    db: Session = Depends(get_db)
):
    """Update company info or toggle active status"""
    try:
        updated_company = crud.update_company(db, symbol, company_update)
        if not updated_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with symbol {symbol} not found"
            )
        return updated_company
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating company: {str(e)}"
        )

@router.delete("/{symbol}")
async def delete_company(symbol: str, db: Session = Depends(get_db)):
    """Remove company from tracking"""
    try:
        success = crud.delete_company(db, symbol)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with symbol {symbol} not found"
            )
        return {"message": f"Company {symbol} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting company: {str(e)}"
        )

@router.get("/{symbol}/metrics", response_model=List[schemas.CompanyMetricsInDB])
async def get_company_metrics_history(
    symbol: str, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """Get metrics history for a company"""
    try:
        # Check if company exists
        company = crud.get_company_by_symbol(db, symbol)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with symbol {symbol} not found"
            )
        
        metrics_history = crud.get_metrics_history(db, symbol, limit)
        return metrics_history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching metrics history: {str(e)}"
        )

@router.get("/{symbol}/metrics/latest", response_model=schemas.CompanyMetricsInDB)
async def get_latest_metrics(symbol: str, db: Session = Depends(get_db)):
    """Get most recent metrics for a company"""
    try:
        # Check if company exists
        company = crud.get_company_by_symbol(db, symbol)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with symbol {symbol} not found"
            )
        
        latest_metrics = crud.get_latest_metrics_by_symbol(db, symbol)
        if not latest_metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No metrics found for company {symbol}"
            )
        
        return latest_metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching latest metrics: {str(e)}"
        )

@router.post("/{symbol}/fetch-metrics")
async def fetch_and_save_metrics(symbol: str, db: Session = Depends(get_db)):
    """Manually trigger metrics fetch for a specific company"""
    try:
        # Check if company exists
        company = crud.get_company_by_symbol(db, symbol)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with symbol {symbol} not found"
            )
        
        # Fetch metrics from Financial Modeling Prep API
        metrics_data = financial_api.fetch_all_company_metrics(symbol)
        
        if not metrics_data or 'symbol' not in metrics_data:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch metrics for {symbol} from external API"
            )
        
        # Save metrics to database
        db_metrics = crud.create_company_metrics(db, company.id, metrics_data)
        
        # Prepare response
        response = {
            "message": f"Successfully fetched and saved metrics for {symbol}",
            "symbol": symbol,
            "metrics_id": db_metrics.id,
            "recorded_at": db_metrics.recorded_at.isoformat(),
            "fields_fetched": len([k for k, v in metrics_data.items() if v is not None]),
            "errors": metrics_data.get('errors', [])
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching metrics for {symbol}: {str(e)}"
        )

@router.get("/overview/dashboard")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get overview dashboard data"""
    try:
        companies_with_metrics = crud.get_companies_with_latest_metrics(db)
        
        total_companies = len(companies_with_metrics)
        companies_with_data = len([c for c in companies_with_metrics if c['latest_metrics']])
        
        dashboard_data = {
            "total_companies": total_companies,
            "companies_with_data": companies_with_data,
            "companies_without_data": total_companies - companies_with_data,
            "api_usage_today": financial_api.request_count,
            "api_limit": financial_api.daily_limit,
            "companies": []
        }
        
        # Add company summary data
        for item in companies_with_metrics:
            company = item['company']
            metrics = item['latest_metrics']
            
            company_summary = {
                "symbol": company.symbol,
                "company_name": company.company_name,
                "sector": company.sector,
                "is_active": company.is_active,
                "last_updated": metrics.recorded_at.isoformat() if metrics else None,
                "pe_ratio": metrics.pe_ratio if metrics else None,
                "market_cap": metrics.market_cap if metrics else None
            }
            
            dashboard_data["companies"].append(company_summary)
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard data: {str(e)}"
        )
