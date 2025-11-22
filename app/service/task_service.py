from datetime import datetime
from pathlib import Path
import fitz
from typing import Optional
from sqlalchemy.orm import Session
import re

from app.repository.task_log_repository import TaskLogRepository
from app.model.task_log import TaskLog
from app.repository.doc_text_repository import DocTextRepository
from app.model.doc_text import DocText
from app.repository.analysis_item_repository import AnalysisItemRepository
from app.model.analysis_item import AnalysisItem
from app.service.ai_client import ask_ai
from app.repository.question_repository import QuestionRepository
from app.repository.explanation_repository import ExplanationRepository
from app.model.question import Question
from app.model.explanation import Explanation

class TaskService:
    def __init__(self, repo: Optional[TaskLogRepository] = None, text_repo: Optional[DocTextRepository] = None, analysis_repo: Optional[AnalysisItemRepository] = None):
        self.repo = repo or TaskLogRepository()
        self.text_repo = text_repo or DocTextRepository()
        self.analysis_repo = analysis_repo or AnalysisItemRepository()
        self.question_repo = QuestionRepository()
        self.expl_repo = ExplanationRepository()

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
                data = page.get_text("dict")
                segs = []
                for b in data.get("blocks", []):
                    if b.get("type", 0) != 0:
                        continue
                    parts = []
                    x0 = None
                    y0 = None
                    x1 = None
                    y1 = None
                    for line in b.get("lines", []):
                        bb = line.get("bbox")
                        if bb:
                            x0 = bb[0] if x0 is None else min(x0, bb[0])
                            y0 = bb[1] if y0 is None else min(y0, bb[1])
                            x1 = bb[2] if x1 is None else max(x1, bb[2])
                            y1 = bb[3] if y1 is None else max(y1, bb[3])
                        tline = "".join([s.get("text", "") for s in line.get("spans", [])])
                        parts.append(tline)
                    txt = "\n".join(parts)
                    txt = re.sub(r"\s+", " ", txt).strip()
                    if txt:
                        segs.append({"text": txt, "bbox": (x0 or 0.0, y0 or 0.0, x1 or 0.0, y1 or 0.0)})
                def union(a, b):
                    ax0, ay0, ax1, ay1 = a
                    bx0, by0, bx1, by1 = b
                    return (min(ax0, bx0), min(ay0, by0), max(ax1, bx1), max(ay1, by1))
                def split_sentences(s: str):
                    parts = re.split(r"(?<=[\.\!\?。！？])\s+", s)
                    parts = [p.strip() for p in parts if p.strip()]
                    return parts if parts else [s]
                def chunk_by_limit(sents, limit=400):
                    chunks = []
                    buf = ""
                    for sent in sents:
                        if not buf:
                            buf = sent
                        elif len(buf) + 1 + len(sent) <= limit:
                            buf = buf + " " + sent
                        else:
                            chunks.append(buf)
                            buf = sent
                    if buf:
                        chunks.append(buf)
                    return chunks
                idx = 0
                while idx < len(segs):
                    acc_txt = segs[idx]["text"]
                    acc_bbox = segs[idx]["bbox"]
                    j = idx + 1
                    while len(acc_txt) < 200 and j < len(segs):
                        acc_txt = acc_txt + " " + segs[j]["text"]
                        acc_bbox = union(acc_bbox, segs[j]["bbox"])
                        j += 1
                    sents = split_sentences(acc_txt)
                    chunks = chunk_by_limit(sents, 400)
                    x0, y0, x1, y1 = acc_bbox
                    bx = float(x0)
                    by = float(y0)
                    bw = float(max(0.0, x1 - x0))
                    bh = float(max(0.0, y1 - y0))
                    for ch in chunks:
                        texts.append(DocText(book_id=task.book_id, page_number=i+1, source="pdf", file_path=str(out_path), text=ch, bbox_x=bx, bbox_y=by, bbox_w=bw, bbox_h=bh))
                    idx = j
            if texts:
                self.text_repo.bulk_create(db, texts)
            self.repo.update(db, task, {"status": "done", "finished_at": datetime.utcnow(), "pages_count": pages})
        except Exception as e:
            self.repo.update(db, task, {"status": "failed", "finished_at": datetime.utcnow(), "message": str(e)})

    def queue_analyze_ai(self, db: Session, book_id: int) -> TaskLog:
        t = TaskLog(book_id=book_id, task_type="analyze_ai", status="queued", message=None, file_name="", output_dir="")
        return self.repo.create(db, t)

    def run_analyze_ai(self, db: Session, task_id: int):
        task = self.repo.get(db, task_id)
        if not task:
            return
        try:
            task = self.repo.update(db, task, {"status": "running", "started_at": datetime.utcnow()})
            ai_items = ask_ai(task.book_id, db)
            qs = []
            for it in ai_items:
                qs.append(Question(book_id=task.book_id, doc_text_id=it.get("doc_text_id"), page_number=it.get("page_number"), text=it.get("question")))
            if qs:
                qs = self.question_repo.bulk_create(db, qs)
                exps = []
                for q, it in zip(qs, ai_items):
                    exps.append(Explanation(question_id=q.id, text=it.get("answer"), provider=it.get("provider"), model=it.get("model")))
                if exps:
                    self.expl_repo.bulk_create(db, exps)
            self.repo.update(db, task, {"status": "done", "finished_at": datetime.utcnow(), "pages_count": None})
        except Exception as e:
            self.repo.update(db, task, {"status": "failed", "finished_at": datetime.utcnow(), "message": str(e)})
