from pydantic import BaseModel,Field, EmailStr, field_validator 
from datetime import datetime, date 
import uuid 


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description='vaild email address')
    first_name: str = Field(..., min_length = 3, max_length = 20, description= 'first name required')
    last_name: str = Field(..., min_length = 3, max_length = 20, description= 'first name required')
    username: str = Field(..., min_length = 3, max_length = 20, description= 'username required')
    date_of_birth: date = Field(..., description='Date of birth in YYYY-MM-DD format')
    password: str = Field(..., min_length = 8, description= 'password(min 8 character)')

    @field_validator('date_of_birth')
    @classmethod

    def age_must_be_18_or_older(cls, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise ValueError('must be 18 years or older')
        return value 

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    username: str 
    date_of_birth: date
    role: str
    is_active: bool
    created_at: datetime 
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    identifier: str = Field(..., description='email or username is required')
    password: str = Field(..., min_length = 8, description= 'password(min 8 characters)')

class Token(BaseModel):
    access_token: str
    token_type: str

class ForgotPassword(BaseModel):
    email: EmailStr = Field(..., description='Account email address is required')