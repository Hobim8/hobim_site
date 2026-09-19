from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from datetime import datetime, date
import uuid


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description='Valid email address')
    first_name: str = Field(..., min_length=3, max_length=20, description='First name required')
    last_name: str = Field(..., min_length=3, max_length=20, description='Last name required')
    username: str = Field(..., min_length=3, max_length=20, description='Username required')
    date_of_birth: date = Field(..., description='Date of birth in YYYY-MM-DD format')
    password: str = Field(..., min_length=8, description='Password (min 8 characters)')

    @field_validator('date_of_birth')
    @classmethod
    def age_must_be_18_or_older(cls, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise ValueError('Must be 18 years or older')
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    username: str
    date_of_birth: date
    role: str
    is_active: bool
    created_at: datetime


class UserLogin(BaseModel):
    identifier: str = Field(..., description='Email or username')
    password: str = Field(..., min_length=8, description='Password (min 8 characters)')


class Token(BaseModel):
    access_token: str
    token_type: str


class ForgotPassword(BaseModel):
    email: EmailStr = Field(..., description='Account email address')


class ResetPassword(BaseModel):
    """Payload for POST /auth/reset-password."""
    token: str = Field(..., description='The signed reset token from the email link')
    new_password: str = Field(..., min_length=8, description='New password (min 8 characters)')