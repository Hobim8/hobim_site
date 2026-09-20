from pydantic import BaseModel, ConfigDict 
from datetime import datetime 
from typing import Optional, List
import uuid 
from app.schemas.pricingtierschema import PricingTierResponse



class ProductCreate(BaseModel):
    name: str
    product_type:str
    slug: str
    description: Optional[str] = None
    content_url: Optional[str] = None  


class ProductResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    product_type: str
    slug: str
    description: Optional[str] = None 
    content_url: Optional[str] = None 
    is_active: bool
    created_at: datetime
    updated_at: datetime 


class ProductDetailResponse(ProductResponse):
    pricing_tiers: List[PricingTierResponse] = []
