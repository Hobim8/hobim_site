from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List 
import uuid

from app.database import get_db
from app.models import User, Product, PricingTier
from app.schemas.productschema import ProductCreate, ProductResponse, ProductDetailResponse
from app.schemas.pricingtierschema import PricingTierResponse, PricingTierCreate
from app.auth.dependencies import get_current_admin


router = APIRouter(prefix='/products', tags=['products'])


@router.post('/', response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, 
                   db: Session = Depends(get_db), 
                   current_admin: User = Depends(get_current_admin)):
    
    if db.query(Product).filter(Product.slug == product_data.slug).first():
        raise HTTPException(status_code=400, detail='product with this slug already exist')

    new_product = Product(
        name=product_data.name,
        product_type=product_data.product_type,
        slug=product_data.slug,
        description=product_data.description,
        content_url=product_data.content_url,
        is_active=True,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.get('/', response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    return products


@router.get('/{slug}', response_model=ProductDetailResponse)
def get_product(slug: str, db: Session = Depends(get_db)):

    slug_product = db.query(Product).filter(Product.slug == slug).first()

    if not slug_product:
        raise HTTPException(
            status_code=404,
            detail='product not found'
        )

    tiers = db.query(PricingTier).filter(
        PricingTier.product_id == slug_product.id
    ).all()

    slug_product.pricing_tiers = tiers

    return slug_product
        

@router.post('/{product_id}/pricing-tiers', response_model=PricingTierResponse, status_code=status.HTTP_201_CREATED)
def create_pricing_tier (product_id: uuid.UUID,
                         tier_data: PricingTierCreate,
                         db: Session=Depends(get_db),
                         current_admin: User = Depends(get_current_admin)):

    product_check = db.query(Product).filter(Product.id == product_id).first()

    if not product_check:
        raise HTTPException(status_code=404,
                            detail='prodcut not found')

    new_product_tier = PricingTier(
        product_id=product_id,
        tier_type=tier_data.tier_type,
        price=tier_data.price,
        currency=tier_data.currency,
        is_active=True
    )

    db.add(new_product_tier)
    db.commit()
    db.refresh(new_product_tier)

    return new_product_tier  


