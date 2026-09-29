from  pydantic import BaseModel, ConfigDict
import uuid 
from datetime import datetime 
from decimal import Decimal 


class PricingTierCreate(BaseModel):
    product_id: uuid.UUID
    price: Decimal
    tier_type: str
    currency: str = "USD"
    is_active: bool = True 
    


class PricingTierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    price: Decimal
    tier_type: str
    currency: str = "USD"
    is_active: bool = True 
    created_at: datetime
    updated_at: datetime


