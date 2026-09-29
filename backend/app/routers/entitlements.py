from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import Entitlement, User 
from app.schemas.entitlementschema import EntitlementGrant, EntitlementResponse
from app.auth.dependencies import get_current_user, get_current_admin


router = APIRouter(prefix='/entitlements', tags=['entitlements'])


@router.post('/', response_model=EntitlementResponse, status_code=status.HTTP_201_CREATED)
def grant_entitlement(
    grant_data: EntitlementGrant,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Admin-only: give a user access to a product, or reactivate a previously revoked one."""

    existing_grant = db.query(Entitlement).filter(
        Entitlement.user_id == grant_data.user_id,
        Entitlement.product_id == grant_data.product_id,
    ).first()

    if existing_grant:
        if existing_grant.status == 'active':
            raise HTTPException(status_code=409, detail='user already has active access to this product')

        existing_grant.status = 'active'
        db.commit()
        db.refresh(existing_grant)  
        return existing_grant

    new_entitlement = Entitlement(
        user_id=grant_data.user_id,
        product_id=grant_data.product_id,
        subscription_id=None,
        status='active',
    )

    db.add(new_entitlement)
    db.commit
    db.refresh(new_entitlement)
    return new_entitlement

@router.patch('/{entitlement_id}/revoke', response_model=EntitlementResponse)
def revoke_entitlement(
    entitlement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Admin_only: revoke a user's access to a product"""

    entitlement = db.query(Entitlement).filter(Entitlement.id == entitlement_id).first()

    if not entitlement:
        raise HTTPException(status_code=404, detail='Entitlement not found')

    entitlement.status = 'revoked'
    db.commit()
    db.refresh(entitlement)

    return entitlement

@router.get('/me', response_model=list[EntitlementResponse])
def my_entitlements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Any logged-in user: see everything they have access to """
    return db.query(Entitlement).filter(Entitlement.user_id == current_user.id).all()

