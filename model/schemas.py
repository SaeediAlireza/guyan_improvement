from pydantic import BaseModel
from datetime import datetime, time


# login
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: int


class TokenData(BaseModel):
    username: str | None = None


# user type
class UserTypeAddRequest(BaseModel):
    name: str


class UserTypeUpdateRequest(BaseModel):
    id: int
    name: str


class UserTypeInfo(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# user
class UserAddRequest(BaseModel):
    user_name: str
    password: str
    fname: str
    lname: str
    user_type_id: int


class UserUpdateRequest(BaseModel):
    id: int
    user_name: str
    fname: str
    lname: str
    user_type_id: int

    class Config:
        from_attributes = True


class UserInfoResponse(BaseModel):
    id: int
    user_name: str
    fname: str
    lname: str
    type: UserTypeInfo

    class Config:
        from_attributes = True
