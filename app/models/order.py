from datetime import datetime
from typing import Optional
from pydantic import validator
from sqlmodel import SQLModel, Field

class OrderBase(SQLModel):
    quantity: int

    @validator("quantity")
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity debe ser mayor que 0")
        return v

class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int 
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(OrderBase):
    customer_username: str
    product: str

class OrderRead(OrderBase):
    id: int
    customer_username: str
    product: str
    price: float
    created_at: datetime

class OrderUpdate(SQLModel):
    quantity: Optional[int] = None

    @validator("quantity")
    def validate_quantity(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Quantity debe ser mayor que cero")
        return value