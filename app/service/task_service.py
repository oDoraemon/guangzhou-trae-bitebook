from datetime import datetime
from pathlib import Path
import fitz
from typing import Optional
from sqlalchemy.orm import Session

from app.repository.task_log_repository import TaskLogRepository
from app.model.task_log import TaskLog
from app.repository.doc_text_repository import DocTextRepository
from app.model.doc_text import DocText

class TaskService:
    def __init__(self, repo: Optional[TaskLogRepository] = None, text_repo: Optional[DocTextRepository] = None):
        self.repo = repo or TaskLogRepository()
        self.text_repo = text_repo or DocTextRepository()

    def queue_split_pdf(self, db: Session, book_id: int, file_name: str, file_path: str, output_dir: Path) -> TaskLog:
        t = TaskLog(
            book_id=book_id,
            task_type="split_pdf",
            status="queued",
            message=None,
            file_name=file_name,
            output_dir=str(output_dir),
        )
        return self.repo.create(db, t)

    def run_split_pdf(self, db: Session, task_id: int, files_dir: Path):
        task = self.repo.get(db, task_id)
        if not task:
            return
        try:
            task = self.repo.update(db, task, {"status": "running", "started_at": datetime.utcnow()})
            src = Path(files_dir) / task.file_name
            doc = fitz.open(str(src))
            out_dir = Path(task.output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            pages = doc.page_count
            texts = []
            for i in range(pages):
                ndoc = fitz.open()
                ndoc.insert_pdf(doc, from_page=i, to_page=i)
                out_path = out_dir / f"page_{i+1:04d}.pdf"
                ndoc.save(str(out_path))
                ndoc.close()
                page = doc.load_page(i)
                txt = page.get_text("text")
                texts.append(DocText(book_id=task.book_id, page_number=i+1, source="pdf", file_path=str(out_path), text=txt))
            if texts:
                self.text_repo.bulk_create(db, texts)
            self.repo.update(db, task, {"status": "done", "finished_at": datetime.utcnow(), "pages_count": pages})
        except Exception as e:
            self.repo.update(db, task, {"status": "failed", "finished_at": datetime.utcnow(), "message": str(e)})
