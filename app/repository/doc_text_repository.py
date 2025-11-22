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

