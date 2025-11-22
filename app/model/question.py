from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base

class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    doc_text_id = Column(Integer, ForeignKey("doc_text.id", ondelete="SET NULL"), nullable=True, index=True)
    page_number = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    book = relationship("Book")
    doc_text = relationship("DocText")

