from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

class EntitlementGrant(BaseModel):

    user_id: uuid.UUID
    product_id: uuid.UUID



class EntitlementResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    product_id: uuid.UUID
    subscription_id: Optional[uuid.UUID] = None
    status: str
    granted_at: datetime
    expires_at: Optional[datetime] = None 

