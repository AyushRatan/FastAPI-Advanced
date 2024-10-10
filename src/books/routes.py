from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from src.books.schemas import Book, BookCreateModel,BookUpdateModel
from src.db.main import get_session
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import AccessTokenBearer, RoleChecker

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin","user"]))


@book_router.get("/",response_model=list[Book])
async def get_books(session:AsyncSession=Depends(get_session), token_details=Depends(access_token_bearer)) -> list[Book]:
    return await book_service.get_all_books(session)


@book_router.get("/user/{user_uid}",response_model=list[Book])
async def get_user_books(user_uid:str,session:AsyncSession=Depends(get_session), token_details=Depends(access_token_bearer)) -> list[Book]:
    books =  await book_service.get_user_books(user_uid,session)
    return books


@book_router.get("/{book_id}", response_model=Book)
async def get_book(book_id: str, session:AsyncSession=Depends(get_session),token_details=Depends(access_token_bearer)) -> Book:
    
    book =  await book_service.get_book(book_id,session)
    if book == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    else:
        return book

@book_router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def add_book(book: BookCreateModel,session:AsyncSession=Depends(get_session),token_details=Depends(access_token_bearer)) -> Book:
    user_id = token_details.get("user")["uid"]
    new_book = await book_service.create_book(book,user_id,session)
    return new_book


@book_router.patch("/", response_model=Book, status_code=status.HTTP_200_OK)
async def update_book(updated_data: BookUpdateModel,book_uid:str,session:AsyncSession=Depends(get_session),token_details=Depends(access_token_bearer)) -> Book:

    updated_book = await book_service.update_book(book_uid,updated_data,session)
    if updated_book == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    else:
        return updated_book



@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def db_delete_book(book_id: str,session:AsyncSession=Depends(get_session),token_details=Depends(access_token_bearer)) -> None:
    book_to_delete = await book_service.get_book(book_id, session)
    if book_to_delete == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    else:
        return await book_service.delete_book(book_id,session)
