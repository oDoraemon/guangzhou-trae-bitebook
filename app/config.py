from pathlib import Path
from typing import List

class Settings:
    def __init__(self):
        base = Path(__file__).resolve().parent
        self.app_name = "BiteBook API"
        self.database_url = "sqlite:///./bitebook.db"
        self.static_dir = base / "static"
        self.files_dir = base / "files"
        self.covers_dir = base / "covers"
        self.cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
        self.swagger_css = "/static/swagger-ui/swagger-ui.min.css"
        self.swagger_js = "/static/swagger-ui/swagger-ui-bundle.js"
        self.redoc_js = "/static/redoc/redoc.standalone.js"

_settings = Settings()

def get_settings() -> Settings:
    return _settings

