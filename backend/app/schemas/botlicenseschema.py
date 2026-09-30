from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid
from typing import Optional


class BotLicenseActivate(BaseModel):

    product_id: uuid.UUID
    broker_account_number: str 
    is_self_hosted: bool = False


class BotLicenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entitlement_id: uuid.UUID
    broker_account_number: str 
    license_key: str
    is_self_hosted: bool
    last_validated_at: Optional[datetime] = None 
    created_at: datetime 


class BotLicenseValidate(BaseModel):

    broker_account_number: str
    license_key: str 


