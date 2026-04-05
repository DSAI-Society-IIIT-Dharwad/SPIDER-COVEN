from backend.database import SessionLocal
from backend.models import PriceSnapshot, Alert
from sqlalchemy import desc
import os

YOUR_SELLER = os.getenv("YOUR_SELLER_NAME", "YourSellerNameHere")

def compute_dominance_score(price: float, coupon: float, is_fba: bool) -> float:
    logistics_bonus = 50 if is_fba else 0
    return (price - coupon) - logistics_bonus   # lower = stronger

def run_undercut_detection(asin: str, pin_code: str):
    db = SessionLocal()
    try:
        rows = db.query(PriceSnapshot)\
            .filter(PriceSnapshot.asin == asin,
                    PriceSnapshot.pin_code == pin_code,
                    PriceSnapshot.is_suspicious == False)\
            .order_by(desc(PriceSnapshot.scraped_at)).limit(50).all()

        if not rows:
            return

        your_rows = [r for r in rows if YOUR_SELLER.lower() in r.seller.lower()]
        comp_rows = [r for r in rows if YOUR_SELLER.lower() not in r.seller.lower()]

        if not your_rows or not comp_rows:
            return

        your_price = min(r.net_price for r in your_rows)
        comp_min   = min(r.net_price for r in comp_rows)
        comp_seller = min(comp_rows, key=lambda r: r.net_price).seller
        gap = your_price - comp_min

        if gap <= 0:
            return   # you are already cheapest

        pct = gap / your_price
        
        comp_min_row = min(comp_rows, key=lambda r: r.net_price)
        if comp_min_row.stock_left is not None and comp_min_row.stock_left <= 5:
            severity = "LOW"
            msg = f"{comp_seller} is undercutting you by ₹{gap:.0f} ({pct*100:.1f}%) but only has {comp_min_row.stock_left} left in stock. Suggestion: DO NOT lower price. Hold steady."
        else:
            severity = "HIGH" if pct > 0.15 else "MED" if pct > 0.05 else "LOW"
            msg = f"{comp_seller} is undercutting you by ₹{gap:.0f} ({pct*100:.1f}%). Reduce by ₹{gap:.0f} to regain Buy Box."

        alert = Alert(
            asin=asin, seller=comp_seller,
            alert_type="UNDERCUT", severity=severity,
            message=msg, winning_gap=gap
        )
        db.add(alert)
        db.commit()
    finally:
        db.close()
