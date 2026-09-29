from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid 

from app.database import get_db
from app.models import Subscription, User
from app.schemas.subscriptionschema import SubscriptionCreate, SubscriptionResponse
from app.auth.dependencies import get_current_user 



router = APIRouter(prefix='/subscription', tags=['subscription'])

@router.post('/', response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_sub (sub_data: SubscriptionCreate, 
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):

    existing_sub= db.query(Subscription).filter(Subscription.user_id == current_user.id,
                                                Subscription.product_id == sub_data.product_id).first()

    if existing_sub:
        raise HTTPException(
            status_code=409, 
            detail='Subscription already exist'
        )
                                        

    new_sub = Subscription(
        user_id=current_user.id,
        product_id=sub_data.product_id,
        pricing_tier_id=sub_data.pricing_tier_id,
        status='pending'
    )

    db.add(new_sub)
    db.commit()
    db.refresh(new_sub) 

    return(new_sub)


@router.get('/me', response_model=list[SubscriptionResponse])
def my_sub (
    db: Session=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()

    return sub 


@router.patch('/{subscription_id}/cancel', response_model=SubscriptionResponse)
def cancel_sub (
    subscription_id: int,
    db: Session=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()

    if not sub:
        raise HTTPException (
            status_code=404,
            detail='subscription not found'
        )

    sub.status = 'cancelled' 

    db.commit()
    db.refresh(sub)

    return sub 