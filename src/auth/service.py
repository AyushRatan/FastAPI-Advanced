from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from .utils import generate_passwd_hash
from .schemas import UserCreateModel


class UserService:
    async def get_user_by_email(self,email:str, session:AsyncSession):
        statement = select(User).where(User.email==email).options(selectinload(User.books))

        result = await session.exec(statement)

        user = result.first()

        return user
    

    async def user_exist(self,email:str, session:AsyncSession):
        user = await self.get_user_by_email(email, session)

        return True if user is not None else False
    
    async def create_user(self,user_data:UserCreateModel,session:AsyncSession):
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)

        new_user.password_hash = generate_passwd_hash(user_data_dict["password"])
        

        session.add(new_user)

        await session.commit()

        return new_user