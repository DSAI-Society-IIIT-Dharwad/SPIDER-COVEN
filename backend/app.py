from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, database, schemas

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Smart Scout Backend Running"}

@app.post("/add_seller")
def add_seller(seller: schemas.SellerCreate, db: Session = Depends(get_db)):

    # 🔍 Check if same seller + asin + price already exists
    existing = db.query(models.Seller).filter(
        models.Seller.asin == seller.asin,
        models.Seller.seller_name == seller.seller_name,
        models.Seller.price == seller.price
    ).first()

    # 🚫 If duplicate → ignore
    if existing:
        return {"status": "ignored", "reason": "duplicate"}

    # ✅ Otherwise insert
    db_seller = models.Seller(**seller.dict())
    db.add(db_seller)
    db.commit()
    db.refresh(db_seller)
    return db_seller

@app.get("/sellers/{asin}")
def get_sellers(asin: str, db: Session = Depends(get_db)):
    return db.query(models.Seller).filter(models.Seller.asin == asin).all()