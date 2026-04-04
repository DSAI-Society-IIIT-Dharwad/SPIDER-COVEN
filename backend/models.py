from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from .database import Base

class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    asin = Column(String, index=True)
    seller_name = Column(String)
    price = Column(Float)
    is_buybox = Column(Boolean)
    delivery_days = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)