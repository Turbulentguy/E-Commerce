from app.database import Base

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric
)
from sqlalchemy.orm import relationship

class OrderItem(Base):
    __tablename__ = "OrderItem"

    id = Column(Integer, primary_key = True)
    order_id = Column(Integer, ForeignKey("Order.id"), nullable = False)
    product_id = Column(Integer, ForeignKey("Product.id"), nullable = False)
    quantity = Column(Integer, nullable = False)
    unit_price = Column(Numeric(10, 2), nullable = False)
    subtotal = Column(Numeric(10, 2), nullable = False)

    order = relationship("Order", back_populates = "order_items")
    product = relationship("Product", back_populates = "order_items")
