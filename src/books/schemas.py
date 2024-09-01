from src.books.books_data import books
from pydantic import BaseModel, Field
from typing import Optional

class BookModel(BaseModel):
    id:int
    name: str
    author: str

class BookCreateModel(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: len(books))
    title: str
    author: str