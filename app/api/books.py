from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db, Base, engine
from app.schema.book import BookCreate, BookUpdate, BookRead
from app.service.book_service import BookService
from app.repository.book_meta_queries import get_latest_by_book_id
from app.repository.task_log_repository import TaskLogRepository

router = APIRouter(prefix="/api/books", tags=["books"])

Base.metadata.create_all(bind=engine)

service = BookService()
task_repo = TaskLogRepository()

@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    try:
        book = service.create_book(db, payload.model_dump())
        return book
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = service.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    data = BookRead.model_validate(book).model_dump()
    meta = get_latest_by_book_id(db, book.id)
    if meta and meta.cover_file:
        data["cover_url"] = f"/covers/{meta.cover_file}"
    t = task_repo.latest_by_book(db, book.id)
    if t:
        data["task_status"] = t.status
        data["task_pages_count"] = t.pages_count
    return data

@router.get("/")
def list_books(q: Optional[str] = None, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = service.list_books(db, q, page, page_size)
    def as_dict(b):
        d = BookRead.model_validate(b).model_dump()
        meta = get_latest_by_book_id(db, b.id)
        if meta and meta.cover_file:
            d["cover_url"] = f"/covers/{meta.cover_file}"
        t = task_repo.latest_by_book(db, b.id)
        if t:
            d["task_status"] = t.status
            d["task_pages_count"] = t.pages_count
        return d
    return {"items": [as_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    try:
        book = service.update_book(db, book_id, payload.model_dump(exclude_unset=True))
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        return book
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_book(db, book_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return
