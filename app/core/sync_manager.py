import logging
from typing import Optional
from app.db.repositories.cart import CartRepository
from app.db.local_db import LocalDB
from app.utils.aws_client import AWSClient

logger = logging.getLogger(__name__)

class SyncManager:
    def __init__(self):
        self.aws_client = AWSClient()
        self.local_db = LocalDB()
        self.cart_repo = CartRepository()

    async def sync_data(self):
        """Sincroniza datos locales con AWS cuando hay conexión"""
        if not await self._is_online():
            return

        pending_operations = self.local_db.get_pending_operations()
        
        for operation in pending_operations:
            try:
                if operation['type'] == 'add':
                    await self.cart_repo.add_to_cart(operation['data'])
                elif operation['type'] == 'update':
                    await self.cart_repo.update_cart_item(operation['data'])
                elif operation['type'] == 'remove':
                    await self.cart_repo.remove_from_cart(operation['item_id'])
                
                self.local_db.remove_pending_operation(operation['id'])
            except Exception as e:
                logger.error(f"Error syncing operation {operation['id']}: {str(e)}")
                continue

    async def _is_online(self) -> bool:
        """Verifica si hay conexión a internet"""
        try:
            await self.aws_client.check_connection()
            return True
        except Exception:
            return False