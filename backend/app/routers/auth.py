"""Auth router — all public authentication endpoints.

Endpoints
---------
POST  /auth/signup           Register a new account (sends verification email)
POST  /auth/login            Exchange credentials for a JWT access token
GET   /auth/verify-email     Activate account via the emailed token
POST  /auth/forgot-password  Request a password-reset email
POST  /auth/reset-password   Set a new password using the emailed token
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.jwt import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    decode_token,
)
from app.auth.security import hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import ForgotPassword, ResetPassword, Token, UserCreate, UserResponse, UserLogin 
from app.services.email import send_password_reset_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account.

    - Checks for duplicate email and username.
    - Hashes the password with bcrypt.
    - Creates the user with is_active=False (inactive until email is verified).
    - Sends a verification email via Resend.
    """
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="This username is already taken.")

    new_user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username,
        date_of_birth=user_data.date_of_birth,
        hashed_password=hash_password(user_data.password),
        is_active=False,  # Activated by /verify-email
        role="user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send the verification email. The token encodes the user's UUID so we
    # don't need a separate tokens table.
    token = create_email_verification_token(str(new_user.id))
    send_verification_email(
        to_email=new_user.email,
        first_name=new_user.first_name,
        token=token,
    )

    return new_user


@router.post("/login", response_model=Token)
def login(login_data: "UserLogin", db: Session = Depends(get_db)):
    """Authenticate with email/username + password and receive a JWT access token."""
    

    user = (
        db.query(User).filter(User.email == login_data.identifier).first()
        or db.query(User).filter(User.username == login_data.identifier).first()
    )

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address first. Check your inbox for the activation link.",
        )

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-email", summary="Activate account via emailed token")
def verify_email(token: str = Query(..., description="Signed verification token from the email link"),
                 db: Session = Depends(get_db)):
    """Activate a user account.

    The frontend calls this endpoint after the user clicks the link in their
    verification email. The link looks like:
    ``https://hobimtrades.com/verify-email?token=<jwt>``
    The frontend reads the ``token`` query param and hits this endpoint.
    """
    try:
        payload = decode_token(token, expected_type="email_verify")
        sub = payload.get("sub")
        if not sub or not isinstance(sub, str):
            raise JWTError("Invalid payload")
        user_id: str = sub
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link is invalid or has expired. Please request a new one.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.is_active:
        return {"message": "Your email is already verified. You can log in."}

    user.is_active = True
    db.commit()

    return {"message": "Email verified successfully. You can now log in."}


@router.post("/forgot-password", summary="Request a password reset email")
def forgot_password(user_data: ForgotPassword, db: Session = Depends(get_db)):
    """Send a password-reset email if the given address is registered.

    Note: always returns 200 regardless of whether the email exists —
    this prevents user enumeration (an attacker finding out which emails
    are registered by trying different addresses).
    """
    user = db.query(User).filter(User.email == user_data.email).first()

    if user:
        token = create_password_reset_token(str(user.id))
        send_password_reset_email(
            to_email=user.email,
            first_name=user.first_name,
            token=token,
        )

    # Always return the same response whether the email exists or not.
    return {
        "message": "If an account with that email exists, a password reset link has been sent."
    }


@router.post("/reset-password", summary="Set a new password using the reset token")
def reset_password(payload: ResetPassword, db: Session = Depends(get_db)):
    """Complete the password-reset flow.

    The frontend collects the token from the URL query param and the user's
    new password, then posts both here.
    """
    try:
        decoded = decode_token(payload.token, expected_type="password_reset")
        sub = decoded.get("sub")
        if not sub or not isinstance(sub, str):
            raise JWTError("Invalid payload")
        user_id: str = sub
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset link is invalid or has expired. Please request a new one.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.hashed_password = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password has been reset successfully. You can now log in with your new password."}

