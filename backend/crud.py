from sqlalchemy.orm import Session
from models import PriceSnapshot


def compute_buybox_scores(db: Session, asin: str, pin_code: str):
    offers = db.query(PriceSnapshot).filter(
        PriceSnapshot.asin == asin,
        PriceSnapshot.pin_code == pin_code
    ).all()

    valid_offers = []
    for offer in offers:
        if not offer.in_stock:
            offer.is_buybox = False
            continue

        if offer.price is None:
            offer.is_buybox = False
            continue

        delivery_days = offer.delivery_days if offer.delivery_days is not None else 99
        score = offer.price + (delivery_days * 10)
        valid_offers.append((offer, score))

    if not valid_offers:
        db.commit()
        return

    winner, _ = min(valid_offers, key=lambda x: x[1])

    for offer, _ in valid_offers:
        offer.is_buybox = (offer.id == winner.id)

    db.commit()


def create_snapshot(db: Session, data):
    snapshot = PriceSnapshot(**data.dict())
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    compute_buybox_scores(db, snapshot.asin, snapshot.pin_code)
    return snapshot


def get_asins(db: Session):
    rows = db.query(PriceSnapshot.asin).distinct().all()
    return [r[0] for r in rows]


def get_prices(db: Session, asin: str, pin_code: str):
    return db.query(PriceSnapshot).filter(
        PriceSnapshot.asin == asin,
        PriceSnapshot.pin_code == pin_code
    ).all()