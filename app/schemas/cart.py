from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CartItemBase(BaseModel):
    product_id: str
    quantity: int
    options: Optional[str] = None

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None
    options: Optional[str] = None

class CartItemInDB(CartItemBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        orm_mode = True