from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime
from app.services.financial_api_service import fetch_all_active_company_metrics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies-scheduler", tags=["scheduler"])

@router.post("/run")
async def trigger_company_scheduler(background_tasks: BackgroundTasks):
    """Manually trigger company metrics fetching scheduler"""
    try:
        logger.info(f"🔄 Manual trigger company scheduler at {datetime.now()}")
        
        # Chạy scheduler trong background để không block request
        background_tasks.add_task(run_company_scheduler)
        
        return {
            "message": "Company scheduler triggered successfully",
            "status": "running_in_background",
            "service": "company_service",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger scheduler: {str(e)}"
        )

@router.get("/status")
async def get_scheduler_status():
    """Get scheduler status"""
    return {
        "service": "company_service",
        "scheduler_status": "ready",
        "description": "Fetches financial metrics for all active companies",
        "endpoint": "/api/v1/scheduler/run"
    }

async def run_company_scheduler():
    """Function được gọi bởi endpoint để chạy scheduler"""
    logger.info(f"🚀 Company Service Scheduler - Manual Run")
    logger.info("=" * 60)
    
    # Gọi hàm main từ financial_api_service
    result = fetch_all_active_company_metrics()
    
    logger.info(f"📊 Kết quả company scheduler:")
    logger.info(f"   ✅ Thành công: {result.get('success_count', 0)} companies")
    logger.info(f"   ❌ Lỗi: {result.get('error_count', 0)} companies")
    logger.info(f"   🔧 API usage: {result.get('api_requests_used', 0)}/{result.get('api_limit', 0)}")
    
    logger.info("✅ Company Service Scheduler completed!")
    return result
