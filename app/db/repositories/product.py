from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_products(self):
        return self.db.query(Product).filter(Product.is_available == True).all()

    def get_product_by_id(self, product_id: str):
        return self.db.query(Product).filter(Product.id == product_id).first()

    def create_product(self, product: ProductCreate):
        db_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            image_url=product.image_url,
            category=product.category,
            ingredients=product.ingredients
        )
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product