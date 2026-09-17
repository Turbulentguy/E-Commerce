import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt

load_dotenv()

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    )

    to_encode.update({
        "exp": expire
    })

    token = jwt.encode(
        to_encode,
        os.getenv("SECRET_KEY"),
        algorithm = os.getenv("ALGORITHM")
    )

    return token