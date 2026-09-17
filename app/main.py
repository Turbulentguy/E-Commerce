from fastapi import FastAPI

from app.database import Base, engine

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order
from app.models.orderitem import OrderItem
from app.models.payment import Payment

from app.routers import auth
from app.routers import categories
from app.routers import products

Base.metadata.create_all(bind = engine)

app = FastAPI()

@app.post("/root")
def Root():
    return {
        "message": "E-Commerce"
    }

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)