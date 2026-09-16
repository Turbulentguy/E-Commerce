from app.database import Base
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Numeric, 
    ForeignKey, 
    Boolean,
    DateTime,
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "Product"

    id = Column(Integer, primary_key = True)
    name = Column(String(255), unique = True, nullable = False)
    description = Column(String(255), nullable = True)
    price = Column(Numeric(10, 2), nullable = True)
    stock = Column(Integer, nullable = False)
    category_id = Column(Integer, ForeignKey("Category.id"), nullable = False)
    sku = Column(String(255), unique = True, nullable = False)
    is_active = Column(Boolean, nullable = False)
    created_at = Column(DateTime, server_default = func.now())
    updated_at = Column(DateTime, server_default = func.now())

    category = relationship("Category", back_populates = "products")
    order_items = relationship("OrderItem", back_populates = "product")