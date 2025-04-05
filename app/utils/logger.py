import logging
import sys
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                "burger_ecommerce.log",
                maxBytes=1024 * 1024 * 5,  # 5 MB
                backupCount=3
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reducir el nivel de logging para algunas librerías
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)