from typing import Coroutine
from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from typing import List, Any
from src.db.models import User
from src.errors import InvalidToken

user_service = UserService()

class TokenBearer(HTTPBearer):
    
    def __init__(self,auto_error=True):
        super().__init__(auto_error=auto_error)

    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)
        
        if not self.token_valid(token):
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail={
                "error":"Invalid or expired token",
                "resolution":"Please get a new token"
            })
        
        # if await token_in_blocklist(token_data["jti"]):
        #     raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail={
        #         "error":"Invalid or expired token",
        #         "resolution":"Please get a new token"
        #     })
        
        self.verify_token_data(token_data)
        
        return token_data
    

    def token_valid(self,token:str) -> bool:

        token_data = decode_token(token)
        print(token_data)
        return token_data is not None 
    
    def verify_token_data(self,token_data):
        raise NotImplementedError("Please Override this method in Child Classes")
    

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide valid access token"
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide valid refresh token"
            )
        


async def get_current_user(token_data:dict = Depends(AccessTokenBearer()),session:AsyncSession = Depends(get_session)):
    user_email = token_data["user"]["email"]

    user = await user_service.get_user_by_email(user_email,session)

    return user

class RoleChecker:
    def __init__(self,allowed_roles:List[str]):
        self.allowed_roles = allowed_roles


    def __call__(self,current_user = Depends(get_current_user)) -> Any:

        if current_user.role in self.allowed_roles:
            return True
        
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this action")

     

