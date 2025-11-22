from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.model.book import Book
from app.repository.book_repository import BookRepository

class BookService:
    def __init__(self, repo: Optional[BookRepository] = None):
        self.repo = repo or BookRepository()

    def create_book(self, db: Session, data: dict) -> Book:
        isbn = data.get("isbn")
        if isbn:
            existing = self.repo.get_by_isbn(db, isbn)
            if existing:
                raise ValueError("ISBN already exists")
        book = Book(**data)
        return self.repo.create(db, book)

    def get_book(self, db: Session, book_id: int) -> Optional[Book]:
        return self.repo.get(db, book_id)

    def list_books(self, db: Session, q: Optional[str], page: int, page_size: int) -> Tuple[List[Book], int]:
        offset = (page - 1) * page_size
        return self.repo.list(db, q, offset, page_size)

    def update_book(self, db: Session, book_id: int, data: dict) -> Optional[Book]:
        book = self.repo.get(db, book_id)
        if not book:
            return None
        isbn = data.get("isbn")
        if isbn and isbn != book.isbn:
            existing = self.repo.get_by_isbn(db, isbn)
            if existing:
                raise ValueError("ISBN already exists")
        return self.repo.update(db, book, data)

    def delete_book(self, db: Session, book_id: int) -> bool:
        book = self.repo.get(db, book_id)
        if not book:
            return False
        self.repo.delete(db, book)
        return True

