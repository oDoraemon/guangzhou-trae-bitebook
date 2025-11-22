from typing import List
from sqlalchemy.orm import Session
from app.model.explanation import Explanation

class ExplanationRepository:
    def bulk_create(self, db: Session, items: List[Explanation]):
        db.add_all(items)
        db.commit()
        for it in items:
            db.refresh(it)
        return items

    def list_by_question(self, db: Session, question_id: int) -> List[Explanation]:
        return db.query(Explanation).filter(Explanation.question_id == question_id).all()

