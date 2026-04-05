import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import PriceSnapshot, Product
from scrapy.exceptions import DropItem
from datetime import datetime, timezone
import redis
import json

class ValidationPipeline:
    def process_item(self, item, spider):
        if not item.get("asin"):
            raise DropItem(f"Missing ASIN in {item}")
        if item.get("price") is not None and float(item.get("price", 0)) <= 0:
            raise DropItem(f"Invalid price in {item}")
        return item

class DeduplicationPipeline:
    def open_spider(self, spider):
        try:
            self.r = redis.Redis(host="localhost", port=6379, db=0)
            self.r.ping()
        except Exception:
            self.r = None   # fallback: no dedup if Redis unavailable
            spider.logger.warning("Redis unavailable — dedup disabled")

    def process_item(self, item, spider):
        if not self.r:
            return item
        key = f"seen:{item.get('asin')}:{item.get('seller')}:{item.get('price')}"
        if self.r.get(key):
            raise DropItem(f"Duplicate: {key}")
        self.r.setex(key, 1800, 1)   # 30-min dedup window
        return item

class HoneypotFilterPipeline:
    def process_item(self, item, spider):
        price = float(item.get("total_price") or 0)
        seller = item.get("seller", "")
        is_suspicious = False

        # Suspiciously round price above ₹5000
        if price > 5000 and price % 1000 == 0:
            is_suspicious = True

        # Seller name looks fake
        fake_patterns = ["test", "seller1", "amazon123"]
        if any(p in seller.lower() for p in fake_patterns):
            is_suspicious = True

        item["is_suspicious"] = is_suspicious
        return item   # flag but never drop — store for analytics

class DatabasePipeline:
    def open_spider(self, spider):
        self.db: Session = SessionLocal()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        try:
            scraped_at = item.get("scraped_at")
            if isinstance(scraped_at, str):
                scraped_at = datetime.fromisoformat(scraped_at)
                
            snapshot = PriceSnapshot(
                asin=item.get("asin"),
                seller=item.get("seller", ""),
                price=float(item.get("price") or 0),
                shipping=float(item.get("shipping") or 0),
                total_price=float(item.get("total_price") or item.get("price") or 0),
                net_price=float(item.get("net_price") or item.get("price") or 0),
                coupon_value=float(item.get("coupon_value") or 0),
                is_buy_box=bool(item.get("is_buy_box", False)),
                is_fba=bool(item.get("is_fba", False)),
                is_suspicious=bool(item.get("is_suspicious", False)),
                pin_code=item.get("pin_code", "600001"),
                dominance_score=float(item.get("dominance_score") or 0),
                stock_left=item.get("stock_left"),
                scraped_at=scraped_at or datetime.now(timezone.utc)
            )
            self.db.add(snapshot)
            # Also upsert product title
            if item.get("title"):
                self.db.merge(Product(asin=item["asin"], title=item["title"]))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            spider.logger.error(f"DB insert failed: {e}")
        return item
