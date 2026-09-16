from app.database import Base
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "Category"

    id = Column(Integer, primary_key = True)
    name = Column(String(55), unique = True, nullable = False)
    description = Column(String(255), unique = True, nullable = False)
    created_at = Column(DateTime, server_default = func.now())
    updated_at = Column(DateTime, server_default = func.now())

    products = relationship("Product", back_populates = "category")