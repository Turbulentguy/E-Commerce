from app.database import Base
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    DateTime
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key = True)
    email = Column(String(255), unique = True, nullable = False)
    password_hash = Column(String(255), nullable = False)
    first_name = Column(String(255), nullable = False)
    last_name = Column(String(255), nullable = False)
    role = Column(String(5), nullable = False)
    is_active = Column(Boolean, nullable = False)
    created_at = Column(DateTime, server_default = func.now())
    updated_at = Column(DateTime, server_default = func.now())

    orders = relationship("Order", back_populates = "user")