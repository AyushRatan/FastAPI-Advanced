from fastapi import APIRouter, Depends, HTTPException
from .schemas import UserCreateModel, UserModel, UserLoginModel
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .utils import verify_password, create_token, decode_token
from fastapi.responses import JSONResponse
from datetime import timedelta

user_service = UserService()
auth_router = APIRouter()

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post("/signup", response_model=UserModel, status_code=201)
async def create_user_account(user_data:UserCreateModel,session:AsyncSession=Depends(get_session)):

    if await user_service.user_exist(user_data.email,session):
        raise HTTPException(status_code=400, detail="User with email already exists")
    
    new_user = await user_service.create_user(user_data,session)
    return new_user


@auth_router.post("/login")
async def login(login_data:UserLoginModel, session:AsyncSession=Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email,session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_token(
                user_data={
                    "email":email,
                    "uid":str(user.uid)
                }
            )

            refresh_token = create_token(
                user_data = {
                    "email":email,
                    "uid":str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)

            )

            return JSONResponse(
                content={
                    "message":"Login Successful",
                    "access_token":access_token,
                    "refresh_token":refresh_token,
                    "user":{
                        "email":email,
                        "uid":str(user.uid)
                    }
                }
            )
        
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
        
    else:
        raise HTTPException(status_code=404, detail="User not found")

    