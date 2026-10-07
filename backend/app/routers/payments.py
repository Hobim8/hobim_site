from fastapi import APIRouter, HTTPException, Depends, status 
from sqlalchemy.orm import Session 
from typing import List, Optional 
import uuid 
import os 


from app.database import get_db
from app.models import User, Payment, Subscription, PricingTier
from app.schemas.paymentschema import PaymentCreate, PaymentResponse, PaymentInitiateResponse
from app.services.flutterwave import initiate_transaction
from app.auth.dependencies import get_current_user

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
router = APIRouter(prefix='/payments', tags=['payments'])

@router.post('/initiate', response_model=PaymentInitiateResponse, status_code=status.HTTP_201_CREATED) 
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscription = db.query(Subscription).filter(
        Subscription.id == data.subscription_id,
        Subscription.user_id == current_user.id 
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail='Subscription not found')

    pricing_tier = db.query(PricingTier).filter(
        PricingTier.id == subscription.pricing_tier_id
    ).first()

    if not pricing_tier:
        raise HTTPException(status_code=404, detail='Pricing tier not found')

    gateway_reference = f"FLW-{uuid.uuid4()}"

    new_payment = Payment(
        user_id=current_user.id,
        subscription_id=subscription.id,
        amount=pricing_tier.price,
        currency=pricing_tier.currency,
        gateway='flutterwave',
        gateway_reference=gateway_reference,
        status='pending',
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    flw_response = initiate_transaction(
        tx_ref=gateway_reference,
        amount=pricing_tier.price,
        currency=pricing_tier.currency,
        email=current_user.email,
        redirect_url=f"{FRONTEND_URL}/payment-complete",
    )

    flw_data = flw_response["data"]

    checkout_url = flw_data["link"]
    flutterwave_transaction_id = flw_data.get("id")

    new_payment.checkout_url = checkout_url
    new_payment.flutterwave_transaction_id = (
        str(flutterwave_transaction_id)
        if flutterwave_transaction_id is not None
        else None
    )

    db.commit()
    db.refresh(new_payment)

    return {"payment": new_payment, "checkout_url": checkout_url}


