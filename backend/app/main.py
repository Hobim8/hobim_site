from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session


from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app.models import User
from app.auth.security import hash_password


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


