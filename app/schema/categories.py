from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str
    description: str

class CategoryCreateResponse(BaseModel):
    name: str

    class Config():
        from_attributes = True

class CategoryResponse(BaseModel):
    name: str
    description: str

    class Config():
        from_attributes = True

class CategoryPaginationResponse(BaseModel):
    items: list[CategoryResponse]
    page: int
    limit: int
    total: int