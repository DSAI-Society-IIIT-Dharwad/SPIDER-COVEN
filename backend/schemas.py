from pydantic import BaseModel

class SellerCreate(BaseModel):
    asin: str
    seller_name: str
    price: float
    is_buybox: bool
    delivery_days: int

class SellerResponse(SellerCreate):
    id: int

    class Config:
        orm_mode = True