from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.jwt import decode_token
from app.database import get_db
from app.models import User

# Tells FastAPI where clients send their access tokens.
# The tokenUrl value is used by the OpenAPI /docs UI to populate the
# "Authorize" button — it must match the login endpoint path.
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency that validates the Bearer token and returns the authenticated User.

    Usage::

        @router.get("/me")
        def me(current_user: User = Depends(get_current_user)):
            return current_user

    Raises:
        401 Unauthorized  — token is missing, malformed, or expired.
        401 Unauthorized  — user ID from the token no longer exists in the DB.
        403 Forbidden     — account exists but email has not been verified yet.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token, expected_type="access")
        sub = payload.get("sub")
        if not sub or not isinstance(sub, str):
            raise credentials_exception
        user_id: str = sub
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before accessing this resource.",
        )

    return user


def get_current_admin (current_user: User=Depends(get_current_user)) -> User:
    if current_user.role !="admin":
        raise HTTPException (status_code=403, detail="Admin access required")
    return current_user
