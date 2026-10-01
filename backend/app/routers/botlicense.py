from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime,timezone


from app.database import get_db
from app.models import BotLicense, User, Entitlement
from app.auth.security import generate_license_key
from app.schemas.botlicenseschema import BotLicenseActivate, BotLicenseCreate, BotLicenseResponse, BotLicenseValidate 
from app.auth.dependencies import get_current_user, get_current_admin



router = APIRouter(prefix='/botlicense', tags=['botlicense'])


@router.post('/', response_model=BotLicenseResponse, status_code=status.HTTP_201_CREATED)
def create_license (
    license_data: BotLicenseCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    if db.query(BotLicense).filter(
        BotLicense.entitlement_id == license_data.entitlement_id
        ).first():
        raise HTTPException(status_code=400, detail='This entitlement already has a license')

    entitlement = db.query(Entitlement).filter(
        Entitlement.id == license_data.entitlement_id).first()
    if not entitlement:
        raise HTTPException(status_code=404, detail='Entitlement not found')

    new_key = generate_license_key()

    new_botlicense = BotLicense(
        entitlement_id = license_data.entitlement_id,
        broker_account_number = license_data.broker_account_number,
        license_key = new_key,
        is_self_hosted = license_data.is_self_hosted,
    ) 

    db.add(new_botlicense)
    db.commit ()
    db.refresh(new_botlicense)

    return(new_botlicense)



@router.post('/activate', response_model=BotLicenseResponse, status_code=status.HTTP_201_CREATED)
def activate_bot_license(
    activation_data: BotLicenseActivate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entitlement = db.query(Entitlement).filter(
        Entitlement.user_id == current_user.id,
        Entitlement.product_id == activation_data.product_id,
        Entitlement.status == 'active',
    ).first()

    if not entitlement:
        raise HTTPException(status_code=403, detail="You don't have active access to this product")

    if db.query(BotLicense).filter(BotLicense.entitlement_id == entitlement.id).first():
        raise HTTPException(status_code=409, detail="This bot is already activated")

    new_key = generate_license_key()

    new_bot_license = BotLicense(
        entitlement_id=entitlement.id,
        broker_account_number=activation_data.broker_account_number,
        license_key=new_key,
        is_self_hosted=activation_data.is_self_hosted,
    )

    db.add(new_bot_license)
    db.commit ()
    db.refresh(new_bot_license)

    return(new_bot_license)  




@router.post("/validate")
def validate_bot_license(
    validation_data: BotLicenseValidate,
    db: Session = Depends(get_db),
):

    license = (
        db.query(BotLicense)
        .filter(
            BotLicense.license_key == validation_data.license_key,
            BotLicense.broker_account_number
            == validation_data.broker_account_number,
        )
        .first()
    )

    
    if not license:
        return {"valid": False}

    
    entitlement = (
        db.query(Entitlement)
        .filter(Entitlement.id == license.entitlement_id)
        .first()
    )

    
    if not entitlement:
        return {"valid": False}

    
    if entitlement.status != "active":
        return {"valid": False}

    
    license.last_validated_at = datetime.now(timezone.utc)

    db.commit()

    return {"valid": True}

    
