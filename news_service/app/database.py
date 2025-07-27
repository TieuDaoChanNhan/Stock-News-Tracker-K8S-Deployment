import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Cấu hình kết nối đến news_db
NEWS_DATABASE_URL = os.getenv("NEWS_DATABASE_URL", "postgresql://user:password@postgresql:5432/news_db")

engine = create_engine(NEWS_DATABASE_URL)
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
    from app.models import article_model, ai_analysis_model, crawl_source_model
    Base.metadata.create_all(bind=engine)
    print("✅ Bảng của News Service đã được tạo trong news_db.")

