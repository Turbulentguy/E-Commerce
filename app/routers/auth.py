from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import bcrypt

from app.database import SessionLocal
from app.schema.auth import UserRegister, UserRegisterResponse
from app.services.auth import create_access_token
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(
    prefix = "/auth",
    tags = ["Auth"]
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model = UserRegisterResponse)
def Register(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    existing_email = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code = 400,
            detail = "Email already registered"
        )

    password_hash = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    new_user = User(
        email = user.email,
        password_hash = password_hash,
        first_name = user.first_name,
        last_name = user.last_name,
        role = "User",
        is_active = True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def Login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if db_user is None or not bcrypt.checkpw(
        form_data.password.encode("utf-8"),
        db_user.password_hash.encode("utf-8")
    ):
        raise HTTPException(
            status_code = 400,
            detail = "Invalid email or password" 
        )

    access_token = create_access_token(
        data = {"sub": str(db_user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/profile")
def Profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return current_user