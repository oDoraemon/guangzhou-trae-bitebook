from sqlalchemy.orm import Session
from app.model.book_meta import BookMeta

class BookMetaRepository:
    def create(self, db: Session, meta: BookMeta) -> BookMeta:
        db.add(meta)
        db.commit()
        db.refresh(meta)
        return meta

    def list_by_book(self, db: Session, book_id: int):
        return db.query(BookMeta).filter(BookMeta.book_id == book_id).all()

    def delete_many(self, db: Session, metas):
        for m in metas:
            db.delete(m)
        db.commit()
