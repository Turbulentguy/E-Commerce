from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.category import Category
from app.dependencies import get_current_user
from app.schema.categories import CategoryCreate, CategoryCreateResponse, CategoryResponse, CategoryPaginationResponse
from app.database import SessionLocal

router = APIRouter(
    tags = ["Categories"]
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.post("/categories", response_model = CategoryCreateResponse)
def addCategory(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code = 403,
            detail = "Admin access required"
        )

    existing_category = db.query(Category).filter(
        Category.name == category.name
    ).first()

    if existing_category:
        raise HTTPException(
            status_code = 400,
            detail = "Category already registered"
        )

    new_category = Category(
        name = category.name,
        description = category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

@router.put("/categories/{category_id}", response_model = CategoryCreate)
def updateCategory(
    category_id: int,
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code = 403,
            detail = "Admin access required"
        )
    
    query = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if query is None:
        raise HTTPException(
            status_code = 404,
            detail = "Category not found"
        )

    query.name = category.name
    query.description = category.description

    db.commit()
    db.refresh(query)

    return query

@router.delete("/categories{category_id}")
def deleteAllCategory(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code = 403,
            detail = "Admin access required"
        )

    query = db.query(Category).filter(
        Category.id == category_id
    ).first()

    db.delete(query)
    db.commit()

@router.get("/categories", response_model = CategoryPaginationResponse)
def getAllCategory(
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Category)

    if search:
        query = query.filter(
            Category.name.ilike(f"%{search}%")
        )

    if query is None:
        raise HTTPException(
            status_code = 404,
            detail = "Category not found"
        )

    total = query.count()

    offset = (page - 1) * limit
    categories = query.offset(offset).limit(limit).all()

    return {
        "items": categories,
        "page": page,
        "limit": limit,
        "total": total
    }

@router.get("/categories/{category_id}", response_model = CategoryResponse)
def getCategoryByID(
    category_id: int,
    db: Session = Depends(get_db)
):
    query = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if query is None:
        raise HTTPException(
            status_code = 404,
            detail = "Category not found"
        )

    return query