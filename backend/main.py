from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
import schemas
import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Scout API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/add_seller")
def add_seller(data: schemas.PriceSnapshotCreate, db: Session = Depends(get_db)):
    row = crud.create_snapshot(db, data)
    return {"message": "stored", "id": row.id}


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return crud.get_asins(db)


@app.get("/prices/{asin}", response_model=list[schemas.PriceSnapshotOut])
def get_prices(asin: str, pin_code: str, db: Session = Depends(get_db)):
    return crud.get_prices(db, asin, pin_code)