from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from pathlib import Path
from app.api.books import router as books_router
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.db import SessionLocal
from app.model.book import Book

app = FastAPI(title="BiteBook API", docs_url=None, redoc_url=None)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="BiteBook API Docs",
        swagger_css_url="/static/swagger-ui/swagger-ui.min.css",
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_ui_parameters={"persistAuthorization": True},
    )

@app.get("/redoc", include_in_schema=False)
def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="BiteBook API ReDoc",
        redoc_js_url="/static/redoc/redoc.standalone.js",
    )

app.include_router(books_router)

@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    try:
        exists = db.execute(select(Book)).scalars().first()
        if not exists:
            samples = [
                Book(title="The Little Prince", author="Antoine de Saint-Exupéry", published_year=1943, description="A pilot meets a prince from another planet."),
                Book(title="Alice's Adventures in Wonderland", author="Lewis Carroll", published_year=1865, description="Alice falls into a fantastical world."),
                Book(title="Peter Pan", author="J. M. Barrie", published_year=1911, description="A boy who never grows up."),
                Book(title="Charlotte's Web", author="E. B. White", published_year=1952, description="Friendship between a pig and a spider."),
                Book(title="Winnie-the-Pooh", author="A. A. Milne", published_year=1926, description="Adventures in the Hundred Acre Wood."),
                Book(title="The Secret Garden", author="Frances Hodgson Burnett", published_year=1911, description="A hidden garden transforms lives."),
                Book(title="Pippi Longstocking", author="Astrid Lindgren", published_year=1945, description="The strongest girl in the world."),
                Book(title="Matilda", author="Roald Dahl", published_year=1988, description="A brilliant girl with telekinetic powers."),
                Book(title="The Lion, the Witch and the Wardrobe", author="C. S. Lewis", published_year=1950, description="Children enter the world of Narnia."),
                Book(title="Harry Potter and the Philosopher's Stone", author="J. K. Rowling", published_year=1997, description="A boy discovers he is a wizard."),
            ]
            for b in samples:
                db.add(b)
            db.commit()
    finally:
        db.close()
