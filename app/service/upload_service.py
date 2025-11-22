import hashlib
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
import fitz  # PyMuPDF

from app.service.book_service import BookService
from app.repository.book_meta_repository import BookMetaRepository
from app.model.book_meta import BookMeta

class UploadService:
    def __init__(self, book_service: Optional[BookService] = None, meta_repo: Optional[BookMetaRepository] = None):
        self.book_service = book_service or BookService()
        self.meta_repo = meta_repo or BookMetaRepository()

    def upload_book(self, db: Session, file: UploadFile, data: dict, files_dir: Path) -> tuple:
        if not file.filename:
            raise ValueError("File name missing")
        if not file.content_type or not file.content_type.startswith("application/pdf"):
            raise ValueError("Only PDF is supported")

        files_dir.mkdir(parents=True, exist_ok=True)
        suffix = ".pdf"
        safe_name = Path(file.filename).stem
        target_name = safe_name + suffix
        target_path = files_dir / target_name
        i = 1
        while target_path.exists():
            target_path = files_dir / f"{safe_name}_{i}{suffix}"
            i += 1

        hasher = hashlib.sha256()
        size = 0
        with target_path.open("wb") as out:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
                size += len(chunk)
                out.write(chunk)

        sha = hasher.hexdigest()

        covers_dir = files_dir.parent / "covers"
        covers_dir.mkdir(parents=True, exist_ok=True)
        cover_file = None
        cover_mime = None
        cover_w = None
        cover_h = None
        try:
            doc = fitz.open(str(target_path))
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("jpeg")
            cover_file = f"{sha[:16]}.jpg"
            cover_path = covers_dir / cover_file
            with cover_path.open("wb") as fimg:
                fimg.write(img_bytes)
            cover_mime = "image/jpeg"
            cover_w = pix.width
            cover_h = pix.height
        except Exception:
            pass

        if not data.get("title"):
            data["title"] = safe_name
        if not data.get("author"):
            data["author"] = "Unknown"
        book = self.book_service.create_book(db, data)
        meta = BookMeta(
            book_id=book.id,
            file_name=file.filename,
            file_path=str(target_path),
            mime_type=file.content_type,
            file_size=size,
            sha256=sha,
            cover_file=cover_file,
            cover_mime=cover_mime,
            cover_width=cover_w,
            cover_height=cover_h,
        )
        meta = self.meta_repo.create(db, meta)
        return book, meta
