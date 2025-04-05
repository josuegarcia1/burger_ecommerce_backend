from sqlalchemy import Column, String, Float, Boolean, Text
from app.db.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    image_url = Column(String)
    category = Column(String)
    ingredients = Column(Text)
    is_available = Column(Boolean, default=True)