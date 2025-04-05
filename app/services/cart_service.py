from typing import List
from app.db.repositories.cart import CartRepository
from app.schemas.cart import CartItemCreate, CartItemInDB, CartItemUpdate
from app.utils.aws_client import AWSClient
from app.core.sync_manager import SyncManager

class CartService:
    def __init__(self, db):
        self.repo = CartRepository(db)
        self.aws_client = AWSClient()
        self.sync_manager = SyncManager()

    async def get_cart_items(self, user_id: str) -> List[CartItemInDB]:
        await self.sync_manager.sync_data()
        
        if await self.aws_client.is_online():
            try:
                items = await self.aws_client.get_cart_items(user_id)
                await self.repo.bulk_update_cart(user_id, items)
                return items
            except Exception:
                return self.repo.get_cart_items(user_id)
        else:
            return self.repo.get_cart_items(user_id)

    async def add_to_cart(self, user_id: str, cart_item: CartItemCreate):
        created_item = self.repo.add_to_cart(user_id, cart_item)
        
        if await self.aws_client.is_online():
            try:
                await self.aws_client.add_to_cart(created_item)
            except Exception:
                self.repo.add_pending_operation({
                    'type': 'add_cart_item',
                    'data': created_item.dict()
                })
        else:
            self.repo.add_pending_operation({
                'type': 'add_cart_item',
                'data': created_item.dict()
            })
        
        return created_item

    async def update_cart_item(self, item_id: str, cart_item: CartItemUpdate):
        updated_item = self.repo.update_cart_item(item_id, cart_item)
        
        if await self.aws_client.is_online():
            try:
                await self.aws_client.update_cart_item(updated_item)
            except Exception:
                self.repo.add_pending_operation({
                    'type': 'update_cart_item',
                    'data': updated_item.dict()
                })
        else:
            self.repo.add_pending_operation({
                'type': 'update_cart_item',
                'data': updated_item.dict()
            })
        
        return updated_item

    async def remove_from_cart(self, item_id: str):
        self.repo.remove_from_cart(item_id)
        
        if await self.aws_client.is_online():
            try:
                await self.aws_client.remove_from_cart(item_id)
            except Exception:
                self.repo.add_pending_operation({
                    'type': 'remove_cart_item',
                    'item_id': item_id
                })
        else:
            self.repo.add_pending_operation({
                'type': 'remove_cart_item',
                'item_id': item_id
            })