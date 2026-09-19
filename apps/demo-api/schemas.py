from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_admin: Optional[bool] = None

class User(UserBase):
    id: int
    role: str
    is_admin: bool

    class Config:
        from_attributes = True

class InvoiceBase(BaseModel):
    amount: float
    description: str
    status: str = "pending"

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
