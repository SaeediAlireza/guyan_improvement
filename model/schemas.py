from pydantic import BaseModel
from datetime import datetime, time


# login
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: int
    email: str
    name: str


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
    name: str
    email: str
    user_type_id: int


class UserUpdateRequest(BaseModel):
    id: int
    user_name: str
    name: str
    email: str
    user_type_id: int

    class Config:
        from_attributes = True


class UserUpdatePasswordRequest(BaseModel):
    id: int
    password: str

    class Config:
        from_attributes = True


class UserInfoResponse(BaseModel):
    id: int
    user_name: str
    name: str
    email: str
    type: UserTypeInfo

    class Config:
        from_attributes = True


# phone number owner
class PhoneNumberOwnerAddRequest(BaseModel):
    name: str


class PhoneNumberOwnerUpdateRequest(BaseModel):
    id: int
    fname: str
    name: str

    class Config:
        from_attributes = True


class PhoneNumberOwnerInfoResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# phone number
class PhoneNumberAddRequest(BaseModel):
    number: str
    phone_number_owner_id: int


class PhoneNumberUpdateRequest(BaseModel):
    id: int
    number: str
    phone_number_owner_id: int

    class Config:
        from_attributes = True


class PhoneNumberInfoResponse(BaseModel):
    id: int
    number: str
    phone_number_owner: PhoneNumberOwnerInfoResponse

    class Config:
        from_attributes = True


# ticket
class TicketAddRequest(BaseModel):
    description: str
    user_id: int


class TicketUpdateRequest(BaseModel):
    id: int
    description: str
    user_id: int

    class Config:
        from_attributes = True


class TicketInfoResponse(BaseModel):
    id: int
    description: str
    user: UserInfoResponse

    class Config:
        from_attributes = True


# internal number
class InternalNumberAddRequest(BaseModel):
    internal_number: str
    path: str
    phone_number_id: int


class InternalNumberUpdateRequest(BaseModel):
    id: int
    internal_number: str
    path: str

    phone_number_id: int

    class Config:
        from_attributes = True


class InternalNumberInfoResponse(BaseModel):
    id: int
    internal_number: str
    path: str
    phone_number: PhoneNumberInfoResponse

    class Config:
        from_attributes = True
