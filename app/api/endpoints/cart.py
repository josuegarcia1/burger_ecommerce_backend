from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.schemas.cart import CartItemCreate, CartItemInDB, CartItemUpdate
from app.services.cart_service import CartService
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=list[CartItemInDB])
async def get_cart_items(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    service = CartService(db)
    return await service.get_cart_items(current_user.id)

@router.post("/", response_model=CartItemInDB)
async def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    service = CartService(db)
    return await service.add_to_cart(current_user.id, item)

@router.put("/{item_id}", response_model=CartItemInDB)
async def update_cart_item(
    item_id: str,
    item: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    service = CartService(db)
    return await service.update_cart_item(item_id, item)

@router.delete("/{item_id}")
async def remove_from_cart(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    service = CartService(db)
    await service.remove_from_cart(item_id)
    return {"message": "Item removed from cart"}