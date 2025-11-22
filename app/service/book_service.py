from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from app.config import get_settings
from app.repository.book_meta_repository import BookMetaRepository
from app.model.book import Book
from app.repository.book_repository import BookRepository

class BookService:
    def __init__(self, repo: Optional[BookRepository] = None, meta_repo: Optional[BookMetaRepository] = None):
        self.repo = repo or BookRepository()
        self.meta_repo = meta_repo or BookMetaRepository()

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
        settings = get_settings()
        metas = self.meta_repo.list_by_book(db, book_id)
        for m in metas:
            try:
                p = Path(m.file_path)
                if p.exists():
                    p.unlink()
            except Exception:
                pass
            try:
                split_dir = settings.files_dir / Path(m.file_name).stem
                if split_dir.exists():
                    shutil.rmtree(split_dir, ignore_errors=True)
            except Exception:
                pass
            try:
                if m.cover_file:
                    cp = settings.covers_dir / m.cover_file
                    if cp.exists():
                        cp.unlink()
                    fe = settings.covers_dir.parent.parent / "front" / "public" / "covers" / m.cover_file
                    if fe.exists():
                        fe.unlink()
            except Exception:
                pass
        if metas:
            self.meta_repo.delete_many(db, metas)
        self.repo.delete(db, book)
        return True
