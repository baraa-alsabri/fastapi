from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Literal

class UserOutModel(BaseModel):
    id: int
    email: EmailStr

class PostModel(BaseModel):
    title: str
    content: str
    published: bool = True
    user_id: int
    owner: UserOutModel

class PostResponseModel(BaseModel):
    id: int
    title: str
    content: str
    published: bool = True
    user_id: int
    owner: UserOutModel
        
class PostOutModel(BaseModel):
    Post: PostResponseModel
    votes: int

class PostResponseModel(PostModel):
    class Config:
        orm_mode = True


class UserModel(BaseModel):
    email: EmailStr
    password: str


class UserResponseModel(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class LoginModel(BaseModel):
    email: EmailStr
    password: str


class TokenModel(BaseModel):
    access_token: str
    token_type: str


class AccessTokenModel(BaseModel):
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int
    direction: Literal[0, 1]
