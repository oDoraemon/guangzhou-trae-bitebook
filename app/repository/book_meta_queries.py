from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.model.book_meta import BookMeta

def get_latest_by_book_id(db: Session, book_id: int) -> Optional[BookMeta]:
    stmt = select(BookMeta).where(BookMeta.book_id == book_id).order_by(desc(BookMeta.created_at)).limit(1)
    return db.execute(stmt).scalars().first()

