from pydantic import BaseModel, Field, EmailStr
import uuid
from datetime import datetime


class UserCreateModel(BaseModel):
    first_name:str = Field(max_length=15)
    last_name:str = Field(max_length=15)
    username:str = Field(max_length=15)
    email:str = Field(max_length=40)
    password:str = Field(min_length=6)


class UserModel(BaseModel):
    uid: uuid.UUID 
    username:str
    email:str 
    first_name:str
    last_name:str
    password_hash:str=Field(exclude=True)
    is_verified:bool
    created_at:datetime
    updated_at:datetime 



class UserLoginModel(BaseModel):
    email:str
    password:str
