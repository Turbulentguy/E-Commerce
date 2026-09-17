from pydantic import BaseModel
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: int
    sku: str
    is_active: bool

class ProductCreateResponse(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: int

    class Config():
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: int
    sku: str
    is_active: bool

    class Config():
        from_attributes = True

class ProductPaginationResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    limit: int
    total: int