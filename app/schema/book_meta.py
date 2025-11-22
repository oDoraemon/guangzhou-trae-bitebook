from pydantic import BaseModel

class BookMetaRead(BaseModel):
    id: int
    book_id: int
    file_name: str
    file_path: str
    mime_type: str
    file_size: int
    sha256: str

    class Config:
        from_attributes = True

class UploadBookResponse(BaseModel):
    book: dict
    meta: BookMetaRead

