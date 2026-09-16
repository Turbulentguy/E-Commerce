from fastapi import FastAPI

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order
from app.models.orderitem import OrderItem
from app.models.payment import Payment

from app.routers import auth

app = FastAPI()

@app.post("/")
def Root():
    return {
        "message": "E-Commerce"
    }

app.include_router(auth.router)