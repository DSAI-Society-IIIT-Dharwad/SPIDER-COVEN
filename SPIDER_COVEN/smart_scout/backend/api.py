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
    cmd = f"cd scraper && scrapy crawl offers_spider -a asin={asin} -a pin_code={pin}"
    subprocess.Popen(cmd, shell=True)
    return {"status": "triggered", "asin": asin, "pin": pin}

@app.post("/analyze/{asin}")
def analyze(asin: str, pin: str = "600001"):
    from backend.intelligence import run_undercut_detection
    run_undercut_detection(asin, pin)
    return {"status": "analysis complete"}

@app.get("/winning_gap/{asin}")
def winning_gap(asin: str, pin: str = "600001", db: Session = Depends(get_db)):
    from backend.intelligence import YOUR_SELLER
    from sqlalchemy import desc
    rows = db.query(PriceSnapshot)\
        .filter(PriceSnapshot.asin == asin,
                PriceSnapshot.pin_code == pin,
                PriceSnapshot.is_suspicious == False)\
        .order_by(desc(PriceSnapshot.scraped_at)).limit(50).all()

    your = [r for r in rows if YOUR_SELLER.lower() in r.seller.lower()]
    comp = [r for r in rows if YOUR_SELLER.lower() not in r.seller.lower()]
    if not your or not comp:
        return {"gap": None, "recommendation": "Not enough data"}

    your_price = min(r.net_price for r in your)
    comp_min   = min(r.net_price for r in comp)
    gap = your_price - comp_min
    return {
        "your_price": round(your_price, 2),
        "competitor_min": round(comp_min, 2),
        "gap": round(gap, 2),
        "recommendation": f"Reduce by ₹{abs(gap):.0f} to regain Buy Box" if gap > 0 else "You hold the lowest net price"
    }
