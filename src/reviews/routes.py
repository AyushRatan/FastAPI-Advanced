from fastapi import APIRouter
from src.db.main import get_session
from .schemas import ReviewCreateModel, ReviewModel
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends
from .service import ReviewService
from src.auth.dependencies import TokenBearer


review_service = ReviewService()
review_router = APIRouter()


@review_router.post("/book/{book_uid}",response_model=ReviewModel)
async def add_review_to_book(book_uid:str,review_data:ReviewCreateModel,session:AsyncSession=Depends(get_session),token_data:dict=Depends(TokenBearer())):

    user_email = token_data.get("user")["email"]
    book_review = await review_service.add_review_to_book(user_email=user_email,book_uid=book_uid,review_data=review_data,session=session)

    return book_review