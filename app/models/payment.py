from app.database import Base

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    String,
    DateTime
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Payment(Base):
    __tablename__ = "Payment"

    id = Column(Integer, primary_key = True)
    order_id = Column(Integer, ForeignKey("Order.id"), nullable = False)
    amount = Column(Numeric(10, 2), nullable = False)
    status = Column(String(10), nullable = False)
    payment_method = Column(String(13), nullable = False)
    transaction_id = Column(String(255), unique = True, nullable = False)
    paid_at = Column(DateTime, server_default = func.now())
    created_at = Column(DateTime, server_default = func.now())

    order = relationship("Order", back_populates = "payment")