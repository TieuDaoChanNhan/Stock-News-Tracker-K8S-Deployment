from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime
from app.database import Base

class CrawlSource(Base):
    __tablename__ = "crawl_sources"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)  # Tên nguồn (VD: "VnExpress - Doanh nghiệp")
    url = Column(String, nullable=False)  # URL cần crawl
    article_container_selector = Column(String, nullable=False)  # Selector chứa bài viết
    title_selector = Column(String, nullable=False)  # Selector tiêu đề
    link_selector = Column(String, nullable=False)  # Selector link
    summary_selector = Column(String, nullable=True)  # Selector tóm tắt
    date_selector = Column(String, nullable=True)  # Selector ngày tháng
    is_active = Column(Boolean, default=True, nullable=False)  # Có hoạt động không
    last_crawled_at = Column(DateTime, nullable=True)  # Lần crawl cuối
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CrawlSource(id={self.id}, name='{self.name}', active={self.is_active})>"
