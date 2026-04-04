from backend.database import SessionLocal, init_db
from backend.models import PriceSnapshot, Product
from datetime import datetime, timezone

def seed():
    init_db()
    db = SessionLocal()
    asins = [
        ("B07SKKG51W", "SKF 6205 Deep Groove Ball Bearing"),
        ("B07PQKK9FB", "SKF 6206 Deep Groove Ball Bearing"),
    ]
    sellers = [
        ("Chennai Bearings", 950.0,  0.0,  True,  True,  "600001"),
        ("Delhi Distributors", 980.0, 0.0, False, False, "600001"),
        ("Mumbai Traders",    1020.0, 50.0, False, True,  "600001"),
    ]
    for asin, title in asins:
        db.merge(Product(asin=asin, title=title))
        for seller, price, ship, is_bb, is_fba, pin in sellers:
            db.add(PriceSnapshot(
                asin=asin, seller=seller, price=price,
                shipping=ship, total_price=price+ship,
                net_price=price+ship, coupon_value=0,
                is_buy_box=is_bb, is_fba=is_fba,
                is_suspicious=False, pin_code=pin,
                dominance_score=price - (50 if is_fba else 0),
                scraped_at=datetime.now(timezone.utc)
            ))
    db.commit()
    db.close()
    print("Seeded 6 snapshot rows into scout.db")

if __name__ == "__main__":
    seed()