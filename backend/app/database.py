from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base 
from dotenv import load_dotenv 
import os 


load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 10})

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("successfully connnected")
    except Exception as e:
        print(f"failed to connect : {e}")











