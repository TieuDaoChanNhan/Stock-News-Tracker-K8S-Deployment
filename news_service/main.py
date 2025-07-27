from fastapi import FastAPI
from app.database import init_db
from app.endpoints import article_endpoints, ai_analysis_endpoints, crawl_source_endpoints, scheduler_endpoints
from app.services.event_publisher import event_publisher

app = FastAPI(
    title="News Service",
    description="Quản lý tin tức, phân tích AI và các nguồn crawl.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    print("🚀 Khởi động News Service...")
    init_db()
    
    # Kết nối RabbitMQ
    try:
        await event_publisher.connect()
        print("✅ Connected to RabbitMQ for event publishing")
    except Exception as e:
        print(f"⚠️ Failed to connect to RabbitMQ: {e}")

@app.on_event("shutdown")
async def on_shutdown():
    print("👋 Shutting down News Service...")
    await event_publisher.close()

# Thêm các router
app.include_router(article_endpoints.router, prefix="/api/v1")
app.include_router(ai_analysis_endpoints.router, prefix="/api/v1")
app.include_router(crawl_source_endpoints.router, prefix="/api/v1")
app.include_router(scheduler_endpoints.router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health_check():
    """Kiểm tra sức khỏe của service"""
    return {"status": "ok", "service": "News Service"}

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)