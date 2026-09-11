import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Numeric 
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



class PricingTier(Base): 
    __tablename__ = "pricing_tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    tier_type = Column(SAEnum("free", "1_month", "6_month", "12_month", "lifetime", name="tier_type"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    pricing_tier_id = Column(UUID(as_uuid=True), ForeignKey("pricing_tiers.id"), nullable=False)
    status = Column(SAEnum("active", "cancelled", "expired", "pending", name="subscription_status"), default = "pending", nullable=False)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Entitlement(Base):
    __tablename__ = "entitlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    status = Column(SAEnum("active", "revoked", "expired", name="entitlement_status"), default="active", nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    __table_args__ = (
    UniqueConstraint("user_id", "product_id", name="uq_user_product_entitlement"),
    )










id — same UUID pattern
user_id — foreign key to users.id
product_id — foreign key to products.id
pricing_tier_id — foreign key to pricing_tiers.id
status — Enum: "active", "cancelled", "expired", "pending"
current_period_start — a DateTime, nullable (empty until the subscription actually activates)
current_period_end — same, nullable — this is what tells your system when a subscription needs renewing
created_at / updated_at — same pattern as always








