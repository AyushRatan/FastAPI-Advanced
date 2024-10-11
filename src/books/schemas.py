from src.books.books_data import books
from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime,date
import uuid
from src.reviews.schemas import ReviewModel

class Book(BaseModel):
    uid:uuid.UUID
    title:str
    author: str
    publisher:str
    published_date:date
    page_count:int
    language:str
    created_at:datetime
    updated_at:datetime

class BookReviewModel(Book):
    reviews:List[ReviewModel]


class BookCreateModel(BaseModel):
    title:str
    author:str
    publisher:str
    published_date:str
    page_count:int
    language:str

class BookUpdateModel(BaseModel):
    title:str | None = None
    author:str | None = None
    publisher:str | None = None
    published_date:str | None = None
    page_count:int | None = None
    language:str | None = None