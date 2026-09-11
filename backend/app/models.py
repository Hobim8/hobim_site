import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text 
from sqlalchemy.orm import relationship 
from sqlalchemy import Enum as SAEnum 
from datetime import datetime 
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base 




class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    email = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    role = Column(SAEnum("user", "admin", name="user_role"), default="user", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)



class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_type = Column(SAEnum("course", "bot", "mentorship", name="product_type"), nullable=False)
    name = Column(String, nullable=False) 
    slug = Column(String, unique=True, nullable=False, index=True)
    content_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)



class pricingtier(Base): 