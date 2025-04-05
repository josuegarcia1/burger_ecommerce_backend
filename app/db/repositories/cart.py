from sqlalchemy.orm import Session
from app.models.cart import CartItem
from app.schemas.cart import CartItemCreate, CartItemUpdate

class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_cart_items(self, user_id: str):
        return self.db.query(CartItem).filter(CartItem.user_id == user_id).all()

    def add_to_cart(self, user_id: str, item: CartItemCreate):
        db_item = CartItem(
            user_id=user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            options=item.options
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update_cart_item(self, item_id: str, item: CartItemUpdate):
        db_item = self.db.query(CartItem).filter(CartItem.id == item_id).first()
        if not db_item:
            return None
        
        if item.quantity is not None:
            db_item.quantity = item.quantity
        if item.options is not None:
            db_item.options = item.options
            
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def remove_from_cart(self, item_id: str):
        db_item = self.db.query(CartItem).filter(CartItem.id == item_id).first()
        if db_item:
            self.db.delete(db_item)
            self.db.commit()
            return True
        return False

    def bulk_update_cart(self, user_id: str, items: list):
        # Implementar actualización masiva según necesidades
        pass