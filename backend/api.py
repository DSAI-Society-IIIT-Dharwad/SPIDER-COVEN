from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db, init_db
from backend.models import PriceSnapshot, Alert, Product
import subprocess, os

app = FastAPI(title="Smart Scout API")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/asins")
def get_asins(db: Session = Depends(get_db)):
    rows = db.query(Product).all()
    return [{"asin": r.asin, "title": r.title} for r in rows]

@app.get("/prices/{asin}")
def get_prices(asin: str, pin: str = None, db: Session = Depends(get_db)):
    q = db.query(PriceSnapshot).filter(PriceSnapshot.asin == asin)
    if pin:
        q = q.filter(PriceSnapshot.pin_code == pin)
    rows = q.order_by(desc(PriceSnapshot.scraped_at)).limit(200).all()
    return [r.__dict__ for r in rows]

@app.get("/sellers")
def get_sellers(db: Session = Depends(get_db)):
    rows = db.query(PriceSnapshot.seller).distinct().all()
    return [r[0] for r in rows]

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    rows = db.query(Alert).order_by(desc(Alert.created_at)).limit(50).all()
    return [r.__dict__ for r in rows]

@app.post("/crawl")
def trigger_crawl(asin: str = "B07SKKG51W", pin: str = "600001"):
    # The current directory logic in run_command:
    # We navigate to scraper and run the command
    cmd = f"cd scraper && scrapy crawl offers_spider -a asin={asin} -a pin_code={pin}"
    subprocess.Popen(cmd, shell=True)
    return {"status": "triggered", "asin": asin, "pin": pin}
