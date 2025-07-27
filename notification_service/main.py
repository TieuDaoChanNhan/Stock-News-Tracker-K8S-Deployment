from fastapi import FastAPI
import asyncio
from app.database import init_db
from app.endpoints import watchlist_endpoints
from app.services.event_consumer import event_consumer

app = FastAPI(
    title="Notification Service",
    description="Quản lý watchlist và gửi thông báo.",
    version="1.0.0"
)

@app.on_event("startup")    
async def on_startup():
    print("🚀 Khởi động Notification Service...")
    init_db()
    
    # Start event consumer trong background task
    asyncio.create_task(event_consumer.start_consuming())
    print("🔄 Event consumer started")

@app.on_event("shutdown")
async def on_shutdown():
    print("👋 Shutting down Notification Service...")
    await event_consumer.close()

# Thêm router
app.include_router(watchlist_endpoints.router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health_check():
    """Kiểm tra sức khỏe của service"""
    return {"status": "ok", "service": "Notification Service"}

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)