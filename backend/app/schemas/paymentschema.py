from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid 
from decimal import Decimal 



class PaymentCreate(BaseModel):
    subscription_id: uuid.UUID 


class PaymentResponse(BaseModel):
    id: uuid.UUID
    subscription_id: uuid.UUID | None
    amount: Decimal
    currency: str
    gateway: str
    gateway_reference: str
    status: str
    checkout_url: str | None
    flutterwave_transaction_id: str | None
    created_at: datetime
    updated_at: datetime 

    model_config = ConfigDict(from_attributes=True)

class PaymentInitiateResponse(BaseModel):
    payment: PaymentResponse
    checkout_url: str