from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.product import Product
from app.dependencies import get_current_user
from app.database import SessionLocal
from app.schema.products import ProductCreate, ProductCreateResponse, ProductResponse, ProductPaginationResponse

router = APIRouter(
    tags = ["Products"]
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.post("/products", response_model = ProductCreateResponse)
def addProduct(
    product: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code = 403,
            detail = "Admin access required"
        )

    existing_name = db.query(Product).filter(
        Product.name == product.name
    ).first()

    if existing_name:
        raise HTTPException(
            status_code = 400,
            detail = "Product already registered"
        )

    new_product = Product(
        name = product.name,
        description = product.description,
        price = product.price,
        stock = product.stock,
        category_id = product.category_id,
        sku = product.sku,
        is_active = product.is_active
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@router.put("/products/{product_id}", response_model = ProductResponse)
def updateAllProduct(
    product_id: int,
    product: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code = 403,
            detail = "Admin access required"
        )

    query = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if query is None:
        raise HTTPException(
            status_code = 404,
            detail = "Product not found"
        )

    query.name = product.name
    query.description = product.description
    query.price = product.price
    query.stock = product.stock
    query.category_id = product.category_id
    query.sku = product.sku
    query.is_active = product.is_active

    db.commit()
    db.refresh(query)

    return query

@router.delete("/products/{product_id}")
def deleteProduct(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code = 403,
            detail = "Admin access required"
        )

    query = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if query is None:
        raise HTTPException(
            status_code = 404,
            detail = "Product not found"
        )

    db.delete(query)
    db.commit()

@router.get("/products", response_model = ProductPaginationResponse)
def getAllProduct(
    search: str | None = None,
    category_id: int | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    if category_id:
        query = query.filter(
            Product.category_id == category_id
        )

    total = query.count()

    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()

    return {
        "items": products,
        "page": page,
        "limit": limit,
        "total": total
    }

@router.get("/products/{product_id}", response_model = ProductResponse)
def getProductByID(
    product_id: int,
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if query is None:
        raise HTTPException(
            status_code = 404,
            detail = "Product not found"
        )

    return query