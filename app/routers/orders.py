from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies import get_current_user
from app.schema.orders import OrderCreate, OrderCreateResponse

from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.orderitem import OrderItem

router = APIRouter(
    tags = ["Orders"]
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.post("/orders", response_model = OrderCreateResponse)
def addOrder(
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["Admin", "User"]:
        raise HTTPException(
            status_code = 403,
            detail = "Admin or Customer access required"
        )

    total_price = 0

    for item in order.items:
        query_item = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if query_item is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Product ID {item.product_id}: not found"
            )

        if item.quantity <= 0:
            raise HTTPException(
                status_code = 400,
                detail = "Quantity musst be greater than 0"
            )

        if item.quantity > query_item.stock:
            raise HTTPException(
                status_code = 400,
                detail = f"Product ID {item.product_id}: Insufficient stock"
            )

        query_item.stock -= item.quantity
        total_price += item.quantity * query_item.price

    new_order = Order(
        user_id = current_user.id,
        total_price = total_price,
        shipping_address = order.shipping_address
    )

    db.add(new_order)
    db.flush()

    for item in order.items:
        query = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if query is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Product ID {item.product_id}: not found"
            )

        new_order_item = OrderItem(
            order_id = new_order.id,
            product_id = item.product_id,
            quantity = item.quantity,
            unit_price = query.price,
            subtotal = query.price * item.quantity
        )

        db.add(new_order_item)

    db.commit()
    db.refresh(new_order)

    return new_order

@router.get("/orders", response_model = list[OrderCreateResponse])
def getAllOrders(
    current_user: User = Depends(get_current_user),
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code = 403,
            detail = "Admin access required"
        )

    query = db.query(Order)
    offset = (page - 1) * limit

    query = query.offset(offset).limit(limit).all()

    return query

@router.get("/orders/me", response_model = list[OrderCreateResponse])
def getMyOrders(
    current_user: User = Depends(get_current_user),
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    if current_user.role not in ["Admin", "User"]:
        raise HTTPException(
            status_code = 403,
            detail = "Customer access required"
        )
    
    query = db.query(Order).filter(
        Order.user_id == current_user.id
    )

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).all()

    return query

@router.get("/orders/{order_id}", response_model = OrderCreateResponse)
def getOrderByID(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["Admin", "User"]:
        raise HTTPException(
            status_code = 403,
            detail = "Admin or User access required"
        )

    if current_user.role == "Admin":
        query = db.query(Order).filter(
            Order.id == order_id
        ).first()

        if query is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Order {order_id}: not found"
            )

    if current_user.role == "User":
        query = db.query(Order).filter(
            (Order.user_id == current_user.id) &
            (Order.id == order_id)
        ).first()

        if query is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Order {order_id}: not found"
            )

    return query

@router.patch("/orders/{order_id}/cancel")
def cancelOrder(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user.role == "Admin":
        query = db.query(Order).filter(
            Order.id == order_id
        ).first()
        
        if query is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Order {order_id} not found"
            )

        query_order = db.query(OrderItem).filter(
            OrderItem.order_id == order_id
        ).all()

        for item in query_order:
            query_product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()

            query_product.stock += item.quantity
        
        query.status = "Cancelled"

    if current_user.role == "User":
        query = db.query(Order).filter(
            (Order.user_id == current_user.id) &
            (Order.id == order_id)
        ).first()

        if query is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Order {order_id} not found"
            )

        query_order = db.query(OrderItem).filter(
            OrderItem.order_id == order_id
        ).all()
        
        for item in query_order:
            query_product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()
        
            query_product.stock += item.quantity

        query.status = "Cancelled"

    db.commit()

@router.patch("/orders/{order_id}/status")
def completeOrder(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "Admin":
        query = db.query(Order).filter(
            Order.id == order_id
        ).first()

        if query is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Order {order_id}: not found"
            )

        query.status = "Completed"

    if current_user.role == "User":
        query = db.query(Order).filter(
            (Order.user_id == current_user.id) &
            (Order.id == order_id)
        ).first()

        if query is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Order {order_id} not found"
            )

        query.status = "Completed"