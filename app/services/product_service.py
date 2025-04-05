from typing import List
from app.db.repositories.product import ProductRepository
from app.schemas.product import Product, ProductCreate
from app.utils.aws_client import AWSClient

class ProductService:
    def __init__(self, db):
        self.repo = ProductRepository(db)
        self.aws_client = AWSClient()

    async def get_all_products(self) -> List[Product]:
        if await self.aws_client.is_online():
            try:
                return await self.aws_client.get_all_products()
            except Exception:
                return self.repo.get_all_products()
        else:
            return self.repo.get_all_products()

    async def get_product_by_id(self, product_id: str) -> Product:
        if await self.aws_client.is_online():
            try:
                return await self.aws_client.get_product_by_id(product_id)
            except Exception:
                return self.repo.get_product_by_id(product_id)
        else:
            return self.repo.get_product_by_id(product_id)

    async def create_product(self, product: ProductCreate) -> Product:
        created_product = self.repo.create_product(product)
        
        if await self.aws_client.is_online():
            try:
                await self.aws_client.create_product(created_product)
            except Exception:
                self.repo.add_pending_operation({
                    'type': 'create_product',
                    'data': created_product.dict()
                })
        else:
            self.repo.add_pending_operation({
                'type': 'create_product',
                'data': created_product.dict()
            })
        
        return created_product