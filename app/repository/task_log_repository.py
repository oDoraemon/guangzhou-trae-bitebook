from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.model.task_log import TaskLog

class TaskLogRepository:
    def create(self, db: Session, task: TaskLog) -> TaskLog:
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update(self, db: Session, task: TaskLog, data: dict) -> TaskLog:
        for k, v in data.items():
            setattr(task, k, v)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def get(self, db: Session, task_id: int) -> Optional[TaskLog]:
        return db.get(TaskLog, task_id)

    def latest_by_book(self, db: Session, book_id: int) -> Optional[TaskLog]:
        stmt = select(TaskLog).where(TaskLog.book_id == book_id).order_by(desc(TaskLog.created_at)).limit(1)
        return db.execute(stmt).scalars().first()

