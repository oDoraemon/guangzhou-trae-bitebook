from typing import List
from sqlalchemy.orm import Session
from app.model.doc_text import DocText

class DocTextRepository:
    def bulk_create(self, db: Session, entries: List[DocText]):
        db.add_all(entries)
        db.commit()
        for e in entries:
            db.refresh(e)
        return entries

    def list_by_book(self, db: Session, book_id: int) -> List[DocText]:
        return db.query(DocText).filter(DocText.book_id == book_id).order_by(DocText.page_number.asc()).all()
