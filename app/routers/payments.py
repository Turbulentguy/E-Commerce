from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

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

        if existing is not None:
            raise HTTPException(
                status_code = 400,
                detail = f"Order {payment.order_id} already existed"
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

        existing = db.query(Payment).filter(
            Payment.order_id == payment.order_id
        ).first()
        
        if existing is not None:
            raise HTTPException(
                status_code = 400,
                detail = f"Order {payment.order_id} already existed"
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
    db.refresh(new_payment)

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

@router.patch("/payments/{payment_id}/status", response_model = PaymentResponse)
def updatePaymentStatus(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code = 403,
            detail = "Admin access required"
        )

    existing = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if existing is None:
        raise HTTPException(
            status_code = 404,
            detail = f"Payment {payment_id} not found"
        )

    if existing.status == "Paid":
        raise HTTPException(
            status_code = 400,
            detail = f"Payment {payment_id} already paid"
        )

    existing.status = "Paid"
    existing.paid_at = datetime.now()

    db.commit()
    db.refresh(existing)

    return existing

@router.patch("/payments/{payment_id}/cancel", response_model = PaymentResponse)
def cancelPayment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["Admin", "User"]:
        raise HTTPException(
            status_code = 403,
            detail = "Admin or User required access"
        )
    
    elif current_user.role == "Admin":
        existing = db.query(Payment).filter(
            Payment.id == payment_id
        ).first()

        if existing is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Payment {payment_id} not found"
            )

        existing.status = "Cancelled"

    elif current_user.role == "User":
        existing = db.query(Payment).join(Order).filter(
            (Payment.id == payment_id) &
            (Order.user_id == current_user.id)
        ).first()

        if existing is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Payment {payment_id} not found"
            )

        existing.status = "Cancelled"

    db.commit()
    db.refresh(existing)

    return existing