from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app.db import get_db, Base, engine
from app.service.upload_service import UploadService
from app.schema.book import BookRead
from app.schema.book_meta import BookMetaRead, UploadBookResponse
from app.model.book_meta import BookMeta
from app.config import get_settings
from app.service.task_service import TaskService

router = APIRouter(prefix="/api/upload", tags=["upload"])

Base.metadata.create_all(bind=engine)

service = UploadService()
task_service = TaskService()

@router.post("/book", response_model=UploadBookResponse, status_code=status.HTTP_201_CREATED)
async def upload_book(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    published_year: Optional[int] = Form(None),
    isbn: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    try:
        files_dir = get_settings().files_dir
        book_data = {"title": title, "author": author, "description": description, "published_year": published_year, "isbn": isbn}
        book, meta = service.upload_book(db, file, book_data, files_dir)
        out_dir = files_dir / Path(meta.file_name).stem
        task = task_service.queue_split_pdf(db, book.id, Path(meta.file_path).name, str(out_dir), out_dir)
        if background_tasks is not None:
            from app.db import SessionLocal
            from app.config import get_settings as _get_settings
            def _runner(tid: int):
                s = SessionLocal()
                try:
                    task_service.run_split_pdf(s, tid, _get_settings().files_dir)
                finally:
                    s.close()
            background_tasks.add_task(_runner, task.id)
        return {"book": BookRead.model_validate(book).model_dump(), "meta": BookMetaRead.model_validate(meta)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
