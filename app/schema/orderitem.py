from pydantic import BaseModel
from decimal import Decimal

class OrderItemCreate(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    class Config():
        from_attributes = True