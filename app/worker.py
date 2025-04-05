import asyncio
import logging
from app.core.sync_manager import SyncManager
from app.utils.logger import setup_logging

async def sync_worker():
    setup_logging()
    logger = logging.getLogger(__name__)
    sync_manager = SyncManager()
    
    while True:
        try:
            logger.info("Iniciando sincronización...")
            await sync_manager.sync_data()
            logger.info("Sincronización completada")
        except Exception as e:
            logger.error(f"Error en sincronización: {str(e)}")
        
        # Esperar 5 minutos antes de la próxima sincronización
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(sync_worker())