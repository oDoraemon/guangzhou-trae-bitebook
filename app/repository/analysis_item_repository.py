from typing import List
from sqlalchemy.orm import Session
from app.model.analysis_item import AnalysisItem

class AnalysisItemRepository:
    def bulk_create(self, db: Session, items: List[AnalysisItem]):
        db.add_all(items)
        db.commit()
        for it in items:
            db.refresh(it)
        return items

    def list_by_book(self, db: Session, book_id: int) -> List[AnalysisItem]:
        return db.query(AnalysisItem).filter(AnalysisItem.book_id == book_id).all()

