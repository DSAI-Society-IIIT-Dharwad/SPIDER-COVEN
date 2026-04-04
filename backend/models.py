from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text
from sqlalchemy.sql import func
from backend.database import Base

class Product(Base):
    __tablename__ = "products"
    asin      = Column(String, primary_key=True)
    title     = Column(String)
    added_at  = Column(DateTime, server_default=func.now())

class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    asin             = Column(String, index=True)
    seller           = Column(String)
    price            = Column(Float)
    shipping         = Column(Float, default=0)
    total_price      = Column(Float)
    net_price        = Column(Float)
    coupon_value     = Column(Float, default=0)
    is_buy_box       = Column(Boolean, default=False)
    is_fba           = Column(Boolean, default=False)
    is_suspicious    = Column(Boolean, default=False)
    pin_code         = Column(String, default="600001")
    dominance_score  = Column(Float)
    scraped_at       = Column(DateTime, index=True)

class Alert(Base):
    __tablename__ = "alerts"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    asin           = Column(String, index=True)
    seller         = Column(String)
    alert_type     = Column(String)   # UNDERCUT, PRICE_WAR, BUY_BOX_LOST
    severity       = Column(String)   # HIGH, MED, LOW
    message        = Column(Text)
    winning_gap    = Column(Float)
    created_at     = Column(DateTime, server_default=func.now())