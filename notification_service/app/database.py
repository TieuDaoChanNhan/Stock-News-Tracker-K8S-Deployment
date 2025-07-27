import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Cấu hình kết nối đến notification_db
NOTIFICATION_DATABASE_URL = os.getenv("NOTIFICATION_DATABASE_URL", "postgresql://user:password@postgresql:5432/notification_db")

engine = create_engine(NOTIFICATION_DATABASE_URL)
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
    from app.models import watchlist_model
    Base.metadata.create_all(bind=engine)
    print("✅ Bảng của Notification Service đã được tạo trong notification_db.")
