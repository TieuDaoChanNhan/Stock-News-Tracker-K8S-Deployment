from fastapi import FastAPI
from app.database import init_db
from app.endpoints import company_endpoints, scheduler_endpoints

app = FastAPI(
    title="Company Service",
    description="Quản lý thông tin công ty và các chỉ số tài chính.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    print("🚀 Khởi động Company Service...")
    init_db()

# Thêm router của service này
app.include_router(company_endpoints.router, prefix="/api/v1")
app.include_router(scheduler_endpoints.router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health_check():
    """Kiểm tra sức khỏe của service"""
    return {"status": "ok", "service": "Company Service"}

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)