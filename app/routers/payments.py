from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database import SessionLocal
from app.dependencies import get_current_user

from app.models.user import User
from app.models.order import Order
from app.models.payments import Payment

from app.schema.payments import PaymentCreate, PaymentResponse

router = APIRouter(
    tags = ["Payments"]
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.post("/payments", response_model = PaymentResponse)
def addPayment(
    payment: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "Admin":
        target = db.query(Order).filter(
            Order.id == payment.order_id 
        ).first()

        if target is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Order {payment.order_id} not found"
            )

        if target.status == "Cancelled":
            raise HTTPException(
                status_code = 400,
                detail = f"Order {payment.order_id} is cancelled and cannot be paid"
            )

        existing = db.query(Payment).filter(
            Payment.order_id == payment.order_id
        ).first()

        if existing.status != "Pending":
            raise HTTPException(
                status_code = 400,
                detail = f"Order {payment.order_id}'s status isn't pending"
            )

        new_payment = Payment(
            order_id = payment.order_id,
            amount = target.total_price,
            status = "Pending",
            payment_method = payment.payment_method,
            transaction_id = f"TXN-{uuid.uuid4().hex}" # Generate random strings
        )

    if current_user.role == "User":
        target = db.query(Order).filter(
            (Order.user_id == current_user.id) &
            (Order.id == payment.order_id)
        ).first()

        if target is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Order {payment.order_id} not found"
            )

        if target.status == "Cancelled":
            raise HTTPException(
                status_code = 400,
                detail = f"Order {payment.order_id} is cancelled and cannot be paid"
            )

        if existing.status != "Pending":
            raise HTTPException(
                status_code = 400,
                detail = f"Order {payment.order_id}'s status isn't pending"
            )

        new_payment = Payment(
            order_id = payment.order_id,
            amount = target.total_price,
            status = "Pending",
            payment_method = payment.payment_method,
            transaction_id = f"TXN-{uuid.uuid4().hex}"
        )

    db.add(new_payment)
    db.commit()
    db.refresh()

    return new_payment

@router.get("/payments/me", response_model = list[PaymentResponse])
def getMyPayment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    orders = db.query(Payment).join(Order).filter(
        Order.user_id == current_user.id
    ).all()

    return orders
