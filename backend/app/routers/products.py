from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List 

from app.database import get_db
from app.models import User, Product
from app.schemas.productschema import ProductCreate, ProductResponse
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

