from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.product import Product, ProductCreate
from app.services.product_service import ProductService
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=list[Product])
async def get_products(db: Session = Depends(get_db)):
    service = ProductService(db)
    return await service.get_all_products()

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    return await service.get_product_by_id(product_id)

@router.post("/", response_model=Product)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    return await service.create_product(product)