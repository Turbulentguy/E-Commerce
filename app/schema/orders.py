from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

from app.schema.orderitem import OrderItemCreate

class Orders(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    shipping_address: str
    items: list[Orders]

class OrderCreateResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_price: Decimal
    shipping_address: str
    created_at: datetime
    order_items: list[OrderItemCreate]

    class Config():
        from_attributes = True