from app.database import Base
from sqlalchemy import (
    Column, 
    Integer, 
    ForeignKey, 
    String, 
    Numeric, 
    DateTime
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__ = "Order"

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable = False)
    status = Column(String(10), default = "Confirmed", nullable = False)
    total_price =  Column(Numeric(10, 2), nullable = False)
    shipping_address = Column(String, nullable = False)
    created_at = Column(DateTime, server_default = func.now())
    updated_at = Column(DateTime, server_default = func.now())

    user = relationship("User", back_populates = "orders")
    order_items = relationship("OrderItem", back_populates = "order")
    payment = relationship("Payment", back_populates = "order")