from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import UserCreateModel, UserModel, UserLoginModel, UserBooksModel
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .utils import verify_password, create_token, decode_token
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user
from src.db.redis import add_jti_to_blocklist


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
                    "uid":str(user.uid),
                    "role":user.role
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


@auth_router.get("/me", response_model=UserBooksModel)
async def get_active_user(user = Depends(get_current_user)):
    return user
    
@auth_router.get("/refresh_token")
async def get_new_access_token(token_details:dict=Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_token(user_data=token_details["user"])
        return JSONResponse(content={
            "access_token":new_access_token
        })
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid or expired token")


@auth_router.get("/logout")
async def revoke_token(token_details:dict=Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(content={
        "message":"Successfully logged out",
    },status_code=status.HTTP_200_OK)