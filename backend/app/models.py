import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Numeric,UniqueConstraint, Date 
from sqlalchemy.orm import Mapped, mapped_column 
from sqlalchemy import Enum as SAEnum 
from datetime import datetime 
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base 




class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)

    username: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    date_of_birth: Mapped[Date] = mapped_column(Date, nullable=False)

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )


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


class BotLicense(Base):
    __tablename__ = "bot_licenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entitlement_id = Column(UUID(as_uuid=True), ForeignKey("entitlements.id"), unique=True, nullable=False)
    broker_account_number = Column(String, nullable=False)
    license_key = Column(String, unique=True, nullable=False)
    is_self_hosted = Column(Boolean, default=False, nullable=False)
    last_validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    gateway = Column(SAEnum("paystack", "flutterwave", "stripe", "crypto", "google_pay", "apple_pay", name="payment_gateway"), nullable=False)
    gateway_reference = Column(String, unique=True, nullable=False)
    status = Column(SAEnum("pending", "success", "failed", "refunded", name="payment_status"), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)









    


















