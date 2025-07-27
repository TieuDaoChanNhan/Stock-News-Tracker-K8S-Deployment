from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship

class ArticleAIAnalysis(Base):
    __tablename__ = "ai_analysis"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('articles.id'), unique=True, nullable=False)
    summary = Column(Text, nullable=True)  # Tóm tắt AI
    category = Column(String, nullable=True)  # 'Địa chính trị', 'Chính sách tiền tệ', etc.
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    impact_score = Column(Float, nullable=True)  # 0.0 to 1.0
    keywords_extracted = Column(Text, nullable=True)  # JSON string của keywords
    analysis_metadata = Column(Text, nullable=True)  # JSON string chứa thông tin phân tích
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    article = relationship("Article", back_populates="ai_analysis")
    
    def __repr__(self):
        return f"<ArticleAIAnalysis(article_id={self.article_id}, category='{self.category}')>"
