from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def _encode(data: dict, expires_delta: timedelta) -> str:
    """Sign a payload and return a JWT string."""
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict) -> str:
    """Short-lived token used to authenticate API requests (60 min)."""
    return _encode({**data, "type": "access"}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_email_verification_token(user_id: str) -> str:
    """One-time token emailed to the user to activate their account (24 h)."""
    return _encode({"sub": user_id, "type": "email_verify"}, timedelta(hours=24))


def create_password_reset_token(user_id: str) -> str:
    """One-time token emailed to the user so they can reset their password (1 h)."""
    return _encode({"sub": user_id, "type": "password_reset"}, timedelta(hours=1))


def decode_token(token: str, expected_type: str) -> dict:
    """Decode and validate a JWT.

    Args:
        token: The raw JWT string.
        expected_type: The 'type' claim this token must carry (e.g. 'access',
            'email_verify', 'password_reset').

    Returns:
        The decoded payload dict.

    Raises:
        JWTError: If the token is invalid, expired, or has the wrong type.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise JWTError("Invalid or expired token")

    if payload.get("type") != expected_type:
        raise JWTError(f"Expected token type '{expected_type}', got '{payload.get('type')}'")

    return payload
