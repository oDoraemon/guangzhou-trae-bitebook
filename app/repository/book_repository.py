from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.model.book import Book

class BookRepository:
    def create(self, db: Session, book: Book) -> Book:
        db.add(book)
        db.commit()
        db.refresh(book)
        return book

    def get(self, db: Session, book_id: int) -> Optional[Book]:
        return db.get(Book, book_id)

    def list(self, db: Session, q: Optional[str], offset: int, limit: int) -> Tuple[List[Book], int]:
        stmt = select(Book)
        count_stmt = select(Book)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(or_(Book.title.like(pattern), Book.author.like(pattern), Book.isbn.like(pattern)))
            count_stmt = count_stmt.where(or_(Book.title.like(pattern), Book.author.like(pattern), Book.isbn.like(pattern)))
        total = db.execute(count_stmt).unique().scalars().all()
        items = db.execute(stmt.offset(offset).limit(limit)).unique().scalars().all()
        return items, len(total)

    def update(self, db: Session, book: Book, data: dict) -> Book:
        for k, v in data.items():
            setattr(book, k, v)
        db.add(book)
        db.commit()
        db.refresh(book)
        return book

    def delete(self, db: Session, book: Book) -> None:
        db.delete(book)
        db.commit()

    def get_by_isbn(self, db: Session, isbn: str) -> Optional[Book]:
        stmt = select(Book).where(Book.isbn == isbn)
        return db.execute(stmt).scalars().first()

