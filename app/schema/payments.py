from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    status: str
    payment_method: str
    transaction_id: str
    paid_at: datetime | None
    created_at: datetime

    class Config():
        from_attributes = True