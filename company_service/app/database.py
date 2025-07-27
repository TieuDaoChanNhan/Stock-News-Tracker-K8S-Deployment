import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Cấu hình kết nối đến company_db
COMPANY_DATABASE_URL = os.getenv("COMPANY_DATABASE_URL", "postgresql://user:password@postgresql:5432/company_db")

engine = create_engine(COMPANY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import models của service này
    from app.models import company_model
    Base.metadata.create_all(bind=engine)
    print("✅ Bảng của Company Service đã được tạo trong company_db.")
