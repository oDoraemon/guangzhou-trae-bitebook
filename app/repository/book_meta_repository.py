from sqlalchemy.orm import Session
from app.model.book_meta import BookMeta

class BookMetaRepository:
    def create(self, db: Session, meta: BookMeta) -> BookMeta:
        db.add(meta)
        db.commit()
        db.refresh(meta)
        return meta

