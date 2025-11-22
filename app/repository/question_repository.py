from typing import List
from sqlalchemy.orm import Session
from app.model.question import Question

class QuestionRepository:
    def bulk_create(self, db: Session, items: List[Question]):
        db.add_all(items)
        db.commit()
        for it in items:
            db.refresh(it)
        return items

    def list_by_book(self, db: Session, book_id: int) -> List[Question]:
        return db.query(Question).filter(Question.book_id == book_id).all()

