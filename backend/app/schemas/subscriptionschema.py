from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid
from typing import Optional



class SubscriptionCreate(BaseModel):
    product_id: uuid.UUID
    pricing_tier_id: uuid.UUID


class SubscriptionResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    product_id: uuid.UUID
    pricing_tier_id: uuid.UUID
    status: str 
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None 
    created_at: datetime
    updated_at: datetime








