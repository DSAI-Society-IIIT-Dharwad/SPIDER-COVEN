from pydantic import BaseModel
from typing import Optional


class PriceSnapshotCreate(BaseModel):
    asin: str
    title: str
    seller: str
    price: Optional[int] = None
    shipping: int = 0
    coupon: int = 0
    net_price: Optional[int] = None
    is_buybox: bool = False
    is_fba: bool = False
    pin_code: str
    in_stock: bool = True
    delivery_days: Optional[int] = None
    scraped_at: str


class PriceSnapshotOut(BaseModel):
    id: int
    asin: str
    title: str
    seller: str
    price: Optional[int]
    shipping: int
    coupon: int
    net_price: Optional[int]
    is_buybox: bool
    is_fba: bool
    pin_code: str
    in_stock: bool
    delivery_days: Optional[int]
    scraped_at: str

    class Config:
        from_attributes = True