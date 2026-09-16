from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session


from app.database import get_db
from app.schemas import UserCreate, UserResponse, Token, UserLogin, ForgotPassword  
from app.models import User
from app.auth.security import hash_password,verify_password 
from app.auth.jwt import create_access_token

app = FastAPI()

@app.post('/signup', response_model=UserResponse)
def signup (user_data: UserCreate, db: Session=Depends(get_db)):

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Account already exists.")

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken.")

    hashed = hash_password(user_data.password)

    new_user = User(email=user_data.email, first_name=user_data.first_name, last_name=user_data.last_name,
                    hashed_password=hashed, username=user_data.username, date_of_birth=user_data.date_of_birth)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user 


@app.post('/login', response_model=Token)
def login(login_data: UserLogin, db: Session=Depends(get_db)):

    user = db.query(User).filter(User.email == login_data.identifier).first() or db.query(User).filter(User.username == login_data.identifier).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='invalid credentials')

    if not user.is_active:
        raise HTTPException(status_code=403, detail='verify your email address')

    access_token = create_access_token({'sub': str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

    

@app.post('/forgot-password')
def forgot_password(user_data: ForgotPassword, db: Session=Depends(get_db)):

    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail='No account registered with this email address')