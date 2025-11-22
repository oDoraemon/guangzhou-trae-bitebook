from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from pathlib import Path
from app.api.books import router as books_router
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.db import SessionLocal, engine, Base
from app.model.book import Book
from app.api.upload import router as upload_router
from app.config import get_settings
from sqlalchemy import text
from app.model.task_log import TaskLog
from app.model.book_meta import BookMeta
from app.model.doc_text import DocText
from app.model.analysis_item import AnalysisItem
from app.model.question import Question
from app.model.explanation import Explanation

settings = get_settings()
app = FastAPI(title=settings.app_name, docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.mount("/covers", StaticFiles(directory=str(settings.covers_dir)), name="covers")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="BiteBook API Docs",
        swagger_css_url=settings.swagger_css,
        swagger_js_url=settings.swagger_js,
        swagger_ui_parameters={"persistAuthorization": True},
    )

@app.get("/redoc", include_in_schema=False)
def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="BiteBook API ReDoc",
        redoc_js_url=settings.redoc_js,
    )

app.include_router(books_router)
app.include_router(upload_router)

@app.on_event("startup")
def seed_data():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        cols_b = [row[1] for row in conn.execute(text("PRAGMA table_info('books')"))]
        if 'summary' not in cols_b:
            conn.execute(text("ALTER TABLE books ADD COLUMN summary TEXT"))
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info('book_meta')"))]
        for name, ddl in [("cover_file", "TEXT"), ("cover_mime", "TEXT"), ("cover_width", "INTEGER"), ("cover_height", "INTEGER")]:
            if name not in cols:
                conn.execute(text(f"ALTER TABLE book_meta ADD COLUMN {name} {ddl}"))
        cols_dt = [row[1] for row in conn.execute(text("PRAGMA table_info('doc_text')"))]
        for name, ddl in [("bbox_x", "REAL"), ("bbox_y", "REAL"), ("bbox_w", "REAL"), ("bbox_h", "REAL")]:
            if name not in cols_dt:
                conn.execute(text(f"ALTER TABLE doc_text ADD COLUMN {name} {ddl}"))
