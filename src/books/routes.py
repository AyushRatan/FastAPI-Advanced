from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from src.books.schemas import BookModel, BookCreateModel
from src.books.books_data import books

book_router = APIRouter()


@book_router.get("/",response_model=list[BookModel])
def get_books() -> list[BookModel]:
    return books


@book_router.get("/{book_id}", response_model=BookModel)
def get_book(book_id: int) -> BookModel:
    for book in books:
        if book["id"] == book_id:
            return book
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.post("/", response_model=BookModel, status_code=status.HTTP_201_CREATED)
def add_book(book: BookCreateModel) -> BookModel:
    print(book.id)
    new_book = BookModel(id=book.id,name=book.title, author=book.author)
    books.append(new_book.model_dump())
    return new_book


@book_router.delete("/{book_id}")
def delete_book(book_id: int) -> None:
    books.pop(book_id)
    return None
